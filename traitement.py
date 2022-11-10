from cv2 import imread, cvtColor, COLOR_BGR2GRAY, imshow, waitKey, destroyAllWindows, threshold, THRESH_BINARY, resize, getStructuringElement, erode, MORPH_RECT, GaussianBlur, dilate, SimpleBlobDetector


def traitement(img):
    modif = cvtColor(img, COLOR_BGR2GRAY)
    modif = threshold(modif, 160, 255, THRESH_BINARY)[1]
    modif = erode(modif, getStructuringElement(
        MORPH_RECT, (5, 5)), iterations=3)
    detector = SimpleBlobDetector()
    return modif


img = imread("C:\\Users\\lheur\\Desktop\\photo_2.jpg")
modif = traitement(img)

img = resize(img, (400, 400))
modif = resize(modif, (400, 400))


imshow('og', img)
imshow('modif', modif)
waitKey(0)
destroyAllWindows()
