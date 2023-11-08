import networkx as nx
from random import randint, seed
import matplotlib.pyplot as plt
from math import sqrt


class Node:
    def __init__(self, label, grid_size, x=None, y=None, offset=0) -> None:
        self.label = label
        self.x = x if x else randint(offset, grid_size)
        self.y = y if y else randint(0, grid_size)
        self.neighbors = set()

    def xy(self):
        return (self.x, self.y)

    def add_neighbor(self, label):
        self.neighbors.add(label)

    def remove_neighbor(self, label):
        self.neighbors.remove()

    def __str__(self) -> str:
        return f"label={self.label} x={self.x} y={self.y} neighbors='{' '.join(self.neighbors)}'"


class Graph:
    def __init__(self, grid_size, k) -> None:
        self._graph = nx.Graph()
        self.nodes = {}
        self.grid_size = grid_size
        self.k = k

    def _distance(self, p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def nodes_pos(self):
        return {
            label: (self.nodes[label].x, self.nodes[label].y)
            for label in self.nodes
            if self._graph.has_node(label)
        }

    def add_node(self, label):
        self.nodes[label] = Node(label, self.grid_size)

    def add_pending_nodes(self):
        for label in self.nodes:
            if not self._graph.has_node(label):
                self._graph.add_node(label)

    def print(self):
        for label in self.nodes:
            if self._graph.has_node(label):
                print(self.nodes[label])

    def display(self):
        nx.draw(
            self._graph,
            pos=self.nodes_pos(),
            with_labels=True,
            node_size=300,
            node_color="skyblue",
        )
        plt.show()

    def connect_nodes(self):
        self.add_pending_nodes()

        for label_n1 in self.nodes:
            if len(self.nodes[label_n1].neighbors) < self.k:
                potential_neighbors = []

                for label_n2 in self.nodes:
                    if (
                        label_n1 != label_n2
                        and label_n2 not in self.nodes[label_n1].neighbors
                    ):
                        d = self._distance(
                            self.nodes[label_n1].xy(), self.nodes[label_n2].xy()
                        )
                        potential_neighbors.append((label_n2, d))

                remaining_neighbor_slots = self.k - len(self.nodes[label_n1].neighbors)
                neighbors = sorted(potential_neighbors, key=lambda x: x[1])[
                    :remaining_neighbor_slots
                ]
                for neighbor in neighbors:
                    self._graph.add_edges_from([(label_n1, neighbor[0])])
                    self.nodes[label_n1].neighbors.add(neighbor[0])
                    self.nodes[neighbor[0]].neighbors.add(label_n1)
