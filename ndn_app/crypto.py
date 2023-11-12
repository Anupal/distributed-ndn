from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID


def generate_keys(key_size=2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size, backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def print_public_key(key_object):
    pem_public_key = key_object.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    print(pem_public_key.decode("utf-8"))


def print_private_key(key_object):
    pem_private_key = key_object.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    print(pem_private_key.decode("utf-8"))


def encrypt_data(data, recipient_public_key):
    encrypted = recipient_public_key.encrypt(
        data.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return encrypted


def decrypt_data(private_key, encrypted_data):
    decrypted = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return decrypted.decode("utf-8")


def sign_data(private_key, data):
    signature = private_key.sign(
        data.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return signature


def verify_signature(public_key, data, signature):
    try:
        public_key.verify(
            signature,
            data.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


# function to load a certificate that is commonly used across the network
def load_certificate(file_path):
    with open(file_path, "rb") as f:
        cert_data = f.read()
    certificate = load_pem_x509_certificate(cert_data, default_backend())
    return certificate


if __name__ == "__main__":
    pvk, pbk = generate_keys()
    _, pbk2 = generate_keys()

    print("PRIVATE KEY")
    print_private_key(pvk)

    print("PUBLIC KEY")
    print_public_key(pbk)

    s = "anupal"
    print("Source string:", s)

    e = encrypt_data(s, pbk)
    print("Encrypted:", e)

    d = decrypt_data(pvk, e)
    print("Decrypted:", d)

    e2 = encrypt_data(s, pbk2)
    try:
        d2 = decrypt_data(pvk, e2)
        print("Decrypted:", d2)
    except ValueError:
        print("Decryption failed!")

    ss = sign_data(pvk, s)
    print("Signed:", ss)

    print("Verify sign:", verify_signature(pbk, s, ss))
