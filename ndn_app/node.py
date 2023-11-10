from math import sqrt

import multiprocessing
import socket
import threading
import time


class Network:
    """
    Responsibilities:
        * Updates neighbor tables (FIB)
            - When hello is received, check certificate
            - If all is okay then add to FIB
        * Sends hello packets periodically
            - FORMAT: [HELLO|SOURCE_LABEL|CERTIFICATE]
        * Handles received hello packets and authenticates using crypto module
        * Handles Interest and Data packets
        * Updates PIT and Content Store
    """

    def _simulate_physical_layer(self, all_nodes, k):
        """
        Calculates euclidean distances to all other nodes and saves only k nearest neighbors.
        This simulates a physical wireless medium where signal from nearby nodes is visible.
        """

        self.x, self.y = all_nodes[self.label]["xy"]

        # calculate all distances
        all_distances = []
        for label in all_nodes:
            if label != self.label:
                all_distances.append(
                    (
                        label,
                        euclidean_distance((self.x, self.y), all_nodes[label]["xy"]),
                    )
                )

        # filter k nearest based on distance
        k_nearest = sorted(all_distances, key=lambda x: x[1])[:k]

        # save labels and server ip:port information
        self.k_nearest = {
            node[0]: (
                all_nodes[node[0]]["server_ip"],
                all_nodes[node[0]]["server_port"],
            )
            for node in k_nearest
        }
        print(f"NEAREST {k} NODES: {self.k_nearest}")

    def __init__(self, label, all_nodes, k, comm) -> None:
        self.comm: SocketCommunication = comm
        self.label = label
        self._simulate_physical_layer(all_nodes, k)

        self.neighbor_table = {}
        self.pit = {}

        self.comm.register_callback(self.hello_handler)
        # self.comm.register_callback(self.data_handler)
        # self.comm.register_callback(self.interest_handler)

    def send_hello(self):
        ...

    def send_hellos(self):
        """
        Loop over k_nearest nodes and send hellos -> label : TCP IP, TCP port
        """

        for node in self.k_nearest:
            ip, port = self.k_nearest[node]
            self.comm.send(ip, port, "hello")

    def hello_handler(self, data):
        """
        Callback for hello packets. This will be called by SocketCommunication object.
        This will handle FIB update here.
        """

        print("Hello handler: data=", data)

    def interest_handler(self, data):
        """
        Callback for interest packets. This will be called by SocketCommunication object.
        This will handle PIT updates and interest propagation.
        """

        print("Interest handler: data=", data)

    def data_handler(self, data):
        """
        Callback for data packets. This will be called by SocketCommunication object.
        This will handle PIT updates and data propagation.
        """

        print("Data handler: data=", data)


def euclidean_distance(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


class Node(multiprocessing.Process):
    """
    Independent process responsible for covering a Sensor/Actuator

    Integrates:
        * Control plane
        * Data plane
        * Sensor/Actuator
    """

    def __init__(self, label, address, port, all_nodes, k, hello_delay):
        super().__init__()
        self.label = label
        self.hello_delay = hello_delay

        comm = SocketCommunication(address, port)
        self.ndn = Network(label, all_nodes, k, comm)

    def run(self):
        """
        Main Application loop.
        """

        self.ndn.comm.listen()

        while True:
            self.ndn.send_hellos()
            time.sleep(self.hello_delay)


class SocketCommunication:
    """
    Manages threads for TCP server and clients.
    """

    def __init__(self, address, port) -> None:
        self.address = address
        self.port = port
        self.callbacks = []

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def send(self, dest_address, dest_port, data):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"Sending message '{data}' to {(dest_address, dest_port)}")
        try:
            client_socket.connect((dest_address, dest_port))
        except Exception:
            print(f"Can't connect to {(dest_address, dest_port)}")
        else:
            client_socket.send(data.encode("utf-8"))

    def _handle_incoming_packet(self, peer_connection, peer_address):
        """
        Decodes received data and passes it to all registered callbacks.

        """
        data = peer_connection.recv(1024).decode("utf-8")
        print(f"Received message '{data}' from {peer_address}")

        # Execute all registered callbacks
        for callback in self.callbacks:
            callback(data)

    def _listen_thread(self):
        """
        Thread to listen for connections.
        Each new connection is handled in a separate thread.
        """

        while True:
            peer_connection, peer_address = self.server_socket.accept()
            client_handler = threading.Thread(
                target=self._handle_incoming_packet,
                args=(peer_connection, peer_address),
            )
            client_handler.start()

    def listen(self):
        """
        Setup TCP server and start listener thread.
        """
        print(f"Listening on {self.address}:{self.port}")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.address, self.port))
        self.server_socket.listen(5)
        threading.Thread(target=self._listen_thread).start()
