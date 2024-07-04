"""Tests the functionality in the mms_client.services.report module."""

from decimal import Decimal

import pytest
import responses
from pendulum import Date

from mms_client.client import MmsClient
from mms_client.types.enums import AreaCode
from mms_client.types.enums import BaseLineSettingMethod
from mms_client.types.enums import CommandMonitorMethod
from mms_client.types.enums import ContractType
from mms_client.types.enums import RemainingReserveAvailability
from mms_client.types.enums import SignalType
from mms_client.types.report import AccessClass
from mms_client.types.report import FileType
from mms_client.types.report import ListReportRequest
from mms_client.types.report import NewReportRequest
from mms_client.types.report import Parameter
from mms_client.types.report import ParameterName
from mms_client.types.report import Periodicity
from mms_client.types.report import ReportDownloadRequestTrnID
from mms_client.types.report import ReportName
from mms_client.types.report import ReportSubType
from mms_client.types.report import ReportType
from mms_client.types.transport import RequestType
from mms_client.utils.errors import AudienceError
from mms_client.utils.web import ClientType
from tests.testutils import parameter_verifier
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import register_mms_request
from tests.testutils import report_item_verifier
from tests.testutils import verify_bsp_resource_list_item
from tests.testutils import verify_list_report_response
from tests.testutils import verify_report_create_request


