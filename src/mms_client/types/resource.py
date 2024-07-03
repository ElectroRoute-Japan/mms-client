"""Contains objects for MMS resources."""

# pylint: disable=too-many-lines

from decimal import Decimal
from enum import Enum
from typing import Annotated
from typing import List
from typing import Optional

from pydantic_core import PydanticUndefined
from pydantic_extra_types.pendulum_dt import Date
from pydantic_xml import attr
from pydantic_xml import element
from pydantic_xml import wrapped

from mms_client.types.base import Payload
from mms_client.types.enums import AreaCode
from mms_client.types.enums import BaseLineSettingMethod
from mms_client.types.enums import BooleanFlag
from mms_client.types.enums import CommandMonitorMethod
from mms_client.types.enums import ContractType
from mms_client.types.enums import Frequency
from mms_client.types.enums import RemainingReserveAvailability
from mms_client.types.enums import ResourceType
from mms_client.types.enums import SignalType
from mms_client.types.fields import ASCII_TEXT
from mms_client.types.fields import JAPANESE_ASCII_TEXT
from mms_client.types.fields import JAPANESE_TEXT
from mms_client.types.fields import address
from mms_client.types.fields import capacity
from mms_client.types.fields import hour
from mms_client.types.fields import minute
from mms_client.types.fields import participant as participant_name
from mms_client.types.fields import pattern_name
from mms_client.types.fields import percentage
from mms_client.types.fields import phone
from mms_client.types.fields import price
from mms_client.types.fields import resource_name
from mms_client.types.fields import resource_short_name
from mms_client.types.fields import system_code
from mms_client.types.fields import transaction_id


def output(alias: str, optional: bool = False):
    """Create a field for an output value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the output value.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        gt=-10000000,
        lt=10000000,
    )


def time(alias: str, optional: bool = False):
    """Create a field for a time value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the time value.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        min_length=8,
        max_length=8,
        pattern=r"^[0-9]{2}:[0-5][0-9]:[0-5][0-9]$",
    )


def power_supply(alias: str, optional: bool = False):
    """Create a field for a power supply value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the power supply value.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        ge=0,
        lt=10000000,
    )


def continuous_operation_frequency(alias: str, optional: bool = False):
    """Create a field for a continuous operation frequency value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the continuous operation frequency value.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        ge=40.0,
        le=70.0,
        decimal_places=1,
    )


class StartupEventType(Enum):
    """Represents the type of event in the startup pattern."""

    STARTUP_OPERATION = "1"
    BOILER_IGNITION = "2"
    TURBINE_STARTUP = "3"
    CONNECTION = "4"
    OUTPUT_SETPOINT1 = "5"
    OUTPUT_SETPOINT2 = "6"
    OUTPUT_SETPOINT3 = "7"
    OUTPUT_SETPOINT4 = "8"
    OUTPUT_SETPOINT5 = "9"
    OUTPUT_SETPOINT6 = "10"
    OUTPUT_SETPOINT7 = "11"
    OUTPUT_SETPOINT8 = "12"
    OUTPUT_SETPOINT9 = "13"
    OUTPUT_SETPOINT10 = "14"
    OUTPUT_SETPOINT11 = "15"
    OUTPUT_SETPOINT12 = "16"
    OUTPUT_SETPOINT13 = "17"
    OUTPUT_SETPOINT14 = "18"
    OUTPUT_SETPOINT15 = "19"
    OUTPUT_SETPOINT16 = "20"
    OUTPUT_SETPOINT17 = "21"
    OUTPUT_SETPOINT18 = "22"
    OUTPUT_SETPOINT19 = "23"
    OUTPUT_SETPOINT20 = "24"
    POWER_SUPPLY_OPERATION = "25"


class StopEventType(Enum):
    """Represents the type of event in the stop pattern."""

    OUTPUT_SETPOINT1 = "1"
    OUTPUT_SETPOINT2 = "2"
    OUTPUT_SETPOINT3 = "3"
    OUTPUT_SETPOINT4 = "4"
    OUTPUT_SETPOINT5 = "5"
    OUTPUT_SETPOINT6 = "6"
    OUTPUT_SETPOINT7 = "7"
    OUTPUT_SETPOINT8 = "8"
    OUTPUT_SETPOINT9 = "9"
    OUTPUT_SETPOINT10 = "10"
    OUTPUT_SETPOINT11 = "11"
    OUTPUT_SETPOINT12 = "12"
    OUTPUT_SETPOINT13 = "13"
    OUTPUT_SETPOINT14 = "14"
    OUTPUT_SETPOINT15 = "15"
    OUTPUT_SETPOINT16 = "16"
    OUTPUT_SETPOINT17 = "17"
    OUTPUT_SETPOINT18 = "18"
    OUTPUT_SETPOINT19 = "19"
    OUTPUT_SETPOINT20 = "20"
    DISCONNECTION = "21"


class ThermalType(Enum):
    """Describes the type of thermal power generation unit."""

    GT = "1"
    GTCC = "2"
    OTHER = "9"


class OverrideOption(Enum):
    """Describes the override option for a power generation unit."""

    VIOLATION = "VIOLATION"
    OVERRIDE = "OVERRIDE"


class Status(Enum):
    """Describes the status of a power generation unit submission."""

    IN_PROGRESS = "WORKING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    DENIED = "DECLINED"


