"""Contains objects for OMI information."""

from pydantic_extra_types.pendulum_dt import Date
from pydantic_xml import attr

from mms_client.types.base import Envelope
from mms_client.types.fields import participant


class MarketSubmit(Envelope):
    """Represents the base fields for a market registration request."""

    # Date of the transaction in the format "YYYY-MM-DD"
    date: Date = attr(name="Date")

    # MMS code of the business entity to which the requesting user belongs, and will be used to track the user who made
    # the request. This value will be checked against the certificate used to make the request.
    participant: str = participant("ParticipantName")

    # The user name of the person making the request. This value is used to track the user who made the request, and
    # will be checked against the certificate used to make the request.
    user: str = attr(name="UserName", min_length=1, max_length=12, pattern=r"^[A-Z0-9]*$")


class MarketQuery(MarketSubmit):
    """Represents the base fields for a market query."""
