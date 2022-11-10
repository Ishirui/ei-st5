from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep

from comm_ard.utils import open_serial_port
from comm_ard.robust_serial import write_order, Order


def setup_camera():
    camera = PiCamera()
    camera.resolution = (640//4, 480//4)
    camera.framerate = 30
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    frame_source = camera.capture_continuous(
        rawCapture, forma='bgr', use_video_port=True)


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

    sleep(2)
    c = 1
    while (c != b''):
        c = serial_file.read(1)