class OutputBand(Payload, tag="OutputBandInfo"):
    """Output band contract.

    The contract type is mandatory for THERMAL (thermal power generation), HYDRO (hydroelectric power generation), and
    PUMP (pumped storage power generation) power sources, except for ONLY_POWER_SUPPLY_1. It cannot be set for other
    power sources.
    """

    # The output of the band, in kW
    output_kW: int = output("Output")

    # The bandwidth of the gas fuel turbine, in kW. It represents the range of power outputs that the turbine can
    # efficiently produce while maintaining stable operation. This parameter is important for determining the
    # flexibility and versatility of the turbine in responding to varying demands on the electrical grid. A wider GF
    # width allows the turbine to adjust its output more effectively to match fluctuations in electricity demand.
    gf_bandwidth_kW: int = capacity("GfWidth", 0)

    # The bandwidth of the load-frequency control, in kW. It represents the range over which a power generation system
    # can adjust its output in response to changes in load demand or frequency deviations on the electrical grid. A
    # wider LFC bandwidth indicates that the power generation system can respond more quickly and effectively to
    # fluctuations in electricity demand or frequency variations, thereby helping to maintain grid stability.
    lfc_bandwidth_kW: int = capacity("AfcWidth", 0)

    # The variation speed of the LFC, in kW/min. It represents the speed of the Load-Frequency Control (LFC) function,
    # which ensures the stability of the power system in response to rapid fluctuations such as frequency changes. A
    # higher LFC change rate indicates that the power system can respond quickly to frequency and load changes, thereby
    # maintaining stability.
    lfc_variation_speed_kW_min: int = capacity("AfcVariationSpeed", 0)

    # The Energy Discharge Curve change rate, in kW/min. It refers to the rate at which the energy discharge curve
    # changes in response to fluctuations in power demand or supply. A higher EDC change rate indicates that the
    # energy discharge curve can adjust more rapidly to changes in demand or supply conditions. This parameter is
    # important for ensuring the stability and reliability of the power system.
    edc_change_rate_kW_min: int = capacity("OtmVariationSpeed", 0)

    # The EDC + LFC variation rate. It refers to the rate of change in both the Energy Discharge Curve (EDC) and the
    # Load Frequency Control (LFC) parameters within a power system, combining both aspects to provide a comprehensive
    # understanding of how quickly the power system can adapt to changes in energy discharge capability and frequency
    # control requirements. This parameter is crucial for assessing the dynamic performance and stability of the power
    # grid under varying operating conditions.
    edc_lfc_change_rate_kW_min: int = capacity("AfcOtmVariationSpeed", 0)


class SwitchOutput(Payload, tag="SwitchOutputInfo"):
    """Switching contract.

    Switching output refers to the amount of electrical power generated when switching power supply between different
    generating facilities or power sources in an electrical system. It indicates the minimum amount of power that the
    system generates or receives when shifting loads from one generating facility to another. The reasons for switching
    may include routine maintenance, abnormal operation of generating facilities, or fluctuations in demand.

    The contract type is mandatory for THERMAL (thermal power generation) power sources, except ONLY_POWER_SUPPLY_1.
    It cannot be set for other power sources.
    """

    # The switching output, in kW
    output_kW: int = capacity("Output", 0)

    # Required switching time for EDC/LFC operable output band
    switch_time_min: int = minute("SwitchTime")


class AfcMinimumOutput(Payload, tag="OutputRangeBelowAfcInfo"):
    """Minimum Output - EDC/LFC Operable Minimum Output contract.

    Contains data related to the minimum power output capability of a power generation unit, specifically concerning
    the operation of EDC (Economic Dispatch Control) and LFC (Load Frequency Control). It provides data related to the
    lowest power output of a generating unit, including how this minimum output affects its participation in economic
    dispatch and load frequency control operations within the power system.

    The contract type is mandatory for THERMAL (thermal power generation) power sources, except for ONLY_POWER_SUPPLY_1.
    It cannot be set for other power sources.
    """

    # The minimum output, in kW
    output_kW: int = capacity("Output", 0)

    # Operation continuity time, in hours. Refers to the duration for which a power generation unit needs to remain
    # operational. In other words, it represents the amount of time that a power generation unit must operate at a
    # steady load. This is necessary to ensure stability in situations such as rapid changes in power demand or under
    # specific conditions. The operational continuity time is determined based on operational requirements, constraints,
    # and the characteristics of the power generation unit.
    operation_time_hr: Decimal = hour("OperationTime")

    # The minimum output variation speed, in kW/min. It refers to the rate at which the power output of a generating
    # unit can change over time. It measures how quickly the power output can increase or decrease in response to
    # changes in demand or other factors. Faster output variation speeds indicate that the unit can adjust its output
    # more rapidly, providing greater flexibility to match fluctuations in demand and maintain system stability. This
    # parameter is important for ensuring grid reliability and efficiency in managing power generation resources.
    variation_speed_kW_min: int = capacity("OutputVariationSpeed", 0)


class StartupEvent(Payload):
    """Describes a single event in the startup pattern of a power generation unit."""

    # The name of the event. Each startup pattern must have a unique name. The STARTUP_OPERATION, BOILER_IGNITION,
    # TURBINE_STARTUP, CONNECTION, and POWER_SUPPLY_OPERATION events are mandatory. At least one of the output set
    # points 1-20 is required.
    name: StartupEventType = attr(name="EventName")

    # the time required to complete the event, within -99:59 to 99:59. The time is in the format "HH:MM" or "-HH:MM".
    change_time: str = attr(
        name="ChangeTime",
        pattern=r"^([0-9]{2}:[0-5][0-9])|(-00:(([0-5][1-9])|([1-5][0-9])))|(-(([0-9][1-9])|([1-9][0-9])):[0-5][0-9])$",
    )

    # The output of the event, in kW
    output_kw: int = capacity("Output", 0)


class StartupPattern(Payload, tag="StartupPatternInfo"):
    """Describes the startup pattern of a power generation unit.

    Refers to the specific parameters or configurations associated with the process of starting up the unit for power
    generation. This data type includes information such as the time duration, sequence of operations, and energy
    consumption associated with starting up the unit from a standby or offline state to full operational capacity. The
    startup pattern data provides insights into the efficiency, reliability, and cost implications of initiating power
    generation from the unit, which are crucial for economic analysis, optimization, and decision-making in the energy
    sector.

    The contract type is mandatory for THERMAL (thermal power generation) power sources, except for ONLY_POWER_SUPPLY_1.
    It cannot be set for other power sources.
    """

    # The name of the startup pattern. These must be unique with respect to the power generation unit.
    pattern_name: str = pattern_name("PatternName")

    # The events associated with this startup pattern
    events: List[StartupEvent] = element(tag="StartupPatternEvent", min_length=6, max_length=25)


class ShutdownEvent(Payload):
    """Describes a single event in the stop pattern of a power generation unit."""

    # The name of the event. Each shutdown pattern must have a unique name. The DISCONNECTION event is mandatory. At
    # least one of the output change points 1-20 is required.
    name: StopEventType = attr(name="EventName")

    # The time required to complete the event, within -99:59 to 00:00. The time is in the format "-HH:MM".
    change_time: str = attr(
        name="ChangeTime",
        pattern=r"^00:00|(-00:(([0-5][1-9])|([1-5][0-9])))|(-(([0-9][1-9])|([1-9][0-9])):[0-5][0-9])$",
    )

    # The output of the event, in kW
    output_kw: int = capacity("Output", 0)


