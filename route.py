from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
from traitement import traitement
from comm_ard.utils import open_serial_port
from comm_ard.robust_serial import write_order, Order, write_i8

#############################################

middle_x = 0
middle_y = 0
middle = 0
left = 0
right = 0

v = 0.15


def setup_camera():
    camera = PiCamera()
    camera.resolution = (640//4, 480//4)
    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size = camera.resolution)


def setup():
    middle_x = 640//8
    middle_y = 480//8


def connect_to_arduino():
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


def main():
    image = camera.capture(rawCapture, format ='rgb')
    image = traitement(rawCapture)
    Sum_middle = []
    for i in range(len(rawCapture[:][middle_y][:])):
        Sum_middle.append(sum(rawCapture[i][middle_y]))
    left = Sum[:middle_x].index(max(Sum_middle[:middle_x]))
    right = Sum[middle_x:].index(max(Sum_middle[middle_x:]))
    middle = (left+right)/2
    erreur = middle_x - middle
    transmit(v, erreur * v_max)


v_max = 0.45  # m.s-1     //VALEUR DONNEE POUR LES ACCUS//
# Paramètres mécaniques
K = 0.17


def transmit(v, w):
    # on va dire au moteurs qu'on les modifie
    write_order(serial_file, Order.MOTOR)

    v_droite = v + K*w
    v_gauche = v - K*w
    if v_droite > v_max:
        v_droite = v_max
    if v_gauche > v_max:
        v_gauche = v_max
    if v_droite < -v_max:
        v_droite = -v_max
    if v_gauche < -v_max:
        v_gauche = -v_max

    # il faut remettre la valeur de la vitesse entre 0 et 100%
    write_i8(serial_file, int(v_droite/v_max * 100))  # moteur droit
    write_i8(serial_file, int(v_gauche/v_max * 100))  # moteur gauche


if __name__ == '__main__':
    setup()
    setup_camera()
    connect_to_arduino()
    while True:
        main()
