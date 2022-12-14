from __future__ import division
import cv2
import numpy as np

from picamera import PiCamera
from picamera.array import PiRGBArray

resolution_target = (160, 128)

camera = PiCamera(sensor_mode = 2)
camera.resolution = resolution_target
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=camera.resolution)

brightness_thresh = 0.1

frame_source = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)

def perception(feedback = False):

    # Input Image
    image = next(frame_source).array
    #image = cv2.flip(image, -1)

    if feedback: cv2.imshow("Image non traitée", image)

    # Output initializing
    detectOut = False
    detect_inter = False
    erreur_orientation = 0.

    # Convert to HSV color space
    blur = cv2.blur(image,(10,10))

    _, thresh1 = cv2.threshold(blur,168,255,cv2.THRESH_BINARY)
    hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)

    # Define range of white color in HSV
    lower_white = np.array([0, 0, 80])
    upper_white = np.array([172, 111, 255])
    
    # Threshold the HSV image
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Remove noise
    kernel_erode = np.ones((6,6), np.uint8)
    eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
    kernel_dilate = np.ones((4,4), np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)

    

    # Find the different contours
    _, contours, _ = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img_contours = np.zeros(dilated_mask.shape)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1] # Sort by area (keep only the biggest one)
    cv2.drawContours(img_contours, contours, -1, (255,0,0), -1)

    if feedback: cv2.imshow("Semi-traitée", img_contours)

    if len(contours) > 0: # Si un blob est detectee
        M = cv2.moments(contours[0])
        cx = int(M['m10']/M['m00']) # Abscisse du centre du blob
        erreur_orientation = image.shape[0]/2 - cx
    else:
        detectOut = True


    # # On cherche des "routes" sur 3 des 4 bords de la camera

    # bord_gauche = img_contours[:,0].tolist()
    # bord_gauche.reverse()
    # bord_haut = img_contours[0,:].tolist()
    # bord_droit = np.transpose(img_contours[:,-1]).tolist()

    # bord = bord_gauche + bord_droit

    # roads_detected = 0
    # detecte = 0
    # for pix in bord:
    #     if pix >= 200:
    #         detecte = 1
    #     if detecte == 1 and pix <= 50:
    #         roads_detected += 1
    #         detecte = 0

    # if roads_detected >= 1:
    #     detect_inter = 1
    

    # New version of intersection detection
    
    # expected_corners = 3
    # blur = cv2.blur(image,(6,6))
    # _,thresh1 = cv2.threshold(blur,168,255,cv2.THRESH_BINARY)
    # hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)

    # # Define range of white color in HSV
    # lower_white = np.array([0, 0, 168])
    # upper_white = np.array([172, 111, 255])
    # # Threshold the HSV image
    # mask = cv2.inRange(hsv, lower_white, upper_white)

    # kernel_erode = np.ones((6,6), np.uint8)
    # eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
    # kernel_dilate = np.ones((4,4), np.uint8)
    # dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)
    # gray = np.float32(dilated_mask)

    # dst = cv2.cornerHarris(gray,5,3,0.10)
    # corners = cv2.goodFeaturesToTrack(gray, 5,0.5,20)
    # corners = np.int0(corners)

    # if len(corners) >= expected_corners:
    #     detect_inter = 1

    # Counting brightness in blurred image

    # img_contours_blurred = cv2.blur(img_contours, (50,50))
    # prop_lit_pixels = np.sum(img_contours_blurred)/(255*camera.resolution[0]*camera.resolution[1])

    # if prop_lit_pixels > 0.15:
    #     detect_inter = 1
    # else:
    #     detect_inter = 0

    # print(prop_lit_pixels)

    # if feedback: cv2.imshow("Image traitée",img_contours)
    # key = cv2.waitKey(1) & 0xFF

    # Maxime's detection (edge detection + looking at total horizontal brightness)

    kernel1 = np.array([[1/9, 1/9, 1/9], [0, 0, 0], [-1/9, -1/9, -1/9]])
    horizontal = cv2.filter2D(src = img_contours, ddepth=-1, kernel=kernel1)
    ligne = horizontal.max(axis=0)
    brightness = np.sum(ligne)/(len(ligne)*255)

    detect_inter = brightness > brightness_thresh

    # Clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    if feedback: 
        cv2.imshow("Image traitée", horizontal)
        cv2.waitKey(1)

    return (erreur_orientation,detect_inter,detectOut)




if __name__ == "__main__":
    while True:
        perception(feedback = True)