class ShutdownPattern(Payload, tag="StopPatternInfo"):
    """Describes the stop pattern of a power generation unit.

    Refers to the specific parameters or configurations associated with the process of shutting down the unit for power
    generation. This data type includes information such as the time duration, sequence of operations, and energy
    consumption associated with shutting down the unit from a standby or offline state to full operational capacity. The
    shutdown pattern data provides insights into the efficiency, reliability, and cost implications of disconnecting
    power generation from the unit, which are crucial for economic analysis, optimization, and decision-making in the
    energy sector.

    The contract type is mandatory for THERMAL (thermal power generation) power sources, except for ONLY_POWER_SUPPLY_1.
    It cannot be set for other power sources.
    """

    # The name of the stop pattern. These must be unique with respect to the power generation unit.
    pattern_name: str = pattern_name("PatternName")

    # The events associated with this stop pattern
    events: List[ShutdownEvent] = element(tag="StopPatternEvent", min_length=2, max_length=21)


class ResourceData(Payload, tag="Resource"):
    """Contains the data common to both resource requests and responses."""

    # The output bands associated with this resource
    output_bands: Optional[List[OutputBand]] = wrapped(default=None, path="OutputBand", min_length=1, max_length=20)

    # The switching outputs associated with this resource
    switch_outputs: Optional[List[SwitchOutput]] = wrapped(
        default=None, path="SwitchOutput", min_length=1, max_length=20
    )

    # The minimum EDC/LFC outputs associated with this resource
    afc_minimum_outputs: Optional[List[AfcMinimumOutput]] = wrapped(
        default=None, path="OutputRangeBelowAfc", min_length=1, max_length=20
    )

    # The startup patterns associated with this resource
    startup_patterns: Optional[List[StartupPattern]] = wrapped(
        default=None, path="StartupPattern", min_length=1, max_length=20
    )

    # The stop patterns associated with this resource
    shutdown_patterns: Optional[List[ShutdownPattern]] = wrapped(
        default=None, path="StopPattern", min_length=1, max_length=20
    )

    # Any comments attached to the resource
    comments: Optional[str] = element(
        default=None, tag="Comments", min_length=1, max_length=128, pattern=JAPANESE_ASCII_TEXT
    )

    # The MMS code of the business entity to which the registration applies
    participant: str = participant_name("ParticipantName")

    # A code that uniquely identifies the power generation unit
    name: str = resource_name("ResourceName")

    # How the power generation unit is used in the market
    contract_type: ContractType = attr(name="ContractType")

    # How the power generation unit produces electricity
    resource_type: ResourceType = attr(name="ResourceType")

    # The region in which the power generation unit is located and in which its energy will be traded
    area: AreaCode = attr(name="Area")

    # The date from which the power generation unit is available to trade
    start: Date = attr(name="StartDate")

    # The date until which the power generation unit is available to trade
    end: Optional[Date] = attr(default=None, name="EndDate")

    # The grid code of the power generation unit
    system_code: str = system_code("SystemCode")

    # An abbreviated name for the power generation unit
    short_name: str = resource_short_name("ResourceShortName")

    # The full name for the power generation unit
    full_name: str = attr("ResourceLongName", min_length=1, max_length=50, pattern=JAPANESE_TEXT)

    # The balancing group code. For non-VPP resources, it is required; for VPP resources, it is optional.
    balancing_group: Optional[str] = attr(
        default=None, name="BgCode", min_length=5, max_length=5, pattern=r"^[a-zA-Z0-9]{5}$"
    )

    # Whether or not the resource is primary control power. Refers to the ability of a power generation unit or system
    # to rapidly adjust its output in response to fluctuations in demand or supply within the electrical grid. This
    # primary control power is essential for maintaining the stability and frequency of the grid, especially during
    # sudden changes in load or generation. Typically, primary control power is provided by resources such as
    # hydroelectric plants, natural gas turbines, or other fast-responding power generation assets. If you want to
    # allow market participation for the specified product category, you should set this to True.
    has_primary: Optional[bool] = attr(default=None, name="Pri")

    # The primary control power response time, in the format "HH:MM:SS". It refers to the time required for a power
    # generation unit to adjust its output in response to changes in demand or supply within the electrical grid. A
    # faster primary control power response time indicates that the unit can respond more quickly to fluctuations in
    # frequency or load, thereby helping to maintain grid stability. This parameter is important for assessing the
    # dynamic performance and reliability of the power system under varying operating conditions. Not applicable for
    # power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_primary is True.
    primary_response_time: Optional[str] = time("PriResponseTime", True)

    # The primary control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # primary control (such as frequency control) is continuously applied by a power generation unit. It represents the
    # period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_primary is True.
    primary_continuous_time: Optional[str] = time("PriContinuousTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if contract_type is not ONLY_POWER_SUPPLY_1
    # and the power source type is not VPP. For other power source types, it must not be set. If resource_type is HYDRO
    # or BATTERY, the value of this field must be less than or equal to the maximum of "rated output + GF width
    # (outside rated output) - minimum output" or "(pumping/charging - output) - minimum output." If resource_type is
    # THERMAL or HYDRO, the value of this field must be less than or equal to "rated output + GF width (outside rated
    # output) - minimum output." If has_primary is "false," the value of this field must be 0.
    primary_available_capacity_kW: Optional[int] = power_supply("PriMaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract_type MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    primary_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="PriRemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If primary_remaining_reserve_utilization
    # is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or AVAILABLE_FOR_UP_AND_DOWN, this field must be set.
    # If primary_remaining_reserve_utilization is set to NOT_AVAILABLE, this field must not be set.
    primary_remaining_reserve_capacity_kW: Optional[int] = capacity("PriRemResvMaximumSupplyQuantity", 0, True)

    # Whether or not the resource is secondary 1 control power. Secondary control power, also known as secondary reserve
    # or frequency containment reserve, refers to a type of reserve power that is used to stabilize the grid frequency
    # in the event of sudden changes in supply or demand. It is one of the mechanisms used in the regulation of grid
    # frequency and is typically provided by power plants or other sources that can quickly adjust their output in
    # response to frequency deviations. The secondary control power is activated automatically and rapidly in response
    # to frequency deviations detected by the grid's control system. If you want to allow market participation for the
    # specified product category, you should set this to True.
    has_secondary_1: Optional[bool] = attr(default=None, name="Sec1")

    # The secondary 1 control power response time, in the format "HH:MM:SS". It refers to the time required for a power
    # generation unit to adjust its output in response to changes in demand or supply within the electrical grid. A
    # faster seoncdary 1 control power response time indicates that the unit can respond more quickly to fluctuations
    # in frequency or load, thereby helping to maintain grid stability. This parameter is important for assessing the
    # dynamic performance and reliability of the power system under varying operating conditions. Not applicable for
    # power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_1 is True.
    secondary_1_response_time: Optional[str] = time("Sec1ResponseTime", True)

    # The secondary 1 control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # secondary 1 control (such as frequency control) is continuously applied by a power generation unit. It represents
    # the period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_1
    # is True.
    secondary_1_continuous_time: Optional[str] = time("Sec1ContinuousTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if the contract_type is not
    # ONLY_POWER_SUPPLY_1 and resource_type is not VPP. For other power source types, it must not be set. If
    # resource_type is HYDRO or BATTERY, the value of this field must be less than or equal to the maximum of "rated
    # output - minimum output" or "(pumping/charging - output) - minimum output." If resource_type is THERMAL or HYDRO,
    # the value of this field must be less than or equal to "rated output - minimum output." If has_secondary_1 is
    # False, the value of this field must be 0.
    secondary_1_available_capacity_kW: Optional[int] = power_supply("Sec1MaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract_type of MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    secondary_1_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Sec1RemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If
    # secondary_1_remaining_reserve_utilization is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or
    # AVAILABLE_FOR_UP_AND_DOWN, this field must be set. If secondary_1_remaining_reserve_utilization is set to
    # NOT_AVAILABLE, this field must not be set.
    secondary_1_remaining_reserve_capacity_kW: Optional[int] = capacity("Sec1RemResvMaximumSupplyQuantity", 0, True)

    # Whether or not the resource is secondary 2 control power. Secondary control power, also known as secondary reserve
    # or frequency containment reserve, refers to a type of reserve power that is used to stabilize the grid frequency
    # in the event of sudden changes in supply or demand. It is one of the mechanisms used in the regulation of grid
    # frequency and is typically provided by power plants or other sources that can quickly adjust their output in
    # response to frequency deviations. The secondary control power is activated automatically and rapidly in response
    # to frequency deviations detected by the grid's control system. If you want to allow market participation for the
    # specified product category, you should set this to True.
    has_secondary_2: Optional[bool] = attr(default=None, name="Sec2")

    # The secondary 2 control power response time, in the format "HH:MM:SS". It refers to the time required for a power
    # generation unit to adjust its output in response to changes in demand or supply within the electrical grid. A
    # faster seoncdary 2 control power response time indicates that the unit can respond more quickly to fluctuations
    # in frequency or load, thereby helping to maintain grid stability. This parameter is important for assessing the
    # dynamic performance and reliability of the power system under varying operating conditions. Not applicable for
    # power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_2 is True.
    secondary_2_response_time: Optional[str] = time("Sec2ResponseTime", True)

    # The secondary 2 control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # secondary 2 control (such as frequency control) is continuously applied by a power generation unit. It represents
    # the period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_2
    # is True.
    secondary_2_continuous_time: Optional[str] = time("Sec2ContinuousTime", True)

    # The secondary 2 control power down time, in the format "HH:MM:SS". Not applicable for power sources with
    # contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_2 is True.
    secondary_2_downtime: Optional[str] = time("Sec2DownTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if the contract_type is not
    # ONLY_POWER_SUPPLY_1 and resource_type is not VPP. For other power source types, it must not be set. The value of
    # this field must be less than or equal to the "rated output." If has_secondary_2 is "false," the value of this
    # field must be 0.
    secondary_2_available_capacity_kW: Optional[int] = power_supply("Sec2MaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract_type of MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    secondary_2_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Sec2RemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If
    # secondary_2_remaining_reserve_utilization is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or
    # AVAILABLE_FOR_UP_AND_DOWN, this field must be set. If secondary_2_remaining_reserve_utilization is set to
    # NOT_AVAILABLE, this field must not be set.
    secondary_2_remaining_reserve_capacity_kW: Optional[int] = capacity("Sec2RemResvMaximumSupplyQuantity", 0, True)

    # Whether or not the resource is tertairy 1 control power. Tertiary control power refers to the capacity of a
    # power generation unit or system to provide regulation services at the tertiary level of frequency control in
    # an electrical grid. In an electrical grid, frequency regulation is typically categorized into primary, secondary,
    # and tertiary control levels, each serving a specific role in maintaining grid stability. Tertiary control,
    # also known as frequency containment reserve (FCR), operates on a slower timescale compared to primary and
    # secondary control. It helps to fine-tune grid frequency over longer periods, usually several minutes to hours,
    # by adjusting the output of power generation units. The tertiary control power is often provided by power plants
    # that can adjust their output relatively quickly but are not as fast as those providing primary and secondary
    # control. This control level helps to ensure that the grid frequency remains within acceptable limits, thus
    # maintaining grid stability and reliability.If you want to allow market participation for the specified product
    # category, you should set this to True.
    has_tertiary_1: Optional[bool] = attr(default=None, name="Ter1")

    # The tertiary 1 control power response time, in the format "HH:MM:SS". It refers to the time required for a power
    # generation unit to adjust its output in response to changes in demand or supply within the electrical grid. A
    # faster tertiary 1 control power response time indicates that the unit can respond more quickly to fluctuations
    # in frequency or load, thereby helping to maintain grid stability. This parameter is important for assessing the
    # dynamic performance and reliability of the power system under varying operating conditions. Not applicable for
    # power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_tertiary_1 is True.
    tertiary_1_response_time: Optional[str] = time("Ter1ResponseTime", True)

    # The tertiary 1 control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # tertiary 1 control (such as frequency control) is continuously applied by a power generation unit. It represents
    # the period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_tertiary_1 is
    # True.
    tertiary_1_continuous_time: Optional[str] = time("Ter1ContinuousTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if the contract_type is not
    # ONLY_POWER_SUPPLY_1 and resource_type is not VPP. For other power source types, it must not be set. If
    # resource_type is HYDRO or BATTERY, the value of this field must be less than or equal to "rated output +
    # (pumping/charging - output)." If resource_type is THERMAL or HYDRO, the value of this field must be less than or
    # equal to "rated output." If has_tertiary_1 is "false," the value of this field must be 0.
    tertiary_1_available_capacity_kW: Optional[int] = power_supply("Ter1MaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract_type of MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    tertiary_1_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Ter1RemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If
    # tertiary_1_remaining_reserve_utilization is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or
    # AVAILABLE_FOR_UP_AND_DOWN, this field must be set. If tertiary_1_remaining_reserve_utilization is set to
    # NOT_AVAILABLE, this field must not be set.
    tertiary_1_remaining_reserve_capacity_kW: Optional[int] = capacity("Ter1RemResvMaximumSupplyQuantity", 0, True)

    # Whether or not the resource is tertairy 2 control power. Tertiary control power refers to the capacity of a
    # power generation unit or system to provide regulation services at the tertiary level of frequency control in
    # an electrical grid. In an electrical grid, frequency regulation is typically categorized into primary, secondary,
    # and tertiary control levels, each serving a specific role in maintaining grid stability. Tertiary control,
    # also known as frequency containment reserve (FCR), operates on a slower timescale compared to primary and
    # secondary control. It helps to fine-tune grid frequency over longer periods, usually several minutes to hours,
    # by adjusting the output of power generation units. The tertiary control power is often provided by power plants
    # that can adjust their output relatively quickly but are not as fast as those providing primary and secondary
    # control. This control level helps to ensure that the grid frequency remains within acceptable limits, thus
    # maintaining grid stability and reliability.If you want to allow market participation for the specified product
    # category, you should set this to True.
    has_tertiary_2: Optional[bool] = attr(default=None, name="Ter2")

    # The tertiary 2 control power response time, in the format "HH:MM:SS". It refers to the time required for a power
    # generation unit to adjust its output in response to changes in demand or supply within the electrical grid. A
    # faster tertiary 2 control power response time indicates that the unit can respond more quickly to fluctuations
    # in frequency or load, thereby helping to maintain grid stability. This parameter is important for assessing the
    # dynamic performance and reliability of the power system under varying operating conditions. Not applicable for
    # power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_tertiary_2 is True.
    tertiary_2_response_time: Optional[str] = time("Ter2ResponseTime", True)

    # The tertiary 2 control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # tertiary 2 control (such as frequency control) is continuously applied by a power generation unit. It represents
    # the period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract_type of ONLY_POWER_SUPPLY_1. Mandatory only if has_tertiary_2 is
    # True.
    tertiary_2_continuous_time: Optional[str] = time("Ter2ContinuousTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if the contract_type is not
    # ONLY_POWER_SUPPLY_1 and resource_type is not VPP. For other power source types, it must not be set. If
    # resource_type is HYDRO or BATTERY, the value of this field must be less than or equal to "rated output +
    # (pumping/charging - output)." If resource_type is THERMAL or HYDRO, the value of this field must be less than or
    # equal to "rated output." If has_tertiary_2 is "false," the value of this field must be 0.
    tertiary_2_available_capacity_kW: Optional[int] = power_supply("Ter2MaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract_type of MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    tertiary_2_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Ter2RemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If
    # tertiary_2_remaining_reserve_utilization is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or
    # AVAILABLE_FOR_UP_AND_DOWN, this field must be set. If tertiary_2_remaining_reserve_utilization is set to
    # NOT_AVAILABLE, this field must not be set.
    tertiary_2_remaining_reserve_capacity_kW: Optional[int] = capacity("Ter2RemResvMaximumSupplyQuantity", 0, True)

    # Primary-Secondary 1 command-and-control and monitoring method. Refers to the methodology or system utilized for
    # regulating and overseeing power generation units' operations in response to external commands or signals. This
    # method encompasses the process by which instructions are transmitted to power generation units, and their
    # performance is monitored to ensure compliance with these instructions. If has_secondary_1 is set to True, then
    # it must be set to DEDICATED_LINE. At least one of the following combinations must be set:
    #   primary_secondary_1_control_method
    #   secondary_2_tertiary_control_method
    primary_secondary_1_control_method: Optional[CommandMonitorMethod] = attr(
        default=None, name="PriSec1CommandOperationMethod"
    )

    # Secondary 2-Tertiary command-and-control and monitoring method. Refers to the methodology or system utilized for
    # regulating and overseeing power generation units' operations in response to external commands or signals. This
    # method encompasses the process by which instructions are transmitted to power generation units, and their
    # performance is monitored to ensure compliance with these instructions.
    secondary_2_tertiary_control_method: Optional[CommandMonitorMethod] = attr(
        default=None, name="Sec2Ter1Ter2CommandOperationMethod"
    )

    # The signal type for the power generation unit
    signal_type: SignalType = attr("SignalType")

    # Method determinining how the baseline is set for a power generation unit. The setting method is available when
    # the contract type is not ONLY_POWER_SUPPLY_1 and at least one of the following is True: has_primary,
    # has_secondary_1, has_secondary_2 or has_tertiary_1. Additionally, it can only be set when resource_type is
    # VPP_GEN, VPP_GEN_AND_DEM or VPP_DEM. It's mandatory in these cases and cannot be set for other power sources.
    baseline_setting_method: Optional[BaseLineSettingMethod] = attr(default=None, name="BaselineSettingMethod")

    # The presence or absences of a POWER_SUPPLY_1 contract. Applies only if the area is Okinawa, in which case it is
    # mandatory. Otherwise, it should not be set.
    has_contract: Optional[BooleanFlag] = attr(default=None, name="ContractExistence")

    # The maximum bid price for POWER_SUPPLY_1 power, in JPY/kW/hr
    declared_maximum_unit_price_kWh: Annotated[Decimal, price("DeclaredMaximumUnitPrice", 10000.00, True)]

    # Presence of voltage regulation function.
    voltage_adjustable: Optional[BooleanFlag] = attr(default=None, name="VoltageAdjustment")

    # Address of the resource. For power sources categorized under POWER_SUPPLY_1, this field is optional, while for
    # all other power sources, it is mandatory.
    address: Optional[str] = address("Address", True)

    # The first part of the phone number of the payee. For power sources categorized under POWER_SUPPLY_1, this field
    # is optional, while for all other power sources, it is mandatory.
    phone_1: Optional[str] = phone("PayeePhonePart1", True, True)

    # The second part of the phone number of the payee. For power sources categorized under POWER_SUPPLY_1, this field
    # is optional, while for all other power sources, it is mandatory.
    phone_2: Optional[str] = phone("PayeePhonePart2", False, True)

    # The third part of the phone number of the payee. For power sources categorized under POWER_SUPPLY_1, this field
    # is optional, while for all other power sources, it is mandatory.
    phone_3: Optional[str] = phone("PayeePhonePart3", False, True)

    # The VEN ID for this power generation unit. If secondary_2_tertiary_control_method is SIMPLE_COMMAND, this field
    # is mandatory. Otherwise, it may not be set.
    ven_id: Optional[str] = attr(default=None, name="VenId", min_length=1, max_length=64, pattern=ASCII_TEXT)

    # The market context for this power generation unit. If secondary_2_tertiary_control_method is SIMPLE_COMMAND, this
    # field is mandatory. Otherwise, it may not be set.
    market_context: Optional[str] = attr(
        default=None, name="MarketContext", min_length=1, max_length=256, pattern=ASCII_TEXT
    )

    # The model designation associated with this power generation unit.
    model: Optional[str] = attr(
        default=None, name="ModelName", min_length=1, max_length=50, pattern=JAPANESE_ASCII_TEXT
    )

    # Rated capacity, in kVA. Indicates the maximum power output that a generator or power plant can sustain over a
    # prolonged period without exceeding its design limits. If the contract_type is anything other than
    # ONLY_POWER_SUPPLY_1 and resource_type is not VPP, this field is mandatory. Otherwise, it cannot be set.
    rated_capacity_kVA: Optional[int] = capacity("RatedCapacity", 1000, True)

    # Rated voltage, in kV. Refers to the nominal voltage level at which a power generation unit is designed to operate.
    # If the contract_type is anything other than ONLY_POWER_SUPPLY_1 and resource_type is not VPP, this field is
    # mandatory. Otherwise, it cannot be set.
    rated_voltage_kV: Annotated[Decimal, attr(default=None, name="RatedVoltage", ge=0.0, le=1000.0, decimal_places=1)]

    # Continuous operation voltage as a percentage of the rated voltage. Refers to the voltage level at which a power
    # generation unit can operate continuously without exceeding its design limits. If the contract_type is anything
    # other than ONLY_POWER_SUPPLY_1 and resource_type is not VPP, this field is mandatory. Otherwise, it cannot be set.
    continuous_operation_voltage: Annotated[Decimal, percentage("ContinuousOperationVoltage", True)]

    # Rated power factor. Refers to the ratio of real power to apparent power in an electrical system. It indicates the
    # efficiency of power transfer between the power generation unit and the electrical grid. If the contract_type is
    # anything other than ONLY_POWER_SUPPLY_1 and resource_type is not VPP, this field is mandatory. Otherwise, it
    # cannot be set.
    rated_power_factor: Annotated[Decimal, percentage("RatedPowerFactor", True)]

    # Frequency of the power generation unit. Refers to the number of cycles per second at which the power generation
    # unit operates. It is an essential parameter for ensuring the synchronization of power generation units within the
    # electrical grid. If the contract_type is anything other than ONLY_POWER_SUPPLY_1 and resource_type is not VPP,
    # this field is mandatory. Otherwise, it cannot be set.
    frequency: Optional[Frequency] = attr(default=None, name="Frequency")

    # The internal efficiency of the power generation unit. If the contract_type is anything other than
    # ONLY_POWER_SUPPLY_1 and resource_type is not VPP, this field is mandatory. Otherwise, it cannot be set.
    internal_efficiency: Optional[str] = attr(
        default=None, name="InPlantRate", min_length=1, max_length=100, pattern=JAPANESE_ASCII_TEXT
    )

    # The lower bound of the continuous operation frequency. Refers to the minimum frequency at which a power
    # generation unit or system can operate continuously without experiencing issues or damage. In electrical power
    # systems, frequency is a crucial parameter that needs to be maintained within a specified range for stable and
    # reliable operation. The lower limit of continuous operation frequency ensures that the system can sustain its
    # operation without dropping below a certain frequency threshold, which could lead to equipment failure or
    # instability in the power grid.
    minimum_continuous_operation_frequency: Annotated[
        Decimal, continuous_operation_frequency("ContinuousOperationFrequencyLower", True)
    ]

    # The upper bound of the continuous operation frequency. Refers to the maximum frequency at which a power generation
    # unit or system can operate continuously without experiencing issues or damage. In electrical power systems,
    # frequency is a crucial parameter that needs to be maintained within a specified range for stable and reliable
    # operation. The upper limit of continuous operation frequency ensures that the system can sustain its operation
    # without exceeding a certain frequency threshold, which could lead to equipment failure or instability in the power
    # grid. If contract_type is anything other than ONLY_POWER_SUPPLY_1 and resource_type is not VPP, this field is
    # mandatory. Otherwise, it cannot be set.
    maximum_continuous_operation_frequency: Annotated[
        Decimal, continuous_operation_frequency("ContinuousOperationFrequencyUpper", True)
    ]

    # Whether or not the power generation unit can be started in black start mode. Black start refers to the process of
    # restarting a power generation unit or system without relying on external power sources. It is a critical
    # capability for power plants to restore electricity supply after a blackout or grid failure. If contract_type is
    # anything other than ONLY_POWER_SUPPLY_1 and resource_type is not VPP, this field is mandatory. Otherwise, it
    # cannot be set.
    can_black_start: Optional[BooleanFlag] = attr(default=None, name="BlackStart")

    # The rated output of the power generation unit, in kW. If contract_type is anything other than ONLY_POWER_SUPPLY_1
    # and resource_type is not VPP, this field is mandatory. Otherwise, it cannot be set.
    rated_output_kW: Optional[int] = capacity("RatedOutput", 0, True)

    # The minimum output of the power generation unit, in kW. For power sources with contract_type of
    # ONLY_POWER_SUPPLY_1, this field cannot be set. If resource_type is not VPP, it must be set. For VPP, the value
    # should be set to 0.
    minimum_output_kW: Optional[int] = capacity("MinimumOutput", 0, True)

    # The maximum authorized output of the power generation unit, in kW. It refers to the maximum amount of electricity
    # that a power generation unit is allowed to supply when operating normally. It represents the maximum power output
    # capacity permitted by the utility company or regulatory authority. If contract_type is anything other than
    # ONLY_POWER_SUPPLY_1 and resource_type is not VPP, this field is mandatory. Otherwise, it cannot be set.
    maximum_output_authorized_kW: Optional[int] = capacity("AuthorizedMaximumOutput", 0, True)

    # How power is generated by thermal power generation units. If contract_type is anything other than
    # ONLY_POWER_SUPPLY_1 and resource_type is THERMAL, then this field is mandatory. For other types of power
    # generation units, this field should not be set.
    thermal_type: Optional[ThermalType] = attr(default=None, name="ThermalType")

    # The amount of electrical energy that can be stored and discharged by a battery system, in kWh. If contract_type
    # is anything other than ONLY_POWER_SUPPLY_1 and resource_type is BATTERY, then this field is mandatory. For other
    # types of power generation units, this field should not be set.
    battery_capacity_kWh: Optional[int] = capacity("BatteryCapacity", 1000, True)

    # Whether or not this power source has pump-up/charging capability. If contract_type is anything other than
    # ONLY_POWER_SUPPLY_1 and resource_type is PUMP or BATTERY, then this field is mandatory. For other types of power
    # generation units, this field should not be set.
    has_pump_charging: Optional[BooleanFlag] = attr(default=None, name="PumpCharging")

    # Capability of adjusting the charging process or operation speed of a system. If contract_type is anything other
    # than ONLY_POWER_SUPPLY_1 and resource_type is PUMP or BATTERY, then this field is mandatory. For other types of
    # power generation units, this field should not be set.
    has_variable_speed_operation: Optional[BooleanFlag] = attr(default=None, name="VariableSpeedOperation")

    # The output power during the generation or discharge process, in kW. If contract_type is anything other than
    # ONLY_POWER_SUPPLY_1 and resource_type is PUMP or BATTERY, then this field is mandatory. For other types of power
    # generation units, this field should not be set.
    discharging_output_kW: Optional[int] = capacity("DischargingOutput", 0, True)

    # The time it takes for power generation or storage system to transition from the command to generate or discharge
    # power to the state of being in parallel operation, where it is actively supplying or absorbing power to/from the
    # grid or another system. If contract_type is anything other than ONLY_POWER_SUPPLY_1 and resource_type is PUMP or
    # BATTERY, then this field is mandatory. For other types of power generation units, this field should not be set.
    discharging_time_min: Optional[int] = minute("DischargingTime", True)

    # The output power during the charging process, in kW. If contract_type is anything other than ONLY_POWER_SUPPLY_1
    # and resource_type is PUMP or BATTERY, then this field is mandatory. For other types of power generation units,
    # this field should not be set.
    charging_output_kw: Optional[int] = capacity("ChargingOutput", 0, True)

    # The time it takes for power generation or storage system to transition from the command to charge to the state of
    # being in parallel operation, where it is actively supplying or absorbing power to/from the grid or another system.
    # If contract_type is anything other than ONLY_POWER_SUPPLY_1 and resource_type is PUMP or BATTERY, then this field
    # is mandatory. For other types of power generation units, this field should not be set.
    charging_time_min: Optional[int] = minute("ChargingTime", True)

    # The duration during which the power generation unit, such as a battery storage system, is capable of operating at
    # its maximum generation or discharge capacity without any constraints or limitations, in hours. If contract_type
    # is anything other than ONLY_POWER_SUPPLY_1 and resource_type is PUMP or BATTERY, then this field is mandatory.
    # For other types of power generation units, this field should not be set.
    full_generation_time_hr: Annotated[Decimal, hour("FullPowerGenerationTime", True)]

    # The duration for which the power generation unit can operate continuously without interruption or the need for
    # rest or maintenance, in hours. If contract_type is anything other than ONLY_POWER_SUPPLY_1, and resource_type is
    # PUMP, then this field is mandatory. For other types of power generation units, this field should not be set.
    continuous_operation_time: Annotated[Decimal, hour("ContinuousOperationTime", True)]

    # The maximum duration for which the power generation unit can continue operating under specific limitations or
    # constraints, in hours. This could include factors such as environmental conditions, equipment maintenance
    # requirements, or regulatory restrictions. If contract_type is ONLY_POWER_SUPPLY_1, then this field cannot be
    # set. Otherwise, this field is optional.
    limitd_continuous_operation_time: Annotated[Decimal, hour("ContinuousOperationTimeLimited", True)]

    # Phase locking is a method used in power systems to synchronize the phase angles of multiple alternating current
    # (AC) sources. In this mode of operation, the frequency and phase of the generated voltage are adjusted to match
    # those of the grid or another AC power source. This ensures that the AC output from the power source is in phase
    # with the grid, allowing for seamless integration and stable operation. If contract_type is anything other than
    # ONLY_POWER_SUPPLY_1 and resource_type is PUMP or HYDRO, then this field is mandatory. For other types of power
    # generation units, this field should not be set.
    is_phase_locked: Optional[BooleanFlag] = attr(default=None, name="PhaseModifyingOperation")

    # Quantity of water consumed, in cubic meters per second. If contract_type is anything other than
    # ONLY_POWER_SUPPLY_1 and resource_type is PUMP or HYDRO, then this field is mandatory. For other types of power
    # generation units, this field should not be set.
    water_usage_m3_sec: Optional[int] = capacity("AmountOfWaterUsed", 0, True)

    # Reservoir capacity in cubic decameters. If contract_type is anything other than ONLY_POWER_SUPPLY_1 and
    # resource_type is PUMP or HYDRO, then this field is mandatory. For other types of power generation units, this
    # field should not be set.
    reservior_capacity_dam3: Optional[int] = capacity("ReservoirCapacity", 0, True)

    # The volume of water that enters a reservoir or water storage facility over a specific period of time, in cubic
    # meters per second. If contract_type is anything other than ONLY_POWER_SUPPLY_1 and resource_type is PUMP or HYDRO,
    # then this field is mandatory. For other types of power generation units, this field should not be set.
    inflow_amount_m3_sec: Optional[int] = capacity("InflowAmount", 0, True)

    # The sustainable power output that a power generation unit can maintain over a specific duration without
    # interruption, in kW. This metric is crucial for assessing the reliability and capacity of a power generation
    # system to meet demand consistently over time. If contract_type is anything other than ONLY_POWER_SUPPLY_1 and
    # resource_type is PUMP or HYDRO, then this field is mandatory. For other types of power generation units, this
    # field should not be set.
    continuous_output_kW: Optional[int] = capacity("ContinuousOperationOutput", 0, True)

    # The ability of hydroelectric power stations or pumped-storage hydroelectric plants to supply power, in kW. It
    # represents the capacity of these facilities to generate electricity using water resources. If contract_type is
    # anything other than ONLY_POWER_SUPPLY_1 and resource_type is PUMP or HYDRO, then this field is mandatory. For
    # other types of power generation units, this field should not be set.
    pumped_supply_capacity_kW: Optional[int] = capacity("PumpedSupply", 0, True)

    # Whether operation of the Fuel Cell Balance of Plant (FCB) system is supported. The FCB is a key component of a
    # fuel cell system responsible for managing various auxiliary functions necessary for the operation of the fuel
    # cell stack. This includes tasks such as managing the flow of reactants (hydrogen and oxygen), controlling
    # temperature and humidity levels within the fuel cell stack, and providing power conditioning for the electrical
    # output of the fuel cell. FCB operation is essential for ensuring the efficient and reliable performance of the
    # overall fuel cell system. If contract_type is anything other than ONLY_POWER_SUPPLY_1, and resource_type is
    # THERMAL, then this field is mandatory. For other types of power generation units, this field should not be set.
    has_fcb_operation: Optional[BooleanFlag] = attr(default=None, name="FcbOperation")

    # Whether the power plant or generating facility can supply a greater amount of electrical power than its normal
    # output. In this mode, the power plant needs to provide additional power to meet increased demand or to ensure
    # the stability of the electrical grid. If contract_type is anything other than ONLY_POWER_SUPPLY_1, and
    # resource_type is THERMAL, then this field is mandatory. For other types of power generation units, this field
    # should not be set.
    has_overpower_operation: Optional[BooleanFlag] = attr(default=None, name="OverPowerOperation")

    # Whether the power generation facility at its maximum capacity to meet peak electricity demand. During peak hours,
    # when electricity demand is at its highest, power plants may operate in peak mode to provide the necessary
    # electricity to the grid. If contract_type is anything other than ONLY_POWER_SUPPLY_1, and resource_type is
    # THERMAL, then this field is mandatory. For other types of power generation units, this field should not be set.
    has_peak_mode_operation: Optional[BooleanFlag] = attr(default=None, name="PeakModeOperation")

    # Whether the power generation facility has a decision support system. If contract_type is anything other than
    # ONLY_POWER_SUPPLY_1, and resource_type is THERMAL, then this field is mandatory. For other types of power
    # generation units, this field should not be set.
    has_dss: Optional[BooleanFlag] = attr(default=None, name="Dss")

    # The maximum power output generated by a power plant when it operates in overpower mode, in kW. If contract_type
    # is anything other than ONLY_POWER_SUPPLY_1, resource_type is THERMAL and has_overpower_operation is YES, this
    # field is mandatory. However, for other types of power sources, this field cannot be set.
    overpower_maximum_output_kW: Optional[int] = capacity("OverPowerOperationMaximumOutput", 0, True)

    # The maximum power output generated by a power plant when it operates in peak mode, in kW. If contract_type is
    # anything other than ONLY_POWER_SUPPLY_1, resource_type is THERMAL and has_peak_mode_operation is YES, this field
    # is mandatory. However, for other types of power sources, this field cannot be set.
    peak_mode_maximum_output_kW: Optional[int] = capacity("PeakModeOperationMaximumOutput", 0, True)

    # The duration during which a power generation unit can effectively operate or generate electricity without
    # interruption, in hours. If contract_type is anything other than ONLY_POWER_SUPPLY_1, and resource_type is THERMAL,
    # then this field is mandatory. For other types of power generation units, this field should not be set.
    operation_time_hr: Annotated[Decimal, hour("OperationTime", True)]

    # The maximum allowable number of times a power generation unit can be started within a specified period. If
    # contract_type is anything other than ONLY_POWER_SUPPLY_1, and resource_type is THERMAL, then this field is
    # mandatory. For other types of power generation units, this field should not be set.
    startups: Optional[int] = attr(default=None, name="NumberOfStartups", ge=0, lt=10000)

    # The minimum output level at which a power generation unit equipped with Emergency Demand Control (EDC) or Load
    # Frequency Control (LFC) capabilities can operate effectively. If contract_type is anything other than
    # ONLY_POWER_SUPPLY_1, and resource_type is THERMAL, then this field is mandatory. For other types of power
    # generation units, this field should not be set.
    edc_lfc_minimum_output_kw: Optional[int] = capacity("AfcMinimumOutput", 0, True)

    # The rate at which a power generation unit equipped with Governor Function (GF) capabilities can adjust its output
    # in response to changes in grid frequency. If contract_type is anything other than ONLY_POWER_SUPPLY_1, and
    # resource_type is THERMAL, HYDRO, OR PUMP; then this field is mandatory. For other types of power generation units,
    # this field should not be set.
    gf_variation_rate: Annotated[Decimal, percentage("GfVariationRate", True)]

    # The range within which a power generation unit can modulate its output beyond its rated output, in kW.
    gf_width_outside_rated_output_kW: Optional[int] = capacity("GfWidthOutOfRatedOutput", 0, True)

    # Whether or not the power generation facility is being transferred to another entity.
    will_transfer: Optional[bool] = attr(default=None, name="Transfer")

    # The previous participant this power generation unit was associated with. This will only be populated if
    # will_transfer is True.
    previous_participant: Optional[str] = participant_name("PreviousParticipantName", True)

    # The previous code for this power generation unit. This will only be populated if will_transfer is True.
    previous_name: Optional[str] = resource_name("PreviousResourceName", True)

    # An option to override the existing data for this power generation unit. If this fails, the response will
    # contain a value of VIOLATION.
    override: Optional[OverrideOption] = attr(default=None, name="OverrideOption")

    # The status of the resource submission. This is automatically set.
    status: Status = attr(default=Status.IN_PROGRESS, name="RecordStatus")

    # An ID representing the transaction
    transaction_id: Optional[str] = transaction_id("TransactionId", True)


class ResourceQuery(Payload, tag="Resource"):
    """The query parameters for a power generation unit."""

    # The MMS code of the business entity to which the registration applies
    participant: Optional[str] = participant_name("ParticipantName", True)

    # A code that uniquely identifies the power generation unit
    name: Optional[str] = resource_name("ResourceName", True)

    # The status of the resources being queried.
    status: Optional[Status] = attr(default=None, name="RecordStatus")
