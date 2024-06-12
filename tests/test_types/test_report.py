"""Tests the functionality in the mms_client.types.report module."""

from decimal import Decimal

from pendulum import DateTime

from mms_client.types.enums import AreaCode
from mms_client.types.enums import BaseLineSettingMethod
from mms_client.types.enums import CommandMonitorMethod
from mms_client.types.enums import ContractType
from mms_client.types.enums import RemainingReserveAvailability
from mms_client.types.enums import SignalType
from mms_client.types.registration import QueryType
from mms_client.types.report import AccessClass
from mms_client.types.report import ApplicationType
from mms_client.types.report import BSPResourceListItem
from mms_client.types.report import Date
from mms_client.types.report import FileType
from mms_client.types.report import ListReportRequest
from mms_client.types.report import ListReportResponse
from mms_client.types.report import NewReportRequest
from mms_client.types.report import NewReportResponse
from mms_client.types.report import OutboundData
from mms_client.types.report import Parameter
from mms_client.types.report import ParameterName
from mms_client.types.report import Periodicity
from mms_client.types.report import ReportBase
from mms_client.types.report import ReportDownloadRequest
from mms_client.types.report import ReportDownloadRequestTrnID
from mms_client.types.report import ReportItem
from mms_client.types.report import ReportName
from mms_client.types.report import ReportSubType
from mms_client.types.report import ReportType
from mms_client.types.report import Timezone
from tests.testutils import parameter_verifier
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import report_item_verifier
from tests.testutils import verify_bsp_resource_list_item
from tests.testutils import verify_list_report_request
from tests.testutils import verify_list_report_response
from tests.testutils import verify_outbound_data
from tests.testutils import verify_report_base
from tests.testutils import verify_report_create_request
from tests.testutils import verify_report_download_request


