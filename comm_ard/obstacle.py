from .robust_serial import write_order, read_i16, Order
from .envoi_commande_arduino import serial_file

def distance_capteur():
    return 90
    write_order(serial_file, Order.READIR)
    dist_capteur = read_i16(serial_file)
    return dist_capteur