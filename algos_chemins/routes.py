import numpy as np
#from salesman import itineraire

def quadrillage(n):
    g = [[] for i in range(n**2)]
    for i in range(n):
        for j in range(n):
            #on met le graphe dans le bon sens pour que les virages fonctionnent
            if i > 0:
                g[n*i + j].append([n*(i-1) + j, 1])
            if j < n-1:
                g[n*i + j].append([n*i +j + 1, 1])            
            if i < n-1:
                g[n*i + j].append([n*(i+1) +j, 1])
            if j > 0:
                g[n*i + j].append([n*i + j -1, 1])

    return g

def deplacement_quadrillage(n, delivery_coords):
    g = quadrillage(n)
    it_points = itineraire(g, delivery_coords)


        
