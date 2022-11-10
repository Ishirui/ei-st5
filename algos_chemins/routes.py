import numpy as np
from salesman import itineraire

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

def deplacement_quadrillage(n, start, delivery_coords, before_start):
    g = quadrillage(n)
    d_c = [start[1]*n + start[0]] + [i[1]*n + i[0] for i in delivery_coords]
    it_sorties, pos_list = itineraire(g, d_c)
    print(it_sorties, pos_list)
    manoeuvres = []
    y = [i//n for i in pos_list] + [before_start[1]]
    x = [i%n for i in pos_list] + [before_start[0]]
    pos_counter = 0
    for i in it_sorties:
        print(manoeuvres)
        if i == -1:
            manoeuvres.append('livraison')
        elif i == 0:
            manoeuvres.append('demi-tour')
            pos_counter += 1
        else:
            if y[pos_counter] == 0:
                if x[pos_counter] == 0:
                    if x[pos_counter - 1] == x[pos_counter]:
                        manoeuvres.append('droite')
                        pos_counter += 1
                    else:
                        manoeuvres.append('gauche')
                        pos_counter += 1
                elif x[pos_counter] == n-1:
                    if x[pos_counter - 1] == x[pos_counter]:
                        manoeuvres.append('gauche')
                        pos_counter += 1
                    else:
                        manoeuvres.append('droite')
                        pos_counter += 1
                else:
                    if x[pos_counter] > x[pos_counter - 1]:
                        if i == 1:
                            manoeuvres.append("milieu")
                            pos_counter += 1
                        else:
                            manoeuvres.append("droite")
                            pos_counter += 1
                    else:
                        if i == 1:
                            manoeuvres.append("gauche")
                            pos_counter += 1
                        else:
                            manoeuvres.append("milieu")
                            pos_counter += 1
            
            elif y[pos_counter] == n-1:
                if x[pos_counter] == 0:
                    if x[pos_counter - 1] == x[pos_counter]:
                        manoeuvres.append('gauche')
                        pos_counter += 1
                    else:
                        manoeuvres.append('droite')
                        pos_counter += 1
                elif x[pos_counter] == n-1:
                    if x[pos_counter - 1] == x[pos_counter]:
                        manoeuvres.append('droite')
                        pos_counter += 1
                    else:
                        manoeuvres.append('gauche')
                        pos_counter += 1
                else:
                    if x[pos_counter] < x[pos_counter - 1]:
                        if i == 1:
                            manoeuvres.append("milieu")
                            pos_counter += 1
                        else:
                            manoeuvres.append("droite")
                            pos_counter += 1
                    else:
                        if i == 1:
                            manoeuvres.append("gauche")
                            pos_counter += 1
                        else:
                            manoeuvres.append("milieu")
                            pos_counter += 1
            elif x[pos_counter] == 0:
                    if y[pos_counter] > y[pos_counter - 1]:
                        if i == 1:
                            manoeuvres.append("milieu")
                            pos_counter += 1
                        else:
                            manoeuvres.append("droite")
                            pos_counter += 1
                    else:
                        if i == 1:
                            manoeuvres.append("gauche")
                            pos_counter += 1
                        else:
                            manoeuvres.append("milieu")
                            pos_counter += 1            
            elif x[pos_counter] == n-1:
                    if y[pos_counter] > y[pos_counter - 1]:
                        if i == 1:
                            manoeuvres.append("milieu")
                            pos_counter += 1
                        else:
                            manoeuvres.append("droite")
                            pos_counter += 1
                    else:
                        if i == 1:
                            manoeuvres.append("gauche")
                            pos_counter += 1
                        else:
                            manoeuvres.append("milieu")
                            pos_counter += 1
            else:
                if i == 1:
                    manoeuvres.append("gauche")
                    pos_counter += 1
                if i == 2:
                    manoeuvres.append("milieu")
                    pos_counter += 1
                if i == 3:   
                    manoeuvres.append("droite")
                    pos_counter += 1 
    return(manoeuvres)


print(deplacement_quadrillage(5, [1,0], [[3,3], [2,2], [0,3]], [0,0]))


                    


                                                              


            
                

            



        
