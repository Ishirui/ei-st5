# INITIALISATION DES FONCTIONS A IMPORTER UTILES


# from stateflow import fct_de_robin_et_pl  # //A MODIFIER\\

from robust_serial import write_order, Order, write_i8, write_i16, read_i16

from utils import open_serial_port

serial_file = open_serial_port(baudrate=115200)


v_max = 0.45  # m.s-1     //A MODIFIER\\

R = 3
r = 1
###################################################


def envoi_commande(v, w):
    # appel fonction stateflow  # //A MODIFIER\\

    # on va dire au moteurs qu'on les modifie
    write_order(serial_file, Order.MOTOR)

    v_droite = v + w
    v_gauche = v - w

    # il faut remettre la valeur de la vitesse entre 0 et 100
    write_i8(serial_file, v_droite/v_max * 100)  # moteur droit
    write_i8(serial_file, v_gauche/v_max * 100)  # moteur gauche


def utilisation_capteurs():
    read_i16(serial_file)  # on lit ce que l'arduino envoie
