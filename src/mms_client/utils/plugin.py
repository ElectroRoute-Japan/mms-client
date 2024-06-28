"""Contains functions for auditability plugins."""

from abc import ABC
from abc import abstractmethod
from logging import getLogger
from typing import Tuple

# Set the default logger for the MMS client
logger = getLogger(__name__)


class Plugin(ABC):
    """Base class for audit plugins."""

    def egress(self, message: bytes, http_headers: dict, operation: str) -> Tuple[bytes, dict]:
        """Handle the MMS request before it is sent.

        Arguments:
        message (bytes):        The message to send.
        http_headers (dict):    The HTTP headers to send.
        operation (str):        The operation being called.

        Returns:
        lxml.etree.Element: The XML message to send.
        dict:               The HTTP headers to send.
        """
        self.audit_request(operation, message)
        return message, http_headers

    def ingress(self, message: bytes, http_headers: dict, operation: str) -> Tuple[bytes, dict]:
        """Handle the MMS response before it is processed.

        Arguments:
        message (bytes):        The message to process.
        http_headers (dict):    The HTTP headers to process.
        operation (str):        The operation being called.

        Returns:
        lxml.etree.Element: The XML message to process.
        dict:               The HTTP headers to process.
        """
        self.audit_response(operation, message)
        return message, http_headers

    @abstractmethod
    def audit_request(self, operation: str, mms_request: bytes) -> None:
        """Audit an MMS request.

        Arguments:
        operation (str):        The SOAP operation being called.
        mms_request (bytes):    The MMS request XML to audit.
        """

    @abstractmethod
    def audit_response(self, operation: str, mms_response: bytes) -> None:
        """Audit an MMS response.

        Arguments:
        operation (str):        The SOAP operation being called.
        mms_response (bytes):   The MMS response XML to audit.
        """
