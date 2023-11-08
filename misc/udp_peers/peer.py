import socket
import threading
import time
import sys
import multiprocessing


def server(rx, label):
    while True:
        message, _ = rx.recvfrom(1024)
        print(f"[{label}] Received : {message}")


def client(tx, label, peer_address):
    message = "hello from " + label
    print(f"[{label}] Sending '{message}' to {peer_address}")
    tx.sendto(message.encode("utf-8"), peer_address)


class Node(multiprocessing.Process):
    def __init__(self, label, address, port, peer_list) -> None:
        super().__init__()
        self.label = label
        self.address = address
        self.port = port
        self.peer_list = peer_list
        self.rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.rx.bind((self.address, self.port))

    def run(self):
        print("Starting node", self.label)
        s = threading.Thread(target=server, args=(self.rx, self.label))
        s.start()
        print(f"[{self.label}] Sending to peer list", self.peer_list)
        while True:
            for peer in self.peer_list:
                client(self.tx, self.label, ("localhost", peer))
                time.sleep(2)

        s.join()


def main():
    labels = ["A", "B", "C", "D", "E"]
    ports = [45000, 45001, 45002, 45003, 45004]

    i = 0
    for label, port in zip(labels, ports):
        print("Loop", label)
        Node(label, "localhost", port, ports[:i] + ports[i + 1 :]).start()
        i += 1


main()
