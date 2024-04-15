"""Contains the definitions for various fields used in the MMS API."""

from pydantic_core import PydanticUndefined
from pydantic_xml import attr

# Describes the regular expression required by the MMS API for Japanese text
JAPANESE_TEXT = r"[\u3000-\u30FF\uFF00-\uFF60\uFFA0-\uFFEF\u4E00-\u9FEA]*"

# Describes the regular expression required by the MMS API for ASCII text
ASCII_TEXT = r"[a-zA-Z0-9 ~!@#$*()_+}{:?>`='/.,%;\^\|\-\]\[\\&lt;&amp;&quot;]*"

# Describes the regular expression required by the MMS API for Japanese or ASCII text
JAPANESE_ASCII_TEXT = f"{JAPANESE_TEXT}|{ASCII_TEXT}"


def participant(alias: str, optional: bool = False):
    """Create a field for a participant ID.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the participant ID.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        min_length=4,
        max_length=4,
        pattern=r"^[A-Z]([0-9]{2}[1-9]|[0-9][1-9][0-9]|[1-9][0-9]{2})$",
    )


def operator_code(alias: str, optional: bool = False):
    """Create a field for an operator code.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the operator code.
    """
    return attr(
        default=None if optional else PydanticUndefined, name=alias, min_length=4, max_length=4, pattern=r"^[A-Z0-9]*$"
    )


def transaction_id(alias: str, optional: bool = False):
    """Create a field for a transaction ID.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the transaction ID.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        min_length=8,
        max_length=10,
        pattern=r"^[a-zA-Z0-9]{8,10}$",
    )


def offer_id(alias: str, optional: bool = False):
    """Create a field for an offer ID.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the offer ID.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        min_length=1,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_-]*$",
    )


def capacity(alias: str, minimum: int, optional: bool = False):
    """Create a field for a capacity value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    minimum (int):      The minimum value for the capacity field.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the capacity value.
    """
    return attr(default=None if optional else PydanticUndefined, name=alias, ge=minimum, le=10000000)


def power_positive(alias: str, optional: bool = False):
    """Create a field for a positive power value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the power value.
    """
    return attr(default=None if optional else PydanticUndefined, name=alias, gt=0, le=10000000)


def price(alias: str, limit: float, optional: bool = False):
    """Create a field for a price value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    limit (int):        The maximum value for the price field.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the price value.
    """
    return attr(default=None if optional else PydanticUndefined, name=alias, ge=0.00, le=limit, decimal_places=2)


def percentage(alias: str, optional: bool = False):
    """Create a field for a percentage value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the percentage value.
    """
    return attr(default=None if optional else PydanticUndefined, name=alias, ge=0.0, le=100.0, decimal_places=1)


def dr_patter_number(alias: str, optional: bool = False):
    """Create a field for a DR pattern number.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the DR pattern number.
    """
    return attr(default=None if optional else PydanticUndefined, name=alias, ge=1, le=20)


def dr_pattern_name(alias: str, optional: bool = False):
    """Create a field for a DR pattern name.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the DR pattern name.
    """
    return attr(
        default=None if optional else PydanticUndefined, name=alias, min_length=1, max_length=20, pattern=JAPANESE_TEXT
    )


def pattern_name(alias: str, optional: bool = False):
    """Create a field for a pattern name.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the pattern name.
    """
    return attr(
        default=None if optional else PydanticUndefined, name=alias, min_length=1, max_length=20, pattern=JAPANESE_TEXT
    )


def company_short_name(alias: str, optional: bool = False):
    """Create a field for a company short name.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the company short name.
    """
    return attr(
        default=None if optional else PydanticUndefined, name=alias, min_length=1, max_length=10, pattern=JAPANESE_TEXT
    )


def address(alias: str, optional: bool = False):
    """Create a field for an address.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the address.
    """
    return attr(
        default=None if optional else PydanticUndefined, name=alias, min_length=1, max_length=50, pattern=JAPANESE_TEXT
    )


def phone(alias: str, first_part: bool, optional: bool = False):
    """Create a field for a phone number.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    first_part (bool):  If True, the field will be the first part of the phone number. If False, the field will be the
                        second part of the phone number.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the phone number.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        min_length=1,
        max_length=5 if first_part else 4,
        pattern=r"^[0-9]*$",
    )


def resource_name(alias: str, optional: bool = False):
    """Create a field for a resource name.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the resource name.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        min_length=1,
        max_length=10,
        pattern=r"^[A-Z0-9_\-]*$",
    )


def resource_short_name(alias: str, optional: bool = False):
    """Create a field for a resource short name.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the resource short name.
    """
    return attr(
        default=None if optional else PydanticUndefined, name=alias, min_length=1, max_length=10, pattern=JAPANESE_TEXT
    )


def contract_id(alias: str, optional: bool = False):
    """Create a field for a contract ID.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the contract ID.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        min_length=19,
        max_length=19,
        pattern=r"^[a-zA-Z0-9]**$",
    )


def jbms_id(alias: str, optional: bool = False):
    """Create a field for a JBMS ID.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the JBMS ID.
    """
    return attr(default=None if optional else PydanticUndefined, name=alias, ge=1, lt=1000000000000000000)


def system_code(alias: str, optional: bool = False):
    """Create a field for a system code.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the system code.
    """
    return attr(
        default=None if optional else PydanticUndefined, name=alias, min_length=5, max_length=5, pattern=r"^[A-Z0-9]*$"
    )


def minute(alias: str, optional: bool = False):
    """Create a field for a minute value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the minute value.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        ge=0,
        le=99,
    )


def hour(alias: str, optional: bool = False):
    """Create a field for an hour value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the hour value.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        ge=0.0,
        lt=100.0,
        decimal_places=1,
    )
