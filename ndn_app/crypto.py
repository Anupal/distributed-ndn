from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID
import datetime
import os

def generate_keys(key_size=2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key



def encrypt_data(data, recipient_public_key):
    encrypted = recipient_public_key.encrypt(
        data.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

def decrypt_data(private_key, encrypted_data):
    decrypted = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode('utf-8')

def sign_data(private_key, data):
    signature = private_key.sign(
        data.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(public_key, data, signature):
    try:
        public_key.verify(
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

def generate_certificate(public_key, private_key, common_name):
    # Create a builder for the certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    certificate_builder = x509.CertificateBuilder()
    certificate_builder = certificate_builder.subject_name(subject)
    certificate_builder = certificate_builder.issuer_name(issuer)
    certificate_builder = certificate_builder.public_key(public_key)
    certificate_builder = certificate_builder.serial_number(x509.random_serial_number())
    certificate_builder = certificate_builder.not_valid_before(datetime.datetime.utcnow())
    certificate_builder = certificate_builder.not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    )

    # Sign the certificate with the node's private key
    certificate = certificate_builder.sign(
        private_key=private_key, algorithm=hashes.SHA256(),
        backend=default_backend()
    )

    return certificate

def export_certificate(certificate, file_name):
    os.makedirs('./certs', exist_ok=True)
    with open(f'./certs/{file_name}', "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))


#function to load a certificate that is commonly used across the network
def load_certificate(file_path):
    with open(file_path, 'rb') as f:
        cert_data = f.read()
    certificate = load_pem_x509_certificate(cert_data, default_backend())
    return certificate

# This main function is just for debugging and testing porpuses and wont be used in our actual application
if __name__ == "__main__":
    private_key1 = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
    private_key2 = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
    cert = generate_certificate(private_key1.public_key(), private_key1, "hello")
    cert2 = generate_certificate(private_key2.public_key(), private_key2, "hallo")
    export_certificate(cert, 'hello_certificate.pem')
    export_certificate(cert2, 'hallo_certificate.pem')
 #   network_cert = load_certificate('path/to/network_certificate.pem')  #Edit the path to the folder of certificates

