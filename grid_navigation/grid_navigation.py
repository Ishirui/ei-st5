import numpy as np


def quadrillage(n, aretes_cassees):
    g = [[] for i in range(n**2)]
    for i in range(n):
        for j in range(n):
            #on met le graphe dans le bon sens pour que les virages fonctionnent
            if i > 0:
                if ((j, i), (j, i-1)) not in aretes_cassees:
                    g[n*i + j].append([n*(i-1) + j, 1])
            if j < n-1:
                if ((j, i), (j+1, i)) not in aretes_cassees:
                    g[n*i + j].append([n*i +j + 1, 1])            
            if i < n-1:
                if ((j, i), (j, i+1)) not in aretes_cassees:
                    g[n*i + j].append([n*(i+1) + j, 1])
            if j > 0:
                if ((j, i), (j-1, i)) not in aretes_cassees:
                    g[n*i + j].append([n*i + j - 1, 1])

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

def simple_graph(g, delivery_nodes):
    v = len(delivery_nodes)
    print("delivery_nodes =",delivery_nodes)
    start_node = delivery_nodes[0]
    end_node = delivery_nodes[-1] #Only really corresponds to the end node in the case of end_node != start_node
    start_node = delivery_nodes[0]
    end_node = delivery_nodes[-1] #Only really corresponds to the end node in the case of end_node != start_node

    res = []
    for i in range(v):
        l = [(0, []) for _ in range(v)]
        for j in range(v):
            if j != i:
                if delivery_nodes[i] == -1:
                    if delivery_nodes[j] == start_node:
                        l[j] = (0, [start_node, -1])
                    elif delivery_nodes[j] == end_node:
                        l[j] = (0, [end_node, -1])
                    else:
                        l[j] = (np.inf, [])
                elif delivery_nodes[j] == -1:
                    if delivery_nodes[i] == start_node:
                        l[j] = (0, [-1, start_node])
                    elif delivery_nodes[i] == end_node:
                        l[j] = (0, [-1, end_node])
                    else:
                        l[j] = (np.inf, [])
                else:
                    l[j] = dijkstra(g, delivery_nodes[i], delivery_nodes[j])
                    
        res.append(l)

    # if -1 in delivery_nodes:
    #     res[0][-1] = (0, [start_node, -1, end_node])
    #     res[-1][0] = (0, [end_node, -1, start_node])
    
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
            # # if i not in chain and simple_g[ind][i][0] > 0:
            if i not in chain and ind != i:
                w_temp = w + simple_g[ind][i][0]
                if w_temp == np.inf:
                    w_comp = np.inf
                else:
                    w_comp, new_chain = tsp(chain[:], w_temp, i, v, simple_g)
                if w_comp < m:
                    best_chain = new_chain
                    m = w_comp
        return (m, best_chain)

def get_paths_between_nodes(g, delivery_nodes):
    v = len(delivery_nodes)
    simple_g = simple_graph(g, delivery_nodes)

    #print(simple_g[:][:][0])
                
    reponse_tsp = tsp([], 0, 0, v, simple_g)
    
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

            print(old_x, new_x, old_y, new_y)

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

def super_flatten(l):
    res = []
    for sublist in l[:-1]:
        res = res + sublist[:-1]
    res = res + l[-1]
    return res

def add_stops(movements):
    res = []
    for l in movements:
        res = res + l
        res.append("stop")
    res[-1] = 'fin'
    return res

def generate_movements(n, start_pos, end_pos, start_card, delivery_coords, aretes_cassees):
    aretes_cassees = aretes_cassees + [(y,x) for (x,y) in aretes_cassees]
    g = quadrillage(n, aretes_cassees)
    start_node = convert_coords_to_node(n, start_pos)
    end_node = convert_coords_to_node(n, end_pos)
    delivery_nodes = [start_node]
    if len(delivery_coords)>0:
        delivery_nodes= delivery_nodes+[convert_coords_to_node(n, coords) for coords in delivery_coords]
    if start_pos != end_pos:
        delivery_nodes.append(-1)
        delivery_nodes.append(end_node)
    
    it_sorties = get_paths_between_nodes(g, delivery_nodes)

    print(it_sorties)

    if start_pos != end_pos:

        if -1 in it_sorties[0] and -1 in it_sorties[1]:
            it_sorties = it_sorties[2:]
        elif -1 in it_sorties[-1] and -1 in it_sorties[-2]:
            it_sorties = it_sorties[:-2]
        else:
            it_sorties = it_sorties[1:-1]

        if it_sorties[0][0] == end_node:
            it_sorties = [list(reversed(path)) for path in list(reversed(it_sorties))]

    node_coords_to_follow = super_flatten([[convert_node_to_coords(n, node) for node in delivery] for delivery in it_sorties])
    #nodes_to_follow = [path[1:] for path in it_sorties]
    #pos_list = [start_pos] + [convert_node_to_coords(n, node) for node in nodes_to_follow]

    ordered_deliveries = sorted(delivery_coords, key=lambda x: node_coords_to_follow.index(x))

    print(delivery_coords)

    cardinals = get_cardinals(n, it_sorties)
    movements = get_movements(cardinals, start_card)
    movs = add_stops(movements)
    return movs, ordered_deliveries


if __name__ == "__main__":
    n = 5
    aretes_cassees = [((1,0), (0,0))]
    delivery_coords = []

    movs = generate_movements(n, (1,0), (0,0), "e", delivery_coords, aretes_cassees)

    print(movs)