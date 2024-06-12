"""Contains the client layer for making report requests to the MMS server."""

from datetime import date as Date
from logging import getLogger
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from mms_client.services.base import ClientProto
from mms_client.services.base import ServiceConfiguration
from mms_client.services.base import mms_endpoint
from mms_client.services.base import mms_multi_endpoint
from mms_client.types.base import Response
from mms_client.types.report import ApplicationType
from mms_client.types.report import BSPResourceListItem
from mms_client.types.report import NewReportRequest
from mms_client.types.report import NewReportResponse
from mms_client.types.report import OutboundData
from mms_client.types.report import Parameter
from mms_client.types.report import ParameterName
from mms_client.types.report import Periodicity
from mms_client.types.report import ReportBase
from mms_client.types.report import ReportDownloadRequestTrnID
from mms_client.types.report import ReportLineBase
from mms_client.types.report import ReportName
from mms_client.types.report import ReportSubType
from mms_client.types.report import ReportType
from mms_client.types.transport import RequestType
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface

# Set the default logger for the MMS client
logger = getLogger(__name__)


# The type variable we'll use to represent report line items
R = TypeVar("R", bound=ReportLineBase)


def attach_transaction_id(
    resp: Response[ReportBase, NewReportResponse],
    attachments: Dict[str, bytes],  # pylint: disable=unused-argument
) -> None:
    """Attach the transaction ID to the response.

    Arguments:
    resp (Response[ReportBase, NewReportResponse]): The MMS response.
    attachments (Dict[str, bytes]):                 Attachements to the response.
    """
    if resp.data and resp.statistics is not None:
        resp.data.transaction_id = resp.statistics.transaction_id or ""


def report_getter_factory(config: ServiceConfiguration, resp_data_type: Type[R], allowed_clients: List[ClientType]):
    """Create a function for getting a report with a transaction ID.

    Arguments:
    config (ServiceConfiguration):      The configuration for the report service.
    resp_data_type (Type[R]):           The type of report data to return.
    allowed_clients (List[ClientType]): The allowed client types for the report service.

    Returns:    A function for getting a report with a transaction ID.
    """

    @mms_multi_endpoint(
        name="ReportDownloadRequestTrnID",
        service=config,
        request_type=RequestType.REPORT,
        allowed_clients=allowed_clients,
        response_envelope_type=OutboundData,
        response_data_type=resp_data_type,
        serializer=Serializer(SchemaType.REPORT_RESPONSE, "OutboundData"),
        for_report=True,
    )
    def get_report_with_transaction_id(
        self: ClientProto,
        request: ReportDownloadRequestTrnID,  # pylint: disable=unused-argument
    ) -> List[resp_data_type]:  # type: ignore[valid-type]
        """Request download of a report with a transaction ID.

        This endpoint is accessible to any client, but may be rejected depending on the type of report being requested.

        Arguments:
        self (ClientProto):                     The client to use for making the request.
        request (ReportDownloadRequestTrnID):   The request to download the report.

        Returns:    The request to download the report.
        """
        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        return ReportBase(  # type: ignore[return-value]
            application_type=ApplicationType.MARKET_REPORT,
            participant=self.participant,
        )

    return get_report_with_transaction_id


class ReportClientMixin:  # pylint: disable=unused-argument
    """Report client for the MMS server."""

    # The configuration for the report service
    config = ServiceConfiguration(
        Interface.MI,
        Serializer(SchemaType.REPORT, "MarketReport"),
    )

    @mms_endpoint(
        name="ReportCreateRequest",
        service=config,
        request_type=RequestType.REPORT,
        response_envelope_type=ReportBase,
        response_data_type=NewReportResponse,
        for_report=True,
    )
    def create_report(self: ClientProto, request: NewReportRequest) -> NewReportResponse:
        """Request creation of a new report.

        This endpoint is only accessible to BSPs.

        Arguments:
        request (NewReportRequest): The request to create the report.

        Returns:    The request to create the report.
        """
        # Attach the participant ID to the request
        request.bsp_name = self.participant

        # NOTE: The return type does not match the method definition but the decorator will return the correct type
        # Return the envelope and the callback function
        return (
            ReportBase(  # type: ignore[return-value]
                application_type=ApplicationType.MARKET_REPORT,
                participant=self.participant,
            ),
            attach_transaction_id,
        )

    # Define the individual report getter functions here
    _get_bsp_resources_request = report_getter_factory(config, BSPResourceListItem, [ClientType.BSP])

    def list_bsp_resources(self, start: Date, end: Date) -> List[BSPResourceListItem]:
        """Create a new report request for a list of BSP resources.

        This report should only be used by BSPs.

        Arguments:
        start (Date):   The start date of the report.
        end (Date):     The end date of the report.

        Returns:    The request to create the report.
        """
        report: NewReportResponse = self.create_report(
            NewReportRequest(
                bsp_name="D001",  # NOTE: This is a dummy value and will be overwritten by the endpoint
                report_type=ReportType.REGISTRATION,
                report_sub_type=ReportSubType.RESOURCES,
                periodicity=Periodicity.ON_DEMAND,
                name=ReportName.BSP_RESOURCE_LIST,
                date=Date.today(),
                parameters=[
                    Parameter(name=ParameterName.START_TIME, value=f"{start.isoformat()}T00:00:00"),
                    Parameter(name=ParameterName.END_TIME, value=f"{end.isoformat()}T00:00:00"),
                ],
            )
        )
        return self._get_bsp_resources_request(
            ReportDownloadRequestTrnID(transaction_id=report.transaction_id)  # pylint: disable=no-member
        )
