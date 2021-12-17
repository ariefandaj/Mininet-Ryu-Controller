import networkx as nx
from networkx.algorithms import tree

def prim (all_links):
    link = all_links
    graph = nx.Graph()
    graph.add_edges_from(link)
    mst = tree.minimum_spanning_edges(graph, algorithm="prim", data=True)
    
    return list(mst)

#hasil mst yg memiliki 9 host
def prim2():
    mst2 = [
        ('3.1', '3.4', {'weight': 0}),
        ('3.1', '3.2', {'weight': 0}),
        ('3.1', '3.5', {'weight': 0}),
        ('3.1', '3.3', {'weight': 0}),
        ('3.2', '2.3', {'weight': 1}),
        ('2.3', '2.1', {'weight': 0}),
        ('2.3', '2.4', {'weight': 0}),
        ('2.3', '2.2', {'weight': 0}),
        ('3.1', '1.1', {'weight': 10}),
        ('1.1', '1.2', {'weight': 0}),
        ('1.1', '1.3', {'weight': 0}),
        ('3.3', '4.1', {'weight': 10}),
        ('4.1', '4.4', {'weight': 0}),
        ('4.1', '4.2', {'weight': 0}),
        ('4.1', '4.3', {'weight': 0}),
        ('4.2', '5.2', {'weight': 1}),
        ('5.2', '5.4', {'weight': 0}),
        ('5.2', '5.1', {'weight': 0}),
        ('5.2', '5.5', {'weight': 0}),
        ('5.2', '5.3', {'weight': 0}),
        ('4.3', '6.2', {'weight': 1}),
        ('6.2', '6.1', {'weight': 0}),
        ('6.2', '6.4', {'weight': 0}),
        ('6.2', '6.6', {'weight': 0}),
        ('6.2', '6.5', {'weight': 0}),
        ('6.2', '6.3', {'weight': 0}),
        ('6.4', '7.1', {'weight': 10}),
        ('7.1', '7.2', {'weight': 0}),
        ('6.5', '9.1', {'weight': 10}),
        ('9.1', '9.2', {'weight': 0}),
        ('6.3', '8.1', {'weight': 10}),
        ('8.1', '8.2', {'weight': 0})
        ]
        
    Graphhhh=nx.Graph()
    Graphhhh.add_edges_from(mst2)
    return list(Graphhhh.edges(data=True))

