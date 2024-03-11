"""Contains objects for MMS offers."""

from decimal import Decimal
from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic_core import PydanticUndefined
from pydantic_extra_types.pendulum_dt import DateTime

from mms_client.types.enums import AreaCode
from mms_client.types.fields import company_short_name
from mms_client.types.fields import dr_patter_number
from mms_client.types.fields import operator_code
from mms_client.types.fields import participant
from mms_client.types.fields import power_positive
from mms_client.types.fields import price
from mms_client.types.fields import resource_name
from mms_client.types.fields import resource_short_name
from mms_client.types.fields import system_code
from mms_client.types.market import MarketType


def offer_id(alias: str, optional: bool = False):
    """Create a field for an offer ID.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the offer ID.
    """
    return Field(
        default=None if optional else PydanticUndefined,
        alias=alias,
        min_length=1,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_-]*$",
    )


class Direction(Enum):
    """Represents the reserve direction of the offer."""

    SELL = "1"  # Increasing the reserves (sell)
    BUY = "2"  # Decreasing the reserves (buy)


class OfferStack(BaseModel):
    """Represents a single price-quantity pair in an offer.

    Notes:
        For the Day-ahead Market, the tertiary 2 sell bidding volume is mandatory.
        For the Week-ahead Market, one of primary, secondary 1, secondary 2, or tertiary 1 sell bidding volumes are
        mandatory.
    """

    # A number used to identify this PQ pair within the offer
    stack_number: int = Field(alias="StackNumber", ge=1, le=20)

    # The minimum quantity that must be provided before the offer can be awarded
    minimum_quantity_kw: int = power_positive("MinimumQuantityInKw")

    # The primary bid quantity in kW
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
    unit_price: Decimal = price("OfferUnitPrice")

    # The ID of the offer to which this stack belongs
    id: Optional[str] = offer_id("OfferId", True)


class OfferData(BaseModel):
    """Describes the data necessary to submit an offer to the MMS.

    Note that this data will also be returned when querying for offers.
    """

    # The separate offers that make up the offer stack
    stack: List[OfferStack] = Field(alias="OfferStack", min_length=1, max_length=20)

    # The identifier for the power resource being traded
    resource: str = resource_name("ResourceName")

    # Date and time of the starting block associated with the offer
    start: DateTime = Field(alias="StartTime")

    # Date and time of the ending block associated with the offer
    end: DateTime = Field(alias="EndTime")

    # The direction of the offer (buy, sell)
    direction: Direction = Field(alias="Direction")

    # The type of market for which the offer is being submitted
    pattern_number: Optional[int] = dr_patter_number("DrPatternNumber", True)

    # The name of the BSP participant submitting the offer
    bsp_participant: Optional[str] = participant("BspParticipantName", True)

    # The abbreviated name of the counterparty
    company_short_name: Optional[str] = company_short_name("CompanyShortName", True)

    # A code identifying the TSO or MO
    operator: Optional[str] = operator_code("OperatorCode", True)

    # The area associated with the offer
    area: Optional[AreaCode] = Field(default=None, alias="Area")

    # The abbreviated name of the resource being traded
    resource_short_name: Optional[str] = resource_short_name("ResourceShortName", True)

    # The grid code of the resource being traded
    system_code: Optional[str] = system_code("SystemCode", True)

    # The date and time when the offer was submitted
    submission_time: Optional[DateTime] = Field(default=None, alias="SubmissionTime")


class OfferCancel(BaseModel):
    """Describes the data necessary to cancel an offer in the MMS."""

    # The identifier for the power resource this offer is trading on
    resource: str = resource_name("ResourceName")

    # The date and time of the starting block associated with the offer
    start: DateTime = Field(alias="StartTime")

    # The date and time of the ending block associated with the offer. You can cancel multiple blocks by specifying the
    # end date and time for any block within the period from the trading day to the specified number of days.
    end: DateTime = Field(alias="EndTime")

    # The type of market for the offer was submitted on
    market_type: MarketType = Field(alias="MarketType")


class OfferQuery(BaseModel):
    """Describes the data necessary to query for offers in the MMS."""

    # The type of market for the offer was submitted on
    market_type: MarketType = Field(alias="MarketType")

    # The identifier for the power resource being requested. If this isn't provided, then all offers for the specified
    # region will be returned
    resource: Optional[str] = resource_name("ResourceName", True)

    # The area associated with the offer. For TSOs and MOs, this field is mandatory
    area: Optional[AreaCode] = Field(default=None, alias="Area")
