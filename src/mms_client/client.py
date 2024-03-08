"""Contains the client layer for communicating with the MMS server."""

from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from pendulum import Date

from mms_client.security.certs import Certificate
from mms_client.security.crypto import CryptoWrapper
from mms_client.types.base import PQ
from mms_client.types.base import D
from mms_client.types.base import MultiResponse
from mms_client.types.base import Response
from mms_client.types.market import MarketCancel
from mms_client.types.market import MarketQuery
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferQuery
from mms_client.types.transport import Attachment
from mms_client.types.transport import MmsRequest
from mms_client.types.transport import RequestDataType
from mms_client.types.transport import RequestType
from mms_client.utils.serialization import PayloadConfig
from mms_client.utils.serialization import SchemaType
from mms_client.utils.web import ClientType
from mms_client.utils.web import InterfaceType
from mms_client.utils.web import ZWrapper


class MmsClient:  # pylint: disable=too-many-instance-attributes
    """User client for the MMS server.

    This class is used to communicate with the MMS server.
    """

    def __init__(
        self,
        participant: str,
        user: str,
        client_type: ClientType,
        cert: Certificate,
        is_admin: bool = False,
        test: bool = False,
    ):
        """Create a new MMS client with the given participant, user, client type, and authentication.

        Arguments:
        participant (str):          The MMS code of the business entity to which the requesting user belongs.
        user (str):                 The user name of the person making the request.
        client_type (ClientType):   The type of client to use. This can be either "bsp" (Balancing Service Provider) or
                                    "tso" (Transmission System Operator).
        cert (Certificate):         The certificate to use for authentication.
        is_admin (bool):            Whether the user is an admin (i.e. is a market operator).
        test (bool):                Whether to use the test server. If True, the client will use the test server. If
                                    False, the client will use the main server.
        """
        # Set the base fields from the arguments.
        self._participant = participant
        self._user = user
        self._is_admin = is_admin
        self._type = client_type
        self._test = test

        # Setup the data necessary to secure the requests
        self._adapter = cert.to_adapter()
        self._signer = CryptoWrapper(cert)

        # Setup the various service connections we'll use
        self._market = PayloadConfig(SchemaType.MARKET, "MarketData", "mi")
        self._registration = PayloadConfig(SchemaType.REGISTRATION, "RegistrationData", "mi")
        self._report = PayloadConfig(SchemaType.REPORT, "MarketReport", "mi")
        self._omi = PayloadConfig(SchemaType.OMI, "MarketData", "omi")

        # Setup a mapping between interfaces and clients so we don't have to create a new client for each request
        self._clients: Dict[InterfaceType, ZWrapper] = {}

    def put_offer(
        self, request: OfferData, market_type: MarketType, days: int, date: Optional[Date] = None
    ) -> OfferData:
        """Submit an offer to the MMS server.

        Arguments:
        request (OfferData):        The offer to submit to the MMS server.
        market_type (MarketType):   The type of market for which the offer is being submitted.
        days (int):                 The number of days ahead for which the offer is being submitted.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.

        Returns:    The offer that has been registered with the MMS server.
        """
        envelope = MarketSubmit(
            date=date or Date.today(),
            participant=self._participant,
            user=self._user,
            market_type=market_type,
            days=days,
        )
        resp, _ = self._request_one(envelope, request, self._market, RequestType.INFO)
        return resp.data

    def query_offer(
        self, request: OfferQuery, market_type: MarketType, days: int, date: Optional[Date] = None
    ) -> List[OfferData]:
        """Query the MMS server for offers.

        Arguments:
        request (OfferQuery):       The query to submit to the MMS server.
        market_type (MarketType):   The type of market for which the offer was submitted.
        days (int):                 The number of days ahead for which the data is being queried.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.

        Returns:    A list of offers that match the query.
        """
        envelope = MarketQuery(
            date=date or Date.today(),
            participant=self._participant,
            user=self._user,
            market_type=market_type,
            days=days,
        )
        resp, _ = self._request_many(envelope, request, self._market, RequestType.INFO, MarketSubmit)
        return resp.data

    def cancel_offer(
        self, request: OfferCancel, market_type: MarketType, days: int, date: Optional[Date] = None
    ) -> OfferData:
        """Cancel an offer in the MMS server.

        Arguments:
        request (OfferCancel):      The offer to cancel in the MMS server.
        market_type (MarketType):   The type of market for which the offer was submitted.
        days (int):                 The number of days ahead for which the data is being cancelled.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.
        """
        envelope = MarketCancel(
            date=date or Date.today(),
            participant=self._participant,
            user=self._user,
            market_type=market_type,
            days=days,
        )
        resp, _ = self._request_one(envelope, request, self._market, RequestType.INFO)
        return resp.data

    def _request_one(
        self,
        payload: PQ,
        data: D,
        config: PayloadConfig,
        req_type: RequestType,
        resp_payload_type: Optional[type] = None,
    ) -> Tuple[Response[PQ, D], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the response.

        Arguments:
        payload (PQ):               The payload envelope to submit to the MMS server.
        data (D):                   The data to submit to the MMS server.
        config (PayloadConfig):     The configuration for the payload.
        req_type (RequestType):     The type of request to submit to the MMS server.
        resp_payload_type (type):   The type of payload to expect in the response. If not provided, the type of the
                                    payload will be used.

        Returns:    The response from the MMS server.
        """
        # First, create the MMS request from the payload and data.
        request = self._to_mms_request(req_type, config.serialize(payload, data))

        # Next, submit the request to the MMS server and get the response.
        resp = self._get_zwrapper(config.schema).submit(request)

        # Now, extract the attachments from the response
        attachments = {a.name: a.data for a in resp.attachments}

        # Finally, deserialize the response and return it.
        return config.deserialize(resp.payload, resp_payload_type or type(payload), type(data)), attachments

    def _request_many(
        self,
        payload: PQ,
        data: D,
        config: PayloadConfig,
        req_type: RequestType,
        resp_payload_type: Optional[type] = None,
    ) -> Tuple[MultiResponse[PQ, D], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the multi-response.

        Arguments:
        payload (PQ):               The payload envelope to submit to the MMS server.
        data (D):                   The data to submit to the MMS server.
        config (PayloadConfig):     The configuration for the payload.
        req_type (RequestType):     The type of request to submit to the MMS server.
        resp_payload_type (type):   The type of payload to expect in the response. If not provided, the type of the
                                    payload will be used.

        Returns:    The multi-response from the MMS server.
        """
        # First, create the MMS request from the payload and data.
        request = self._to_mms_request(req_type, config.serialize(payload, data))

        # Next, submit the request to the MMS server and get the response.
        resp = self._get_zwrapper(config.schema).submit(request)

        # Now, extract the attachments from the response
        attachments = {a.name: a.data for a in resp.attachments}

        # Finally, deserialize the response and return it.
        return config.deserialize_multi(resp.payload, resp_payload_type or type(payload), type(data)), attachments

    def _to_mms_request(
        self,
        req_type: RequestType,
        data: bytes,
        return_req: bool = False,
        attachments: Optional[Dict[str, bytes]] = None,
    ) -> MmsRequest:
        """Convert the given data to an MMS request.

        Arguments:
        req_type (RequestType):         The type of request to submit to the MMS server.
        data (bytes):                   The data to submit to the MMS server.
        return_req (bool):              Whether to return the request data in the response. This is False by default.
        attachments (Dict[str, bytes]): The attachments to send with the request.

        Arguments:    The MMS request to submit to the MMS server.
        """
        # Convert the attachments to the correct the MMS format
        attachment_data = (
            [Attachment(signature=self._signer.sign(data), name=name, data=data) for name, data in attachments.items()]
            if attachments
            else []
        )

        # Embed the data and the attachments in the MMS request and return it
        return MmsRequest(
            requestType=req_type,
            adminRole=self._is_admin,
            requestDataCompressed=False,
            requestDataType=RequestDataType.XML,
            sendRequestDataOnSuccess=return_req,
            sendResponseDataCompressed=False,
            requestSignature=self._signer.sign(data),
            requestData=data,
            attachmentData=attachment_data,
        )

    def _get_zwrapper(self, schema: SchemaType) -> ZWrapper:
        """Return the ZWrapper for the given schema.

        Arguments:
        schema (SchemaType):    The XSD schema we'll be using for validation. This will determine the interface to use.

        Returns:    A Zeep client we can use to make requests to the MMS server.
        """
        # First, infer the interface from the schema. We'll use "omi" for OMI schemas, and "mi" for all others.
        interface = "omi" if schema == SchemaType.OMI else "mi"

        # Next, check if we already have a client for this interface. If not, create one.
        if interface not in self._clients:
            self._clients[interface] = ZWrapper(self._type, interface, self._adapter, True, self._test)

        # Finally, return the client.
        return self._clients[interface]
