from robust_serial import write_order, read_i16

def distance_capteur():
    write_order(serial_file, Order.READIR)
    dist_capteur = read_i16(serial_file)
    return dist_capteur