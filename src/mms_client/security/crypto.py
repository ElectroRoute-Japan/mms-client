"""Contains objects for cryptographic operations."""

from base64 import b64encode
from hashlib import sha256

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

from mms_client.security.certs import Certificate


class CryptoWrapper:
    """Wraps the cryptographic operations necessary for signing and encrypting MMS payload data."""

    def __init__(self, cert: Certificate):
        """Create a new CryptoWrapper with the given certificate.

        Arguments:
        cert (Certificate): The certificate to use for cryptographic operations.
        """
        # First, save our certificate for later use
        self._cert = cert

        # Next, import the private key from the certificate
        private_key, _, _ = load_key_and_certificates(
            self._cert.certificate, self._cert.passphrase.encode(), default_backend()
        )

        # Now, we need to assert typing on this private key to make mypy happy
        if isinstance(private_key, RSAPrivateKey):
            self._private_key = private_key
        else:
            raise TypeError(f"Private key of type ({type(private_key).__name__}) was not expected.")

        # Finally, save our padding and algorithm for later use
        self._padding = padding.PKCS1v15()
        self._algorithm = hashes.SHA256()

    def sign(self, data: bytes) -> bytes:
        """Create a signature from the given data using the certificate.

        Arguments:
        data (bytes):   The data to be encrypted.

        Returns:    A base64-encoded string containing the signature.
        """
        # First, hash the data using SHA256
        hashed = sha256(data)

        # Next, sign the hash using the private key
        signature = self._private_key.sign(hashed.digest(), self._padding, self._algorithm)

        # Finally, return the base64-encoded signature
        return b64encode(signature)
