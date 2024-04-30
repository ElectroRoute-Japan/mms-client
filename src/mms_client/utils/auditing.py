"""Contains functions for auditability plugins."""

from abc import ABC
from abc import abstractmethod
from logging import getLogger

from lxml.etree import _Element as Element
from lxml.etree import tostring
from zeep import Plugin
from zeep.wsdl.definitions import Operation

# Set the default logger for the MMS client
logger = getLogger(__name__)


class AuditPlugin(ABC, Plugin):
    """Base class for audit plugins."""

    def egress(self, envelope: Element, http_headers: dict, operation: Operation, binding_options):
        """Handle the MMS request before it is sent.

        Arguments are the same as in the egress method of the Plugin class.

        Returns:
        lxml.etree.Element: The XML message to send.
        dict:               The HTTP headers to send.
        """
        data = tostring(envelope, encoding="UTF-8", xml_declaration=True)
        self.audit_request(operation.name, data)
        return envelope, http_headers

    def ingress(self, envelope: Element, http_headers: dict, operation: Operation):
        """Handle the MMS response before it is processed.

        Arguments are the same as in the ingress method of the Plugin class.

        Returns:
        lxml.etree.Element: The XML message to process.
        dict:               The HTTP headers to process.
        """
        data = tostring(envelope, encoding="UTF-8", xml_declaration=True)
        self.audit_response(operation.name, data)
        return envelope, http_headers

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
