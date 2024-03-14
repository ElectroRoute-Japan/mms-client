"""Contains the client layer for making market requests to the MMS server."""

from datetime import date as Date
from typing import List
from typing import Optional

from mms_client.security.certs import Certificate
from mms_client.security.crypto import CryptoWrapper
from mms_client.services.base import BaseClient
from mms_client.types.market import MarketCancel
from mms_client.types.market import MarketQuery
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferQuery
from mms_client.types.transport import RequestType
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface
from mms_client.utils.web import ZWrapper


class MarketClient:
    """Market client for the MMS server."""

    def __init__(
        self,
        participant: str,
        user: str,
        client_type: ClientType,
        cert: Certificate,
        is_admin: bool = False,
        test: bool = False,
    ):
        """Create a new MMS market client with the given participant, user, client type, and authentication.

        Arguments:
        participant (str):          The MMS code of the business entity to which the requesting user belongs.
        user (str):                 The user name of the person making the request.
        client_type (ClientType):   The type of client to use for making requests to the MMS server.
        cert (Certificate):         The certificate to use for signing requests.
        is_admin (bool):            Whether the user is an admin (i.e. is a market operator).
        test (bool):                Whether to use the test server.
        """
        # Save the base field associated with the client
        self._participant = participant
        self._user = user

        # First, create a new Zeep wrapper for the given client type and certificate
        wrapper = ZWrapper(client_type, Interface.MI, cert.to_adapter(), True, test)

        # Next, create a new signer for the given certificate
        signer = CryptoWrapper(cert)

        # Now, create a new serializer for the market schema
        serializer = Serializer(SchemaType.MARKET, "MarketData")

        # Finally, create the MMS client
        self._client = BaseClient(client_type, wrapper, signer, serializer, is_admin)

    def put_offer(
        self, request: OfferData, market_type: MarketType, days: int, date: Optional[Date] = None
    ) -> OfferData:
        """Submit an offer to the MMS server.

        This endpoint is only accessible to BSPs.

        Arguments:
        request (OfferData):        The offer to submit to the MMS server.
        market_type (MarketType):   The type of market for which the offer is being submitted.
        days (int):                 The number of days ahead for which the offer is being submitted.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.

        Returns:    The offer that has been registered with the MMS server.
        """
        self._client.verify_audience(ClientType.BSP)
        envelope = MarketSubmit(
            date=date or Date.today(),
            participant=self._participant,
            user=self._user,
            market_type=market_type,
            days=days,
        )
        resp, _ = self._client.request_one(envelope, request, RequestType.INFO)
        return resp.data

    def query_offers(
        self, request: OfferQuery, market_type: MarketType, days: int, date: Optional[Date] = None
    ) -> List[OfferData]:
        """Query the MMS server for offers.

        This endpoint is accessible to all client types.

        Arguments:
        request (OfferQuery):       The query to submit to the MMS server.
        market_type (MarketType):   The type of market for which the offer was submitted.
        days (int):                 The number of days ahead for which the data is being queried.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.

        Returns:    A list of offers that match the query.
        """
        self._client.verify_audience()
        envelope = MarketQuery(
            date=date or Date.today(),
            participant=self._participant,
            user=self._user,
            market_type=market_type,
            days=days,
        )
        resp, _ = self._client.request_many(envelope, request, RequestType.INFO, MarketSubmit)
        return resp.data

    def cancel_offer(
        self, request: OfferCancel, market_type: MarketType, days: int, date: Optional[Date] = None
    ) -> OfferCancel:
        """Cancel an offer in the MMS server.

        This endpoint is only accessible to BSPs.

        Arguments:
        request (OfferCancel):      The offer to cancel in the MMS server.
        market_type (MarketType):   The type of market for which the offer was submitted.
        days (int):                 The number of days ahead for which the data is being cancelled.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.
        """
        self._client.verify_audience(ClientType.BSP)
        envelope = MarketCancel(
            date=date or Date.today(),
            participant=self._participant,
            user=self._user,
            market_type=market_type,
            days=days,
        )
        resp, _ = self._client.request_one(envelope, request, RequestType.INFO)
        return resp.data
