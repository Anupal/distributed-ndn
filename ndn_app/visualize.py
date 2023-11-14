import networkx as nx
import matplotlib.pyplot as plt
from constants import NODES, MINIMUM_NEIGHBORS
from node import euclidean_distance
from pprint import pprint

graph = nx.Graph()

neighbor_dict = {}

# add nodes to graph and calculate knn
for node_id in NODES:
    graph.add_node(node_id)

    knn_candidates = []
    for nei_id in NODES:
        if node_id != nei_id:
            d = euclidean_distance(NODES[node_id]["xy"], NODES[nei_id]["xy"])
            knn_candidates.append((nei_id, d))

    knn = [nei[0] for nei in sorted(knn_candidates, key=lambda x: x[1])][
        :MINIMUM_NEIGHBORS
    ]
    neighbor_dict[node_id] = knn

pprint(neighbor_dict)

# connect edges
for node_id in neighbor_dict:
    edges = [(node_id, nei_id) for nei_id in neighbor_dict[node_id]]
    graph.add_edges_from(edges)

# visualize
nodes_pos = {node_id: NODES[node_id]["xy"] for node_id in NODES}
nx.draw(
    graph,
    pos=nodes_pos,
    with_labels=True,
    node_size=300,
    node_color="skyblue",
)
plt.show()
