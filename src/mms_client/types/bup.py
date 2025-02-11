"""Contains objects for BUPs."""

from decimal import Decimal
from enum import Enum
from typing import Annotated
from typing import List
from typing import Optional

from pydantic_core import PydanticUndefined
from pydantic_extra_types.pendulum_dt import DateTime
from pydantic_xml import attr
from pydantic_xml import element
from pydantic_xml import wrapped

from mms_client.types.base import Payload
from mms_client.types.enums import AreaCode
from mms_client.types.fields import capacity
from mms_client.types.fields import company_short_name
from mms_client.types.fields import participant
from mms_client.types.fields import power_positive
from mms_client.types.fields import price
from mms_client.types.fields import resource_name
from mms_client.types.fields import resource_short_name
from mms_client.types.fields import system_code


def abc_price(alias: str, optional: bool = False):
    """Create a field for an abc price.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the abc price.
    """
    return attr(
        default=None if optional else PydanticUndefined, name=alias, gt=-100000.0, lt=100000.0, decimal_places=1
    )


class Status(Enum):
    """Enum representing the possible statuses of a pattern."""

    INACTIVE = "0"
    ACTIVE = "1"


class StartupCostBand(Payload, tag="BandStartup"):
    """Represents a band of a startup cost."""

    # The band number which must be unique within the startup cost and will identify this band in sequence.
    number: int = attr(name="CaseNo", ge=1, le=10)

    # The time at which the startup cost is applied. This value must be greater than or equal to 0.
    stop_time_hours: int = attr(name="StopTime", ge=0, lt=1000)

    # The V3 unit price charged for this band.
    v3_unit_price: int = attr(name="V3", ge=0, lt=100000000)

    # The remarks associated with this band.
    remarks: Optional[str] = attr(default=None, name="Remark", min_length=1, max_length=30)


class AbcBand(Payload, tag="BandAbc"):
    """Represents a band of an ABC, whatever that is."""

    # The band number which must be unique within the ABC and will identify this band in sequence.
    number: int = attr(name="Band", ge=1, le=5)

    # The capacity from which the band is allowed to operate.
    from_capacity: int = power_positive("FromCap")

    # The a term of the band.
    a: Decimal = abc_price("a")

    # The b term of the band.
    b: Decimal = abc_price("b")

    # The c term of the band.
    c: Decimal = abc_price("c")


class BupBand(Payload):
    """Represents a band of a BUP."""

    # The band number which must be unique within the BUP and will identify this band in sequence.
    number: int = attr(name="Band", ge=1, le=20)

    # The capacity from which the band is allowed to operate. If the resource_type on the associated resource is set to
    # THERMAL or HYDRO then the value of this field must be greater than or equal to 0. Otherwise, the value of this
    # field is unrestricted.
    from_capacity: int = capacity("FromCap", -10000000)

    # The V1 unit price charged for this band.
    v1_unit_price: Decimal = price("V1", 10000.00)

    # The V2 unit price charged for this band. This value is only valid when the contract_type on the associated
    # resource is set to anything other than ONLY_POWER_SUPPLY_1.
    v2_unit_price: Annotated[Decimal, price("V2", 10000.00, True)]


class Bup(Payload):
    """Represents a balancing unit profile."""

    # The V4 unit price charged for this pattern. This value is only valid when the contract_type on the associated
    # resource is set to anything other than ONLY_POWER_SUPPLY_1.
    v4_unit_price: Annotated[Decimal, price("V4", 10000.00, True)]

    # The bands associated with this BUP.
    bands: List[BupBand] = element(name="BandBup", min_length=1, max_length=20)


class Pattern(Payload):
    """Represents a pattern associated with a BUP."""

    # A number identifying this pattern in the overall sequence of patterns
    number: int = attr(name="PatternNo", ge=1, le=10)

    # The status of the pattern
    status: Status = attr(name="PatternStatus")

    # Any comments associated with the pattern
    remarks: Optional[str] = attr(default=None, name="PatternRemark", min_length=1, max_length=50)

    # The balancing unit profile associated with this pattern
    balancing_unit_profile: Optional[Bup] = element(defualt=None, name="Bup")

    # The quadratic pricing bands associated with this pattern
    abc: Annotated[Optional[List[AbcBand]], wrapped(default=None, path="Abc", min_length=1, max_length=5)]

    # The startup cost bands associated with this pattern
    startup_costs: Annotated[
        Optional[List[StartupCostBand]], wrapped(default=None, path="StartupCost", min_length=1, max_length=10)
    ]


class BupSubmit(Payload):
    """Represents the data included with a BUP."""

    # The resource with which the BUP is associated
    resource_code: str = resource_name("ResourceName")

    # The start date and time for the validity period of the BUP
    start: DateTime = attr(name="StartTime")

    # The end date and time for the validity period of the BUP
    end: DateTime = attr(name="EndTime")

    # The patterns associated with this BUP
    patterns: List[Pattern] = element(name="PatternData", max_length=10)

    # The name of the BSP participant submitting the BUP. This will only be populated when the object is returned.
    participant_name: Optional[str] = participant("BspParticipantName", True)

    # The name of the company submitting the BUP. This will only be populated when the object is returned.
    company: Optional[str] = company_short_name("CompanyShortName", True)

    # The area associated with the BUP. This will only be populated when the object is returned.
    area: Optional[AreaCode] = attr(default=None, name="Area")

    # The name of the resource being traded. This will only be populated when the object is returned.
    resource_name: Optional[str] = resource_short_name("ResourceShortName", True)

    # The MMS code of the business entity to which the registration applies. This will only be populated when the
    # object is returned.
    system_code: Optional[str] = system_code("SystemCode", True)


class BupQuery(BupSubmit):
    """Represents the data included with a BUP query."""

    # Whether or not the BUP is the default
    is_default: Optional[bool] = attr(default=None, name="StandingFlag")

    # The resource with which the BUP is associated
    resource_code: str = resource_name("ResourceName")

    # The start date and time for the validity period of the BUP
    start: Annotated[DateTime, attr(default=None, name="StartTime")]

    # The end date and time for the validity period of the BUP
    end: Annotated[DateTime, attr(default=None, name="EndTime")]
