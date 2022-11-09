from __future__ import division
import cv2
import numpy as np
import time

from picamera import PiCamera

camera=PiCamera()

def test_camera():
    global camera
    camera.resolution= (100,(240/360)*100)
    camera.framerate = 24
    output = np.empty((240, 320, 3), dtype=np.uint8)
    camera.capture(output, 'rgb')
    output = output.reshape((112, 128, 3))
    output = output[:100, :100, :]
    return output

#PRENDRE PHOTO

def perception():
# Input Image

    image=test_camera()


     
    scale_percent = 100 # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    image = cv2.flip(image, -1)

    detectOut=0
    detect_inter=0
    erreur_orientation=0

    # Convert to HSV color space

    blur = cv2.blur(image,(5,5))
    #ret,thresh1 = cv2.threshold(image,127,255,cv2.THRESH_BINARY)
    ret,thresh1 = cv2.threshold(blur,168,255,cv2.THRESH_BINARY)
    hsv = cv2.cvtColor(thresh1, cv2.COLOR_RGB2HSV)

    # Define range of white color in HSV
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([172, 111, 255])
    # Threshold the HSV image
    mask = cv2.inRange(hsv, lower_white, upper_white)
    #cv2.imwrite('out_test.png', mask)
    # Remove noise
    kernel_erode = np.ones((6,6), np.uint8)

    eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
    kernel_dilate = np.ones((4,4), np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)

    # Find the different contours
    #contours,hierarchy= cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    im2,contours, hierarchy = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img_contours = np.zeros(dilated_mask.shape)
    cv2.drawContours(img_contours, contours, -1, (255,0,0), 3)
    # Sort by area (keep only the biggest one)

    #cv2.imwrite('out_test.png', im2)
    #print (len(contours))
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]


    if len(contours) > 0:
        M = cv2.moments(contours[0])
        # Centroid
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        #print("Centroid of the biggest area: ({}, {})".format(cx, cy))
        erreur_orientation = image.shape[0]/2-cx
    else:
        detectOut=1


    #edge detection
    A=dilated_mask[:,0].tolist()
    A.reverse()
    B=dilated_mask[0,:].tolist()
    C=np.transpose(dilated_mask[:,-1]).tolist()
    Grande_Liste=A+B+C
    hits=0
    detecte=0
    for pix in Grande_Liste:
        if pix>=200:
            detecte=1
        if detecte==1 and pix<=50:
            hits+=1
            detecte=0
    #print("hits : ",hits)
    if hits >= 2:
        detect_inter=1
        #prend une photo de l'intersection




   
    return (erreur_orientation,detect_inter,detectOut)


