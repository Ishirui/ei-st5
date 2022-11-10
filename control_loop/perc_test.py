from __future__ import division
import cv2
import numpy as np
import time

from picamera import PiCamera
from picamera.array import PiRGBArray

camera = PiCamera()
camera.resolution = (640//4, 480//4)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=camera.resolution)


frame_source = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)

def perception():

    # Input Image
    image = next(frame_source).array
    #image=cv2.imread("test_photo.jpg")
    image = cv2.flip(image, -1)

    cv2.imshow("Image non traitée", image)

    # Output initializing
    detectOut = 0
    detect_inter = 0
    erreur_orientation = 0

    # Convert to HSV color space
    blur = cv2.blur(image,(5,5))
    _, thresh1 = cv2.threshold(blur,168,255,cv2.THRESH_BINARY)
    hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)

    # Define range of white color in HSV
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([172, 111, 255])
    
    # Threshold the HSV image
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Remove noise
    kernel_erode = np.ones((6,6), np.uint8)
    eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
    kernel_dilate = np.ones((4,4), np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)

    # Find the different contours
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img_contours = np.zeros(dilated_mask.shape)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1] # Sort by area (keep only the biggest one)
    cv2.drawContours(img_contours, contours, -1, (255,0,0), -1)
    print("shapes",dilated_mask.shape,img_contours.shape)

    kernel1 = np.array([[1, 1, 1],
                    [0, 0, 0],
                    [-1, -1, -1]])
    
    horizontal = cv2.filter2D(src=img_contours, ddepth=-1, kernel=kernel1)
    print(horizontal.shape)
    cv2.imshow("horizontal", horizontal)
    cv2.waitKey(0)
    n_horizontal = []

    for row in horizontal.transpose():
        maxi = max(row)
        n_horizontal.append([maxi for _ in row])

    horizontal = np.array(n_horizontal).transpose()
    # Show extracted horizontal lines
    cv2.imshow("n_horizontal", horizontal)
    cv2.waitKey(0)



    if len(contours) > 0: # Si un blob est detectee
        M = cv2.moments(contours[0])
        cx = int(M['m10']/M['m00']) # Abscisse du centre du blob
        erreur_orientation = image.shape[0]/2 - cx
    else:
        detectOut = 1


    # On cherche des "routes" sur 3 des 4 bords de la camera

    bord_gauche = img_contours[:,0].tolist()
    bord_gauche.reverse()
    bord_haut = img_contours[0,:].tolist()
    bord_droit = np.transpose(img_contours[:,-1]).tolist()

    bord = bord_gauche + bord_haut + bord_droit

    roads_detected = 0
    detecte = 0
    for pix in bord:
        if pix >= 200:
            detecte = 1
        if detecte == 1 and pix <= 50:
            roads_detected += 1
            detecte = 0

    if roads_detected >= 2:
        detect_inter = 1
    

    cv2.imshow("Image traitée",img_contours)
    key = cv2.waitKey(1) & 0xFF


    # Clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    return (erreur_orientation,detect_inter,detectOut)




if __name__ == "__main__":
    while True:
        perception()