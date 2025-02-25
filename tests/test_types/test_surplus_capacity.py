"""Tests the functionality of the mms_client.types.surplus_capacity module."""

from pendulum import DateTime
from pendulum import Timezone

from mms_client.types.enums import AreaCode
from mms_client.types.surplus_capcity import OperationalRejectCategory
from mms_client.types.surplus_capcity import RejectCategory
from mms_client.types.surplus_capcity import SurplusCapacityData
from mms_client.types.surplus_capcity import SurplusCapacityQuery
from mms_client.types.surplus_capcity import SurplusCapacitySubmit
from tests.testutils import read_request_file
from tests.testutils import verify_surplus_capacity_data
from tests.testutils import verify_surplus_capacity_query
from tests.testutils import verify_surplus_capacity_submit


def test_surplus_capacity_submit_defaults():
    """Test that the SurplusCapacitySubmit class initializes and converts to XML as we expect."""
    # First, create a new surplus capacity submit request
    request = SurplusCapacitySubmit(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == (
        b"""<RemainingReserveData ResourceName="FAKE_RESO" DrPatternNumber="1" StartTime="2024-04-12T15:00:00" EndTime="2024-04-12T18:00:00"/>"""
    )
    verify_surplus_capacity_submit(
        request,
        "FAKE_RESO",
        1,
        DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
    )


def test_surplus_capacity_submit_full():
    """Test that the SurplusCapacityData class initializes and converts to XML as we expect."""
    # First, create a new surplus capacity data request
    request = SurplusCapacityData(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
        upward_capacity=100,
        upward_capacity_rejected=RejectCategory.FUEL_RESTRICTION,
        upward_capacity_rejection_reason="Not enough fuel",
        downward_capacity=200,
        downward_capacity_rejected=RejectCategory.RIVER_FLOW_RESTRICTION,
        downward_capacity_rejection_reason="Not enough river",
        voltage_adjustment_rejected=OperationalRejectCategory.EQUIPMENT_FAILURE,
        voltage_adjustment_rejection_reason="The voltage broke",
        black_start_rejected=OperationalRejectCategory.NOT_SUPPORTED,
        black_start_rejection_reason="Only white starts supported",
        over_power_capacity=9001,
        over_power_rejected=OperationalRejectCategory.OTHER,
        over_power_rejection_reason="It broke the sensor",
        peak_mode_capacity=9002,
        peak_mode_rejected=OperationalRejectCategory.OTHER,
        peak_mode_rejection_reason="It broke the sensor",
        system_security_pump_rejected=OperationalRejectCategory.OTHER,
        system_security_pump_rejection_reason="She can't take much more of this, captain",
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == read_request_file("surplus_capacity_submit_full.xml").encode("UTF-8")
    verify_surplus_capacity_submit(
        request,
        "FAKE_RESO",
        1,
        DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        upward_capacity=100,
        upward_capacity_rejected=RejectCategory.FUEL_RESTRICTION,
        upward_capacity_rejection_reason="Not enough fuel",
        downward_capacity=200,
        downward_capacity_rejected=RejectCategory.RIVER_FLOW_RESTRICTION,
        downward_capacity_rejection_reason="Not enough river",
        voltage_adjustment_rejected=OperationalRejectCategory.EQUIPMENT_FAILURE,
        voltage_adjustment_rejection_reason="The voltage broke",
        black_start_rejected=OperationalRejectCategory.NOT_SUPPORTED,
        black_start_rejection_reason="Only white starts supported",
        over_power_capacity=9001,
        over_power_rejected=OperationalRejectCategory.OTHER,
        over_power_rejection_reason="It broke the sensor",
        peak_mode_capacity=9002,
        peak_mode_rejected=OperationalRejectCategory.OTHER,
        peak_mode_rejection_reason="It broke the sensor",
        system_security_pump_rejected=OperationalRejectCategory.OTHER,
        system_security_pump_rejection_reason="She can't take much more of this, captain",
    )


def test_surplus_capacity_data_defaults():
    """Test that the SurplusCapacityData class initializes and converts to XML as we expect."""
    # First, create a new surplus capacity data request
    request = SurplusCapacityData(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert (
        data
        == b"""<RemainingReserveData ResourceName="FAKE_RESO" DrPatternNumber="1" StartTime="2024-04-12T15:00:00" EndTime="2024-04-12T18:00:00"/>"""
    )
    verify_surplus_capacity_data(
        request,
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
    )


def test_surplus_capacity_data_full():
    """Test that the SurplusCapacityData class initializes and converts to XML as we expect."""
    # First, create a new surplus capacity data request
    request = SurplusCapacityData(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
        area=AreaCode.CHUBU,
        participant="F100",
        company="偽会社",
        system_code="FSYS0",
        resource_name="偽電力",
        upward_capacity=100,
        upward_capacity_rejected=RejectCategory.FUEL_RESTRICTION,
        upward_capacity_rejection_reason="Not enough fuel",
        downward_capacity=200,
        downward_capacity_rejected=RejectCategory.RIVER_FLOW_RESTRICTION,
        downward_capacity_rejection_reason="Not enough river",
        voltage_adjustment_rejected=OperationalRejectCategory.EQUIPMENT_FAILURE,
        voltage_adjustment_rejection_reason="The voltage broke",
        black_start_rejected=OperationalRejectCategory.NOT_SUPPORTED,
        black_start_rejection_reason="Only white starts supported",
        over_power_capacity=9001,
        over_power_rejected=OperationalRejectCategory.OTHER,
        over_power_rejection_reason="It broke the sensor",
        peak_mode_capacity=9002,
        peak_mode_rejected=OperationalRejectCategory.OTHER,
        peak_mode_rejection_reason="It broke the sensor",
        system_security_pump_rejected=OperationalRejectCategory.OTHER,
        system_security_pump_rejection_reason="She can't take much more of this, captain",
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == read_request_file("surplus_capacity_data_full.xml").encode("UTF-8")
    verify_surplus_capacity_data(
        request,
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        area=AreaCode.CHUBU,
        participant="F100",
        company="偽会社",
        system_code="FSYS0",
        resource_name="偽電力",
        upward_capacity=100,
        upward_capacity_rejected=RejectCategory.FUEL_RESTRICTION,
        upward_capacity_rejection_reason="Not enough fuel",
        downward_capacity=200,
        downward_capacity_rejected=RejectCategory.RIVER_FLOW_RESTRICTION,
        downward_capacity_rejection_reason="Not enough river",
        voltage_adjustment_rejected=OperationalRejectCategory.EQUIPMENT_FAILURE,
        voltage_adjustment_rejection_reason="The voltage broke",
        black_start_rejected=OperationalRejectCategory.NOT_SUPPORTED,
        black_start_rejection_reason="Only white starts supported",
        over_power_capacity=9001,
        over_power_rejected=OperationalRejectCategory.OTHER,
        over_power_rejection_reason="It broke the sensor",
        peak_mode_capacity=9002,
        peak_mode_rejected=OperationalRejectCategory.OTHER,
        peak_mode_rejection_reason="It broke the sensor",
        system_security_pump_rejected=OperationalRejectCategory.OTHER,
        system_security_pump_rejection_reason="She can't take much more of this, captain",
    )


def test_surplus_capacity_query_defaults():
    """Test that the SurplusCapacityQuery class initializes and converts to XML as we expect."""
    # First, create a new surplus capacity query request
    request = SurplusCapacityQuery(
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<RemainingReserveDataQuery StartTime="2024-04-12T15:00:00" EndTime="2024-04-12T18:00:00"/>"""
    verify_surplus_capacity_query(
        request,
        DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
    )


def test_surplus_capacity_query_full():
    """Test that the SurplusCapacityQuery class initializes and converts to XML as we expect."""
    # First, create a new surplus capacity query request
    request = SurplusCapacityQuery(
        resource_code="FAKE_RESO",
        pattern_number=1,
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert (
        data
        == b"""<RemainingReserveDataQuery ResourceName="FAKE_RESO" DrPatternNumber="1" StartTime="2024-04-12T15:00:00" EndTime="2024-04-12T18:00:00"/>"""
    )
    verify_surplus_capacity_query(
        request,
        DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        "FAKE_RESO",
        1,
    )
