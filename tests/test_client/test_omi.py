"""Tests the functionality in the mms_client.services.omi module."""

import pytest
import responses
from pendulum import Date
from pendulum import DateTime
from pendulum import Timezone

from mms_client.client import MmsClient
from mms_client.types.surplus_capcity import OperationalRejectCategory
from mms_client.types.surplus_capcity import RejectCategory
from mms_client.types.surplus_capcity import SurplusCapacityQuery
from mms_client.types.surplus_capcity import SurplusCapacitySubmit
from mms_client.types.transport import RequestType
from mms_client.utils.errors import AudienceError
from mms_client.utils.web import ClientType
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import register_mms_request
from tests.testutils import verify_surplus_capacity_data


def test_put_surplus_capacity_invalid_client(mock_certificate):
    """Test that the put_surplus_capacity method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.TSO, mock_certificate, test=True)

    # Next, create our test surplus capacity data
    request = SurplusCapacitySubmit(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
    )

    # Now, attempt to put surplus capacity data with the invalid client type; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.put_surplus_capacity(request, Date(2024, 4, 12))

    # Finvally, verify the details of the raised exception
    assert (
        str(ex_info.value)
        == "MarketSubmit_RemainingReserveData: Invalid client type, 'TSO' provided. Only 'BSP' is supported."
    )


@responses.activate
def test_put_surplus_capacity_works(mock_certificate):
    """Test that the put_surplus_capacity method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test surplus capacity data
    request = SurplusCapacitySubmit(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
        upward_capacity=100,
        upward_capacity_rejected=RejectCategory.FUEL_RESTRICTION,
        upward_capacity_rejection_reason="Some reason",
        downward_capacity=200,
        downward_capacity_rejected=RejectCategory.RIVER_FLOW_RESTRICTION,
        downward_capacity_rejection_reason="Some reason",
        voltage_adjustment_rejected=OperationalRejectCategory.OTHER,
        voltage_adjustment_rejection_reason="Some reason",
        black_start_rejected=OperationalRejectCategory.EQUIPMENT_FAILURE,
        black_start_rejection_reason="Some reason",
        over_power_capacity=300,
        over_power_rejected=OperationalRejectCategory.NOT_SUPPORTED,
        over_power_rejection_reason="Some reason",
        peak_mode_capacity=400,
        peak_mode_rejected=OperationalRejectCategory.OTHER,
        peak_mode_rejection_reason="Some reason",
        system_security_pump_rejected=OperationalRejectCategory.OTHER,
        system_security_pump_rejection_reason="Some reason",
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.OMI,
        (
            "4+Z9CcPI0vUJVPRdUY7RIoIPNgQKMZG1FfWQ+vIAB6InKDzXFoFZ3GKVs6gxbdQMLjFhsCC7M6wgp7NuSKVslDLRxl8janoXzzQovKsEDw"
            "bpIt3+8C+UGjqdghlOxlLvkrlG70EMkSP31cTKkbqYBc+FNHrsgH6dQX2XvGg+dEG0javmNUsVDNJzCJdoLsoZ4/44hZg+yqn+Njs/p6EP"
            "aXDtefiOZNfGmel6BkA75xMgEjRiG754jFYQwDT/4nWY1vY0iO8cSltx+QRi6XxXRplDuu5uCbEMYYrC1joZCUcXxN4j+ANA7G9hDq6N7b"
            "eIMH+dhbciWk+iXfRsGoMtF46cPzABVH0Piq5QFcbA11nusLw8DZcZEYcdD19M2sIWBMponER+A2DWlF7Ofarljcn+E1JOI637D8FUmlu1"
            "Lej0i0mXm/Gl3qNcmK/yQet11+lDP6fYK1kBZ6IUM8ZNvVMtxPhMxYG5MkLKBVpY7IoNjC/aN2TCGOi6uSN1aQAniJR+IO0ahlINuVhsOZ"
            "Reb2zdi73nVufTz3IGPZcnoKeZH+KLz00hEntJNa+qGJYJWok6yDclab9lh5mwQjKkxOKnKvvy/Wj2PaYldppAoRcATVeEpiWQy0aAoMk+"
            "hE5Wj1Vgz5CRuKR4hbIdY0/zC01vdr5lvSm2+gqEru1JjjE="
        ),
        read_request_file("put_surplus_capacity_request.xml"),
        read_file("surplus_capacity_response.xml"),
        url="https://www5.tdgc.jp/axis2/services/OmiWebService",
        warnings=True,
        multipart=True,
    )

    # Now, attempt to put surplus capacity data with the valid client type; this should succeed
    resp = client.put_surplus_capacity(request, Date(2024, 4, 12))

    # Finally, verify the response
    verify_surplus_capacity_data(
        resp,
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        upward_capacity=100,
        upward_capacity_rejected=RejectCategory.FUEL_RESTRICTION,
        upward_capacity_rejection_reason="Some reason",
        downward_capacity=200,
        downward_capacity_rejected=RejectCategory.RIVER_FLOW_RESTRICTION,
        downward_capacity_rejection_reason="Some reason",
        voltage_adjustment_rejected=OperationalRejectCategory.OTHER,
        voltage_adjustment_rejection_reason="Some reason",
        black_start_rejected=OperationalRejectCategory.EQUIPMENT_FAILURE,
        black_start_rejection_reason="Some reason",
        over_power_capacity=300,
        over_power_rejected=OperationalRejectCategory.NOT_SUPPORTED,
        over_power_rejection_reason="Some reason",
        peak_mode_capacity=400,
        peak_mode_rejected=OperationalRejectCategory.OTHER,
        peak_mode_rejection_reason="Some reason",
        system_security_pump_rejected=OperationalRejectCategory.OTHER,
        system_security_pump_rejection_reason="Some reason",
    )


