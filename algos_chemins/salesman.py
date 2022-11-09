import numpy as np
from dijkstra import dijkstra

def simple_graph(g, delivery_coords):
    v = len(delivery_coords)
    res = []
    for i in range(v):
        l = [[0, []] for _ in range(v)]
        for j in range(v):
            if j != i:
                l[j] = dijkstra(g, delivery_coords[i], delivery_coords[j])
        res.append(l)
    return res

def tsp(chain, w, ind, v, simple_g):
    chain.append(ind)
    if len(chain) == v + 1:
        return w, chain
    elif len(chain) == v:
        w_temp = w + simple_g[ind][0][0]
        return tsp(chain, w_temp, 0, v, simple_g)
    else:
        m = np.inf
        best_chain = []
        for i in range(v):
            if i not in chain and simple_g[ind][i][0] > 0:
                w_temp = w + simple_g[ind][i][0]
                w_comp, new_chain = tsp(chain[:], w_temp, i, v, simple_g)
                if w_comp < m:
                    best_chain = new_chain
                    m = w_comp
        return (m, best_chain)

def itineraire(g, delivery_coords):
    v = len(delivery_coords)
    simple_g = simple_graph(g, delivery_coords)

    #print(simple_g[:][:][0])
                
    reponse_tsp =  tsp([], 0, 0, v, simple_g)
    it_points = [simple_g[reponse_tsp[1][v-i-1]][reponse_tsp[1][v-i]][1] for i in range(v)]
    
    position_list = []
    it_exit_numbers = []
    turn_start = it_points[-1][-2]
    for i in it_points:
        turn_pos = i[0]
        turn_end = i[1]
        exit_number = (unprecise_index(g[turn_pos], turn_end) - unprecise_index(g[turn_pos], turn_start))%len(g[turn_pos])
        it_exit_numbers.append(exit_number)
        position_list.append(turn_pos)
        for j in range(len(i) - 2):
            turn_pos = i[j + 1]
            turn_start = i[j]
            turn_end = i[j + 2]
            exit_number = (unprecise_index(g[turn_pos], turn_end) - unprecise_index(g[turn_pos], turn_start))%len(g[turn_pos])
            it_exit_numbers.append(exit_number)
            position_list.append(turn_pos)
        it_exit_numbers.append(-1)
        turn_start = turn_pos
    
    return it_exit_numbers, position_list + [delivery_coords[0]]
    

def unprecise_index(l, x):
    for i in range(len(l)):
        if l[i][0] == x:
            return i
    


""" g = [
    [
        [1, 1],
        [2, 3]
    ],
    [
        [0, 1],
        [2, 1]
    ],
    [
        [0, 3],
        [1,1],
        [3, 2],
        [5, 1]
    ],
    [
        [2,2],
        [4,1],
        [5,1]
    ],
    [
        [3,1]
    ],
    [
        [3,1],
        [2, 1]
    ]
] """


                        
                    


                    



        
                
    
            

                
