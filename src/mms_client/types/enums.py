"""Contains enums common to all MMS types."""

from enum import Enum


class ValidationStatus(Enum):
    """Represents the status of the validation check done on an element."""

    PASSED = "PASSED"  # The validation check for all data within the element has succeeded.
    WARNING = "WARNING"  # There are data within the element that have triggered warnings during the validation check.
    PASSED_PARTIAL = "PASSED_PARTIAL"  # Some data within the element has failed the validation check.
    FAILED = "FAILED"  # The data inside the element failed the validation check.
    NOT_DONE = "NOT_DONE"  # There are data with incomplete validation checks within the element.


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