def test_put_surplus_capacities_invalid_client(mock_certificate):
    """Test that the put_surplus_capacity method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.TSO, mock_certificate, test=True)

    # Next, create our test surplus capacity data
    request = SurplusCapacitySubmit(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
    )

    # Now, attempt to put surplus capacity data with the invalid client type; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.put_surplus_capacities([request], Date(2024, 4, 12))

    # Finvally, verify the details of the raised exception
    assert (
        str(ex_info.value)
        == "MarketSubmit_RemainingReserveData: Invalid client type, 'TSO' provided. Only 'BSP' is supported."
    )


@responses.activate
def test_put_surplus_capacities_works(mock_certificate):
    """Test that the put_surplus_capacities method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test surplus capacity data
    request = SurplusCapacitySubmit(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
        upward_capacity=100,
        upward_capacity_rejected=RejectCategory.FUEL_RESTRICTION,
        upward_capacity_rejection_reason="Some reason",
        downward_capacity=200,
        downward_capacity_rejected=RejectCategory.RIVER_FLOW_RESTRICTION,
        downward_capacity_rejection_reason="Some reason",
        voltage_adjustment_rejected=OperationalRejectCategory.OTHER,
        voltage_adjustment_rejection_reason="Some reason",
        black_start_rejected=OperationalRejectCategory.EQUIPMENT_FAILURE,
        black_start_rejection_reason="Some reason",
        over_power_capacity=300,
        over_power_rejected=OperationalRejectCategory.NOT_SUPPORTED,
        over_power_rejection_reason="Some reason",
        peak_mode_capacity=400,
        peak_mode_rejected=OperationalRejectCategory.OTHER,
        peak_mode_rejection_reason="Some reason",
        system_security_pump_rejected=OperationalRejectCategory.OTHER,
        system_security_pump_rejection_reason="Some reason",
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.OMI,
        (
            "4+Z9CcPI0vUJVPRdUY7RIoIPNgQKMZG1FfWQ+vIAB6InKDzXFoFZ3GKVs6gxbdQMLjFhsCC7M6wgp7NuSKVslDLRxl8janoXzzQovKsEDw"
            "bpIt3+8C+UGjqdghlOxlLvkrlG70EMkSP31cTKkbqYBc+FNHrsgH6dQX2XvGg+dEG0javmNUsVDNJzCJdoLsoZ4/44hZg+yqn+Njs/p6EP"
            "aXDtefiOZNfGmel6BkA75xMgEjRiG754jFYQwDT/4nWY1vY0iO8cSltx+QRi6XxXRplDuu5uCbEMYYrC1joZCUcXxN4j+ANA7G9hDq6N7b"
            "eIMH+dhbciWk+iXfRsGoMtF46cPzABVH0Piq5QFcbA11nusLw8DZcZEYcdD19M2sIWBMponER+A2DWlF7Ofarljcn+E1JOI637D8FUmlu1"
            "Lej0i0mXm/Gl3qNcmK/yQet11+lDP6fYK1kBZ6IUM8ZNvVMtxPhMxYG5MkLKBVpY7IoNjC/aN2TCGOi6uSN1aQAniJR+IO0ahlINuVhsOZ"
            "Reb2zdi73nVufTz3IGPZcnoKeZH+KLz00hEntJNa+qGJYJWok6yDclab9lh5mwQjKkxOKnKvvy/Wj2PaYldppAoRcATVeEpiWQy0aAoMk+"
            "hE5Wj1Vgz5CRuKR4hbIdY0/zC01vdr5lvSm2+gqEru1JjjE="
        ),
        read_request_file("put_surplus_capacity_request.xml"),
        read_file("surplus_capacity_response.xml"),
        url="https://www5.tdgc.jp/axis2/services/OmiWebService",
        warnings=True,
        multipart=True,
    )

    # Now, attempt to put surplus capacity data with the valid client type; this should succeed
    resp = client.put_surplus_capacities([request], Date(2024, 4, 12))

    # Finally, verify the response
    assert len(resp) == 1
    verify_surplus_capacity_data(
        resp[0],
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        upward_capacity=100,
        upward_capacity_rejected=RejectCategory.FUEL_RESTRICTION,
        upward_capacity_rejection_reason="Some reason",
        downward_capacity=200,
        downward_capacity_rejected=RejectCategory.RIVER_FLOW_RESTRICTION,
        downward_capacity_rejection_reason="Some reason",
        voltage_adjustment_rejected=OperationalRejectCategory.OTHER,
        voltage_adjustment_rejection_reason="Some reason",
        black_start_rejected=OperationalRejectCategory.EQUIPMENT_FAILURE,
        black_start_rejection_reason="Some reason",
        over_power_capacity=300,
        over_power_rejected=OperationalRejectCategory.NOT_SUPPORTED,
        over_power_rejection_reason="Some reason",
        peak_mode_capacity=400,
        peak_mode_rejected=OperationalRejectCategory.OTHER,
        peak_mode_rejection_reason="Some reason",
        system_security_pump_rejected=OperationalRejectCategory.OTHER,
        system_security_pump_rejection_reason="Some reason",
    )


