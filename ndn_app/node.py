from copy import copy
from math import sqrt

import json
import multiprocessing
import os
import random
import socket
import threading
import time
import constants
import re


class InterestMessage:
    """
    Class for INTEREST, its source label, data address and retry index.
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

    def __init__(self, label, ip, port, cert):
        self.certificate = cert
        self.label = label
        self.ip = ip
        self.port = port

    def get_string(self, ack=False):
        id = constants.HELLO_ID
        if ack:
            id = constants.HELLO_ACK_ID
        return f"[{id}][{self.label}][{self.ip}][{self.port}][{self.certificate}]"


class DataMessage:
    """
    Class for DATA, its source label, data address and actual data.
    """

    def __init__(self, label, data_address, data):
        self.label = label
        self.data_address = data_address
        self.data = data

    def get_string(self):
        return f"[1][{self.label}][{self.data_address}][{self.data}]"


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
        # print(f"NEAREST {k} NODES: {self.k_nearest}")

    def __init__(self, label, all_nodes, k, comm, hello_delay, hello_message) -> None:
        self.comm: SocketCommunication = comm
        self.label = label
        self.sensor_data_callback = None
        self.originator_callback = None
        self._simulate_physical_layer(all_nodes, k)
        self.hello_delay = hello_delay
        self.hello_message = hello_message

        self.neighbor_table = FIB()
        self.pit = {}

        self.packet_counters = {
            "in": {
                "hello": 0,
                "hello_ack": 0,
                "interest": 0,
                "data": 0,
            },
            "out": {
                "hello": 0,
                "hello_ack": 0,
                "interest_org": 0,
                "interest_fwd": 0,
                "data_org": 0,
                "data_fwd": 0,
            },
        }

        self.comm.register_callback(self.hello_handler)
        self.comm.register_callback(self.data_handler)
        self.comm.register_callback(self.interest_handler)

    def send_hello(self, ip, port):
        self.comm.send(ip, port, self.hello_message.get_string())
        self.packet_counters["out"]["hello"] += 1

    def send_hello_ack(self, ip, port):
        self.comm.send(ip, port, self.hello_message.get_string(ack=True))
        self.packet_counters["out"]["hello_ack"] += 1

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
            self.comm.send(
                self.neighbor_table.table[neighbor_label].tcp_ip,
                self.neighbor_table.table[neighbor_label].tcp_port,
                payload,
            )
            self.packet_counters["out"]["interest_org"] += 1

    def forward_interests(self, data_address, retry_index, ignore_neighbor=""):
        """
        Go through FIB table and forward interests to all neighbors except ignore_neighbor which
        forwarded the interest to us.
        """
        payload = InterestMessage(data_address, self.label, retry_index).get_string()
        for neighbor_label in copy(self.neighbor_table.table):
            if neighbor_label != ignore_neighbor:
                self.comm.send(
                    self.neighbor_table.table[neighbor_label].tcp_ip,
                    self.neighbor_table.table[neighbor_label].tcp_port,
                    payload,
                )
                self.packet_counters["out"]["interest_fwd"] += 1

    def send_data(self, neighbor_label, data_address, data):
        payload = DataMessage(self.label, data_address, data).get_string()
        self.comm.send(
            self.neighbor_table.table[neighbor_label].tcp_ip,
            self.neighbor_table.table[neighbor_label].tcp_port,
            payload,
        )
        self.packet_counters["out"]["data_org"] += 1

    def forward_data(self, data_address, data):
        payload = DataMessage(self.label, data_address, data).get_string()

        for ref_data_address, neighbor_label in copy(self.pit):
            if ref_data_address == data_address:
                self.comm.send(
                    self.neighbor_table.table[neighbor_label].tcp_ip,
                    self.neighbor_table.table[neighbor_label].tcp_port,
                    payload,
                )
                self.pit.pop((ref_data_address, neighbor_label))
                self.packet_counters["out"]["data_fwd"] += 1

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
                label=label, ip=ip_address, port=port, cert=cert
            )
        elif data_array[0] == "1":
            label = int(data_array[1])
            data_address = data_array[2]
            data_payload = data_array[3]
            return 1, DataMessage(label, data_address, data_payload)
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
            if data_type == 0:
                self.packet_counters["in"]["hello"] += 1
            if data_type == 4:
                self.packet_counters["in"]["hello_ack"] += 1

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
            self.packet_counters["in"]["interest"] += 1
            # Check if I own the data
            sensor_data = self.sensor_data_callback(message.data_address)

            if sensor_data:
                # print(f"I own the data {message.data_address} : {sensor_data}")
                self.send_data(message.label, message.data_address, sensor_data)

            # Forward interest message
            else:
                if (message.data_address, message.label) in self.pit:
                    # Detect interest loop (duplicate interest)
                    if (
                        self.pit[(message.data_address, message.label)]
                        >= message.retry_index
                    ):
                        ...
                        # print(
                        #     f"Duplicate interest packet MINE:{self.pit[(message.data_address, message.label)]} IN:{message.retry_index}"
                        # )
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
                    self.pit[
                        (message.data_address, message.label)
                    ] = message.retry_index
                    self.forward_interests(
                        message.data_address, message.retry_index, message.label
                    )

    def data_handler(self, data):
        """
        Callback for data packets. This will be called by SocketCommunication object.
        This will handle PIT updates and data propagation.
        """
        data_type, message = self._decode_data(data)

        if data_type == 1:
            self.packet_counters["in"]["data"] += 1
            if not self.originator_callback(message.data_address, message.data):
                self.forward_data(message.data_address, message.data)


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

    def __init__(
        self, x, y, label, data_address, address, port, all_nodes, k, hello_delay, mgmt
    ):
        super().__init__()
        self.x = x
        self.y = y
        self.label = label
        self.hello_delay = hello_delay

        comm = SocketCommunication(address, port)
        # TODO use actual cert here
        cert = "ULTRA_CERT"
        hello_message = HelloMessage(label=label, ip=address, port=port, cert=cert)
        self.data_address = data_address
        self.client_data_address = ""
        self.ndn = Network(label, all_nodes, k, comm, hello_delay, hello_message)
        self.ndn.sensor_data_callback = self.sensor_handler
        self.ndn.originator_callback = self.originator_handler
        self.mgmt = mgmt

    def originate_interest(self, data_address, retry_index):
        self.client_data_address = data_address
        self.ndn.originate_interest(self.client_data_address, retry_index)

    def originator_handler(self, data_address, data):
        if data_address == self.client_data_address:
            print(f"Sensor value received: {data_address} = {data}", flush=True)
            self.client_data_address = ""
            return True

    def sensor_handler(self, data_address):
        if data_address == self.data_address:
            return random.random()

    def save_state(self):
        if not os.path.exists("stats"):
            # Create the directory if it doesn't exist
            os.makedirs("stats")
        with open(f"stats/{self.label}", "w") as file:
            file.write(
                json.dumps(
                    {
                        self.label: {
                            "x": self.x,
                            "y": self.y,
                            "comm": {
                                "server_ip": self.ndn.comm.address,
                                "server_port": self.ndn.comm.port,
                            },
                            "packet_counters": self.ndn.packet_counters,
                            "data_address": self.data_address,
                            "label": self.label,
                            "ndn": {
                                "fib": [
                                    {
                                        "label": nei,
                                        "hello_count": self.ndn.neighbor_table.table[
                                            nei
                                        ].hello_count,
                                    }
                                    for nei in self.ndn.neighbor_table.table
                                ],
                                "pit": [
                                    {"data_address": data_address, "label": label}
                                    for data_address, label in self.ndn.pit
                                ],
                            },
                        }
                    },
                    indent=2,
                )
            )

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
        flip = 0
        while True:
            self.ndn.send_hellos()
            time.sleep(self.hello_delay)

            # decrement hello counts after two cycles
            if flip > 0:
                self.ndn.neighbor_table.update_counts()
                flip = 0
            else:
                flip += 1

            # Handle mgmt commands if any
            if not self.mgmt.empty():
                task = self.mgmt.get()
                print("MGMT task:", task, flush=True)
                print(f"*** Node={self.label} ***")
                if task["call"] == "send_interest_packet":
                    self.originate_interest(task["args"][0], task["args"][1])
                elif task["call"] == "print_fib":
                    print(f"FIB:{self.ndn.neighbor_table}")
                elif task["call"] == "print_pit":
                    print(f"PIT:{self.ndn.pit}")
                elif task["call"] == "print_counters":
                    print("INPUT COUNTERS:")
                    for counter in self.ndn.packet_counters["in"]:
                        print(f"{counter}: {self.ndn.packet_counters['in'][counter]}")
                    print("OUTPUT COUNTERS:")
                    for counter in self.ndn.packet_counters["out"]:
                        print(f"{counter}: {self.ndn.packet_counters['out'][counter]}")

            self.save_state()


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
            ...
            # print(f"Can't connect to {(dest_address, dest_port)}")
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
        # print(f"Listening on {self.address}:{self.port}")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.address, self.port))
        self.server_socket.listen(5)
        threading.Thread(target=self._listen_thread).start()
