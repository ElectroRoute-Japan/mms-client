"""Tests the functionality in the mms_client.types.resource module."""

from datetime import date as Date
from decimal import Decimal

from mms_client.types.enums import AreaCode
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
from tests.testutils import afc_minimum_output_verifier
from tests.testutils import event_verifier
from tests.testutils import output_band_verifier
from tests.testutils import pattern_verifier
from tests.testutils import switch_output_verifier
from tests.testutils import verify_resource_data


def test_resource_data_defaults():
    """Test that the ResourceData class initializes and converts to XML as expected."""
    # First, create a new resource data request
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

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == (
        """<Resource ParticipantName="F100" ResourceName="FAKE_RESO" ContractType="1" ResourceType="6" AreaCode="01" """
        """StartDate="2024-04-10" SystemCode="FSYS0" ResourceShortName="偽電力" ResourceLongName="この発電機は偽物です" """
        """PriRemResvUtilization="0" Sec1RemResvUtilization="0" Sec2RemResvUtilization="0" Ter1RemResvUtilization="0" """
        """Ter2RemResvUtilization="0" SignalType="1" RecordStatus="APPROVED"/>"""
    ).encode("UTF-8")
    verify_resource_data(
        request,
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


def test_resource_data_full():
    """Test that the ResourceData class initializes and converts to XML as expected."""
    # First, create a new resource data request
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
                    StartupEvent(name=StartupEventType.STARTUP_OPERATION, charge_time="00:10", output_kw=5000),
                    StartupEvent(name=StartupEventType.BOILER_IGNITION, charge_time="01:20", output_kw=6000),
                    StartupEvent(name=StartupEventType.TURBINE_STARTUP, charge_time="10:03", output_kw=7000),
                    StartupEvent(name=StartupEventType.CONNECTION, charge_time="-01:01", output_kw=8000),
                    StartupEvent(name=StartupEventType.POWER_SUPPLY_OPERATION, charge_time="-00:50", output_kw=9000),
                    StartupEvent(name=StartupEventType.OUTPUT_SETPOINT13, charge_time="-10:05", output_kw=10000),
                ],
            )
        ],
        shutdown_patterns=[
            ShutdownPattern(
                pattern_name="偽パターン２",
                events=[
                    ShutdownEvent(name=StopEventType.OUTPUT_SETPOINT1, charge_time="-45:33", output_kw=5000),
                    ShutdownEvent(name=StopEventType.DISCONNECTION, charge_time="-00:32", output_kw=10),
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

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")
    print(request)

    # Finally, verify that the request was created with the correct parameters
    assert data == (
        """<Resource ParticipantName="F100" ResourceName="FAKE_RESO" ContractType="2" ResourceType="1" AreaCode="03" """
        """StartDate="2024-04-10" EndDate="2044-04-11" SystemCode="FSYS0" ResourceShortName="偽電力" ResourceLongName"""
        """="この発電機は偽物です" BgCode="FKBG1" Pri="true" PriResponseTime="00:54:22" PriContinuousTime="95:59:59" """
        """PriMaximumSupplyQuantity="200000" PriRemResvUtilization="3" PriRemResvMaximumSupplyQuantity="50000" """
        """Sec1="true" Sec1ResponseTime="01:33:00" Sec1ContinuousTime="10:00:00" Sec1MaximumSupplyQuantity="100000" """
        """Sec1RemResvUtilization="0" Sec1RemResvMaximumSupplyQuantity="25000" Sec2="true" Sec2ResponseTime="10:00:"""
        """55" Sec2ContinuousTime="99:00:00" Sec2DownTime="00:00:00" Sec2MaximumSupplyQuantity="300000" Sec2RemResvUt"""
        """ilization="1" Sec2RemResvMaximumSupplyQuantity="60000" Ter1="true" Ter1ResponseTime="00:00:00" Ter1Continu"""
        """ousTime="99:59:59" Ter1MaximumSupplyQuantity="380900" Ter1RemResvUtilization="2" Ter1RemResvMaximumSupplyQ"""
        """uantity="90000" Ter2="true" Ter2ResponseTime="05:00:00" Ter2ContinuousTime="00:00:40" Ter2MaximumSupplyQua"""
        """ntity="1000000" Ter2RemResvUtilization="3" Ter2RemResvMaximumSupplyQuantity="200000" PriSec1CommandOperati"""
        """onMethod="1" Sec2Ter1Ter2CommandOperationMethod="2" SignalType="2" BaselineSettingMethod="2" ContractExist"""
        """ence="1" DeclaredMaximumUnitPrice="25.45" VoltageAdjustment="0" Address="〒100-0001 東京都千代田区千代田１−１−１" """
        """PayeePhonePart1="03" PayeePhonePart2="1234" PayeePhonePart3="5678" VenId="FAKEVENID231AJSDF12435T" """
        """MarketContext="FAKECONTEXT" ModelName="FAKEMODEL" RatedCapacity="750000" RatedVoltage="999.9" ContinuousOp"""
        """erationVoltage="95.6" RatedPowerFactor="99.0" Frequency="50" InternalEfficiency="97% FOR REAL YO" Continuo"""
        """usOperationFrequencyLower="52.4" ContinuousOperationFrequencyUpper="55.6" BlackStart="1" RatedOutput="2000"""
        """000" MinimumOutput="500000" AuthorizedMaximumOutput="0" ThermalType="2" BatteryCapacity="1523000" PumpChar"""
        """ging="1" VariableSpeedOperation="0" DischargingOutput="340000" DischargingTime="44" ChargingOutput="42000"""
        """0" ChargingTime="55" FullGenerationTime="77.7" ContinuousOperationTime="37.7" LimitedContinuousOperationTi"""
        """me="88.8" PhaseLocked="1" AmountOfWaterUsed="7777777" ReservoirCapacity="1234567" InflowAmount="9876543" """
        """ContinuousOperationOutput="1337" PumpedSupply="42069" FcbOperation="1" OverPowerOperation="1" PeakModeOper"""
        """ation="1" Dss="1" OverPowerOperationMaximumOutput="444444" PeakModeOperationMaximumOutput="222222" Operati"""
        """onTime="80.0" NumberOfStartups="9001" AfcMinimumOutput="9002" GfVariationRate="23.5" GfWidthOutOfRatedOutp"""
        """ut="235023" Transfer="false" PreviousParticipantName="A001" PreviousResourceName="FAKE_RES1" OverrideOptio"""
        """n="OVERRIDE" RecordStatus="WORKING" TransactionId="derpderp"><OutputBand><OutputBandInfo Output="100" GfWi"""
        """dth="1000" AfcWidth="2000" AfcVariationSpeed="100" OtmVariationSpeed="200" AfcOtmVariationSpeed="300"/>"""
        """</OutputBand><SwitchOutput><SwitchOutputInfo Output="3000" SwitchTime="40"/></SwitchOutput><OutputRangeBel"""
        """owAfc><OutputRangeBelowAfcInfo Output="4000" OperationTime="50.1" OutputVariationSpeed="400"/></OutputRang"""
        """eBelowAfc><StartupPattern><StartupPatternInfo PatternName="偽パターン１"><StartupPatternEvent EventName="1" """
        """ChargeTime="00:10" Output="5000"/><StartupPatternEvent EventName="2" ChargeTime="01:20" Output="6000"/>"""
        """<StartupPatternEvent EventName="3" ChargeTime="10:03" Output="7000"/><StartupPatternEvent EventName="4" """
        """ChargeTime="-01:01" Output="8000"/><StartupPatternEvent EventName="25" ChargeTime="-00:50" Output="9000"/>"""
        """<StartupPatternEvent EventName="17" ChargeTime="-10:05" Output="10000"/></StartupPatternInfo></StartupPatt"""
        """ern><StopPattern><StopPatternInfo PatternName="偽パターン２"><StopPatternEvent EventName="1" ChargeTime="""
        """"-45:33" Output="5000"/><StopPatternEvent EventName="21" ChargeTime="-00:32" Output="10"/></StopPatternInf"""
        """o></StopPattern><Comments>偽コメント FAKE COMMENT FTW</Comments></Resource>"""
    ).encode("UTF-8")
    verify_resource_data(
        request,
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
        address="〒100-0001 東京都千代田区千代田１−１−１",
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
