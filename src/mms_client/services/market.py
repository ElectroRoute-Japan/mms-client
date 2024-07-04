"""Contains the client layer for making market requests to the MMS server."""

from logging import getLogger
from typing import List
from typing import Optional

from pydantic_extra_types.pendulum_dt import Date

from mms_client.services.base import ClientProto
from mms_client.services.base import ServiceConfiguration
from mms_client.services.base import mms_endpoint
from mms_client.services.base import mms_multi_endpoint
from mms_client.types.award import AwardQuery
from mms_client.types.award import AwardResponse
from mms_client.types.market import MarketCancel
from mms_client.types.market import MarketQuery
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferQuery
from mms_client.types.reserve import ReserveRequirement
from mms_client.types.reserve import ReserveRequirementQuery
from mms_client.types.transport import RequestType
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface

# Set the default logger for the MMS client
logger = getLogger(__name__)


class MarketClientMixin:  # pylint: disable=unused-argument
    """Market client for the MMS server."""

    # The configuration for the market service
    config = ServiceConfiguration(Interface.MI, Serializer(SchemaType.MARKET, "MarketData"))

    @mms_endpoint(
        name="MarketQuery_ReserveRequirementQuery",
        service=config,
        request_type=RequestType.INFO,
        response_envelope_type=MarketSubmit,
        response_data_type=ReserveRequirement,
    )
    def query_reserve_requirements(
        self: ClientProto, request: ReserveRequirementQuery, days: int, date: Optional[Date] = None
    ) -> List[ReserveRequirement]:
        """Query the MMS server for reserve requirements.

        This endpoint is accessible to all client types.

        Arguments:
        request (ReserveRequirementQuery):  The query to submit to the MMS server.
        date (Date):                        The date of the transaction in the format "YYYY-MM-DD". This value defaults
                                            to the current date.
        days (int):                         The number of days ahead for which the data is being queried.

        Returns:    A list of reserve requirements that match the query.
        """
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return MarketQuery(  # type: ignore[return-value]
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
            days=days,
        )

    @mms_endpoint(
        name="MarketSubmit_OfferData", service=config, request_type=RequestType.MARKET, allowed_clients=[ClientType.BSP]
    )
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
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return MarketSubmit(  # type: ignore[return-value]
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
            market_type=market_type,
            days=days,
        )

    @mms_multi_endpoint(
        name="MarketSubmit_OfferData", service=config, request_type=RequestType.MARKET, allowed_clients=[ClientType.BSP]
    )
    def put_offers(
        self: ClientProto, requests: List[OfferData], market_type: MarketType, days: int, date: Optional[Date] = None
    ) -> List[OfferData]:
        """Submit multiple offers to the MMS server.

        This endpoint is only accessible to BSPs.

        Arguments:
        requests (List[OfferData]): The offers to submit to the MMS server.
        market_type (MarketType):   The type of market for which the offers are being submitted.
        days (int):                 The number of days ahead for which the offers are being submitted.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.

        Returns:    A list of offers that have been registered with the MMS server.
        """
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return MarketSubmit(  # type: ignore[return-value]
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
            market_type=market_type,
            days=days,
        )

    @mms_multi_endpoint(
        name="MarketQuery_OfferQuery",
        service=config,
        request_type=RequestType.MARKET,
        response_envelope_type=MarketSubmit,
        response_data_type=OfferData,
    )
    def query_offers(self: ClientProto, request: OfferQuery, days: int, date: Optional[Date] = None) -> List[OfferData]:
        """Query the MMS server for offers.

        This endpoint is accessible to all client types.

        Arguments:
        request (OfferQuery):       The query to submit to the MMS server.
        days (int):                 The number of days ahead for which the data is being queried.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.

        Returns:    A list of offers that match the query.
        """
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return MarketQuery(  # type: ignore[return-value]
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
            days=days,
        )

    @mms_endpoint(
        name="MarketCancel_OfferCancel",
        service=config,
        request_type=RequestType.MARKET,
        allowed_clients=[ClientType.BSP],
    )
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

        Returns:    Data identifying the offer that was cancelled.
        """
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return MarketCancel(  # type: ignore[return-value]
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
            market_type=market_type,
            days=days,
        )

    @mms_endpoint(
        name="MarketQuery_AwardResultsQuery",
        service=config,
        request_type=RequestType.MARKET,
        response_data_type=AwardResponse,
    )
    def query_awards(self: ClientProto, request: AwardQuery, days: int, date: Optional[Date] = None) -> AwardResponse:
        """Query the MMS server for award results.

        This endpoint is accessible to all client types.

        If no values are specified for Area, Associated Area, Power Generation Unit Code, or GC Registration Flag,
        the results for all areas will be retrieved. If one or more of these criteria are specified, the results will
        be filtered according to the specified criteria. If no value is specified for the retrieval period, the default
        value for this field is 1.

        Arguments:
        request (AwardQuery):       The query to submit to the MMS server.
        days (int):                 The number of days ahead for which the data is being queried.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.

        Returns:    The award results that match the query.
        """
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return MarketQuery(  # type: ignore[return-value]
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
            days=days,
        )
