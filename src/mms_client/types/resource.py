"""Contains objects for MMS resources."""

from datetime import date as Date
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic_core import PydanticUndefined
from pydantic_xml import attr
from pydantic_xml import element
from pydantic_xml import wrapped

from mms_client.types.base import Payload
from mms_client.types.enums import AreaCode
from mms_client.types.fields import capacity, minute, hour, pattern_name, participant, resource_name, system_code, resource_short_name, JAPANESE_TEXT


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


class ContractType(Enum):
    """Describes the type of contract for a power generation unit."""

    MARKET = "1"
    MARKET_AND_POWER_SUPPLY_2 = "2"
    POWER_SUPPLY_2 = "3"
    ONLY_POWER_SUPPLY_1 = "4"
    MARKET_AND_REMAINING_RESERVE_UTILIZATION = "5"
    REMAINING_RESERVE_UTILIZATION = "6"


class ResourceType(Enum):
    """How the power generation unit produces electricity."""

    THERMAL = "1"
    HYDRO = "2"
    PUMP = "3"
    BATTERY = "4"
    VPP_GEN = "5"
    VPP_GEN_AND_DEM = "6"
    VPP_DEM = "7"


class RemainingReserveAvailability(Enum):
    """Describes the availability of remaining reserves for a power generation unit."""

    NOT_AVAILABLE = "0"
    AVAILABLE_FOR_UP_ONLY = "1"
    AVAILABLE_FOR_DOWN_ONLY = "2"
    AVAILABLE_FOR_UP_AND_DOWN = "3"


class CommandMonitorMethod(Enum):
    """Describes how the power generation unit is monitored and commanded."""

    DEDICATED_LINE = "1"
    SIMPLE_COMMAND = "2"
    OFFLINE = "3"


class BaseLineSettingMethod(Enum):
    """Describe how the baseline is set for a power generation unit."""

    PREDICTION_BASE = "1"
    MEASUREMENT_BASE = "2"


class OutputBand(Payload):
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
    gf_bandwidth_kW: int = capacity("GfWidth")

    # The bandwidth of the load-frequency control, in kW. It represents the range over which a power generation system
    # can adjust its output in response to changes in load demand or frequency deviations on the electrical grid. A
    # wider LFC bandwidth indicates that the power generation system can respond more quickly and effectively to 
    # fluctuations in electricity demand or frequency variations, thereby helping to maintain grid stability.
    lfc_bandwidth_kW: int = capacity("AfcWidth")

    # The variation speed of the LFC, in kW/min. It represents the speed of the Load-Frequency Control (LFC) function,
    # which ensures the stability of the power system in response to rapid fluctuations such as frequency changes. A
    # higher LFC change rate indicates that the power system can respond quickly to frequency and load changes, thereby
    # maintaining stability.
    lfc_variation_speed_kW_min: int = capacity("AfcVariationSpeed")

    # The Energy Discharge Curve change rate, in kW/min. It refers to the rate at which the energy discharge curve
    # changes in response to fluctuations in power demand or supply. A higher EDC change rate indicates that the
    # energy discharge curve can adjust more rapidly to changes in demand or supply conditions. This parameter is
    # important for ensuring the stability and reliability of the power system.
    edc_change_rate_kW_min: int = capacity("OtmVariationSpeed")

    # The EDC + LFC variation rate. It refers to the rate of change in both the Energy Discharge Curve (EDC) and the
    # Load Frequency Control (LFC) parameters within a power system, combining both aspects to provide a comprehensive
    # understanding of how quickly the power system can adapt to changes in energy discharge capability and frequency
    # control requirements. This parameter is crucial for assessing the dynamic performance and stability of the power
    # grid under varying operating conditions.
    edc_lfc_change_rate_kW_min: int = capacity("AfcOtmVariationSpeed")


class SwitchOutput(Payload):
    """Switching contract.
    
    Switching output refers to the amount of electrical power generated when switching power supply between different
    generating facilities or power sources in an electrical system. It indicates the minimum amount of power that the
    system generates or receives when shifting loads from one generating facility to another. The reasons for switching
    may include routine maintenance, abnormal operation of generating facilities, or fluctuations in demand.

    The contract type is mandatory for THERMAL (thermal power generation) power sources, except ONLY_POWER_SUPPLY_1.
    It cannot be set for other power sources.
    """
    
    # The switching output, in kW
    output_kW: int = capacity("Output")

    # Required switching time for EDC/LFC operable output band
    switch_time_min: int = minute("SwitchTime")


