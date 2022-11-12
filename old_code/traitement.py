import cv2


def traitement(img):

    # conversion en noir et blanc

    modif = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # seuil pour garder seulement la ligne blanche

    modif = cv2.threshold(modif, 200, 255, cv2.THRESH_BINARY)[1]

    return modif


###################################################################
# zone pour tester le traitement
###################################################################

# img = cv2.imread("C:\\Users\\lheur\\Desktop\\p1.jpg")
# modif = traitement(img)

# img = cv2.resize(img, (400, 400))
# modif = cv2.resize(modif, (400, 400))


# cv2.imshow('og', img)
# cv2.imshow('modif', modif)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
