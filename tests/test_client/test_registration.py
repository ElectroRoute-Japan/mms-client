"""Tests the functionality in the mms_client.services.registration module."""

from decimal import Decimal

import pytest
import responses
from pendulum import Date

from mms_client.client import MmsClient
from mms_client.types.enums import AreaCode
from mms_client.types.registration import QueryAction
from mms_client.types.resource import AfcMinimumOutput
from mms_client.types.resource import BaseLineSettingMethod
from mms_client.types.resource import BooleanFlag
from mms_client.types.resource import CommandMonitorMethod
from mms_client.types.resource import ContractType
from mms_client.types.resource import Frequency
from mms_client.types.resource import OutputBand
from mms_client.types.resource import OverrideOption
from mms_client.types.resource import RemainingReserveAvailability
from mms_client.types.resource import ResourceData
from mms_client.types.resource import ResourceQuery
from mms_client.types.resource import ResourceType
from mms_client.types.resource import ShutdownEvent
from mms_client.types.resource import ShutdownPattern
from mms_client.types.resource import SignalType
from mms_client.types.resource import StartupEvent
from mms_client.types.resource import StartupEventType
from mms_client.types.resource import StartupPattern
from mms_client.types.resource import Status
from mms_client.types.resource import StopEventType
from mms_client.types.resource import SwitchOutput
from mms_client.types.resource import ThermalType
from mms_client.types.transport import RequestType
from mms_client.utils.web import ClientType
from tests.testutils import afc_minimum_output_verifier
from tests.testutils import event_verifier
from tests.testutils import output_band_verifier
from tests.testutils import pattern_verifier
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import register_mms_request
from tests.testutils import switch_output_verifier
from tests.testutils import verify_resource_data


