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
    
    # Add nodes to the graph and optionally export their certificates
    for i in range(1, constants.NUM_NODES + 1):
        node_label = str(i)
        graph.add_node(node_label)
        
        # Optional: Export each node's certificate to a file
        certificate_filename = f"node_{node_label}_certificate.pem"
        graph.nodes[node_label].export_certificate(certificate_filename)
    
    # Connect the nodes as per the graph logic. This will now also simulate encrypted and signed communication.
    graph.connect_nodes()
    
    # Print the graph nodes and display the graph
    graph.print()
    graph.display()

if __name__ == "__main__":
    main()

