"""Contains the HTTP/web layer for communicating with the MMS server."""

from enum import StrEnum
from logging import getLogger
from pathlib import Path
from typing import List
from typing import Optional

from backoff import expo
from backoff import on_exception
from requests import Session
from requests_pkcs12 import Pkcs12Adapter
from zeep import Client
from zeep.cache import SqliteCache
from zeep.exceptions import TransportError
from zeep.xsd.valueobjects import CompoundValue

from mms_client.types.transport import MmsRequest
from mms_client.types.transport import MmsResponse
from mms_client.utils.multipart_transport import MultipartTransport
from mms_client.utils.plugin import Plugin

# Set the default logger for the MMS client
logger = getLogger(__name__)


class ClientType(StrEnum):
    """Identifies the type of client to use.

    The client can be either "bsp" (Balancing Service Provider), "mo" (Market Operator), or "tso" (Transmission System
    Operator).
    """

    BSP = "bsp"
    MO = "mo"
    TSO = "tso"


class Interface(StrEnum):
    """Identifies the type of interface to use.

    The interface can be either "omi" (Other Market Initiator) or "mi" (Market Initiator).
    """

    OMI = "omi"
    MI = "mi"


class ServiceEndpoint:
    """Represents the endpoints for the main, backup, and test servers for a given web service."""

    def __init__(self, main: str, backup: str, test: str):
        """Create a new service endpoint with the given main, backup, and test URLs.

        This object is meant to obfuscate the service endpoint so that the web client can automatically switch between
        the main and backup endpoints in case of an error. Alternatively, this allows the client to switch to the test
        endpoint for testing purposes.
        """
        self.main = main
        self.backup = backup
        self.test = test
        self._selected = self.main

    @property
    def selected(self) -> str:
        """Return the currently selected URL."""
        return self._selected

    def select(self, error: bool = False, test: bool = False):
        """Select the main, backup, or test URL based on the given parameters.

        Arguments:
        error (bool):   If True, select the backup URL.
        test (bool):    If True, select the test URL.
        """
        if error:
            self._selected = self.backup
        elif test:
            self._selected = self.test
        else:
            self._selected = self.main


# Defines the service endpoints for the BSP, MO and TSO clients for the OMI and MI web services, respectively.
BSP_MO_URLS = {
    Interface.OMI: ServiceEndpoint(
        main="https://www5.tdgc.jp/axis2/services/OmiWebService",
        backup="https://www6.tdgc.jp/axis2/services/OmiWebService",
        test="https://www7.tdgc.jp/axis2/services/OmiWebService",
    ),
    Interface.MI: ServiceEndpoint(
        main="https://www2.tdgc.jp/axis2/services/MiWebService",
        backup="https://www3.tdgc.jp/axis2/services/MiWebService",
        test="https://www4.tdgc.jp/axis2/services/MiWebService",
    ),
}
TSO_URLS = {
    Interface.OMI: ServiceEndpoint(
        main="https://maiwlba103v07.tdgc.jp/axis2/services/OmiWebService",
        backup="https://mbiwlba103v07.tdgc.jp/axis2/services/OmiWebService",
        test="https://mbiwlba103v08.tdgc.jp/axis2/services/OmiWebService",
    ),
    Interface.MI: ServiceEndpoint(
        main="https://maiwlba103v03.tdgc.jp/axis2/services/MiWebService",
        backup="https://mbiwlba103v03.tdgc.jp/axis2/services/MiWebService",
        test="https://mbiwlba103v06.tdgc.jp/axis2/services/MiWebService",
    ),
}


# The original service binding names, to be mapped to our actual endpoints
SERVICE_BINDINGS = {
    Interface.MI: "{urn:abb.com:project/mms}MiWebServiceSOAP",
    Interface.OMI: "{urn:ws.web.omi.co.jp}OmiWebServiceSOAP",
}


def fatal_code(e: TransportError) -> bool:
    """Return True if the given exception is a fatal HTTP error code.

    Arguments:
    e (RequestException):   The exception to check.
    """
    return 400 <= e.status_code < 500


