from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime

class CryptoNode:
    def __init__(self, network_name="hospital-net"):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.certificate = self.generate_certificate(network_name)

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
        
    def export_certificate(self, file_name):
        with open(file_name, "wb") as f:
            f.write(self.certificate.public_bytes(serialization.Encoding.PEM))
        
    




















