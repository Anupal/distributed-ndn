from copy import copy
from math import sqrt

import multiprocessing
import socket
import threading
import time
import constants
import re


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

    def __init__(self, label, all_nodes, k, comm, hello_delay, hello_message) -> None:
        self.comm: SocketCommunication = comm
        self.label = label
        self._simulate_physical_layer(all_nodes, k)
        self.hello_delay = hello_delay
        self.hello_message = str(hello_message)

        self.neighbor_table = {}
        self.pit = {}

        self.comm.set_hello_function(self.send_hello)

    def send_hello(self, ip, port):
        self.comm.send(ip, port, self.hello_message)

    def send_hellos(self):
        """
        Loop over k_nearest nodes and send hellos -> label : TCP IP, TCP port
        """

        for node in self.k_nearest:
            ip, port = self.k_nearest[node]
            self.send_hello(ip, port)
            time.sleep(self.hello_delay)

    def callback_hello(self):
        """
        Handle FIB update here.
        """
        self.comm.update_fib()


def euclidean_distance(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


class HelloMessage:
    """
    Class for HELLO, its source label and the issued certificate
    """

    def __init__(self, neighbor_label, ip, port, cert):
        self.certificate = cert
        self.neighbour_label = neighbor_label
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"[{constants.HELLO_ID}][{self.neighbour_label}][{self.ip}][{self.port}][{self.certificate}]"


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
        # TODO use actual cert here
        cert = "ULTRA_CERT"
        hello_message = HelloMessage(neighbor_label=label, ip=address, port=port, cert=cert)

        self.ndn = Network(label, all_nodes, k, comm, hello_delay, hello_message)

    def run(self):
        """
        Main Application loop.
        """

        # Send hello:
        self.ndn.comm.listen()
        self.ndn.send_hellos()
        time.sleep(self.hello_delay + 2)

        # Main loop:
        while True:
            self.ndn.send_hellos()
            self.ndn.callback_hello()
            time.sleep(self.hello_delay)


class FIB:
    """
    Data structure for FIB table. Table is represented as dictionary with the labels being the
    key and the rest being the value in form of instances of the FIB_ROW class
    """

    class FIB_Row:
        def __init__(self, tcp_ip, tcp_port, certificate):
            self.tcp_ip = tcp_ip
            self.tcp_port = tcp_port
            self.certificate = certificate
            self.hello_count = 1

        def increment_hello_count(self):
            self.hello_count += 1

        def decrement_hello_count(self):
            self.hello_count -= 1
            return self.hello_count > 0

    def __init__(self):
        self.table = {}

    def received_hello(self, hello_message: HelloMessage):
        if hello_message.neighbour_label in self.table:
            if not self.table[hello_message.neighbour_label] == constants.MAX_HELLO_COUNT:
                self.table[hello_message.neighbour_label].increment_hello_count()
        else:
            self.table[hello_message.neighbour_label] = self.FIB_Row(hello_message.ip, hello_message.port,
                                                                     hello_message.certificate)

    def update_counts(self):
        for each_key in copy(self.table).keys():
            count_bigger_zero = self.table[each_key].decrement_hello_count()
            if not count_bigger_zero:
                del self.table[each_key]


class SocketCommunication:
    """
    Manages threads for TCP server and clients.
    """

    def __init__(self, address, port) -> None:
        self.address = address
        self.port = port
        self.callbacks = []
        self.fib = FIB()
        self.send_hello = None

    def update_fib(self):
        self.fib.update_counts()

    def set_hello_function(self, send_hello):
        self.send_hello = send_hello

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
        data_type, decoded_data = self._decode_data(data)

        if data_type == 0:
            self.fib.received_hello(decoded_data)
            self.send_hello(decoded_data.ip, decoded_data.port)
        elif data_type == 1:
            print("received data")  # TODO
        elif data_type == 2:
            print("received interest")  # TODO
        # Execute all registered callbacks
        for callback in self.callbacks:
            callback(data)

    def _decode_data(self, data):
        data_array = re.findall(r'[([^]]+]', data)
        if data_array[0] == 0:
            label = data_array[1]
            ip_address = data_array[2]
            port = int(data_array[3])
            cert = data_array[4]
            # TODO: Validate cert here
            if re.match(ip_address, r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'):
                return 0, HelloMessage(neighbor_label=label, ip=ip_address, port=port, cert=cert)
            else:
                raise Exception("Invalid IP address")
        elif data_array[1] == 1:
            return 1, "TODO"
        elif data_array[2] == 2:
            return 2, "TODO"
        else:
            return -1, "DATA GETS IGNORED, SINCE TYPE -1 DOESN'T EXIST"

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
