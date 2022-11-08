import numpy as np

def ts(g, nb_cars, delivery_coords):
    v = len(g)
    x = np.zeros((v, v))