@responses.activate
def test_list_reports_works(mock_certificate):
    """Test that the list_reports method works as expected."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, register the create request call with the responses library
    register_mms_request(
        RequestType.REPORT,
        (
            "np18jIDueh9BZXI5vHfp9tGIJk2GuQdsuPEV7sQS3ed/T725UYQ5rxLkOr3H70ALeqkGo4YGWOE2NtapJohHJ6nsFdF8DzVoGnzajIp08"
            "urYB9Y6Gvp+iNIgn4uzF2laMxmsFeWtiyPj7PPcxGF9iVGAAiPII8se/iT8nXYbrenKoReh83sAh3WaaF8T3pVoc2/fsj9FCleMIQGQUX"
            "tapeFfgt4nX2lEKyzLktq/DkhgFqU3wrHpmHkmO/BCQpd3JLjQaTTVzYEq774idTrwICmpPY1m727/EYNO85SY27djX9n+62YrRJzSSQb"
            "wmQ4Kuy0kE1V8UrJv7B6wqVoddB9YOLJtPEliCn2nV6RL/TNTOF8XCW7udXKq/vgNGLFr9/2W+BEds8q75I+R3tSmxsx4sNtk633bQuNb"
            "+rWatyOdKrxt5qdhRpb++v4rmWOpvEF6NSSywfRUgCLviZE2ldeRJhdHm7BoEq24LdX9TkzTakLZDBalfCJsiBaPQ55TuJfL+d5j0JdcH"
            "xI0g/iG3ywlJxiAteBYI6fZN9mlQZfP5A4CGdJIRvAC7p2d4G9PNH2XoT6PLfOosnXpVjkOvkaxOE/K/PHO8ZNeTVwMn7Oaj9hYFE9CNb"
            "Fc3IWITZ/6GNbIAjGXBYYmpU1x9nzViSzFwgpvzArDSMxZXH+6OZY="
        ),
        read_request_file("list_reports_request_full.xml"),
        read_file("list_reports_response_full.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, create our test report list request
    request = ListReportRequest(
        report_type=ReportType.REGISTRATION,
        report_sub_type=ReportSubType.RESOURCES,
        periodicity=Periodicity.ON_DEMAND,
        date=Date(2024, 4, 12),
        name=ReportName.BSP_RESOURCE_LIST,
    )

    # Request our test BSP resource list; this should succeed
    resp = client.list_reports(request)

    # Finally, verify the response
    verify_list_report_response(
        resp,
        report_type=ReportType.REGISTRATION,
        report_sub_type=ReportSubType.RESOURCES,
        periodicity=Periodicity.ON_DEMAND,
        date=Date(2024, 4, 12),
        name=ReportName.BSP_RESOURCE_LIST,
        verifiers=[
            report_item_verifier(
                report_type=ReportType.REGISTRATION,
                report_sub_type=ReportSubType.RESOURCES,
                periodicity=Periodicity.ON_DEMAND,
                date=Date(2024, 4, 12),
                name=ReportName.BSP_RESOURCE_LIST,
                access_class=AccessClass.BSP,
                filename="BSP_ResourceList_F100_202404121011.xml",
                file_type=FileType.XML,
                transaction_id="derpderp",
                file_size=981,
                is_binary=True,
                expiry_date=Date(2024, 4, 14),
                description="OND_0023b Resource List for BSP",
            )
        ],
    )


@responses.activate
def test_create_report_works(mock_certificate):
    """Test that the create_report method works as expected."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, register the create request call with the responses library
    register_mms_request(
        RequestType.REPORT,
        (
            "uEnI0LjHkcOD2c+lSsuUODu+jdAj494crJd5kIZmblSPbJXrDYMEzuMXGM/WCGfS5DYcWJKCEJHTazMqqcMVIxh+g+JEDJawJF++rltFV"
            "BRliHfvY9dOPxfrmAQ5I4b7R1Cv6LnUqTXE9emiGQv8LiSYgnGBhSL53zg61YblODZ0w1xpL0UKOqKLqlP1+Qeloc4r8N94FkcOqmQREI"
            "73TPVm0P2r885P/Lf9YGbreAly41+uOaTsiRDTqItnIf4Uk7KQhGBceLqzkWBpJorV+TorpxxF2zabo7HhAwM5qTQd7Y28xR2rX4fnQbW"
            "6YdmatsAkR2Up/HPEYC/bYZ/fw/4ZBEtPxOE0qbH3k5Q+KOoVIqFIpln3BoMZfDvStcXpmyJDmv6EzJzyA7oqBVVHJNv/gpveRsCJa0lf"
            "eW66FByDEatPW/MmKEl1FAe2JY8dCaPrJa6csP4d+XJq26oFwdiWd09Pz9S0q4PrpCCZ85YhXnfQQHafpw/4nXqQfVbVf6y5X+LKfvy7u"
            "iw7pHMIIdq10cBS5HETt66jBieoULXrrGHqBTZPRMndhuZY7gs50rNOBmwxArNf7TsQ8vyXJ2xcVp0PVTBdagr/QilR81KcZjCsrkvICI"
            "lRb/3le9KT4JtZx8s8jzEdHRCKc3TFKxkXgRYvNozyWbBe+N+eUNY="
        ),
        read_request_file("create_report_request_full.xml"),
        read_file("create_report_response_full.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, create our test report list request
    request = NewReportRequest(
        bsp_name="F100",
        report_type=ReportType.REGISTRATION,
        report_sub_type=ReportSubType.RESOURCES,
        periodicity=Periodicity.ON_DEMAND,
        name=ReportName.BSP_RESOURCE_LIST,
        date=Date(2024, 4, 12),
        parameters=[
            Parameter(name=ParameterName.START_TIME, value="2024-04-12T00:00:00"),
            Parameter(name=ParameterName.END_TIME, value="2024-04-12T23:59:59"),
        ],
    )

    # Request a new report; this should succeed
    resp = client.create_report(request)

    # Finally, verify the response
    assert resp.transaction_id == "derpderp"
    verify_report_create_request(
        resp,
        report_type=ReportType.REGISTRATION,
        report_sub_type=ReportSubType.RESOURCES,
        periodicity=Periodicity.ON_DEMAND,
        report_name=ReportName.BSP_RESOURCE_LIST,
        date=Date(2024, 4, 12),
        bsp_name="F100",
        verifiers=[
            parameter_verifier(
                ParameterName.START_TIME,
                "2024-04-12T00:00:00",
            ),
            parameter_verifier(
                ParameterName.END_TIME,
                "2024-04-13T00:00:00",
            ),
        ],
    )


def test_list_bsp_resources_invalid_client(mock_certificate):
    """Test that the list_bsp_resources method raises an exception when called by a non-BSP client."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.TSO, mock_certificate)

    # Now, request our test BSP resource list; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.list_bsp_resources(date=Date(2024, 4, 12))

    # Finvally, verify the details of the raised exception
    assert (
        str(ex_info.value)
        == "ReportDownloadRequestTrnID: Invalid client type, 'TSO' provided. Only 'BSP' is supported."
    )


@responses.activate
def test_list_bsp_resources_works(mock_certificate):
    """Test that the list_bsp_resources method works as expected."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, register the create request call with the responses library
    register_mms_request(
        RequestType.REPORT,
        (
            "mNjcHz2s55SiilIuhX87jAsSwo/lS8Oxh550nngrAVLSC0V/opH2iRnnRMI4J/oP5sGQ27fEtaYl08Ipqo5RwvzLOUbDaKQJgw2QIPe0/"
            "F1TgG06ZmrvQiOhtCMNgoaTXaDdyKJUMN4Q546LiWxQd/5aQdjEiJwVUjyfPXjse159LMeDdbBN8ZfPVTtYpq3yBpcg48YxYAU1I58IAm"
            "BDnJu8tqQ4t8528h/Uh0hVJpW4qbindOclO+ZaPl5GY5gCVdA/7uAiSCq1o+anb1A4EofZnZ/UxjOwGZHj2EE4db+e+cotd5tBkL60geL"
            "/J+SnKJuw6duHvYAMwEJYe42iBF7TujYLaYFGtcWc8KcJksxhP7sIpaDhuvyy9PQvJS+iNqeC0PDFVnHfmj0CXYDm068aL/V+4PWMayR8"
            "8M4LxRwbe9LuWG56PcPiKwuxCG9YlM9BC9ZGwQ8NW8vbrgubIP+yjwtQg470LvcI8NP13258PaF9UP9Rro3Vhu1qH8SOxm4128tpMQGe0"
            "9SvG815VhbjnicsY3UMqHZiLfzmk3o6V9x/P5bj+mxp47ZdmnvFtbz1tyhil5/koKhiXqtp7iHbRBr+ULFOnwbOMTHDb9D0SfDVTMnvZW"
            "PRW9LJ77HdcMzt1Ak79bERsKnXkvL8aTnQs22cje1P9kX2pFYAAUM="
        ),
        read_request_file("download_report_request_full.xml"),
        read_file("download_report_response_full.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, request our test BSP resource list; this should succeed
    resp = client.list_bsp_resources(ReportDownloadRequestTrnID(transaction_id="derpderp"))

    # Finally, verify the response
    assert len(resp) == 1
    verify_bsp_resource_list_item(
        resp[0],
        row_number=1,
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
        baseline_setting_method=BaseLineSettingMethod.PREDICTION_BASE,
        signal_type=SignalType.ACTUAL_OUTPUT_ORDER,
        primary_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_AND_DOWN,
        secondary_1_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        secondary_2_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_ONLY,
        tertiary_1_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_DOWN_ONLY,
        tertiary_2_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
    )
