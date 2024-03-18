"""Contains the definitions for various fields used in the MMS API."""

from pydantic_core import PydanticUndefined
from pydantic_xml import attr

# Describes the regular expression required by the MMS API for Japanese text
JAPANESE_TEXT = r"^[\u3000-\u30FF\uFF00-\uFF60\uFFA0-\uFFEF\u4E00-\u9FEA]*$"


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


def price(alias: str, optional: bool = False):
    """Create a field for a price value.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the price value.
    """
    return attr(default=None if optional else PydanticUndefined, name=alias, ge=0.00, le=10000.00, decimal_places=2)


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
