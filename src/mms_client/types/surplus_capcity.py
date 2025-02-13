"""Contains objects for surplus capacity information."""

from enum import Enum
from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from pydantic_xml import attr

from mms_client.types.base import Payload
from mms_client.types.enums import AreaCode
from mms_client.types.fields import company_short_name
from mms_client.types.fields import participant
from mms_client.types.fields import power_positive
from mms_client.types.fields import resource_name
from mms_client.types.fields import resource_short_name
from mms_client.types.fields import system_code


class RejectCategory(Enum):
    """Represents the category of the reason for rejecting a surplus capacity request."""

    FUEL_RESTRICTION = "1"
    RIVER_FLOW_RESTRICTION = "2"
    WORK_RELATED = "3"
    OTHER = "9"


class OperationalRejectCategory(Enum):
    """Represents the category of the reason for rejecting an operational request.

    This include voltage adjustment, black start, over-power, peak mode or system security pump request.
    """

    EQUIPMENT_FAILURE = "1"
    NOT_SUPPORTED = "2"
    OTHER = "9"


class SurplusCapacitySubmit(Payload, tag="RemainingReserveData"):
    """Represents the base fields for a surplus capacity response."""

    # The name of the resource for which the surplus capacity is being submitted
    resource_code: str = resource_name("ResourceName")

    # The DR pattern number for which the surplus capacity is being submitted
    pattern_number: int = attr(name="DrPatternNumber", ge=1, le=20)

    # The start block from when the surplus capacity should apply
    start: DateTime = attr(name="StartTime")

    # The end block until when the surplus capacity should apply
    end: DateTime = attr(name="EndTime")

    # The available surplus capacity that can be increased or dispatched when needed, such as in response to grid
    # demand fluctuations. This should not be submitted for standalone generators.
    upward_capacity: Optional[int] = power_positive("RemainingReserveUp", True)

    # In the case where excess surplus capacity is rejected, this field will indicate the category of the reason.
    upward_capacity_rejected: Optional[RejectCategory] = attr(default=None, name="RemainingReserveUpRejectFlag")

    # If the upward dispatch is rejected, this field will indicate a specific reason.
    upward_capacity_rejection_reason: Optional[str] = attr(
        default=None, name="RemainingReserveUpRejectReason", min_length=1, max_length=50
    )

    # The available surplus capacity that can be decreased when needed, such as in response to grid demand fluctuations.
    # This should not be submitted for standalone generators.
    downward_capacity: Optional[int] = power_positive("RemainingReserveDown", True)

    # In the case where excess surplus capacity is rejected, this field will indicate the category of the reason.
    downward_capacity_rejected: Optional[RejectCategory] = attr(default=None, name="RemainingReserveDownRejectFlag")

    # If the downward dispatch is rejected, this field will indicate a specific reason.
    downward_capacity_rejection_reason: Optional[str] = attr(
        default=None, name="RemainingReserveDownRejectReason", min_length=1, max_length=50
    )

    # If voltage adjustment is rejected, this field will indicate the category of the reason.
    voltage_adjustment_rejected: Optional[OperationalRejectCategory] = attr(
        default=None, name="VoltageAdjustmentRejectFlag"
    )

    # If voltage adjustment is rejected, this field will indicate a specific reason.
    voltage_adjustment_rejection_reason: Optional[str] = attr(
        default=None, name="VoltageAdjustmentRejectReason", min_length=1, max_length=50
    )

    # If black start is rejected, this field will indicate the category of the reason.
    black_start_rejected: Optional[OperationalRejectCategory] = attr(default=None, name="BlackStartRejectFlag")

    # If black start is rejected, this field will indicate a specific reason.
    black_start_rejection_reason: Optional[str] = attr(
        default=None, name="BlackStartRejectReason", min_length=1, max_length=50
    )

    # The additional reserve capacity that can be utilized in cases of excessive or "overpower" conditions, such as
    # when demand exceeds usual levels.
    over_power_capacity: Optional[int] = power_positive("OverPowerRemainingReserveUp", True)

    # In the case where over-power capacity is rejected, this field will indicate the category of the reason.
    over_power_rejected: Optional[OperationalRejectCategory] = attr(default=None, name="OverPowerRejectFlag")

    # If over-power capacity is rejected, this field will indicate a specific reason.
    over_power_rejection_reason: Optional[str] = attr(
        default=None, name="OverPowerRejectReason", min_length=1, max_length=50
    )

    # The available surplus capacity that can be increased specifically during peak demand periods
    peak_mode_capacity: Optional[int] = power_positive("PeakModeRemainingReserveUp", True)

    # In the case where peak mode capacity is rejected, this field will indicate the category of the reason.
    peak_mode_rejected: Optional[OperationalRejectCategory] = attr(default=None, name="PeakModeRejectFlag")

    # If peak mode capacity is rejected, this field will indicate a specific reason.
    peak_mode_rejection_reason: Optional[str] = attr(
        default=None, name="PeakModeRejectReason", min_length=1, max_length=50
    )

    # Indicates whether the operation of a pumped-storage hydroelectric pump is restricted or disallowed for system
    # security reasons.
    system_security_pump_rejected: Optional[OperationalRejectCategory] = attr(
        default=None, name="SystemSecurityPumpRejectFlag"
    )

    # If the operation of a pumped-storage hydroelectric pump is restricted or disallowed for system security reasons,
    # this field will indicate a specific reason.
    system_security_pump_rejection_reason: Optional[str] = attr(
        default=None, name="SystemSecurityPumpRejectReason", min_length=1, max_length=50
    )


class SurplusCapacityData(SurplusCapacitySubmit, tag="RemainingReserveData"):
    """Represents the base fields for a surplus capacity response."""

    # The region in which the resource for which surplus capacity is being submitted is located
    area: Optional[AreaCode] = attr(default=None, name="Area")

    # The name of the BSP participant submitting the surplus capacity
    participant: Optional[str] = participant("ParticipantName", True)

    # The abbreviated name of the company submitting the surplus capacity
    company: Optional[str] = company_short_name("CompanyShortName", True)

    # The MMS code of the business entity to which the registration applies
    system_code: Optional[str] = system_code("SystemCode", True)

    # The abbreviated name of the resource being traded
    resource_name: Optional[str] = resource_short_name("ResourceShortName", True)


class SurplusCapacityQuery(Payload, tag="RemainingReserveDataQuery"):
    """Represents the base fields for a surplus capacity query."""

    # The name of the resource for which the surplus capacity is being submitted
    resource_code: Optional[str] = resource_name("ResourceName", True)

    # The DR pattern number for which the surplus capacity is being submitted
    pattern_number: Optional[int] = attr(default=None, name="DrPatternNumber", ge=1, le=20)

    # The start block from when the surplus capacity should apply
    start: DateTime = attr(name="StartTime")

    # The end block until when the surplus capacity should apply
    end: DateTime = attr(name="EndTime")
