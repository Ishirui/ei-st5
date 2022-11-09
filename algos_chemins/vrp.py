import numpy as np
from dijkstra import dijkstra
from salesman import simple_graph, tsp
from routes import quadrillage

def itineraires_flotte(g, start, delivery_coords, nb_cars):
    v = len(delivery_coords) + nb_cars
    d_c = [start for _ in range(nb_cars)] + delivery_coords
    simple_g = simple_graph(g, d_c)

    res_vrp = tsp([], 0, 0, v, simple_g)
    print(res_vrp)
    it_points = [simple_g[res_vrp[1][v-i-1]][res_vrp[1][v-i]][1] for i in range(v)]
    return it_points
    
    
    
g = quadrillage(4)

print(itineraires_flotte(g, 0, [7, 4, 3], 2))

