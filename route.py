from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
from traitement import traitement
from comm_ard.utils import open_serial_port
from comm_ard.robust_serial import write_order, Order
from comm_ard.envoi_commande_arduino import transmit
import numpy as np

#############################################


def main():

    # On récupère l'image depuis la caméra, on la traite (cf traitement.py)

    image = next(frame_source).array
    image = traitement(image)

    # L'indice sera l'endroit où est la ligne blanche, -1 veut dire qu'il n'y a pas de ligne blanche en vue

    index_lb = -1

    # On récupère l'indice de la ligne blanche avec la moyenne des indices des pixels blancs seulement au milieu de la caméra (j'ai pas su faire plus malin)

    MAX = np.max(image[middle_y][:])
    WHERE = np.where(image[middle_y][:] == MAX)
    try_index = int(np.mean(WHERE[0]))

    # on vérifie qu'il s'agit bien d'un pixel blanc et non pas d'un noir

    if image[middle_y][try_index] > 200:
        index_lb = try_index

    # index_lb est positif s'il a été affecté dans le bloc if ci-dessus

    if index_lb >= 0:
        transmit(0, 0)
        w = 2*(middle_x - index_lb)/camera.resolution[0] * rot
        transmit(v, w)
    else:
        transmit(v, 0)

    # cette ligne est nécessaire pour que la caméra marche (je sais pas pourquoi)

    rawCapture.truncate(0)


if __name__ == '__main__':

    ################################################################################################
    # connection à l'arduino
    ################################################################################################

    global serial_file
    try:
        # Open serial port (for communication with Arduino)
        serial_file = open_serial_port(baudrate=115200)
    except Exception as e:
        print('exception')
        raise e

    is_connected = False
    # Initialize communication with Arduino
    while not is_connected:
        print("Trying connection to Arduino...")
        write_order(serial_file, Order.HELLO)
        bytes_array = bytearray(serial_file.read(1))
        if not bytes_array:
            sleep(2)
            continue
        byte = bytes_array[0]
        if byte in [Order.HELLO.value, Order.ALREADY_CONNECTED.value]:
            is_connected = True
            print('connecté')

    ################################################################################################
    # Définition des variables dont on se sert, initialisation de la caméra
    ################################################################################################

    middle_x = 160//2
    middle_y = 128//2

    camera = PiCamera()
    camera.resolution = (160, 128)
    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    frame_source = camera.capture_continuous(
        rawCapture, format="bgr", use_video_port=True)

    rot = 10
    v = 0.2

    # c'est tipar

    while True:
        main()
