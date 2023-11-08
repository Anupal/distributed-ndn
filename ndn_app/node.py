import socket
import threading
import multiprocessing


class DataPlane:
    """
    Responsibilities:
        * Handles Interest and Data packets
        * Updates PIT and Content Store
    """


class ControlPlane:
    """
    Responsibilities:
        * Updates neighbor tables (FIB)
            - When hello is received, check certificate
            - If all is okay then add to FIB
        * Sends hello packets periodically
            - FORMAT: [HELLO|SOURCE_LABEL|CERTIFICATE]
        * Handles received hello packets and authenticates using crypto module
    """


class Node(multiprocessing.Process):
    """
    Independent process responsible for covering a Sensor/Actuator

    Integrates:
        * Control plane
        * Data plane
        * Sensor/Actuator
    """

    def run(self):
        ...


class SocketCommunication:
    """
    Manages threads for TCP server and clients.
    """

    def __init__(self, label, address, port) -> None:
        self.label = label
        self.address = address
        self.port = port
        self.callbacks = []

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def send(self, dest_address, dest_port, data):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(
            f"[ {self.label} ] Sending message '{data}' to {(dest_address, dest_port)}"
        )
        try:
            client_socket.connect((dest_address, dest_port))
        except Exception:
            print(f"[ {self.label} ] Can't connect to {(dest_address, dest_port)}")
        else:
            client_socket.send(data.encode("utf-8"))

    def _handle_incoming_packet(self, peer_connection, peer_address):
        """
        Decodes received data and passes it to all registered callbacks.

        """
        data = peer_connection.recv(1024).decode("utf-8")
        print(f"[ {self.label} ] Received message '{data}' from {peer_address}")

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