class ZWrapper:
    """Wrapper for the Zeep client that handles the HTTP/web layer for communicating with the MMS server.

    Note that this is the lowest layer of the client, and is only responsible for handing off the final request to the
    Zeep client. This class is meant to be used by the higher-level client classes that take in the actual request and
    return the actual response.
    """

    def __init__(
        self,
        domain: str,
        client: ClientType,
        interface: Interface,
        adapter: Pkcs12Adapter,
        plugins: Optional[List[Plugin]] = None,
        cache: bool = True,
        test: bool = False,
    ):
        """Create a new Zeep wrapper object for a specific MMS service endpoint.

        Arguments:
        domain (str):               The domain to use when signing the content ID to MTOM attachments.
        client (ClientType):        The type of client to use. This can be either "bsp" (Balancing Service Provider) or
                                    "tso" (Transmission System Operator). This will determine which service endpoint to
                                    use.
        interface (Interface):      The type of interface to use. This can be either "omi" (Other Market Initiator) or
                                    "mi" (Market Initiator). This will determine which service endpoint to use as well
                                    as the service and port to use.
        adapter (Pkcs12Adapter):    The PKCS12 adapter containing the certificate and private key to use for
                                    authenticating with the MMS server.
        plugins (List[Plugin]):     A list of Zeep plugins to use with the client. This is useful for adding additional
                                    functionality to the client, such as auditing or logging.
        cache (bool):               If True, use a cache for the Zeep client. This is useful for avoiding repeated
                                    lookups of the WSDL file, which should result in lower latency.
        test (bool):                If True, use the test service endpoint. This is useful for testing the client.
        """
        # First, we'll check that the client is valid. If it's not, we'll raise a ValueError.
        if client in [ClientType.BSP, ClientType.MO]:
            urls = BSP_MO_URLS
        elif client == ClientType.TSO:
            urls = TSO_URLS
        else:
            raise ValueError(f"Invalid client, '{client}'. Only 'bsp', 'mo', and 'tso' are supported.")

        # We need to determine the service port and location of the WSDL file based on the given interface. If the
        # interface is neither "omi" nor "mi", we raise a ValueError.
        self._interface = interface
        if self._interface == Interface.MI:
            location = Path(__file__).parent.parent / "schemas" / "wsdl" / "mi-web-service-jbms.wsdl"
        elif self._interface == Interface.OMI:
            location = Path(__file__).parent.parent / "schemas" / "wsdl" / "omi-web-service.wsdl"
        else:
            raise ValueError(f"Invalid interface, '{self._interface}'. Only 'mi' and 'omi' are supported.")

        # Next, we need to select the correct service endpoint based on the given client and interface.
        self._endpoint = urls[self._interface]
        self._endpoint.select(test=test)

        # Now, we need to create a new session and mount the PKCS12 adapter to it. This is necessary for
        # authenticating with the MMS server. Note, that if we are not in test mode, we also need to mount the
        # PKCS12 adapter to the backup endpoint to make sure we can switch between the main and backup endpoints in
        # case of an error.
        sess = Session()
        sess.mount(self._endpoint.selected, adapter)
        if not test:
            sess.mount(self._endpoint.backup, adapter)

        # Finally, we create the Zeep client with the given WSDL file location, session, and cache settings and then,
        # from that client, we create the SOAP service with the given service binding and selected endpoint.
        self._transport = MultipartTransport(
            domain, cache=SqliteCache() if cache else None, session=sess, plugins=plugins
        )
        self._client = Client(
            wsdl=str(location.resolve()),
            transport=self._transport,
        )
        self._create_service()

    def register_attachment(self, operation: str, name: str, attachment: bytes) -> str:
        """Register a multipart attachment.

        Arguments:
        operation (str):    The name of the operation.
        name (str):         The name of the attachment.
        attachment (bytes): The data to be attached.

        Returns:    The content ID of the attachment, which should be used in place of the attachment data.
        """
        return self._transport.register_attachment(operation, name, attachment)

    @on_exception(expo, TransportError, max_tries=3, giveup=fatal_code, logger=logger)  # type: ignore[arg-type]
    def submit(self, req: MmsRequest) -> MmsResponse:
        """Submit the given request to the MMS server and return the response.

        Arguments:
        req (MmsRequest):   The MMS request to submit.

        Returns:    The MMS response.
        """
        try:
            logger.debug(f"Submitting MMS request request to {self._interface.name} service")

            # Submit the request to the MMS server and retrieve the response
            resp: CompoundValue = self._service["submitAttachment"](**req.to_arguments())

            # Validate the response and return it
            return MmsResponse.model_validate(resp.__values__)
        except TransportError as e:
            # If we got a server fault error, then we'll switch to the backup endpoint. In any case, we'll raise the
            # exception so that our back-off can handle it or pass the exception up the stack.
            logger.error(
                f"MMS request to {self._interface.name} service failed with status code: {e.status_code}",
                exc_info=e,
            )
            if e.status_code >= 500:
                logger.warning(f"MMS server error, switching to backup endpoint: {self._endpoint.backup}")
                self._endpoint.select(error=True)
                self._create_service()
            raise

    def _create_service(self):
        """Create a new SOAP service with the currently selected endpoint.

        This is useful for switching between the main and backup endpoints in case of an error.
        """
        logger.debug(f"Creating new {self._interface.name} service with endpoint: {self._endpoint.selected}")
        self._service = self._client.create_service(SERVICE_BINDINGS[self._interface], self._endpoint.selected)
