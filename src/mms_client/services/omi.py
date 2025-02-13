"""Contains the client layer for making OMI requests to the MMS server."""

from logging import getLogger
from typing import List
from typing import Optional

from pydantic_extra_types.pendulum_dt import Date

from mms_client.services.base import ClientProto
from mms_client.services.base import ServiceConfiguration
from mms_client.services.base import mms_endpoint
from mms_client.services.base import mms_multi_endpoint
from mms_client.types.omi import MarketQuery
from mms_client.types.omi import MarketSubmit
from mms_client.types.surplus_capcity import SurplusCapacityData
from mms_client.types.surplus_capcity import SurplusCapacityQuery
from mms_client.types.surplus_capcity import SurplusCapacitySubmit
from mms_client.types.transport import RequestType
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface

# Set the default logger for the MMS client
logger = getLogger(__name__)


class OMIClientMixin:  # pylint: disable=unused-argument
    """OMI client for the MMS server."""

    # The configuration for the OMI service
    config = ServiceConfiguration(Interface.OMI, Serializer(SchemaType.OMI, "MarketData"))

    @mms_endpoint(
        name="MarketSubmit_RemainingReserveData",
        service=config,
        request_type=RequestType.OMI,
        response_data_type=SurplusCapacityData,
        allowed_clients=[ClientType.BSP],
    )
    def put_surplus_capacity(
        self: ClientProto, request: SurplusCapacitySubmit, date: Optional[Date] = None
    ) -> SurplusCapacityData:
        """Submit an offer to the MMS server.

        This endpoint is only accessible to BSPs.

        Arguments:
        request (SurplusCapacitySubmit):    The surplus capacity data to submit to the MMS server.
        date (Date):                        The date of the transaction in the format "YYYY-MM-DD". This value defaults
                                            to the current date.

        Returns:    The surplus capacity data that has been registered with the MMS server.
        """
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return MarketSubmit(  # type: ignore[return-value]
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
        )

    @mms_multi_endpoint(
        name="MarketSubmit_RemainingReserveData",
        service=config,
        request_type=RequestType.OMI,
        response_data_type=SurplusCapacityData,
        allowed_clients=[ClientType.BSP],
    )
    def put_surplus_capacities(
        self: ClientProto, requests: List[SurplusCapacitySubmit], date: Optional[Date] = None
    ) -> List[SurplusCapacityData]:
        """Submit multiple surplus capacity data to the MMS server.

        This endpoint is only accessible to BSPs.

        Arguments:
        requests (list[SurplusCapacitySubmit]): The surplus capacity data to submit to the MMS server.
        date (Date):                            The date of the transaction in the format "YYYY-MM-DD". This value
                                                defaults to the current date.

        Returns:    A list of surplus capacity data that have been registered with the MMS server.
        """
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return MarketSubmit(  # type: ignore[return-value]
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
        )

    @mms_multi_endpoint(
        name="MarketQuery_RemainingReserveDataQuery",
        service=config,
        request_type=RequestType.OMI,
        response_envelope_type=MarketSubmit,
        response_data_type=SurplusCapacityData,
        allowed_clients=[ClientType.BSP, ClientType.TSO],
    )
    def query_surplus_capacity(
        self: ClientProto, request: SurplusCapacityQuery, date: Optional[Date] = None
    ) -> List[SurplusCapacityData]:
        """Query the MMS server for surplus capacity data.

        This endpoint is only accessible to BSPs and TSOs.

        Arguments:
        request (SurplusCapacityQuery): The query to submit to the MMS server.
        date (Date):                    The date of the transaction in the format "YYYY-MM-DD". This value defaults to
                                        the current date.

        Returns:    A list of surplus capacity data that match the query.
        """
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return MarketQuery(  # type: ignore[return-value]
            date=date or Date.today(),
            participant=self.participant,
            user=self.user,
        )
