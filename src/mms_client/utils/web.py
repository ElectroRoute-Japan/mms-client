"""Contains the HTTP/web layer for communicating with the MMS server."""

from pathlib import Path
from typing import Literal

from requests import Session
from requests_pkcs12 import Pkcs12Adapter
from zeep import Client
from zeep import Transport
from zeep.cache import SqliteCache

from mms_client.types.transport import MmsRequest
from mms_client.types.transport import MmsResponse

# The following constants identify the ports for the OMI and MI web services, respectively.
MI_WEBSERVICE_PORT = "MiWebService"
OMI_WEBSERVICE_PORT = "OmiWebService"

# Identifies the type of client to use. The client can be either "bsp" (Balancing Service Provider) or "tso"
# (Transmission System Operator).
ClientType = Literal["bsp", "tso"]

# Identifies the type of interface to use. The interface can be either "omi" (Other Market Initiator) or
# "mi" (Market Initiator).
InterfaceType = Literal["omi", "mi"]


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


# Defines the service endpoints for the BSP and TSO clients for the OMI and MI web services, respectively.
URLS = {
    "bsp": {
        "omi": ServiceEndpoint(
            main="https://www5.tdgc.jp/axis2/services/OmiWebService",
            backup="https://www6.tdgc.jp/axis2/services/OmiWebService",
            test="https://www7.tdgc.jp/axis2/services/OmiWebService",
        ),
        "mi": ServiceEndpoint(
            main="https://www2.tdgc.jp/axis2/services/MiWebService",
            backup="https://www3.tdgc.jp/axis2/services/MiWebService",
            test="https://www4.tdgc.jp/axis2/services/MiWebService",
        ),
    },
    "tso": {
        "omi": ServiceEndpoint(
            main="https://maiwlba103v07.tdgc.jp/axis2/services/OmiWebService",
            backup="https://mbiwlba103v07.tdgc.jp/axis2/services/OmiWebService",
            test="https://mbiwlba103v08.tdgc.jp/axis2/services/OmiWebService",
        ),
        "mi": ServiceEndpoint(
            main="https://maiwlba103v03.tdgc.jp/axis2/services/MiWebService",
            backup="https://mbiwlba103v03.tdgc.jp/axis2/services/MiWebService",
            test="https://mbiwlba103v06.tdgc.jp/axis2/services/MiWebService",
        ),
    },
}


class ZWrapper:
    """Wrapper for the Zeep client that handles the HTTP/web layer for communicating with the MMS server.

    Note that this is the lowest layer of the client, and is only responsible for handing off the final request to the
    Zeep client. This class is meant to be used by the higher-level client classes that take in the actual request and
    return the actual response.
    """

    def __init__(
        self,
        client: ClientType,
        interface: InterfaceType,
        adapter: Pkcs12Adapter,
        cache: bool = True,
        test: bool = False,
    ):
        """Create a new Zeep wrapper object for a specific MMS service endpoint.

        Arguments:
        client (ClientType):        The type of client to use. This can be either "bsp" (Balancing Service Provider) or
                                    "tso" (Transmission System Operator). This will determine which service endpoint to
                                    use.
        interface (InterfaceType):  The type of interface to use. This can be either "omi" (Other Market Initiator) or
                                    "mi" (Market Initiator). This will determine which service endpoint to use as well
                                    as the service and port to use.
        adapter (Pkcs12Adapter):    The PKCS12 adapter containing the certificate and private key to use for
                                    authenticating with the MMS server.
        cache (bool):               If True, use a cache for the Zeep client. This is useful for avoiding repeated
                                    lookups of the WSDL file, which should result in lower latency.
        test (bool):                If True, use the test service endpoint. This is useful for testing the client.
        """
        # First, we'll check that the client is valid. If it's not, we'll raise a ValueError.
        if client not in URLS:
            raise ValueError(f"Invalid client, '{client}'. Only 'bsp' and 'tso' are supported.")

        # We need to determine the service port and location of the WSDL file based on the given interface. If the
        # interface is neither "omi" nor "mi", we raise a ValueError.
        if interface == "mi":
            self._service_port = MI_WEBSERVICE_PORT
            self._location = Path(__file__).parent / "schemas" / "wsdl" / "mi-web-service-jbms.wsdl"
        elif interface == "omi":
            self._service_port = OMI_WEBSERVICE_PORT
            self._location = Path(__file__).parent / "schemas" / "wsdl" / "omi-web-service.wsdl"
        else:
            raise ValueError(f"Invalid interface, '{interface}'. Only 'mi' and 'omi' are supported.")

        # Next, we need to select the correct service endpoint based on the given client and interface.
        self._endpoint = URLS[client][interface]
        self._endpoint.select(test=test)

        # Now, we need to create a new session and mount the PKCS12 adapter to it. This is necessary for
        # authenticating with the MMS server. Note, that if we are not in test mode, we also need to mount the
        # PKCS12 adapter to the backup endpoint to make sure we can switch between the main and backup endpoints in
        # case of an error.
        sess = Session()
        sess.mount(self._endpoint.selected, adapter)
        if not test:
            sess.mount(self._endpoint.backup, adapter)

        # Finally, we create the Zeep client with the given WSDL file location, session, and cache settings.
        self._client = Client(
            wsdl=str(self._location.resolve()),
            transport=Transport(cache=SqliteCache() if cache else None, session=sess),
        )

    def submit(self, req: MmsRequest) -> MmsResponse:
        """Submit the given request to the MMS server and return the response."""
        resp = self._client.service[self._service_port](req.model_dump(by_alias=True))
        return MmsResponse.model_validate(resp)
