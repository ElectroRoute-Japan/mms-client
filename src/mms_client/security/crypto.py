"""Contains objects for cryptographic operations."""

from base64 import b64decode
from base64 import b64encode

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15

from mms_client.security.certs import Certificate


class CryptoWrapper:
    """Wraps the cryptographic operations necessary for signing and encrypting MMS payload data."""

    def __init__(self, cert: Certificate):
        """Create a new CryptoWrapper with the given certificate.

        Arguments:
        cert (Certificate): The certificate to use for cryptographic operations.
        """
        # Extract the public key and private key data from the certificate
        private_key = RSA.import_key(cert.private_key())
        public_key = RSA.import_key(cert.public_key())

        # Create a new signer from the private key and a new verifier from the public key
        self._signer = pkcs1_15.new(private_key)
        self._verifier = pkcs1_15.new(public_key)

    def verify(self, content: bytes, signature: bytes) -> bool:
        """Verify a signature against the given content using the certificate.

        Arguments:
        content (bytes):    The content to verify.
        signature (bytes):  The signature to verify against the content.

        Returns:    True if the signature is valid, False otherwise.
        """
        # Hash the content using SHA256
        hashed = SHA256.new(content)

        # Verify the signature using the public key. This will raise a ValueError if the signature is invalid.
        # We catch this exception and return False to indicate that the signature is invalid.
        try:
            self._verifier.verify(hashed, b64decode(signature))
            return True
        except ValueError:
            return False

    def sign(self, data: bytes) -> bytes:
        """Create a signature from the given data using the certificate.

        Arguments:
        data (bytes):   The data to be encrypted.

        Returns:    A base64-encoded string containing the signature.
        """
        # First, hash the data using SHA256
        hashed = SHA256.new(data)

        # Next, sign the hash using the private key
        signature = self._signer.sign(hashed)

        # Finally, return the base64-encoded signature
        return b64encode(signature)
