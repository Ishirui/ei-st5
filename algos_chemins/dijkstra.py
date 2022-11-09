import numpy as np

def dijkstra(g, a, b):
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

g = [
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
        [3, 2]
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
        [3,1]
    ]
]

#print(dijkstra(g, 0, 2))



        




        