def test_put_resource_invalid_client(mock_certificate):
    """Test that the put_resource method raises an exception when called by a non-BSP client."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.TSO, mock_certificate, test=True)

    # Next, create our test resource data
    request = ResourceData(
        participant="F100",
        name="FAKE_RESO",
        contract_type=ContractType.MARKET,
        resource_type=ResourceType.VPP_GEN_AND_DEM,
        area=AreaCode.HOKKAIDO,
        start=Date(2024, 4, 10),
        system_code="FSYS0",
        short_name="偽電力",
        full_name="この発電機は偽物です",
        primary_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        secondary_1_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        secondary_2_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        tertiary_1_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        tertiary_2_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        signal_type=SignalType.ACTUAL_OUTPUT_ORDER,
        status=Status.APPROVED,
    )

    # Now, try to submit the resource; this should raise an exception
    with pytest.raises(ValueError) as ex_info:
        _ = client.put_resource(request)

    # Finvally, verify the details of the raised exception
    assert (
        str(ex_info.value)
        == "RegistrationSubmit_Resource: Invalid client type, 'TSO' provided. Only 'BSP' is supported."
    )


@responses.activate
def test_put_resource_works(mock_certificate):
    """Test that the put_resource method works as expected."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test resource data
    request = ResourceData(
        output_bands=[
            OutputBand(
                output_kW=100,
                gf_bandwidth_kW=1000,
                lfc_bandwidth_kW=2000,
                lfc_variation_speed_kW_min=100,
                edc_change_rate_kW_min=200,
                edc_lfc_change_rate_kW_min=300,
            )
        ],
        switch_outputs=[SwitchOutput(output_kW=3000, switch_time_min=40)],
        afc_minimum_outputs=[AfcMinimumOutput(output_kW=4000, operation_time_hr=50.1, variation_speed_kW_min=400)],
        startup_patterns=[
            StartupPattern(
                pattern_name="偽パターン１",
                events=[
                    StartupEvent(name=StartupEventType.STARTUP_OPERATION, change_time="00:10", output_kw=5000),
                    StartupEvent(name=StartupEventType.BOILER_IGNITION, change_time="01:20", output_kw=6000),
                    StartupEvent(name=StartupEventType.TURBINE_STARTUP, change_time="10:03", output_kw=7000),
                    StartupEvent(name=StartupEventType.CONNECTION, change_time="-01:01", output_kw=8000),
                    StartupEvent(name=StartupEventType.POWER_SUPPLY_OPERATION, change_time="-00:50", output_kw=9000),
                    StartupEvent(name=StartupEventType.OUTPUT_SETPOINT13, change_time="-10:05", output_kw=10000),
                ],
            )
        ],
        shutdown_patterns=[
            ShutdownPattern(
                pattern_name="偽パターン２",
                events=[
                    ShutdownEvent(name=StopEventType.OUTPUT_SETPOINT1, change_time="-45:33", output_kw=5000),
                    ShutdownEvent(name=StopEventType.DISCONNECTION, change_time="-00:32", output_kw=10),
                ],
            )
        ],
        comments="偽コメント FAKE COMMENT FTW",
        participant="F100",
        name="FAKE_RESO",
        contract_type=ContractType.MARKET_AND_POWER_SUPPLY_2,
        resource_type=ResourceType.THERMAL,
        area=AreaCode.TOKYO,
        start=Date(2024, 4, 10),
        end=Date(2044, 4, 11),
        system_code="FSYS0",
        short_name="偽電力",
        full_name="この発電機は偽物です",
        balancing_group="FKBG1",
        has_primary=True,
        primary_response_time="00:54:22",
        primary_continuous_time="95:59:59",
        primary_available_capacity_kW=200000,
        primary_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_AND_DOWN,
        primary_remaining_reserve_capacity_kW=50000,
        has_secondary_1=True,
        secondary_1_response_time="01:33:00",
        secondary_1_continuous_time="10:00:00",
        secondary_1_available_capacity_kW=100000,
        secondary_1_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        secondary_1_remaining_reserve_capacity_kW=25000,
        has_secondary_2=True,
        secondary_2_response_time="10:00:55",
        secondary_2_continuous_time="99:00:00",
        secondary_2_downtime="00:00:00",
        secondary_2_available_capacity_kW=300000,
        secondary_2_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_ONLY,
        secondary_2_remaining_reserve_capacity_kW=60000,
        has_tertiary_1=True,
        tertiary_1_response_time="00:00:00",
        tertiary_1_continuous_time="99:59:59",
        tertiary_1_available_capacity_kW=380900,
        tertiary_1_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_DOWN_ONLY,
        tertiary_1_remaining_reserve_capacity_kW=90000,
        has_tertiary_2=True,
        tertiary_2_response_time="05:00:00",
        tertiary_2_continuous_time="00:00:40",
        tertiary_2_available_capacity_kW=1000000,
        tertiary_2_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_AND_DOWN,
        tertiary_2_remaining_reserve_capacity_kW=200000,
        primary_secondary_1_control_method=CommandMonitorMethod.DEDICATED_LINE,
        secondary_2_tertiary_control_method=CommandMonitorMethod.SIMPLE_COMMAND,
        signal_type=SignalType.DIFFERENTIAL_OUTPUT_ORDER,
        baseline_setting_method=BaseLineSettingMethod.MEASUREMENT_BASE,
        has_contract=BooleanFlag.YES,
        declared_maximum_unit_price_kWh=25.45,
        voltage_adjustable=BooleanFlag.NO,
        address="〒100-0001 東京都千代田区千代田１−１−１",
        phone_1="03",
        phone_2="1234",
        phone_3="5678",
        ven_id="FAKEVENID231AJSDF12435T",
        market_context="FAKECONTEXT",
        model="FAKEMODEL",
        rated_capacity_kVA=750000,
        rated_voltage_kV=999.9,
        continuous_operation_voltage=95.6,
        rated_power_factor=99.0,
        frequency=Frequency.EAST,
        internal_efficiency="97% FOR REAL YO",
        minimum_continuous_operation_frequency=52.4,
        maximum_continuous_operation_frequency=55.6,
        can_black_start=BooleanFlag.YES,
        rated_output_kW=2000000,
        minimum_output_kW=500000,
        maximum_output_authorized_kW=0,
        thermal_type=ThermalType.GTCC,
        battery_capacity_kWh=1523000,
        has_pump_charging=BooleanFlag.YES,
        has_variable_speed_operation=BooleanFlag.NO,
        discharging_output_kW=340000,
        discharging_time_min=44,
        charging_output_kw=420000,
        charging_time_min=55,
        full_generation_time_hr=77.7,
        continuous_operation_time=37.7,
        limitd_continuous_operation_time=88.8,
        is_phase_locked=BooleanFlag.YES,
        water_usage_m3_sec=7777777,
        reservior_capacity_dam3=1234567,
        inflow_amount_m3_sec=9876543,
        continuous_output_kW=1337,
        pumped_supply_capacity_kW=42069,
        has_fcb_operation=BooleanFlag.YES,
        has_overpower_operation=BooleanFlag.YES,
        has_peak_mode_operation=BooleanFlag.YES,
        has_dss=BooleanFlag.YES,
        overpower_maximum_output_kW=444444,
        peak_mode_maximum_output_kW=222222,
        operation_time_hr=80.0,
        startups=9001,
        edc_lfc_minimum_output_kw=9002,
        gf_variation_rate=23.5,
        gf_width_outside_rated_output_kW=235023,
        will_transfer=False,
        previous_participant="A001",
        previous_name="FAKE_RES1",
        override=OverrideOption.OVERRIDE,
        status=Status.IN_PROGRESS,
        transaction_id="derpderp",
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.REGISTRATION,
        (
            "id0MOFNI1jdOVarYdFWGCWMbVCZfSh/WTqxyO4kuZnWAs2xSMgnP0stWU79q0fdU1oWqCFZalp/GpqYQhYwVBkgVDns/yAqX55lnjiuLq"
            "E90vNYeKw9J/+mXpA/+oibaJluwMRq78hVS9BkpKDmcXhD02yagS7GnU8knegykO0fpUyNMh/HsDQiqgoE3rrdDSQxdOfAfiwXOfEoNo7"
            "i4BP9XmYK4JOb1QenZBJcZy84yZukuw3quC1NguKtCFEHRAlLFPbVzD1N36Bo+5SYnysHBevOLDwP1Bdv+nVDUAGGTdDXcjo0ZiqYrCjM"
            "K7GtVnDEtgLolCviPcRQx8jfi1/6ngJVOO+DJaT+raNsby3T7IxRJl+IFfxpzg6SrNxNPCCS/aUxYHv+Iba/b4tAyJuwZx9i8FAZJclZh"
            "ceVMdZq4GG2aju25TlJI2JxVGOusKl17SWUp+616Zd5nsvPrvCmumQWpvjxSUHG932/h8fqX2cM2E8d4jirmDu00tHXDOtfpC479W99+L"
            "zE5HPLe6iDBWFT1dpGYNV3oCek4T1vsLGZGGcjLnNKcLvpEVvprpoYMku2LMTu+Yy2ba8FppUPoBF1DGJr4Webec/yUdGjO9JeM5e7SGN"
            "PxLtw7hMrh4Vau+vSBHNOtQ3vZ2CRvoAlAK+HdXzQooe9/FJOQHIE="
        ),
        read_request_file("put_resource_request.xml"),
        read_file("put_resource_response.xml"),
        warnings=True,
        multipart=True,
        encoded=True,
    )

    # Now, attempt to put a resource with the valid client type; this should succeed
    resp = client.put_resource(request)

    # Finally, verify the response
    verify_resource_data(
        resp,
        output_band_verifiers=[output_band_verifier(100, 1000, 2000, 100, 200, 300)],
        switch_verifiers=[switch_output_verifier(3000, 40)],
        afc_minimum_verifiers=[afc_minimum_output_verifier(4000, Decimal("50.1"), 400)],
        startup_verifiers=[
            pattern_verifier(
                "偽パターン１",
                [
                    event_verifier(StartupEventType.STARTUP_OPERATION, "00:10", 5000),
                    event_verifier(StartupEventType.BOILER_IGNITION, "01:20", 6000),
                    event_verifier(StartupEventType.TURBINE_STARTUP, "10:03", 7000),
                    event_verifier(StartupEventType.CONNECTION, "-01:01", 8000),
                    event_verifier(StartupEventType.POWER_SUPPLY_OPERATION, "-00:50", 9000),
                    event_verifier(StartupEventType.OUTPUT_SETPOINT13, "-10:05", 10000),
                ],
            )
        ],
        shutdown_verifiers=[
            pattern_verifier(
                "偽パターン２",
                [
                    event_verifier(StopEventType.OUTPUT_SETPOINT1, "-45:33", 5000),
                    event_verifier(StopEventType.DISCONNECTION, "-00:32", 10),
                ],
            )
        ],
        comments="偽コメント FAKE COMMENT FTW",
        participant="F100",
        name="FAKE_RESO",
        contract_type=ContractType.MARKET_AND_POWER_SUPPLY_2,
        resource_type=ResourceType.THERMAL,
        area=AreaCode.TOKYO,
        start=Date(2024, 4, 10),
        end=Date(2044, 4, 11),
        system_code="FSYS0",
        short_name="偽電力",
        full_name="この発電機は偽物です",
        balancing_group="FKBG1",
        has_primary=True,
        primary_response_time="00:54:22",
        primary_continuous_time="95:59:59",
        primary_available_capacity_kW=200000,
        primary_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_AND_DOWN,
        primary_remaining_reserve_capacity_kW=50000,
        has_secondary_1=True,
        secondary_1_response_time="01:33:00",
        secondary_1_continuous_time="10:00:00",
        secondary_1_available_capacity_kW=100000,
        secondary_1_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        secondary_1_remaining_reserve_capacity_kW=25000,
        has_secondary_2=True,
        secondary_2_response_time="10:00:55",
        secondary_2_continuous_time="99:00:00",
        secondary_2_downtime="00:00:00",
        secondary_2_available_capacity_kW=300000,
        secondary_2_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_ONLY,
        secondary_2_remaining_reserve_capacity_kW=60000,
        has_tertiary_1=True,
        tertiary_1_response_time="00:00:00",
        tertiary_1_continuous_time="99:59:59",
        tertiary_1_available_capacity_kW=380900,
        tertiary_1_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_DOWN_ONLY,
        tertiary_1_remaining_reserve_capacity_kW=90000,
        has_tertiary_2=True,
        tertiary_2_response_time="05:00:00",
        tertiary_2_continuous_time="00:00:40",
        tertiary_2_available_capacity_kW=1000000,
        tertiary_2_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_AND_DOWN,
        tertiary_2_remaining_reserve_capacity_kW=200000,
        primary_secondary_1_control_method=CommandMonitorMethod.DEDICATED_LINE,
        secondary_2_tertiary_control_method=CommandMonitorMethod.SIMPLE_COMMAND,
        signal_type=SignalType.DIFFERENTIAL_OUTPUT_ORDER,
        baseline_setting_method=BaseLineSettingMethod.MEASUREMENT_BASE,
        has_contract=BooleanFlag.YES,
        declared_maximum_unit_price_kWh=Decimal("25.45"),
        voltage_adjustable=BooleanFlag.NO,
        address="〒１００ー０００１東京都千代田区千代田１ー１ー１",
        phone_1="03",
        phone_2="1234",
        phone_3="5678",
        ven_id="FAKEVENID231AJSDF12435T",
        market_context="FAKECONTEXT",
        model="FAKEMODEL",
        rated_capacity_kVA=750000,
        rated_voltage_kV=Decimal("999.9"),
        continuous_operation_voltage=Decimal("95.6"),
        rated_power_factor=Decimal("99.0"),
        frequency=Frequency.EAST,
        internal_efficiency="97% FOR REAL YO",
        minimum_continuous_operation_frequency=Decimal("52.4"),
        maximum_continuous_operation_frequency=Decimal("55.6"),
        can_black_start=BooleanFlag.YES,
        rated_output_kW=2000000,
        minimum_output_kW=500000,
        maximum_output_authorized_kW=0,
        thermal_type=ThermalType.GTCC,
        battery_capacity_kWh=1523000,
        has_pump_charging=BooleanFlag.YES,
        has_variable_speed_operation=BooleanFlag.NO,
        discharging_output_kW=340000,
        discharging_time_min=44,
        charging_output_kw=420000,
        charging_time_min=55,
        full_generation_time_hr=Decimal("77.7"),
        continuous_operation_time=Decimal("37.7"),
        limitd_continuous_operation_time=Decimal("88.8"),
        is_phase_locked=BooleanFlag.YES,
        water_usage_m3_sec=7777777,
        reservior_capacity_dam3=1234567,
        inflow_amount_m3_sec=9876543,
        continuous_output_kW=1337,
        pumped_supply_capacity_kW=42069,
        has_fcb_operation=BooleanFlag.YES,
        has_overpower_operation=BooleanFlag.YES,
        has_peak_mode_operation=BooleanFlag.YES,
        has_dss=BooleanFlag.YES,
        overpower_maximum_output_kW=444444,
        peak_mode_maximum_output_kW=222222,
        operation_time_hr=80.0,
        startups=9001,
        edc_lfc_minimum_output_kw=9002,
        gf_variation_rate=Decimal("23.5"),
        gf_width_outside_rated_output_kW=235023,
        will_transfer=False,
        previous_participant="A001",
        previous_name="FAKE_RES1",
        override=OverrideOption.OVERRIDE,
        status=Status.IN_PROGRESS,
        transaction_id="derpderp",
    )


