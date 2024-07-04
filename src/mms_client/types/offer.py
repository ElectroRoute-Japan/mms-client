"""Contains objects for MMS offers."""

from decimal import Decimal
from typing import List
from typing import Optional

from pendulum import Timezone
from pydantic import field_serializer
from pydantic import field_validator
from pydantic_extra_types.pendulum_dt import DateTime
from pydantic_xml import attr
from pydantic_xml import element

from mms_client.types.base import Payload
from mms_client.types.enums import AreaCode
from mms_client.types.enums import Direction
from mms_client.types.fields import company_short_name
from mms_client.types.fields import dr_patter_number
from mms_client.types.fields import offer_id
from mms_client.types.fields import operator_code
from mms_client.types.fields import participant
from mms_client.types.fields import power_positive
from mms_client.types.fields import price
from mms_client.types.fields import resource_name
from mms_client.types.fields import resource_short_name
from mms_client.types.fields import system_code
from mms_client.types.market import MarketType


class OfferStack(Payload):
    """Represents a single price-quantity pair in an offer request.

    Notes:
        For the Day-ahead Market, the tertiary 2 sell bidding volume is mandatory.
        For the Week-ahead Market, one of primary, secondary 1, secondary 2, or tertiary 1 sell bidding volumes are
        mandatory.
    """

    # A number used to identify this PQ pair within the offer. Ensure that there are no duplicates of the combination
    # of the same resource, pattern number, start date and time, and bid management number in the submitted data. In
    # case of multiple bids in the same time slot and for the same resource, each bid must have a unique number. Enter
    # '1' for a single bid.
    number: int = attr(name="StackNumber", ge=1, le=20)

    # The minimum quantity that must be provided before the offer can be awarded. For resources with dedicated line
    # control or monitoring methods, must be 5000kW or higher. For resources with simple command (online) control
    # or monitoring methods, must be 1000kW or higher.
    minimum_quantity_kw: int = power_positive("MinimumQuantityInKw")

    # The primary bid quantity in kW. Must be equal to or greater than minimum_quantity_kw. For non-VPP resources, the
    # total bid volume of all records with the same resource and start date and time must be below the maximum supply
    # capacity for the corresponding product category of the power source. However, in the case of tertiary adjustment
    # power 2, it must be the value obtained by subtracting the total agreed capacity of effective tertiary adjustment
    # power 1. For VPP power sources, the total bid volume of all records with the same power source code and start
    # date and time must be below the maximum supply capacity registered for the corresponding product category in the
    # pattern number.
    primary_qty_kw: Optional[int] = power_positive("PrimaryOfferQuantityInKw", True)

    # The first secondary bid quantity in kW
    secondary_1_qty_kw: Optional[int] = power_positive("Secondary1OfferQuantityInKw", True)

    # The second secondary bid quantity in kW
    secondary_2_qty_kw: Optional[int] = power_positive("Secondary2OfferQuantityInKw", True)

    # The first tertiary bid quantity in kW
    tertiary_1_qty_kw: Optional[int] = power_positive("Tertiary1OfferQuantityInKw", True)

    # The second tertiary bid quantity in kW.
    tertiary_2_qty_kw: Optional[int] = power_positive("Tertiary2OfferQuantityInKw", True)

    # The unit price of the power, in JPY/kW/segment
    unit_price: Decimal = price("OfferUnitPrice", 10000.00)

    # The ID of the offer to which this stack belongs
    id: Optional[str] = offer_id("OfferId", True)


class OfferData(Payload):
    """Describes the data common to both offer requests and responses."""

    # The separate offers that make up the offer stack
    stack: List[OfferStack] = element(tag="OfferStack", min_length=1, max_length=20)

    # The identifier for the power resource being traded
    resource: str = resource_name("ResourceName")

    # Date and time of the starting block associated with the offer
    start: DateTime = attr(name="StartTime")

    # Date and time of the ending block associated with the offer
    end: DateTime = attr(name="EndTime")

    # The direction of the offer (buy, sell)
    direction: Direction = attr(name="Direction")

    # The type of market for which the offer is being submitted. Must be a valid pattern number for the submission date
    # Required for VPP resources. Ensure there are no duplicate pattern numbers for the same resource and start time.
    pattern_number: Optional[int] = dr_patter_number("DrPatternNumber", True)

    # The name of the BSP participant submitting the offer
    bsp_participant: Optional[str] = participant("BspParticipantName", True)

    # The abbreviated name of the counterparty
    company_short_name: Optional[str] = company_short_name("CompanyShortName", True)

    # A code identifying the TSO or MO
    operator: Optional[str] = operator_code("OperatorCode", True)

    # The area associated with the offer
    area: Optional[AreaCode] = attr(default=None, name="Area")

    # The abbreviated name of the resource being traded
    resource_short_name: Optional[str] = resource_short_name("ResourceShortName", True)

    # The grid code of the resource being traded
    system_code: Optional[str] = system_code("SystemCode", True)

    # The date and time when the offer was submitted
    submission_time: Optional[DateTime] = attr(default=None, name="SubmissionTime")

    @field_serializer("start", "end", "submission_time")
    def encode_datetime(self, value: DateTime) -> str:
        """Encode the datetime to an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=None).isoformat() if value else ""

    @field_validator("start", "end", "submission_time")
    def decode_datetime(cls, value: DateTime) -> DateTime:  # pylint: disable=no-self-argument
        """Decode the datetime from an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=Timezone("Asia/Tokyo"))


class OfferCancel(Payload):
    """Describes the data necessary to cancel an offer in the MMS."""

    # The identifier for the power resource this offer is trading on
    resource: str = resource_name("ResourceName")

    # The date and time of the starting block associated with the offer
    start: DateTime = attr(name="StartTime")

    # The date and time of the ending block associated with the offer. You can cancel multiple blocks by specifying the
    # end date and time for any block within the period from the trading day to the specified number of days.
    end: DateTime = attr(name="EndTime")

    # The type of market for the offer was submitted on
    market_type: MarketType = attr(name="MarketType")

    @field_serializer("start", "end")
    def encode_datetime(self, value: DateTime) -> str:
        """Encode the datetime to an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=None).isoformat()

    @field_validator("start", "end")
    def decode_datetime(cls, value: DateTime) -> DateTime:  # pylint: disable=no-self-argument
        """Decode the datetime from an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=Timezone("Asia/Tokyo"))


class OfferQuery(Payload):
    """Describes the data necessary to query for offers in the MMS."""

    # The type of market for the offer was submitted on
    market_type: MarketType = attr(name="MarketType")

    # The identifier for the power resource being requested. If this isn't provided, then all offers for the specified
    # region will be returned
    resource: Optional[str] = resource_name("ResourceName", True)

    # The area associated with the offer. For TSOs and MOs, this field is mandatory
    area: Optional[AreaCode] = attr(default=None, name="Area")