class AfcMinimumOutput(Payload):
    """Minimum Output - EDC/LFC Operable Minimum Output contract.
    
    Contains data related to the minimum power output capability of a power generation unit, specifically concerning
    the operation of EDC (Economic Dispatch Control) and LFC (Load Frequency Control). It provides data related to the
    lowest power output of a generating unit, including how this minimum output affects its participation in economic
    dispatch and load frequency control operations within the power system.

    The contract type is mandatory for THERMAL (thermal power generation) power sources, except for ONLY_POWER_SUPPLY_1.
    It cannot be set for other power sources.
    """
    
    # The minimum output, in kW
    output_kW: int = capacity("Output")

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
    variation_speed_kW_min: int = capacity("OutputVariationSpeed")


class StartupEvent(Payload):
    """Describes a single event in the startup pattern of a power generation unit."""

    # The name of the event. Each startup pattern must have a unique name. The STARTUP_OPERATION, BOILER_IGNITION,
    # TURBINE_STARTUP, CONNECTION, and POWER_SUPPLY_OPERATION events are mandatory. At least one of the output set
    # points 1-20 is required.
    name: StartupEventType = attr(name="EventName")

    # the time required to complete the event, within -99:59 to 99:59. The time is in the format "HH:MM" or "-HH:MM".
    charge_time: str = attr(name="ChargeTime", pattern=r"^([0-9]{2}:[0-5][0-9])|(-00:(([0-5][1-9])|([1-5][0-9])))|(-(([0-9][1-9])|([1-9][0-9])):[0-5][0-9])$")

    # The output of the event, in kW
    output_kw: int = capacity("Output")


class StartupPattern(Payload):
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
    charge_time: str = attr(name="ChargeTime", pattern=r"^00:00|(-00:(([0-5][1-9])|([1-5][0-9])))|(-(([0-9][1-9])|([1-9][0-9])):[0-5][0-9])$")

    # The output of the event, in kW
    output_kw: int = capacity("Output")


class ShutdownPattern(Payload):
    """Describes the stop pattern of a power generation unit.
    
    Refers to the specific parameters or configurations associated with the process of shutting down the unit for power
    generation. This data type includes information such as the time duration, sequence of operations, and energy
    consumption associated with shutting down the unit from a standby or offline state to full operational capacity. The
    shutdown pattern data provides insights into the efficiency, reliability, and cost implications of disconnecting power
    generation from the unit, which are crucial for economic analysis, optimization, and decision-making in the energy
    sector.

    The contract type is mandatory for THERMAL (thermal power generation) power sources, except for ONLY_POWER_SUPPLY_1.
    It cannot be set for other power sources.
    """

    # The name of the stop pattern. These must be unique with respect to the power generation unit.
    pattern_name: str = pattern_name("PatternName")

    # The events associated with this stop pattern
    events: List[ShutdownEvent] = element(tag="StopPatternEvent", min_length=2, max_length=21)


