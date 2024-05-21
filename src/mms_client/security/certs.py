"""Contains functionality associated with certificates."""

from pathlib import Path
from ssl import PROTOCOL_TLSv1_2
from typing import Union

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import NoEncryption
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from requests_pkcs12 import Pkcs12Adapter


class Certificate:
    """Describes a certificate composed of a cert file and a key file."""

    # The encoding to use for MMS certificates
    encoding = Encoding.PEM

    def __init__(self, cert: Union[str, Path, bytes], passphrase: str):
        """Create a new Certificate.

        Creates a new certificate from the absolute path to the certificate file and a passpharse.

        Arguments:
        cert:           The certificate file. If a string, it should be the absolute path to the certificate file. If
                        bytes, it should be the contents of the certificate file.
        passphrase:     The passphrase the certificate is encrypted with
        """
        # Get the certificate file contents
        if isinstance(cert, (str, Path)):
            with open(cert, "rb") as file:
                self._cert = file.read()
        else:
            self._cert = cert

        # Save the passphrase
        self._passphrase = passphrase

        # Load the private key using the cryptography library
        private_key, _, _ = load_key_and_certificates(self._cert, self._passphrase.encode("UTF-8"))
        if isinstance(private_key, RSAPrivateKey):
            self._private = private_key
        else:
            raise TypeError(f"Private key of type ({type(private_key).__name__}) was not expected.")

    @property
    def certificate(self) -> bytes:
        """Return the certificate data."""
        return self._cert

    @property
    def passphrase(self) -> str:
        """Return the full path to the passphrase."""
        return self._passphrase

    def public_key(self) -> bytes:
        """Extract the public key from the certificate.

        Returns: The public key in PEM format.
        """
        return self._private.public_key().public_bytes(Certificate.encoding, PublicFormat.PKCS1)

    def private_key(self) -> bytes:
        """Extract the private key from the certificate.

        THIS SHOULD NOT, UNDER ANY CIRCUMSTANCES, BE PRINTED OR LOGGED!!!

        Returns: The private key in PEM format.
        """
        return self._private.private_bytes(Certificate.encoding, PrivateFormat.PKCS8, NoEncryption())

    def to_adapter(self) -> Pkcs12Adapter:
        """Convert the certificate to a Pkcs12Adapter."""
        return Pkcs12Adapter(pkcs12_data=self._cert, pkcs12_password=self._passphrase, ssl_protocol=PROTOCOL_TLSv1_2)
