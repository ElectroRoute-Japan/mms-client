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


class Frequency(IntEnum):
    """Represents the frequency of power sources."""

    EAST = 50
    WEST = 60
