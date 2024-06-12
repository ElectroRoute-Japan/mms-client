"""Tests the functionality in the mms_client.services.report module."""

from datetime import date as Date
from decimal import Decimal

import pytest
import responses
from mock import patch

from mms_client.client import MmsClient
from mms_client.types.enums import AreaCode
from mms_client.types.enums import BaseLineSettingMethod
from mms_client.types.enums import CommandMonitorMethod
from mms_client.types.enums import ContractType
from mms_client.types.enums import RemainingReserveAvailability
from mms_client.types.enums import SignalType
from mms_client.types.transport import RequestType
from mms_client.utils.errors import AudienceError
from mms_client.utils.web import ClientType
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import register_mms_request
from tests.testutils import verify_bsp_resource_list_item
from tests.testutils import verify_list_report_request
from tests.testutils import verify_list_report_response
from tests.testutils import verify_outbound_data
from tests.testutils import verify_report_base
from tests.testutils import verify_report_create_request
from tests.testutils import verify_report_download_request


@responses.activate
@patch("mms_client.services.report.Date")
def test_list_bsp_resources_invalid_client(mock_date, mock_certificate):
    """Test that the list_bsp_resources method raises an exception when called by a non-BSP client."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.TSO, mock_certificate)

    # Mock out the today function so that we can control the date
    mock_date.today.return_value = Date(2024, 4, 12)

    # Next, register the create request call with the responses library
    register_mms_request(
        RequestType.REPORT,
        (
            "Qj8lUiIqIwLpxieSobzSlF79Z/j/61zOqLmfufXBdYGKiBWTKcmJC6c9Zb0spoOs3/5WrFKTNZALhsDwkh3NbKNVgDKIXcK4g8jj/IRC3"
            "w8dvXhkaPx0G0h795N9uQdM4RaeV1ANuF/KxkG1+WMoaPs4OlxgCLlRIzVmgfcgCBpNAXaCrwqMFo7kJnZcyYqwsgFeFu0japyMoukAra"
            "6T6reggZua6jNiOi9NC/gwUHFme1slsXj3dok0yWempqQUztNA5NnaFxUSHKDBXIQ0WD1gHvQRo6qVx1x5jTw8NrTtykujNBGMUr1lcmL"
            "4g5g1Mdz7PF0/fYbQjCGuHecXxpn8DzMLfpR7SG6akuhloEDVhpr3BzmhZG7OctwpMz8LVpESnF44noSVB1Ytd/0egeUy6e3HgmUXo59L"
            "I1npNhS8BEtpaIW5Carlb+9FKUVibkKlfQ6mpGlTIEYyvcwlJBIbPcawur0ZYR5puSnjW1bqvWqFQ8HUOSpOZHSuHpnR03HFNZc1ARAAm"
            "fmluhXTyvhNSYca69YyvT+vt79y2MhbqaTX93YXibt/SRoICAvoucW76Zkn9GRyfa4ZrenkmUF5GBHLoGLEiEJWzsbULYSt2kexMJqMde"
            "azBFQAZNXDya7CsXy+95UfOrohM5ZbTYIC7wPJbnDj3fTq+tuyrYc="
        ),
        read_request_file("create_report_request_full.xml"),
        read_file("create_report_response_full.xml"),
        url="https://maiwlba103v03.tdgc.jp/axis2/services/MiWebService",
        warnings=True,
        multipart=True,
    )

    # Now, request our test BSP resource list; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.list_bsp_resources(start=Date(2024, 4, 12), end=Date(2024, 4, 13))

    # Finvally, verify the details of the raised exception
    assert (
        str(ex_info.value)
        == "ReportDownloadRequestTrnID: Invalid client type, 'TSO' provided. Only 'BSP' is supported."
    )


@responses.activate
@patch("mms_client.services.report.Date")
def test_list_bsp_resources_works(mock_date, mock_certificate):
    """Test that the list_bsp_resources method works as expected."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Mock out the today function so that we can control the date
    mock_date.today.return_value = Date(2024, 4, 12)

    # Next, register the create request call with the responses library
    register_mms_request(
        RequestType.REPORT,
        (
            "Qj8lUiIqIwLpxieSobzSlF79Z/j/61zOqLmfufXBdYGKiBWTKcmJC6c9Zb0spoOs3/5WrFKTNZALhsDwkh3NbKNVgDKIXcK4g8jj/IRC3"
            "w8dvXhkaPx0G0h795N9uQdM4RaeV1ANuF/KxkG1+WMoaPs4OlxgCLlRIzVmgfcgCBpNAXaCrwqMFo7kJnZcyYqwsgFeFu0japyMoukAra"
            "6T6reggZua6jNiOi9NC/gwUHFme1slsXj3dok0yWempqQUztNA5NnaFxUSHKDBXIQ0WD1gHvQRo6qVx1x5jTw8NrTtykujNBGMUr1lcmL"
            "4g5g1Mdz7PF0/fYbQjCGuHecXxpn8DzMLfpR7SG6akuhloEDVhpr3BzmhZG7OctwpMz8LVpESnF44noSVB1Ytd/0egeUy6e3HgmUXo59L"
            "I1npNhS8BEtpaIW5Carlb+9FKUVibkKlfQ6mpGlTIEYyvcwlJBIbPcawur0ZYR5puSnjW1bqvWqFQ8HUOSpOZHSuHpnR03HFNZc1ARAAm"
            "fmluhXTyvhNSYca69YyvT+vt79y2MhbqaTX93YXibt/SRoICAvoucW76Zkn9GRyfa4ZrenkmUF5GBHLoGLEiEJWzsbULYSt2kexMJqMde"
            "azBFQAZNXDya7CsXy+95UfOrohM5ZbTYIC7wPJbnDj3fTq+tuyrYc="
        ),
        read_request_file("create_report_request_full.xml"),
        read_file("create_report_response_full.xml"),
        warnings=True,
        multipart=True,
    )
    register_mms_request(
        RequestType.REPORT,
        (
            "mNjcHz2s55SiilIuhX87jAsSwo/lS8Oxh550nngrAVLSC0V/opH2iRnnRMI4J/oP5sGQ27fEtaYl08Ipqo5RwvzLOUbDaKQJgw2QIPe0/F1TgG06ZmrvQiOhtCMNgoaTXaDdyKJUMN4Q546LiWxQd/5aQdjEiJwVUjyfPXjse159LMeDdbBN8ZfPVTtYpq3yBpcg48YxYAU1I58IAmBDnJu8tqQ4t8528h/Uh0hVJpW4qbindOclO+ZaPl5GY5gCVdA/7uAiSCq1o+anb1A4EofZnZ/UxjOwGZHj2EE4db+e+cotd5tBkL60geL/J+SnKJuw6duHvYAMwEJYe42iBF7TujYLaYFGtcWc8KcJksxhP7sIpaDhuvyy9PQvJS+iNqeC0PDFVnHfmj0CXYDm068aL/V+4PWMayR88M4LxRwbe9LuWG56PcPiKwuxCG9YlM9BC9ZGwQ8NW8vbrgubIP+yjwtQg470LvcI8NP13258PaF9UP9Rro3Vhu1qH8SOxm4128tpMQGe09SvG815VhbjnicsY3UMqHZiLfzmk3o6V9x/P5bj+mxp47ZdmnvFtbz1tyhil5/koKhiXqtp7iHbRBr+ULFOnwbOMTHDb9D0SfDVTMnvZWPRW9LJ77HdcMzt1Ak79bERsKnXkvL8aTnQs22cje1P9kX2pFYAAUM="
        ),
        read_request_file("download_report_request_full.xml"),
        read_file("download_report_response_full.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, request our test BSP resource list; this should succeed
    resp = client.list_bsp_resources(start=Date(2024, 4, 12), end=Date(2024, 4, 13))

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
