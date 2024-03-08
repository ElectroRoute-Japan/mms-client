"""Contains objects for market information."""

from enum import Enum
from typing import Optional

from pendulum import Date
from pydantic import Field

from mms_client.types.base import RequestPayload
from mms_client.types.fields import participant


class MarketType(Enum):
    """Represents the type of market for which the data is being submitted."""

    DAY_AHEAD = "DAM"
    WEEK_AHEAD = "WAM"


class BaseMarketRequest(RequestPayload):
    """Represents the header of a market request."""

    # Date of the transaction in the format "YYYY-MM-DD"
    date: Date = Field(alias="Date")

    # MMS code of the business entity to which the requesting user belongs, and will be used to track the user who made
    # the request. This value will be checked against the certificate used to make the request.
    participant: str = participant("ParticipantName")

    # The user name of the person making the request. This value is used to track the user who made the request, and
    # will be checked against the certificate used to make the request.
    user: str = Field(alias="UserName", min_length=1, max_length=12, pattern=r"^[A-Z0-9]*$")

    # The type of market for which the data is being submitted
    market_type: Optional[MarketType] = Field(default=None, alias="MarketType")


class MarketQuery(BaseMarketRequest):
    """Represents the base fields for a market query."""

    # If the market type is specified as "DAM" (day-ahead market), the number of days should be specified as "1".
    # Otherwise, this field indicates the number of days ahead for which the data is being queried.
    days: int = Field(default=1, alias="NumOfDays", ge=1, le=7)


class MarketSubmit(BaseMarketRequest):
    """Represents the base fields for a market registration request."""

    # If the market type is specified as "DAM" (day-ahead market), the number of days should be specified as "1".
    # Otherwise, this field indicates the number of days ahead for which the data is being submitted.
    days: int = Field(default=1, alias="NumOfDays", ge=1, le=31)


class MarketCancel(BaseMarketRequest):
    """Represents the base fields for a market cancellation request."""

    # If the market type is specified as "DAM" (day-ahead market), the number of days should be specified as "1".
    # Otherwise, this field indicates the number of days ahead for which the data is being cancelled.
    days: int = Field(default=1, alias="NumOfDays", ge=1, le=31)
