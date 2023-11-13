from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID
from base64 import b64encode, b64decode


def generate_keys(key_size=2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size, backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def str_public_key(key_object):
    return b64encode(
        key_object.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    ).decode("utf-8")


def str_private_key(key_object):
    return key_object.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


def encrypt_data(data, recipient_public_key):
    encrypted = recipient_public_key.encrypt(
        data.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return b64encode(encrypted).decode("utf-8")


def decrypt_data(private_key, encrypted_data):
    try:
        decrypted = private_key.decrypt(
            b64decode(encrypted_data),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return decrypted.decode("utf-8")
    except Exception:
        return None


def sign_data(private_key, data):
    signature = private_key.sign(
        data.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return b64encode(signature).decode("utf-8")


def verify_signature(public_key, data, signature):
    try:
        public_key.verify(
            b64decode(signature),
            data.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


def get_public_key_from_string(public_key_string):
    return serialization.load_pem_public_key(
        b64decode(public_key_string), backend=default_backend()
    )


# function to load a certificate that is commonly used across the network
def load_certificate(file_path):
    with open(file_path, "rb") as f:
        cert_data = f.read()
    certificate = load_pem_x509_certificate(cert_data, default_backend())
    return certificate
