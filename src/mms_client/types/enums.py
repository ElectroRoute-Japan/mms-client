"""Contains enums common to all MMS types."""

from enum import Enum
from enum import IntEnum


class AreaCode(Enum):
    """Represents the area code of the market."""

    HOKKAIDO = "01"
    TOHOKU = "02"
    TOKYO = "03"
    CHUBU = "04"
    HOKURIKU = "05"
    KANSAI = "06"
    CHUGOKU = "07"
    SHIKOKU = "08"
    KYUSHU = "09"
    OKINAWA = "10"


class Direction(Enum):
    """Represents the reserve direction of the offer."""

    SELL = "1"  # Increasing the reserves (sell)
    # Note: Support for the BUY direction was removed from the MMS API
    # BUY = "2"  # Decreasing the reserves (buy)


class ContractResult(Enum):
    """Represents the result of a contract."""

    FULL = "1"
    PARTIAL = "2"


class Frequency(IntEnum):
    """Represents the frequency of power sources."""

    EAST = 50
    WEST = 60


class ResourceType(Enum):
    """How the power generation unit produces electricity."""

    THERMAL = "01"
    HYDRO = "02"
    PUMP = "03"
    BATTERY = "04"
    VPP_GEN = "05"
    VPP_GEN_AND_DEM = "06"
    VPP_DEM = "07"


class RemainingReserveAvailability(Enum):
    """Describes the availability of remaining reserves for a power generation unit."""

    NOT_AVAILABLE = "0"
    AVAILABLE_FOR_UP_ONLY = "1"
    AVAILABLE_FOR_DOWN_ONLY = "2"
    AVAILABLE_FOR_UP_AND_DOWN = "3"


class ContractType(Enum):
    """Describes the type of contract for a power generation unit."""

    MARKET = "1"
    MARKET_AND_POWER_SUPPLY_2 = "2"
    POWER_SUPPLY_2 = "3"
    ONLY_POWER_SUPPLY_1 = "4"
    MARKET_AND_REMAINING_RESERVE_UTILIZATION = "5"
    REMAINING_RESERVE_UTILIZATION = "6"


class CommandMonitorMethod(Enum):
    """Describes how the power generation unit is monitored and commanded."""

    DEDICATED_LINE = "1"
    SIMPLE_COMMAND = "2"
    OFFLINE = "3"


class BaseLineSettingMethod(Enum):
    """Describe how the baseline is set for a power generation unit."""

    PREDICTION_BASE = "1"
    MEASUREMENT_BASE = "2"


class SignalType(Enum):
    """Describes the type of signal used to monitor and command a power generation unit."""

    ACTUAL_OUTPUT_ORDER = "1"
    DIFFERENTIAL_OUTPUT_ORDER = "2"


class BooleanFlag(Enum):
    """Represents a Boolean value as an enumeration.

    There are many places throughout the MMS documenation where Boolean values are treated as enums for reasons that are
    not clear. This is a common pattern and this class is provided to make it easier to handle these cases without
    having many different enum classes
    """

    YES = "1"
    NO = "0"
