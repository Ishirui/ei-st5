import cv2


def traitement(img):
    modif = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    modif = cv2.threshold(modif, 170, 255, cv2.THRESH_BINARY)[1]
    #modif = cv2.erode(modif, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=1)
    return modif


# img = cv2.imread("C:\\Users\\lheur\\Desktop\\p1.jpg")
# modif = traitement(img)

# img = cv2.resize(img, (400, 400))
# modif = cv2.resize(modif, (400, 400))


# cv2.imshow('og', img)
# cv2.imshow('modif', modif)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
