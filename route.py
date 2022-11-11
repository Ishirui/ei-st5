from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
from traitement import traitement
from comm_ard.utils import open_serial_port
from comm_ard.robust_serial import write_order, Order, write_i8
from comm_ard.envoi_commande_arduino import transmit
from numpy import where

#############################################


def main():
    image = next(frame_source).array
    image = traitement(image)

    left = -1
    right = -1
    middle = middle_x

    index = -1

    try_index = where(image[middle_y][:])[0][0]

    if image[middle_y][try_index] > 200:
        index = try_index

    if index > 0:
        w = (middle - index) * rot
        transmit(v, w)
    else:
        transmit(v, 0)

    # try_left = where(image[middle_y][:middle_x] ==
    #                  max(image[middle_y][:middle_x]))[0][0]
    # try_right = where(image[middle_y][middle_x:] ==
    #                   max(image[middle_y][middle_x:]))[0][0]
    # if image[middle_y][left] > 200:
    #     left = try_left
    # if image[middle_y][middle_x+right] > 200:
    #     right = try_right
    # if left != -1 and right != -1:
    #     middle = (left + right)/2
    # if abs(middle_x-middle) > 25:
    #     transmit(0.15, (middle_x - middle)/camera.resolution[0] * rot)
    # else:
    #     transmit(0.15, 0)
    rawCapture.truncate(0)


if __name__ == '__main__':

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

    middle_x = 160//2
    middle_y = 128//2

    camera = PiCamera()
    camera.resolution = (160, 128)
    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    frame_source = camera.capture_continuous(
        rawCapture, format="bgr", use_video_port=True)

    rot = 0.2
    v = 0.2
    while True:
        main()
