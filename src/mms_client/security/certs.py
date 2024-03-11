"""Contains functionality associated with certificates."""

from pathlib import Path
from typing import Union

from requests_pkcs12 import Pkcs12Adapter


class Certificate:
    """Describes a certificate composed of a cert file and a key file."""

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

    @property
    def certificate(self) -> bytes:
        """Return the certificate data."""
        return self._cert

    @property
    def passphrase(self) -> str:
        """Return the full path to the passphrase."""
        return self._passphrase

    def to_adapter(self) -> Pkcs12Adapter:
        """Convert the certificate to a Pkcs12Adapter."""
        return Pkcs12Adapter(pkcs12_data=self._cert, pkcs12_password=self._passphrase)