class Resource(Payload):
    """Contains the data common to both resource requests and responses."""

    # The output bands associated with this resource
    output_bands: List[OutputBand] = wrapped(path="OutputBand/OutputBandInfo", min_length=0, max_length=20)

    # The switching outputs associated with this resource
    switch_outputs: List[SwitchOutput] = wrapped(path="SwitchOutput/SwitchOutputInfo", min_length=0, max_length=20)

    # The minimum EDC/LFC outputs associated with this resource
    afc_minimum_outputs: List[AfcMinimumOutput] = wrapped(path="OutputRangeBelowAfc/OutputRangeBelowAfcInfo", min_length=0, max_length=20)

    # The startup patterns associated with this resource
    startup_patterns: List[StartupPattern] = wrapped(path="StartupPattern/StartupPatternInfo", min_length=0, max_length=20)

    # The stop patterns associated with this resource
    shutdown_patterns: List[ShutdownPattern] = wrapped(path="StopPattern/StopPatternInfo", min_length=0, max_length=20)

    # The MMS code of the business entity to which the power generation unit belongs
    participant: str = participant("ParticipantName")

    # A code that uniquely identifies the power generation unit
    code: str = resource_name("ResourceName")

    # How the power generation unit is used in the market
    contract_type: ContractType = attr(name="ContractType")

    # How the power generation unit produces electricity
    resource_type: ResourceType = attr(name="ResourceType")

    # The region in which the power generation unit is located and in which its energy will be traded
    area: AreaCode = attr(name="AreaCode")

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
    balancing_group: Optional[str] = attr(default=None, name="BgCode", min_length=5, max_length=5, pattern=r"^[a-zA-Z0-9]{5}$")

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
    # power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_primary is True.
    primary_response_time: Optional[str] = time("PriResponseTime", True)

    # The primary control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # primary control (such as frequency control) is continuously applied by a power generation unit. It represents the
    # period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_primary is True.
    primary_continuous_time: Optional[str] = time("PriContinuousTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if the contract type is not 
    # ONLY_POWER_SUPPLY_1 and the power source type is not VPP. For other power source types, it must not be set. If the
    # power source type is HYDRO or BATTERY, the value of this field must be less than or equal to the maximum of 
    # "rated output + GF width (outside rated output) - minimum output" or "(pumping/charging - output) - minimum 
    # output." If the power source type is THERMAL or HYDRO, the value of this field must be less than or equal to 
    # "rated output + GF width (outside rated output) - minimum output." If has_primary is "false," the value of this
    # field must be 0.
    primary_available_capacity_kW: Optional[int] = power_supply("PriMaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract types MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    primary_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="PriRemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If primary_remaining_reserve_utilization
    # is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or AVAILABLE_FOR_UP_AND_DOWN, this field must be set.
    # If primary_remaining_reserve_utilization is set to NOT_AVAILABLE, this field must not be set.
    primary_remaining_reserve_capacity_kW: Optional[int] = capacity("PriRemResvMaximumSupplyQuantity", True)

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
    # power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_1 is True.
    secondary_1_response_time: Optional[str] = time("Sec1ResponseTime", True)

    # The secondary 1 control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # secondary 1 control (such as frequency control) is continuously applied by a power generation unit. It represents
    # the period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_1 is True.
    secondary_1_continuous_time: Optional[str] = time("Sec1ContinuousTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if the contract type is not 
    # ONLY_POWER_SUPPLY_1 and the power source type is not VPP. For other power source types, it must not be set. If the
    # power source type is HYDRO or BATTERY, the value of this field must be less than or equal to the maximum of 
    # "rated output - minimum output" or "(pumping/charging - output) - minimum output." If the power source type is
    # THERMAL or HYDRO, the value of this field must be less than or equal to "rated output - minimum output." If
    # has_secondary_1 is "false," the value of this field must be 0.
    secondary_1_available_capacity_kW: Optional[int] = power_supply("Sec1MaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract types MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    secondary_1_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Sec1RemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If
    # secondary_1_remaining_reserve_utilization is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or
    # AVAILABLE_FOR_UP_AND_DOWN, this field must be set. If secondary_1_remaining_reserve_utilization is set to
    # NOT_AVAILABLE, this field must not be set.
    secondary_1_remaining_reserve_capacity_kW: Optional[int] = capacity("Sec1RemResvMaximumSupplyQuantity", True)

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
    # power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_2 is True.
    secondary_2_response_time: Optional[str] = time("Sec2ResponseTime", True)

    # The secondary 2 control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # secondary 2 control (such as frequency control) is continuously applied by a power generation unit. It represents
    # the period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_2 is True.
    secondary_2_continuous_time: Optional[str] = time("Sec2ContinuousTime", True)

    # The secondary 2 control power down time, in the format "HH:MM:SS". Not applicable for power sources with contract
    # type ONLY_POWER_SUPPLY_1. Mandatory only if has_secondary_2 is True.
    secondary_2_downtime: Optional[str] = time("Sec2DownTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if the contract type is not 
    # ONLY_POWER_SUPPLY_1 and the power source type is not VPP. For other power source types, it must not be set. The
    # value of this field must be less than or equal to the "rated output." If has_secondary_2 is "false," the value
    # of this field must be 0.
    secondary_1_available_capacity_kW: Optional[int] = power_supply("Sec2MaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract types MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    secondary_2_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Sec2RemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If
    # secondary_2_remaining_reserve_utilization is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or
    # AVAILABLE_FOR_UP_AND_DOWN, this field must be set. If secondary_2_remaining_reserve_utilization is set to
    # NOT_AVAILABLE, this field must not be set.
    secondary_2_remaining_reserve_capacity_kW: Optional[int] = capacity("Sec2RemResvMaximumSupplyQuantity", True)

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
    # power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_tertiary_1 is True.
    tertiary_1_response_time: Optional[str] = time("Ter1ResponseTime", True)

    # The tertiary 1 control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # tertiary 1 control (such as frequency control) is continuously applied by a power generation unit. It represents
    # the period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_tertiary_1 is True.
    tertiary_1_continuous_time: Optional[str] = time("Ter1ContinuousTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if the contract type is not 
    # ONLY_POWER_SUPPLY_1 and the power source type is not VPP. For other power source types, it must not be set. If the
    # power source type is HYDRO or BATTERY, the value of this field must be less than or equal to "rated output +
    # (pumping/charging - output)." If the power source type is THERMAL or HYDRO, the value of this field must be less
    # than or equal to "rated output." If has_tertiary_1 is "false," the value of this field must be 0.
    tertiary_1_available_capacity_kW: Optional[int] = power_supply("Ter1MaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract types MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    tertiary_1_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Ter1RemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If
    # tertiary_1_remaining_reserve_utilization is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or
    # AVAILABLE_FOR_UP_AND_DOWN, this field must be set. If tertiary_1_remaining_reserve_utilization is set to
    # NOT_AVAILABLE, this field must not be set.
    tertiary_1_remaining_reserve_capacity_kW: Optional[int] = capacity("Ter1RemResvMaximumSupplyQuantity", True)

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
    # power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_tertiary_2 is True.
    tertiary_2_response_time: Optional[str] = time("Ter2ResponseTime", True)

    # The tertiary 2 control power continuous time, in the format "HH:MM:SS". It refers to the duration for which a
    # tertiary 2 control (such as frequency control) is continuously applied by a power generation unit. It represents
    # the period during which the power plant or generating unit can sustain a continuous adjustment to its output to
    # maintain system frequency within acceptable limits. This parameter is essential for ensuring grid stability and
    # reliability by providing continuous support to the power system during frequency disturbances or fluctuations.
    # Not applicable for power sources with contract type ONLY_POWER_SUPPLY_1. Mandatory only if has_tertiary_2 is True.
    tertiary_2_continuous_time: Optional[str] = time("Ter2ContinuousTime", True)

    # The amount of electricity that a power provider can supply. It represents the quantity of electricity that can be
    # reliably supplied by generating facilities or power supply equipment within a specific time frame. The value can
    # be either 0 or within the range of 1000 to 9999999. It is mandatory if the contract type is not 
    # ONLY_POWER_SUPPLY_1 and the power source type is not VPP. For other power source types, it must not be set. If the
    # power source type is HYDRO or BATTERY, the value of this field must be less than or equal to "rated output +
    # (pumping/charging - output)." If the power source type is THERMAL or HYDRO, the value of this field must be less
    # than or equal to "rated output." If has_tertiary_2 is "false," the value of this field must be 0.
    tertiary_2_available_capacity_kW: Optional[int] = power_supply("Ter2MaximumSupplyQuantity", True)

    # How the surplus capacity of a power generation unit can be utilized. For contract types MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    tertiary_2_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Ter2RemResvUtilization")

    # The amount of surplus power that can be supplied for utilization, in kW. If
    # tertiary_2_remaining_reserve_utilization is set to AVAILABLE_FOR_UP_ONLY, AVAILABLE_FOR_DOWN_ONLY, or
    # AVAILABLE_FOR_UP_AND_DOWN, this field must be set. If tertiary_2_remaining_reserve_utilization is set to
    # NOT_AVAILABLE, this field must not be set.
    tertiary_2_remaining_reserve_capacity_kW: Optional[int] = capacity("Ter2RemResvMaximumSupplyQuantity", True)

    # Primary-Secondary 1 command-and-control and monitoring method. Refers to the methodology or system utilized for
    # regulating and overseeing power generation units' operations in response to external commands or signals. This
    # method encompasses the process by which instructions are transmitted to power generation units, and their
    # performance is monitored to ensure compliance with these instructions. If has_secondary_1 is set to True, then
    # it must be set to DEDICATED_LINE. At least one of the following combinations must be set:
    #   primary_secondary_1_control_method
    #   secondary_2_tertiary_control_method
    primary_secondary_1_control_method: Optional[CommandMonitorMethod] = attr(default=None, name="PriSec1CommandOperationMethod")

    # Secondary 2-Tertiary command-and-control and monitoring method. Refers to the methodology or system utilized for
    # regulating and overseeing power generation units' operations in response to external commands or signals. This
    # method encompasses the process by which instructions are transmitted to power generation units, and their
    # performance is monitored to ensure compliance with these instructions.
    secondary_2_tertiary_control_method: Optional[CommandMonitorMethod] = attr(default=None, name="Sec2Ter1Ter2CommandOperationMethod")

    # Method determinining how the baseline is set for a power generation unit. The setting method is available when
    # the contract type is not ONLY_POWER_SUPPLY_1 and at least one of the following is True: has_primary,
    # has_secondary_1, has_secondary_2 or has_tertiary_1. Additionally, it can only be set when the power source type
    # is VPP_GEN, VPP_GEN_AND_DEM or VPP_DEM. It's mandatory in these cases and cannot be set for other power sources.
    baseline_setting_method: Optional[BaseLineSettingMethod] = attr(default=None, name="BaselineSettingMethod")