def test_report_base():
    """Test that the ReportBase class initializes and converts to XML as expected."""
    # First, create a new report base request
    request = ReportBase(
        application_type=ApplicationType.MARKET_REPORT,
        participant="F100",
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<MarketReport ApplicationType="MARKET_REPORT" ParticipantName="F100"/>"""
    verify_report_base(request, ApplicationType.MARKET_REPORT, "F100")


def test_report_create_request():
    """Test that the ReportCreateRequest class initializes and converts to XML as expected."""
    # First, create a new report create request
    request = NewReportRequest(
        report_type=ReportType.REGISTRATION,
        report_sub_type=ReportSubType.RESOURCES,
        periodicity=Periodicity.ON_DEMAND,
        name=ReportName.BSP_RESOURCE_LIST,
        date=Date(2024, 4, 12),
        bsp_name="F100",
        parameters=[
            Parameter(name=ParameterName.START_TIME, value="2024-04-12T00:00:00"),
            Parameter(name=ParameterName.END_TIME, value="2024-04-13T00:00:00"),
        ],
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == read_request_file("create_report_request.xml").encode("UTF-8")
    verify_report_create_request(
        request,
        ReportType.REGISTRATION,
        ReportSubType.RESOURCES,
        Periodicity.ON_DEMAND,
        ReportName.BSP_RESOURCE_LIST,
        Date(2024, 4, 12),
        "F100",
        [
            parameter_verifier(ParameterName.START_TIME, "2024-04-12T00:00:00"),
            parameter_verifier(ParameterName.END_TIME, "2024-04-13T00:00:00"),
        ],
    )


def test_report_create_response():
    """Test that the ReportCreateResponse class initializes and converts from XML as expected."""
    # First, read the XML file
    xml = read_file("create_report_request.xml")

    # Next, attempt to convert the XML to a ReportCreateResponse object
    data = NewReportResponse.from_xml(xml)

    # Finally, verify that the request was created with the correct parameters
    assert data.transaction_id == ""
    verify_report_create_request(
        data,
        ReportType.REGISTRATION,
        ReportSubType.RESOURCES,
        Periodicity.ON_DEMAND,
        ReportName.BSP_RESOURCE_LIST,
        Date(2024, 4, 12),
        "F100",
        [
            parameter_verifier(ParameterName.START_TIME, "2024-04-12T00:00:00"),
            parameter_verifier(ParameterName.END_TIME, "2024-04-13T00:00:00"),
        ],
    )


def test_report_list_request():
    """Test that the ListReportRequest class initializes and converts to XML as expected."""
    # First, create a new report list request
    request = ListReportRequest(
        report_type=ReportType.REGISTRATION,
        report_sub_type=ReportSubType.RESOURCES,
        periodicity=Periodicity.ON_DEMAND,
        date=Date(2024, 4, 12),
        name=ReportName.BSP_RESOURCE_LIST,
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == read_request_file("list_report_request_full.xml").encode("UTF-8")
    verify_list_report_request(
        request,
        ReportType.REGISTRATION,
        ReportSubType.RESOURCES,
        Periodicity.ON_DEMAND,
        Date(2024, 4, 12),
        ReportName.BSP_RESOURCE_LIST,
    )


def test_report_list_response():
    """Test that the ListReportResponse class initializes and converts to XML as expected."""
    # First, create a new report list response
    response = ListReportResponse(
        report_type=ReportType.REGISTRATION,
        report_sub_type=ReportSubType.RESOURCES,
        periodicity=Periodicity.ON_DEMAND,
        date=Date(2024, 4, 12),
        name=ReportName.BSP_RESOURCE_LIST,
        reports=[
            ReportItem(
                report_type=ReportType.REGISTRATION,
                report_sub_type=ReportSubType.RESOURCES,
                periodicity=Periodicity.ON_DEMAND,
                date=Date(2024, 4, 12),
                name=ReportName.BSP_RESOURCE_LIST,
                access_class=AccessClass.BSP,
                filename="W9_023[1]_As490_FAKE_NEG.xml",
                file_type=FileType.CSV,
                transaction_id="derpderp",
                file_size=100,
                is_binary=True,
                expiry_date=Date(2024, 4, 14),
                description="偽コメント FAKE COMMENT FTW",
            ),
        ],
    )

    # Next, convert the response to XML
    data = response.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the response was created with the correct parameters
    assert data == read_request_file("list_report_response_full.xml").encode("UTF-8")
    verify_list_report_response(
        response,
        ReportType.REGISTRATION,
        ReportSubType.RESOURCES,
        Periodicity.ON_DEMAND,
        Date(2024, 4, 12),
        ReportName.BSP_RESOURCE_LIST,
        [
            report_item_verifier(
                ReportType.REGISTRATION,
                ReportSubType.RESOURCES,
                Periodicity.ON_DEMAND,
                Date(2024, 4, 12),
                ReportName.BSP_RESOURCE_LIST,
                AccessClass.BSP,
                "W9_023[1]_As490_FAKE_NEG.xml",
                FileType.CSV,
                "derpderp",
                100,
                True,
                Date(2024, 4, 14),
                "偽コメント FAKE COMMENT FTW",
            ),
        ],
    )


def test_report_download_request():
    """Test that the ReportDownloadRequest class initializes and converts to XML as expected."""
    # First, create a new report download request
    request = ReportDownloadRequest(
        report_type=ReportType.REGISTRATION,
        report_sub_type=ReportSubType.RESOURCES,
        periodicity=Periodicity.ON_DEMAND,
        name=ReportName.BSP_RESOURCE_LIST,
        date=Date(2024, 4, 12),
        access_class=AccessClass.BSP,
        filename="W9_023[1]_As490_FAKE_NEG.xml",
        file_type=FileType.CSV,
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == read_request_file("download_report_request.xml").encode("UTF-8")
    verify_report_download_request(
        request,
        ReportType.REGISTRATION,
        ReportSubType.RESOURCES,
        Periodicity.ON_DEMAND,
        ReportName.BSP_RESOURCE_LIST,
        Date(2024, 4, 12),
        AccessClass.BSP,
        "W9_023[1]_As490_FAKE_NEG.xml",
        FileType.CSV,
    )


def test_report_download_transaction_id():
    """Test that the ReportDownloadRequestTrnID class initializes and converts to XML as expected."""
    # First, create a new report download request
    request = ReportDownloadRequestTrnID(
        transaction_id="derpderp",
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<ReportDownloadRequestTrnID TransactionId="derpderp"/>"""
    assert request.transaction_id == "derpderp"


def test_outbound_data():
    """Test that the OutboundData class initializes and converts to XML as expected."""
    # First, create a new outbound data request
    request = OutboundData(
        dataset_name=ReportName.BSP_RESOURCE_LIST,
        dataset_type=Periodicity.ON_DEMAND,
        date=Date(2024, 4, 12),
        date_type=QueryType.TRADE,
        timezone=Timezone.JST,
        publish_time=DateTime(2024, 4, 12, 15),
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == (
        b"""<OutboundData DatasetName="BSP_ResourceList" DatasetType="ON_DEMAND" Date="2024-04-12" DateType="TRADE" """
        b"""DateTimeIndicator="JST" PublishTime="2024-04-12T15:00:00"/>"""
    )
    verify_outbound_data(
        request,
        ReportName.BSP_RESOURCE_LIST,
        Periodicity.ON_DEMAND,
        Date(2024, 4, 12),
        DateTime(2024, 4, 12, 15),
    )


def test_bsp_resource_list():
    """Test that the BSPResourceListItem class initializes and converts to XML as expected."""
    # First, create a new BSP resource list item
    request = BSPResourceListItem(
        participant="F100",
        company_short_name="偽会社",
        start=Date(2024, 4, 12),
        end=Date(2044, 4, 13),
        short_name="偽電力",
        full_name="FAKE_RESO",
        system_code="FSYS0",
        area=AreaCode.CHUBU,
        has_primary=True,
        has_secondary_1=True,
        has_secondary_2=True,
        has_tertiary_1=True,
        has_tertiary_2=True,
        contract_type=ContractType.MARKET,
        primary_secondary_1_control_method=CommandMonitorMethod.DEDICATED_LINE,
        secondary_2_tertiary_control_method=CommandMonitorMethod.SIMPLE_COMMAND,
        tertiary_2_adjustment_coefficient=Decimal("42.00"),
        baseline_setting_method=BaseLineSettingMethod.MEASUREMENT_BASE,
        signal_type=SignalType.ACTUAL_OUTPUT_ORDER,
        primary_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_AND_DOWN,
        secondary_1_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        secondary_2_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_ONLY,
        tertiary_1_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_DOWN_ONLY,
        tertiary_2_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == read_request_file("bsp_resource_list_full.xml").encode("UTF-8")
    verify_bsp_resource_list_item(
        request,
        participant="F100",
        company_short_name="偽会社",
        start=Date(2024, 4, 12),
        end=Date(2044, 4, 13),
        short_name="偽電力",
        full_name="FAKE_RESO",
        system_code="FSYS0",
        area=AreaCode.CHUBU,
        has_primary=True,
        has_secondary_1=True,
        has_secondary_2=True,
        has_tertiary_1=True,
        has_tertiary_2=True,
        contract_type=ContractType.MARKET,
        primary_secondary_1_control_method=CommandMonitorMethod.DEDICATED_LINE,
        secondary_2_tertiary_control_method=CommandMonitorMethod.SIMPLE_COMMAND,
        tertiary_2_adjustment_coefficient=Decimal("42.00"),
        baseline_setting_method=BaseLineSettingMethod.MEASUREMENT_BASE,
        signal_type=SignalType.ACTUAL_OUTPUT_ORDER,
        primary_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_AND_DOWN,
        secondary_1_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        secondary_2_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_ONLY,
        tertiary_1_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_DOWN_ONLY,
        tertiary_2_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
    )
