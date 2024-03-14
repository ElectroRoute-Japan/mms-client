"""Contains enums common to all MMS types."""

from enum import Enum


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
