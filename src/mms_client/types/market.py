"""Contains objects for market information."""

from enum import Enum
from typing import Optional

from pydantic_extra_types.pendulum_dt import Date
from pydantic_xml import attr, element
from pydantic_xml import BaseXmlModel

from mms_client.types.base import Envelope
from mms_client.types.fields import participant


class MarketType(Enum):
    """Represents the type of market for which the data is being submitted."""

    DAY_AHEAD = "DAM"
    WEEK_AHEAD = "WAM"


class BaseMarketRequest(Envelope):
    """Represents the header of a market request."""

    # Date of the transaction in the format "YYYY-MM-DD"
    date: Date = attr(name="Date")

    # MMS code of the business entity to which the requesting user belongs, and will be used to track the user who made
    # the request. This value will be checked against the certificate used to make the request.
    participant: str = participant("ParticipantName")

    # The user name of the person making the request. This value is used to track the user who made the request, and
    # will be checked against the certificate used to make the request.
    user: str = attr(name="UserName", min_length=1, max_length=12, pattern=r"^[A-Z0-9]*$")


class Defaults(BaseXmlModel):
    """Represents the default settings to apply when submitting a market request."""

    # Whether or not the submission represents the default
    is_default: bool = attr(name="StandingFlag")


class MarketQuery(BaseMarketRequest):
    """Represents the base fields for a market query."""

    # If the market type is specified as "DAM" (day-ahead market), the number of days should be specified as "1".
    # Otherwise, this field indicates the number of days ahead for which the data is being queried.
    days: int = attr(default=1, name="NumOfDays", ge=1, le=7)


class MarketSubmit(BaseMarketRequest):
    """Represents the base fields for a market registration request."""

    # The type of market for which the data is being submitted
    market_type: Optional[MarketType] = attr(default=None, name="MarketType")

    # If the market type is specified as "DAM" (day-ahead market), the number of days should be specified as "1".
    # Otherwise, this field indicates the number of days ahead for which the data is being submitted.
    days: int = attr(default=1, name="NumOfDays", ge=1, le=31)

    # Default values to include with the submission. The request will be rejected if this is included in a request
    # where it is not allowed.
    defaults: Optional[Defaults] = element(default=None, name="StandingData")


class MarketCancel(BaseMarketRequest):
    """Represents the base fields for a market cancellation request."""

    # The type of market for which the data is being submitted
    market_type: MarketType = attr(name="MarketType")

    # If the market type is specified as "DAM" (day-ahead market), the number of days should be specified as "1".
    # Otherwise, this field indicates the number of days ahead for which the data is being cancelled.
    days: int = attr(default=1, name="NumOfDays", ge=1, le=31)
