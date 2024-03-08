"""Contains objects for cryptographic operations."""

from base64 import b64encode

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

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
        private_key = RSA.import_key(cert.certificate, passphrase=cert.passphrase)

        # Finally, create a signer from the private key
        self._signer = pkcs1_15.new(private_key)

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
