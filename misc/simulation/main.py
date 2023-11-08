import constants

from random import seed
from graph import Graph


def main():
    print("GRAPH INIT")
    print(f"NUM NODES: {constants.NUM_NODES}")
    print(f"GRID SIZE: {constants.GRID_SIZE}x{constants.GRID_SIZE}")
    print(f"K: {constants.CONNECTIVITY}")

    seed(constants.RANDOM_SEED)
    graph = Graph(constants.GRID_SIZE, constants.CONNECTIVITY)
    for i in range(1, constants.NUM_NODES + 1):
        graph.add_node(str(i))
    graph.add_pending_nodes()
    graph.connect_nodes()
    graph.print()
    graph.display()


if __name__ == "__main__":
    main()
