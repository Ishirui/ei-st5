import numpy as np


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

def dijkstra(g, a, b):
    #Prend une liste d'adjacence
    v = len(g)
    node_dist = [np.inf for i in range(v)]
    to_be_visited = [a]
    unvisited = [True for i in range(v)]
    node_dist[a] = 0
    unfinished = True
    while unfinished:
        if to_be_visited == []:
            unfinished = False
        else:
            node = to_be_visited.pop(0)
            unvisited[node] = False
            for i in g[node]:
                if unvisited[i[0]]:
                    to_be_visited.append(i[0])   
                node_dist[i[0]] = min(node_dist[node] + i[1], node_dist[i[0]])
    
    res = [b]
    unfinished = True
    d = node_dist[b]
    for _ in range(v):
        if unfinished:
            n = res[-1]
            for i in g[n]:
                if node_dist[i[0]] + i[1] == d:
                    d = node_dist[i[0]]
                    n = i[0]
        
            res.append(n)
            unfinished =  (n != a)

    return node_dist[b], res

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

def get_paths_between_nodes(g, delivery_coords):
    v = len(delivery_coords)
    simple_g = simple_graph(g, delivery_coords)

    #print(simple_g[:][:][0])
                
    reponse_tsp =  tsp([], 0, 0, v, simple_g)
    it_points = [simple_g[reponse_tsp[1][v-i-1]][reponse_tsp[1][v-i]][1] for i in range(v)]

    return it_points

def convert_node_to_coords(n, node):
    x = node % n
    y = node // n

    return x,y

def convert_coords_to_node(n, coords):
    x,y = coords[0], coords[1]
    return n*y+x

def get_cardinals(n, node_paths):
    res = []
    for delivery in node_paths:
        new_deliv = []
        for prev_node, node in zip(delivery, delivery[1:]):
            old_x, old_y = convert_node_to_coords(n, prev_node)
            new_x,new_y = convert_node_to_coords(n, node)

            if new_x-old_x == 1:
                cardinal_dir = "e"
            elif new_x-old_x == -1:
                cardinal_dir = "w"
            elif new_y-old_y == 1:
                cardinal_dir = "n"
            elif new_y-old_y == -1:
                cardinal_dir = "s"

            new_deliv.append(cardinal_dir)
        res.append(new_deliv)

    return res


card_movement_translation_matrix = \
    {"n":{"n":"f", "s":"b", "e":"d", "w":"g"},\
    "s":{"n":"b", "s":"f", "e":"g", "w":"d"},\
    "e":{"n":"g", "s":"d", "e":"f", "w":"b"},\
    "w":{"n":"d", "s":"g", "e":"b", "w":"f"}\
    }

def get_movements(cardinals, start_cardinality):
    res = []
    last_cardinality = start_cardinality
    for delivery in cardinals:
        new_deliv = []
        for prev_card, card in zip([last_cardinality]+delivery, delivery):
            movement = card_movement_translation_matrix[prev_card][card]
            new_deliv.append(movement)
            last_cardinality = card
        res.append(new_deliv)

    return res

def add_stops(movements):
    res = []
    for l in movements:
        res = res + l
        res.append("stop")
    return res

def generate_movements(n, start_pos, start_card, delivery_coords):
    g = quadrillage(n, delivery_coords)
    d_c = [convert_coords_to_node(n, start_pos)] + [convert_coords_to_node(n, coords) for coords in delivery_coords]
    it_sorties = get_paths_between_nodes(g, d_c)

    cardinals = get_cardinals(n, it_sorties)
    movements = get_movements(cardinals, start_card)
    movs = add_stops(movements)

    return movs


if __name__ == "__main__":
    n = 4
    g = quadrillage(n, [[[0,0],[1,0]]])
    delivery_coords = [[0,1],[1,1]]
    start = [0,0]
    d_c = [start[1]*n + start[0]] + [i[1]*n + i[0] for i in delivery_coords]
    it_sorties = get_paths_between_nodes(g, d_c)
    movs = add_stops(get_movements(get_cardinals(n, it_sorties), "n"))

    print(movs)