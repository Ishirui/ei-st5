from .robust_serial import write_order, read_i16, Order
from .transmit import serial_file

def distance_capteur():
    write_order(serial_file, Order.READIR)
    dist_capteur = read_i16(serial_file)
    return dist_capteur