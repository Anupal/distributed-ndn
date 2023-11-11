from copy import copy
from math import sqrt

import multiprocessing
import socket
import threading
import time
import constants
import re


class InterestMessage:
    """
    Class for INTEREST, data address, its source label and retry index.
    """

    def __init__(self, data_address, label, retry_index):
        self.data_address = data_address
        self.label = label
        self.retry_index = retry_index

    def get_string(self):
        return f"[2][{self.label}][{self.data_address}][{self.retry_index}]"


class HelloMessage:
    """
    Class for HELLO, its source label and the issued certificate
    """

    def __init__(self, neighbor_label, ip, port, cert):
        self.certificate = cert
        self.label = neighbor_label
        self.ip = ip
        self.port = port

    def get_string(self, ack=False):
        id = constants.HELLO_ID
        if ack:
            id = constants.HELLO_ACK_ID
        return f"[{id}][{self.label}][{self.ip}][{self.port}][{self.certificate}]"


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

        def __repr__(self) -> str:
            return f"(comm={self.tcp_ip}:{self.tcp_port} count={self.hello_count})"

        def increment_hello_count(self):
            self.hello_count += 1

        def decrement_hello_count(self):
            self.hello_count -= 1
            return self.hello_count > 0

    def __init__(self):
        self.table = {}

    def __repr__(self) -> str:
        return ", ".join([f"({self.table[row]})" for row in self.table])

    def received_hello(self, hello_message: HelloMessage):
        if hello_message.label in self.table:
            if self.table[hello_message.label].hello_count <= constants.MAX_HELLO_COUNT:
                self.table[hello_message.label].increment_hello_count()
        else:
            self.table[hello_message.label] = self.FIB_Row(
                hello_message.ip, hello_message.port, hello_message.certificate
            )

    def update_counts(self):
        """
        Decrement all hello counts in FIB.
        """
        for each_key in copy(self.table):
            count_bigger_zero = self.table[each_key].decrement_hello_count()
            if not count_bigger_zero:
                del self.table[each_key]


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
        self.hello_message = hello_message

        self.neighbor_table = FIB()
        self.pit = {}

        self.comm.register_callback(self.hello_handler)
        # self.comm.register_callback(self.data_handler)
        self.comm.register_callback(self.interest_handler)

    def send_hello(self, ip, port):
        self.comm.send(ip, port, self.hello_message.get_string())

    def send_hello_ack(self, ip, port):
        self.comm.send(ip, port, self.hello_message.get_string(ack=True))

    def send_hellos(self):
        """
        Loop over k_nearest nodes and send hellos -> label : TCP IP, TCP port
        """

        for node in self.k_nearest:
            ip, port = self.k_nearest[node]
            self.send_hello(ip, port)

    def originate_interest(self, data_address, retry_index):
        """
        Introduce an interest packet in the network. This node will become the originator.
        """
        payload = InterestMessage(data_address, self.label, retry_index).get_string()
        for neighbor_label in copy(self.neighbor_table.table):
            print(f"*** Sending interest to neighbor {neighbor_label} ***")
            self.comm.send(
                self.neighbor_table.table[neighbor_label].tcp_ip,
                self.neighbor_table.table[neighbor_label].tcp_port,
                payload,
            )

    def forward_interests(self, data_address, retry_index, ignore_neighbor=""):
        """
        Go through FIB table and forward interests to all neighbors except ignore_neighbor which
        forwarded the interest to us.
        """
        payload = InterestMessage(data_address, self.label, retry_index).get_string()
        for neighbor_label in copy(self.neighbor_table.table):
            if neighbor_label != ignore_neighbor:
                print(f"*** Forwarding interest to neighbor {neighbor_label} ***")
                self.comm.send(
                    self.neighbor_table.table[neighbor_label].tcp_ip,
                    self.neighbor_table.table[neighbor_label].tcp_port,
                    payload,
                )

    def _decode_data(self, data):
        data_array = re.findall(r"\[([^\]]+)\]", data)
        if data_array[0] == "0" or data_array[0] == "4":
            label = int(data_array[1])
            ip_address = data_array[2]
            port = int(data_array[3])
            cert = data_array[4]
            # TODO: Validate cert here
            data_type = int(data_array[0])
            return data_type, HelloMessage(
                neighbor_label=label, ip=ip_address, port=port, cert=cert
            )
        elif data_array[0] == "1":
            return 1, "TODO"
        elif data_array[0] == "2":
            label = int(data_array[1])
            data_address = data_array[2]
            retry_index = int(data_array[3])
            data_type = int(data_array[0])
            return 2, InterestMessage(data_address, label, retry_index)
        else:
            return -1, "DATA GETS IGNORED, SINCE TYPE -1 DOESN'T EXIST"

    def hello_handler(self, data):
        """
        Callback for hello packets. This will be called by SocketCommunication object.
        This will handle FIB update here.
        """
        data_type, message = self._decode_data(data)

        if data_type == 0 or data_type == 4:
            print("Hello handler: data=", data)

            self.neighbor_table.received_hello(message)
            if data_type == 0:
                self.send_hello_ack(message.ip, message.port)

    def interest_handler(self, data):
        """
        Callback for interest packets. This will be called by SocketCommunication object.
        This will handle PIT updates and interest propagation.
        """
        data_type, message = self._decode_data(data)

        if data_type == 2:
            print("Interest handler: data=", data)

            # TODO: Check if I own the data

            if (message.data_address, message.label) in self.pit:
                # Detect interest loop (duplicate interest)
                if (
                    self.pit[(message.data_address, message.label)]
                    >= message.retry_index
                ):
                    print(
                        f"Duplicate interest packet MINE:{self.pit[(message.data_address, message.label)]} IN:{message.retry_index}"
                    )
                # Retry interest
                else:
                    self.pit[
                        (message.data_address, message.label)
                    ] = message.retry_index
                    self.forward_interests(
                        message.data_address, message.retry_index, message.label
                    )
            # New interest
            else:
                self.pit[(message.data_address, message.label)] = message.retry_index
                self.forward_interests(
                    message.data_address, message.retry_index, message.label
                )

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
        # TODO use actual cert here
        cert = "ULTRA_CERT"
        hello_message = HelloMessage(
            neighbor_label=label, ip=address, port=port, cert=cert
        )

        self.ndn = Network(label, all_nodes, k, comm, hello_delay, hello_message)

    def run(self):
        """
        Main Application loop.
        """

        # start TCP listener
        self.ndn.comm.listen()

        # Send initial hellos to pre-populate tables
        self.ndn.send_hellos()
        time.sleep(self.hello_delay + 2)

        # Main loop:
        i = 0
        flip = 0
        while True:
            print("FIB:", self.ndn.neighbor_table.table)
            print("PIT:", self.ndn.pit)

            if self.label == 0:
                self.ndn.originate_interest("/data/2", i)
            i += 1

            self.ndn.send_hellos()
            time.sleep(self.hello_delay)

            # decrement hello counts after two cycles
            if flip > 0:
                self.ndn.neighbor_table.update_counts()
                flip = 0
            else:
                flip += 1


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

        # print(f"Sending message '{data}' to {(dest_address, dest_port)}")
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
        # print(f"Received message '{data}' from {peer_address}")

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
