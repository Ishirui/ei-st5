import numpy as np
from salesman import itineraire, unprecise_index

def quadrillage(n, aretes_cassees):
    g = [[] for i in range(n**2)]
    for i in range(n):
        for j in range(n):
            #on met le graphe dans le bon sens pour que les virages fonctionnent
            if i > 0:
                if [[j, i], [j, i-1]] not in aretes_cassees:
                    g[n*i + j].append([n*(i-1) + j, 1])
            if j < n-1:
                if [[j, i], [j+1, i]] not in aretes_cassees:
                    g[n*i + j].append([n*i +j + 1, 1])            
            if i < n-1:
                if [[j, i], [j, i+1]] not in aretes_cassees:
                    g[n*i + j].append([n*(i+1) +j, 1])
            if j > 0:
                if [[j, i], [j-1, j]] not in aretes_cassees:
                    g[n*i + j].append([n*i + j -1, 1])

    return g

def deplacement_quadrillage(n, start, delivery_coords, before_start, aretes_cassees):
    g = quadrillage(n, aretes_cassees)
    print(g[n*aretes_cassees[0][0][1] + n*aretes_cassees[0][0][0]])
    d_c = [start[1]*n + start[0]] + [i[1]*n + i[0] for i in delivery_coords]
    it_sorties, pos_list = itineraire(g, d_c)
    print(it_sorties, pos_list)
    it_sorties[0] = (unprecise_index(g[pos_list[0]], pos_list[1]) - unprecise_index(g[pos_list[0]], n*before_start[1] + before_start[0]))%len(g[pos_list[0]])
    manoeuvres = []
    y = [i//n for i in pos_list] + [before_start[1]]
    x = [i%n for i in pos_list] + [before_start[0]]
    pos_counter = 0
    ordered_livraison = []
    for i in it_sorties:
        if i == -1:
            manoeuvres.append('livraison')
            ordered_livraison.append([x[pos_counter], y[pos_counter]])
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
                    elif x[pos_counter] < x[pos_counter - 1]:
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
                        else:
                            manoeuvres.append("droite")
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
                    elif x[pos_counter] > x[pos_counter - 1]:
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
                        else:
                            manoeuvres.append("droite")
                            pos_counter += 1  
            elif x[pos_counter] == 0:
                    if y[pos_counter] < y[pos_counter - 1]:
                        if i == 1:
                            manoeuvres.append("milieu")
                            pos_counter += 1
                        else:
                            manoeuvres.append("droite")
                            pos_counter += 1
                    elif y[pos_counter] > y[pos_counter - 1]:
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
                        else:
                            manoeuvres.append("droite")
                            pos_counter += 1                                
            elif x[pos_counter] == n-1:
                    if y[pos_counter] > y[pos_counter - 1]:
                        if i == 1:
                            manoeuvres.append("milieu")
                            pos_counter += 1
                        else:
                            manoeuvres.append("droite")
                            pos_counter += 1
                    elif y[pos_counter] < y[pos_counter - 1]:
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
                        else:
                            manoeuvres.append("droite")
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
    return(manoeuvres, [[x[i],y[i]] for i in range(len(x) - 1)], ordered_livraison)

#def rentrer_au_bercail(n, bercail, aretes_cassees):


#def dictionnaire(n, aretes_cassees):


if __name__ == "__main__":
    print(deplacement_quadrillage(4, [0,0], [[3,3], [2,2], [0,3]], [0,1], [[[0, 3], [0, 2]], [[0,2], [0, 3]], [[3, 3], [2, 3]], [[2, 3], [3, 3]]]))

"""[[[0, 2], [0, 1]], [[0,2], [0, 3]]]"""
                    


                                                              


            
                

            



        
