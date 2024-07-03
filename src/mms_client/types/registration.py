"""Contains objects for registrations."""

from enum import Enum
from typing import Optional

from pydantic_extra_types.pendulum_dt import Date
from pydantic_xml import attr

from mms_client.types.base import Envelope


class QueryAction(Enum):
    """Represents the type of query being made."""

    NORMAL = "NORMAL"
    LATEST = "LATEST"


class QueryType(Enum):
    """Represents the type of data being queried."""

    TRADE = "TRADE"


class RegistrationSubmit(Envelope):
    """Represents the base fields for a registration request."""


class RegistrationQuery(Envelope):
    """Represents the base fields for a registration query."""

    # The query type being made.
    # NORMAL: Retrieve all records that match the specified conditions.
    # LATEST: Retrieve only the latest record that matches the specified conditions.
    action: QueryAction = attr(default=QueryAction.NORMAL, name="Action")

    # The type of data being queried
    query_type: QueryType = attr(default=QueryType.TRADE, name="DateType")

    # Date of the transaction in the format "YYYY-MM-DD"
    date: Optional[Date] = attr(default=None, name="Date")


class RegistrationApproval(Envelope):
    """Represents the base fields for a registration approval request."""
