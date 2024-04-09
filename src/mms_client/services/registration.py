"""Contains the client layer for making registration requests to the MMS server."""

from datetime import date as Date
from typing import List
from typing import Optional

from mms_client.services.base import ClientProto
from mms_client.services.base import ServiceConfiguration
from mms_client.services.base import mms_endpoint
from mms_client.services.base import mms_multi_endpoint
from mms_client.types.registration import QueryAction
from mms_client.types.registration import QueryType
from mms_client.types.registration import RegistrationQuery
from mms_client.types.registration import RegistrationSubmit
from mms_client.types.resource import ResourceData
from mms_client.types.resource import ResourceQuery
from mms_client.types.transport import RequestType
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface


class RegistrationClientMixin:  # pylint: disable=unused-argument
    """Registration client for the MMS server."""

    # The configuration for the registration service
    config = ServiceConfiguration(Interface.MI, Serializer(SchemaType.REGISTRATION, "RegistrationData"))

    @mms_endpoint("RegistrationSubmit_Resource", config, RequestType.REGISTRATION, ClientType.BSP)
    def put_resource(self: ClientProto, request: ResourceData) -> ResourceData:
        """Submit a new resource to the MMS server.

        This endpoint is only accessible to BSPs.

        Arguments:
        request (ResourceData): The resource to register with the MMS server.

        Returns:    The resource that has been registered with the MMS server.
        """
        # For some reason, the registration DTOs require that the participant ID exist on the payload rather than on
        # the envelope so we need to set it before we return the envelope.
        request.participant = self.participant

        # Create and return the registration submit DTO.
        return RegistrationSubmit()  # type: ignore[return-value]

    @mms_multi_endpoint(
        "RegistrationQuery_Resource",
        config,
        RequestType.REGISTRATION,
        resp_envelope_type=RegistrationSubmit,
        resp_data_type=ResourceData,
    )
    def query_resources(
        self: ClientProto, request: ResourceQuery, action: QueryAction, date: Optional[Date] = None
    ) -> List[ResourceData]:
        """Query resources from the MMS server.

        Arguments:
        request (ResourceQuery):    The query to send to the MMS server.
        action (QueryAction):       The type of query being made. NORMAL for all records or LATEST for the most recent.
        date (Date):                The date of the transaction in the format "YYYY-MM-DD". This value defaults to the
                                    current date.

        Returns:    A list of resources that match the query.
        """
        # For some reason, the registration DTOs require that the participant ID exist on the payload rather than on
        # the envelope so we need to set it before we return the envelope.
        request.participant = self.participant

        # Inject our parameters into the query and return it.
        return RegistrationQuery(  # type: ignore[return-value]
            action=action,
            query_type=QueryType.TRADE,
            date=date or Date.today(),
        )
