import networkx as nx
from random import randint, seed
import matplotlib.pyplot as plt
from math import sqrt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime


class Node:
    def __init__(self, label, grid_size, x=None, y=None, offset=0, network_name="hospital-net") -> None:
        self.label = label
        self.x = x if x else randint(offset, grid_size)
        self.y = y if y else randint(0, grid_size)
        self.neighbors = set()

        # Generate key pair for asymmetric encryption/decryption and signing/verifying
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.certificate = self.generate_certificate(network_name)


    def xy(self):
        return (self.x, self.y)

    def add_neighbor(self, label):
        self.neighbors.add(label)

    def remove_neighbor(self, label):
        if label in self.neighbors:
            self.neighbors.remove(label)

    def encrypt_data(self, data, recipient_public_key):
        encrypted = recipient_public_key.encrypt(
            data.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    def decrypt_data(self, encrypted_data):
        decrypted = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode('utf-8')

    def sign_data(self, data):
        signature = self.private_key.sign(
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, data, signature):
        try:
            self.public_key.verify(
                signature,
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def generate_certificate(self, common_name):
        # Create a builder for the certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        certificate_builder = x509.CertificateBuilder()
        certificate_builder = certificate_builder.subject_name(subject)
        certificate_builder = certificate_builder.issuer_name(issuer)
        certificate_builder = certificate_builder.public_key(self.public_key)
        certificate_builder = certificate_builder.serial_number(x509.random_serial_number())
        certificate_builder = certificate_builder.not_valid_before(datetime.datetime.utcnow())
        certificate_builder = certificate_builder.not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        )

        # Sign the certificate with the node's private key
        certificate = certificate_builder.sign(
            private_key=self.private_key, algorithm=hashes.SHA256(),
            backend=default_backend()
        )

        return certificate
    
    def export_certificate(self, file_name):
        with open(file_name, "wb") as f:
            f.write(self.certificate.public_bytes(serialization.Encoding.PEM))

    def __str__(self) -> str:
        return f"label={self.label} x={self.x} y={self.y} neighbors='{' '.join(self.neighbors)}'"

# Using the method
node = Node('Node1', 1000)
node.export_certificate("node1_certificate.pem")

class Graph:
    def __init__(self, grid_size, k) -> None:
        self._graph = nx.Graph()
        self.nodes = {}
        self.grid_size = grid_size
        self.k = k

    def _distance(self, p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def nodes_pos(self):
        return {label: (node.x, node.y) for label, node in self.nodes.items()}

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
        plt.figure(figsize=(12, 8))
        nx.draw(
            self._graph,
            pos=self.nodes_pos(),
            with_labels=True,
            node_size=500,
            node_color="skyblue",
            font_size=10
        )
        plt.title("Graph Visualization")
        plt.show()

    def connect_nodes(self):
        self.add_pending_nodes()

        for label_n1 in self.nodes:
            node_n1 = self.nodes[label_n1]
            if len(node_n1.neighbors) < self.k:
                potential_neighbors = []

                for label_n2 in self.nodes:
                    node_n2 = self.nodes[label_n2]
                    if label_n1 != label_n2 and label_n2 not in node_n1.neighbors:
                        d = self._distance(node_n1.xy(), node_n2.xy())
                        potential_neighbors.append((label_n2, d))

                remaining_neighbor_slots = self.k - len(node_n1.neighbors)
                neighbors = sorted(potential_neighbors, key=lambda x: x[1])[:remaining_neighbor_slots]
                
                for neighbor_label, _ in neighbors:
                    node_n2 = self.nodes[neighbor_label]

                    # Simulate encrypted and signed communication
                    message = f"Hello from {label_n1}"
                    encrypted_message = node_n1.encrypt_data(message, node_n2.public_key)
                    decrypted_message = node_n2.decrypt_data(encrypted_message)

                    # Node n1 signs the message
                    signature = node_n1.sign_data(message)
                    # Node n2 verifies the signature
                    signature_valid = node_n2.verify_signature(message, signature)

                    if signature_valid:
                        print(f"Node {neighbor_label} verified the signature successfully.")
                    else:
                        print(f"Signature verification failed for message from Node {label_n1}.")

                    print(f"Node {label_n1} sent encrypted message: {encrypted_message}")
                    print(f"Node {neighbor_label} received decrypted message: {decrypted_message}")

                    # Add edges between nodes
                    self._graph.add_edges_from([(label_n1, neighbor_label)])
                    node_n1.neighbors.add(neighbor_label)
                    node_n2.neighbors.add(label_n1)