def test_query_surplus_capacity_invalid_client(mock_certificate):
    """Test that the query_surplus_capacity method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.MO, mock_certificate, test=True)

    # Next, create our test surplus capacity data
    request = SurplusCapacityQuery(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
    )

    # Now, attempt to query surplus capacity with the invalid client type; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.query_surplus_capacity(request, Date(2024, 4, 12))

    # Finvally, verify the details of the raised exception
    assert (
        str(ex_info.value)
        == "MarketQuery_RemainingReserveDataQuery: Invalid client type, 'MO' provided. Only 'BSP' or 'TSO' are supported."
    )


@responses.activate
def test_query_surplus_capacity_works(mock_certificate):
    """Test that the query_surplus_capacity method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test surplus capacity data
    request = SurplusCapacityQuery(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.OMI,
        (
            "2ye5sLzR64AxhuLWtKYM1meyrTJJDeSYZfVkE/gsGwcloCfRoUv1CTYFhYXFnQroerB7l4ktk54ix5ZoprF0w26h350Xq3JUHkk5ANtsiI"
            "UQqlyLX3WP7l3yrvAK68B7EKZbQToAlC3TNCEtxhJLEr4xP3x5dLJYT3quhDJvDr7+nKNFxS1J62XHv9Mb5M6ahfXWio1qGdMxy//fyKrs"
            "eONjb6VIJscQB71WgKkm6mFeAXVdnLWpIb6LkZDU/6nrKi90HBQs8wA8Q8hlytevXe9Y4a5nZQ/tXMeccX75UBSwVvRJTh7WDc6CwjlarQ"
            "SabXj+QI19m0bqP0RRtoxQvL6b7Y6zo5DmE2m2n93Vl1UtbGmnd/qRp7sFXE13NByFIFOOV0ypEeRTTHFSVksqfGBdpK1WV2pNk/6SRRVG"
            "3+fY/UK0qU63YpiV/7BZ2ZmUYWAV8MpFaaKMH7gnCAF5RyYuqcSFyNc3dIAGs2TdlUFqPAOLjXC/JDMc6X+Z8lgdwMolKS0GOmVmtrdYsQ"
            "eVBq3sjg2AFZASedG0l2ydwzxuc6xvVpQ+RfxfDQ9jDpCXEONU8I1Y+4xgne5ldOeQXrSTf0j8MyJFs1vu/f7OXOhsjhTz4qszQqXdcN+8"
            "lufaetSLhSjCK4mWMVmB080L3k54Vea1BwQAYcnA7ZVaENc="
        ),
        read_request_file("query_surplus_capacity_request.xml"),
        read_file("surplus_capacity_response.xml"),
        url="https://www5.tdgc.jp/axis2/services/OmiWebService",
        warnings=True,
        multipart=True,
    )

    # Now, attempt to query surplus capacity with the valid client type; this should succeed
    resp = client.query_surplus_capacity(request, Date(2024, 4, 12))

    # Finally, verify the response
    assert len(resp) == 1
    verify_surplus_capacity_data(
        resp[0],
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        upward_capacity=100,
        upward_capacity_rejected=RejectCategory.FUEL_RESTRICTION,
        upward_capacity_rejection_reason="Some reason",
        downward_capacity=200,
        downward_capacity_rejected=RejectCategory.RIVER_FLOW_RESTRICTION,
        downward_capacity_rejection_reason="Some reason",
        voltage_adjustment_rejected=OperationalRejectCategory.OTHER,
        voltage_adjustment_rejection_reason="Some reason",
        black_start_rejected=OperationalRejectCategory.EQUIPMENT_FAILURE,
        black_start_rejection_reason="Some reason",
        over_power_capacity=300,
        over_power_rejected=OperationalRejectCategory.NOT_SUPPORTED,
        over_power_rejection_reason="Some reason",
        peak_mode_capacity=400,
        peak_mode_rejected=OperationalRejectCategory.OTHER,
        peak_mode_rejection_reason="Some reason",
        system_security_pump_rejected=OperationalRejectCategory.OTHER,
        system_security_pump_rejection_reason="Some reason",
    )
