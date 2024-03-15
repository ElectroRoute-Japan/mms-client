"""Contains the client layer for making market requests to the MMS server."""

from datetime import date as Date
from typing import List
from typing import Optional

from mms_client.services.base import ClientProto
from mms_client.services.base import ServiceConfiguration
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


class MarketClientMixin:
    """Market client for the MMS server."""

    # The configuration for the market service
    config = ServiceConfiguration(Interface.MI, Serializer(SchemaType.MARKET, "MarketData"))

    def put_offer(
        self: ClientProto, request: OfferData, market_type: MarketType, days: int, date: Optional[Date] = None
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
        self.verify_audience(ClientType.BSP)
        envelope = MarketSubmit(
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
            market_type=market_type,
            days=days,
        )
        resp, _ = self.request_one(envelope, request, MarketClientMixin.config, RequestType.INFO)
        return resp.data

    def query_offers(
        self: ClientProto, request: OfferQuery, market_type: MarketType, days: int, date: Optional[Date] = None
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
        self.verify_audience()
        envelope = MarketQuery(
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
            market_type=market_type,
            days=days,
        )
        resp, _ = self.request_many(
            envelope, request, MarketClientMixin.config, RequestType.INFO, MarketSubmit, OfferData
        )
        return resp.data

    def cancel_offer(
        self: ClientProto, request: OfferCancel, market_type: MarketType, days: int, date: Optional[Date] = None
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
        self.verify_audience(ClientType.BSP)
        envelope = MarketCancel(
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
            market_type=market_type,
            days=days,
        )
        resp, _ = self.request_one(envelope, request, MarketClientMixin.config, RequestType.INFO)
        return resp.data
