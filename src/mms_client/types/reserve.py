"""Contains objects for MMS reserve requirements."""

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
from mms_client.types.fields import power_positive
from mms_client.types.market import MarketType


class Requirement(Payload):
    """Represents a reserve requirement."""

    # The start block of the requirement
    start: DateTime = attr(name="StartTime")

    # The end block of the requirement
    end: DateTime = attr(name="EndTime")

    # The direction of the requirement
    direction: Direction = attr(name="Direction")

    # The primary reserve quantity in kW
    primary_qty_kw: Optional[int] = power_positive("PrimaryReserveQuantityInKw", True)

    # The first secondary reserve quantity in kW
    secondary_1_qty_kw: Optional[int] = power_positive("Secondary1ReserveQuantityInKw", True)

    # The second secondary reserve quantity in kW
    secondary_2_qty_kw: Optional[int] = power_positive("Secondary2ReserveQuantityInKw", True)

    # The first tertiary reserve quantity in kW
    tertiary_1_qty_kw: Optional[int] = power_positive("Tertiary1ReserveQuantityInKw", True)

    # The second tertiary reserve quantity in kW
    tertiary_2_qty_kw: Optional[int] = power_positive("Tertiary2ReserveQuantityInKw", True)

    # The minimum reserve of compound primary and secondary 1 in kW
    primary_secondary_1_qty_kw: Optional[int] = power_positive("CompoundPriSec1ReserveQuantityInKw", True)

    # The minimum reserve of compound primary and secondary 2 in kW
    primary_secondary_2_qty_kw: Optional[int] = power_positive("CompoundPriSec2ReserveQuantityInKw", True)

    # The minimum reserve of compound primary and tertiary 1 in kW
    primary_tertiary_1_qty_kw: Optional[int] = power_positive("CompoundPriTer1ReserveQuantityInKw", True)

    @field_serializer("start", "end")
    def encode_datetime(self, value: DateTime) -> str:
        """Encode the datetime to an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=None).isoformat()

    @field_validator("start", "end")
    def decode_datetime(cls, value: DateTime) -> DateTime:  # pylint: disable=no-self-argument
        """Decode the datetime from an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=Timezone("Asia/Tokyo"))


class ReserveRequirement(Payload):
    """Represents a set of reserve requirements."""

    # The area for which the reserve requirement applies
    area: AreaCode = attr(name="Area")

    # The requirements associated with the area
    requirements: List[Requirement] = element(tag="Requirement", min_length=1)


class ReserveRequirementQuery(Payload):
    """Represents a request to query reserve requirements."""

    # The market type for which to query reserve requirements
    market_type: MarketType = attr(name="MarketType")

    # The area for which to query reserve requirements
    area: Optional[AreaCode] = attr(default=None, name="Area")