def test_query_resources_invalid_client(mock_certificate):
    """Test that the query_resources method raises an exception when called by a non-BSP client."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.MO, mock_certificate, test=True)

    # Next, create our test resource query
    query = ResourceQuery(
        participant="F100",
        name="FAKE_RESO",
        status=Status.APPROVED,
    )

    # Now, try to query resources; this should raise an exception
    with pytest.raises(ValueError) as ex_info:
        _ = client.query_resources(query, QueryAction.NORMAL, Date(2024, 4, 11))

    # Finvally, verify the details of the raised exception
    assert (
        str(ex_info.value)
        == "RegistrationQuery_Resource: Invalid client type, 'MO' provided. Only 'BSP' or 'TSO' are supported."
    )


@responses.activate
def test_query_resources_works(mock_certificate):
    """Test that the query_resources method works as expected."""
    # First, create our MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test resource query
    query = ResourceQuery(
        participant="F100",
        name="FAKE_RESO",
        status=Status.APPROVED,
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.REGISTRATION,
        (
            "CdYPCLid6clLRClHQKnU06lscstA9XqyEIPc8qjYR2gi2O3GvcUuqWYQYBgaJ4kj9vrAIFgRUtk24cy0AeCX3cUp7lgpDI/2d5hSx4bx1"
            "n6m7ufUJvCeqe8+FC38gZSMGBqFiCNmP/OWU9M3Dfr66fqzmX52yCK/wDNVC6Y7XUfCWkImYMSniTy1OCi+vFZ5bnWIO9FDo33GHioZ+2"
            "vyCQ1P8pGy4YnxL8Iv9Iit4p+hctZsIJmb/IZEFZqEc3DmnWsxllSEVy/kPd/HYv60FxUPH3c5Zvcg2YHC7gsLNs4YC+8ZRKwEj4QTp4m"
            "kEkC45NvnYcjBxW9QkJ8UkPMY3QL0Sdrmmj12uq/dLRyObZvJwlC5MJkns+Jhm/uOAHd1/cVVoAoKIGCw8csYROy9/qb7ifI+Zkx64dSM"
            "FVXuuIOuP4O9yo6JwHBcB3XTLg/wFiTT6kp/YL6f18FBLxkY956El51fZTYKYAjiI4x2sANsy1Fd4GRiDNRRQnMMlQwI7evMJEeQEo+s0"
            "CLiD6kFdmgzBB9ZdkIIZ9iYipGs1MEoxNKhkLwtOEHVdmAi0Lb8nUvkUAXut97xLCwE03NRPoNkaMjzOMABLGRNPjAO0OMHEjIKP4UVS/"
            "AqoVGzT9c9Kakf8qoPuuOBLJ3+/vdkpENps0Aj1dVKuy9oTC5iIAY="
        ),
        read_request_file("query_resources_request.xml"),
        read_file("put_resource_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to put a resource with the valid client type; this should succeed
    resp = client.query_resources(query, QueryAction.NORMAL, Date(2024, 4, 11))

    # Finally, verify the response
    assert len(resp) == 1
    verify_resource_data(
        resp[0],
        output_band_verifiers=[output_band_verifier(100, 1000, 2000, 100, 200, 300)],
        switch_verifiers=[switch_output_verifier(3000, 40)],
        afc_minimum_verifiers=[afc_minimum_output_verifier(4000, Decimal("50.1"), 400)],
        startup_verifiers=[
            pattern_verifier(
                "偽パターン１",
                [
                    event_verifier(StartupEventType.STARTUP_OPERATION, "00:10", 5000),
                    event_verifier(StartupEventType.BOILER_IGNITION, "01:20", 6000),
                    event_verifier(StartupEventType.TURBINE_STARTUP, "10:03", 7000),
                    event_verifier(StartupEventType.CONNECTION, "-01:01", 8000),
                    event_verifier(StartupEventType.POWER_SUPPLY_OPERATION, "-00:50", 9000),
                    event_verifier(StartupEventType.OUTPUT_SETPOINT13, "-10:05", 10000),
                ],
            )
        ],
        shutdown_verifiers=[
            pattern_verifier(
                "偽パターン２",
                [
                    event_verifier(StopEventType.OUTPUT_SETPOINT1, "-45:33", 5000),
                    event_verifier(StopEventType.DISCONNECTION, "-00:32", 10),
                ],
            )
        ],
        comments="偽コメント FAKE COMMENT FTW",
        participant="F100",
        name="FAKE_RESO",
        contract_type=ContractType.MARKET_AND_POWER_SUPPLY_2,
        resource_type=ResourceType.THERMAL,
        area=AreaCode.TOKYO,
        start=Date(2024, 4, 10),
        end=Date(2044, 4, 11),
        system_code="FSYS0",
        short_name="偽電力",
        full_name="この発電機は偽物です",
        balancing_group="FKBG1",
        has_primary=True,
        primary_response_time="00:54:22",
        primary_continuous_time="95:59:59",
        primary_available_capacity_kW=200000,
        primary_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_AND_DOWN,
        primary_remaining_reserve_capacity_kW=50000,
        has_secondary_1=True,
        secondary_1_response_time="01:33:00",
        secondary_1_continuous_time="10:00:00",
        secondary_1_available_capacity_kW=100000,
        secondary_1_remaining_reserve_utilization=RemainingReserveAvailability.NOT_AVAILABLE,
        secondary_1_remaining_reserve_capacity_kW=25000,
        has_secondary_2=True,
        secondary_2_response_time="10:00:55",
        secondary_2_continuous_time="99:00:00",
        secondary_2_downtime="00:00:00",
        secondary_2_available_capacity_kW=300000,
        secondary_2_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_ONLY,
        secondary_2_remaining_reserve_capacity_kW=60000,
        has_tertiary_1=True,
        tertiary_1_response_time="00:00:00",
        tertiary_1_continuous_time="99:59:59",
        tertiary_1_available_capacity_kW=380900,
        tertiary_1_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_DOWN_ONLY,
        tertiary_1_remaining_reserve_capacity_kW=90000,
        has_tertiary_2=True,
        tertiary_2_response_time="05:00:00",
        tertiary_2_continuous_time="00:00:40",
        tertiary_2_available_capacity_kW=1000000,
        tertiary_2_remaining_reserve_utilization=RemainingReserveAvailability.AVAILABLE_FOR_UP_AND_DOWN,
        tertiary_2_remaining_reserve_capacity_kW=200000,
        primary_secondary_1_control_method=CommandMonitorMethod.DEDICATED_LINE,
        secondary_2_tertiary_control_method=CommandMonitorMethod.SIMPLE_COMMAND,
        signal_type=SignalType.DIFFERENTIAL_OUTPUT_ORDER,
        baseline_setting_method=BaseLineSettingMethod.MEASUREMENT_BASE,
        has_contract=BooleanFlag.YES,
        declared_maximum_unit_price_kWh=Decimal("25.45"),
        voltage_adjustable=BooleanFlag.NO,
        address="〒１００ー０００１東京都千代田区千代田１ー１ー１",
        phone_1="03",
        phone_2="1234",
        phone_3="5678",
        ven_id="FAKEVENID231AJSDF12435T",
        market_context="FAKECONTEXT",
        model="FAKEMODEL",
        rated_capacity_kVA=750000,
        rated_voltage_kV=Decimal("999.9"),
        continuous_operation_voltage=Decimal("95.6"),
        rated_power_factor=Decimal("99.0"),
        frequency=Frequency.EAST,
        internal_efficiency="97% FOR REAL YO",
        minimum_continuous_operation_frequency=Decimal("52.4"),
        maximum_continuous_operation_frequency=Decimal("55.6"),
        can_black_start=BooleanFlag.YES,
        rated_output_kW=2000000,
        minimum_output_kW=500000,
        maximum_output_authorized_kW=0,
        thermal_type=ThermalType.GTCC,
        battery_capacity_kWh=1523000,
        has_pump_charging=BooleanFlag.YES,
        has_variable_speed_operation=BooleanFlag.NO,
        discharging_output_kW=340000,
        discharging_time_min=44,
        charging_output_kw=420000,
        charging_time_min=55,
        full_generation_time_hr=Decimal("77.7"),
        continuous_operation_time=Decimal("37.7"),
        limitd_continuous_operation_time=Decimal("88.8"),
        is_phase_locked=BooleanFlag.YES,
        water_usage_m3_sec=7777777,
        reservior_capacity_dam3=1234567,
        inflow_amount_m3_sec=9876543,
        continuous_output_kW=1337,
        pumped_supply_capacity_kW=42069,
        has_fcb_operation=BooleanFlag.YES,
        has_overpower_operation=BooleanFlag.YES,
        has_peak_mode_operation=BooleanFlag.YES,
        has_dss=BooleanFlag.YES,
        overpower_maximum_output_kW=444444,
        peak_mode_maximum_output_kW=222222,
        operation_time_hr=80.0,
        startups=9001,
        edc_lfc_minimum_output_kw=9002,
        gf_variation_rate=Decimal("23.5"),
        gf_width_outside_rated_output_kW=235023,
        will_transfer=False,
        previous_participant="A001",
        previous_name="FAKE_RES1",
        override=OverrideOption.OVERRIDE,
        status=Status.IN_PROGRESS,
        transaction_id="derpderp",
    )
