"""Contains objects for MMS award results."""

from decimal import Decimal
from enum import Enum
from typing import List
from typing import Optional

from pendulum import Timezone
from pydantic import field_serializer
from pydantic import field_validator
from pydantic_core import PydanticUndefined
from pydantic_extra_types.pendulum_dt import DateTime
from pydantic_xml import attr
from pydantic_xml import element
from pydantic_xml import wrapped

from mms_client.types.base import Payload
from mms_client.types.enums import AreaCode
from mms_client.types.enums import BooleanFlag
from mms_client.types.enums import CommandMonitorMethod
from mms_client.types.enums import ContractResult
from mms_client.types.enums import Direction
from mms_client.types.enums import ResourceType
from mms_client.types.fields import company_short_name
from mms_client.types.fields import contract_id
from mms_client.types.fields import dr_patter_number
from mms_client.types.fields import dr_pattern_name
from mms_client.types.fields import jbms_id
from mms_client.types.fields import offer_id
from mms_client.types.fields import operator_code
from mms_client.types.fields import participant
from mms_client.types.fields import power_positive
from mms_client.types.fields import price
from mms_client.types.fields import resource_name
from mms_client.types.fields import resource_short_name
from mms_client.types.fields import system_code
from mms_client.types.market import MarketType


def baseload_file_name(alias: str, optional: bool = False):
    """Create a field for a baseload file name.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the baseload file name.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        min_length=31,
        max_length=40,
        pattern=r"^W9_[0-9]{4}_[0-9]{8}_[0-9]{2}_[A-Z0-9]{5}_[A-Z0-9_\-]{1,10}\.xml$",
    )


class SubRequirement(Enum):
    """Commodity combination categories."""

    PRIMARY = "PRI"
    SECONDARY_1 = "SEC1"
    SECONDARY_2 = "SEC2"
    TERTIARY_1 = "TER1"
    PRIMARY_SECONDARY_1 = "PRI-SEC1"
    PRIMARY_SECONDARY_2 = "PRI-SEC2"
    PRIMARY_TERTIARY_1 = "PRI-TER1"
    SECONDARY = "SEC1-SEC2"
    SECONDARY_1_TERTIARY_1 = "SEC1-TER1"
    SECONDARY_2_TERTIARY_1 = "SEC2-TER1"
    PRIAMRY_SECONDARY = "PRI-SEC1-SEC2"
    PRIMARY_SECONDARY_1_TERTIARY_1 = "PRI-SEC1-TER1"
    PRIMARY_SECONDARY_2_TERTIARY_1 = "PRI-SEC2-TER1"
    SECONDARY_TERTIARY_1 = "SEC1-SEC2-TER1"
    PRIMARY_SECONDARY_TERTIARY_1 = "PRI-SEC1-SEC2-TER1"


class ContractSource(Enum):
    """Describes the source of the contract."""

    MA = "1"
    SWITCHING = "2"


class AwardQuery(Payload, tag="AwardResultsQuery"):
    """Query object for bid awards."""

    # The market for which results should be retrieved
    market_type: MarketType = attr(name="MarketType")

    # The area for which results should be retrieved. If this isn't provided, then all results will be retrieved
    area: Optional[AreaCode] = attr(default=None, name="Area")

    # The associated area. If the API user is a BSP, this field cannot be set
    linked_area: Optional[AreaCode] = attr(default=None, name="LinkedArea")

    # The name of the resource for which results should be retrieved. If this isn't provided, then all results will be
    # retrieved for all resources
    resource: Optional[str] = resource_name("ResourceName", True)

    # The start date and time for which results should be retrieved. Should conform with the start of a block
    start: DateTime = attr(name="StartTime")

    # The end date and time for which results should be retrieved. Should conform with the end of a block. You can
    # specify the end date and time of any block within the period from the transaction date to the number of days to
    # get multiple blocks.
    end: DateTime = attr(name="EndTime")

    # Whether we are before gate close or after gate close. If this isn't provided, then all results will be retrieved
    # regardless of gate closure.
    gate_closed: Optional[BooleanFlag] = attr(default=None, name="AfterGC")

    @field_serializer("start", "end")
    def encode_datetime(self, value: DateTime) -> str:
        """Encode the datetime to an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=None).isoformat()

    @field_validator("start", "end")
    def decode_datetime(cls, value: DateTime) -> DateTime:  # pylint: disable=no-self-argument
        """Decode the datetime from an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=Timezone("Asia/Tokyo"))


class Award(Payload):
    """Represents the details of a bid award."""

    # Unique identifier assigned to the contract
    contract_id: str = contract_id("ContractId")

    # Unique identifier assigned to the contract by the JBMS
    jbms_id: int = jbms_id("JbmsId")

    # The area of the power generation unit generating the electricity
    area: AreaCode = attr(name="Area")

    # The associated area. If the API user is a BSP, it is not set.
    linked_area: Optional[AreaCode] = attr(default=None, name="LinkedArea")

    # A code identifying the power generation unit for which this bid was awarded
    resource: str = resource_name("ResourceName")

    # An abbreviated name for the power generation unit for which this bid was awarded
    resource_short_name: str = resource_short_name("ResourceShortName")

    # The grid code of the resource being traded
    system_code: str = system_code("SystemCode")

    # How the power generation unit produces electricity
    resource_type: ResourceType = attr(name="ResourceType")

    # The type of market for which the offer is being submitted. Must be a valid pattern number for the submission date
    # Required for VPP resources. Ensure there are no duplicate pattern numbers for the same resource and start time.
    pattern_number: Optional[int] = dr_patter_number("DrPatternNumber", True)

    # The name of the list pattern with which this award is associated
    pattern_name: Optional[str] = dr_pattern_name("DrPatternName", True)

    # The participant ID of the BSP associated with this bid award
    bsp_participant: str = participant("BspParticipantName")

    # The abbreviated name of the counterparty
    company_short_name: str = company_short_name("CompanyShortName")

    # A code identifying the TSO or MO
    operator: str = operator_code("OperatorCode")

    # Primary-Secondary 1 command-and-control and monitoring method. Refers to the methodology or system utilized for
    # regulating and overseeing power generation units' operations in response to external commands or signals. This
    # method encompasses the process by which instructions are transmitted to power generation units, and their
    # performance is monitored to ensure compliance with these instructions. If has_secondary_1 is set to True, then
    # it must be set to DEDICATED_LINE. At least one of the following combinations must be set:
    #   primary_secondary_1_control_method
    #   secondary_2_tertiary_control_method
    primary_secondary_1_control_method: Optional[CommandMonitorMethod] = attr(
        default=None, name="CommandOperationMethodPriSec1"
    )

    # Secondary 2-Tertiary command-and-control and monitoring method. Refers to the methodology or system utilized for
    # regulating and overseeing power generation units' operations in response to external commands or signals. This
    # method encompasses the process by which instructions are transmitted to power generation units, and their
    # performance is monitored to ensure compliance with these instructions.
    secondary_2_tertiary_control_method: Optional[CommandMonitorMethod] = attr(
        default=None, name="CommandOperationMethodSec2Ter1Ter2"
    )

    # Bid unit price, in JPY/kW/segment
    offer_price: Decimal = price("OfferPrice", 10000.00)

    # The contract price, in JPY/kW/segment
    contract_price: Decimal = price("ContractPrice", 10000.00)

    # The performance evaluation coefficient, alpha
    performance_evaluation_coefficient: Decimal = attr(name="PerfEvalCoeff", ge=0.00, le=100.0, decimal_places=2)

    # The corrected unit price, in JPY/kW/segment
    corrected_unit_price: Decimal = price("CorrectedUnitPrice", 1000000.00)

    # The commodity combination category. This is only set for non-BSP users.
    sub_requirement: Optional[SubRequirement] = attr(default=None, name="SubRequirementType")

    # The primary offer quantity in kW. If the API user is a BSP, this field is not set for the contract results
    # generated by the TSO's power source exchange.
    primary_offer_qty: Optional[int] = power_positive("PrimaryOfferQuantityInKw", True)

    # The secondary 1 offer quantity, in kW. If the API user is a BSP, this field is not set for the contract results
    # generated by the TSO's power source exchange.
    secondary_1_offer_qty: Optional[int] = power_positive("Secondary1OfferQuantityInKw", True)

    # The secondary 2 offer quantity, in kW. If the API user is a BSP, this field is not set for the contract results
    # generated by the TSO's power source exchange.
    secondary_2_offer_qty: Optional[int] = power_positive("Secondary2OfferQuantityInKw", True)

    # The tertiary 1 offer quantity, in kW. If the API user is a BSP, this field is not set for the contract results
    # generated by the TSO's power source exchange.
    tertiary_1_offer_qty: Optional[int] = power_positive("Tertiary1OfferQuantityInKw", True)

    # The tertiary 2 offer quantity, in kW. If the API user is a BSP, this field is not set for the contract results
    # generated by the TSO's power source exchange.
    tertiary_2_offer_qty: Optional[int] = power_positive("Tertiary2OfferQuantityInKw", True)

    # The primary award quantity, in kW
    primary_award_qty: Optional[int] = power_positive("PrimaryAwardQuantityInKw", True)

    # The secondary 1 award quantity, in kW
    secondary_1_award_qty: Optional[int] = power_positive("Secondary1AwardQuantityInKw", True)

    # The secondary 2 award quantity, in kW
    secondary_2_award_qty: Optional[int] = power_positive("Secondary2AwardQuantityInKw", True)

    # The tertiary 1 award quantity, in kW
    tertiary_1_award_qty: Optional[int] = power_positive("Tertiary1AwardQuantityInKw", True)

    # The tertiary 2 award quantity, in kW
    tertiary_2_award_qty: Optional[int] = power_positive("Tertiary2AwardQuantityInKw", True)

    # The primary contract quantity, in kW
    primary_contract_qty: Optional[int] = power_positive("PrimaryContractQuantityInKw", True)

    # The secondary 1 contract quantity, in kW
    secondary_1_contract_qty: Optional[int] = power_positive("Secondary1ContractQuantityInKw", True)

    # The secondary 2 contract quantity, in kW
    secondary_2_contract_qty: Optional[int] = power_positive("Secondary2ContractQuantityInKw", True)

    # The tertiary 1 contract quantity, in kW
    tertiary_1_contract_qty: Optional[int] = power_positive("Tertiary1ContractQuantityInKw", True)

    # The tertiary 2 contract quantity, in kW
    tertiary_2_contract_qty: Optional[int] = power_positive("Tertiary2ContractQuantityInKw", True)

    # The primary effective contracted quantity, in kW
    primary_valid_qty: Optional[int] = power_positive("PrimaryValidQuantityInKw", True)

    # The secondary 1 effective contracted quantity, in kW
    secondary_1_valid_qty: Optional[int] = power_positive("Secondary1ValidQuantityInKw", True)

    # The secondary 2 effective contracted quantity, in kW
    secondary_2_valid_qty: Optional[int] = power_positive("Secondary2ValidQuantityInKw", True)

    # The tertiary 1 effective contracted quantity, in kW
    tertiary_1_valid_qty: Optional[int] = power_positive("Tertiary1ValidQuantityInKw", True)

    # The compound fulfillment quantity, in kW
    compound_valid_qty: Optional[int] = power_positive("CompoundValidQuantityInKw", True)

    # The primary invalid contract quantity, in kW
    primary_invalid_qty: Optional[int] = power_positive("PrimaryInvalidQuantityInKw", True)

    # The secondary 1 invalid contract quantity, in kW
    secondary_1_invalid_qty: Optional[int] = power_positive("Secondary1InvalidQuantityInKw", True)

    # The secondary 2 invalid contract quantity, in kW
    secondary_2_invalid_qty: Optional[int] = power_positive("Secondary2InvalidQuantityInKw", True)

    # The tertiary 1 invalid contract quantity, in kW
    tertiary_1_invalid_qty: Optional[int] = power_positive("Tertiary1InvalidQuantityInKw", True)

    # Name of the file containing the negative baseload data
    negative_baseload_file: Optional[str] = baseload_file_name("BaselineLoadFileNameNeg", True)

    # Name of the file containing the positive baseload data
    positive_baseload_file: Optional[str] = baseload_file_name("BaselineLoadFileNamePos", True)

    # The date and time when the offer was submitted. If the API user is a BSP, this attribute is not set for the
    # contract results generated by the TSO's power source exchange.
    submission_time: Optional[DateTime] = attr(default=None, name="SubmissionTime")

    # Contract result (full, partial)
    offer_award_level: ContractResult = attr(name="OfferAwardedLevel")

    # The ID of the offer to which this stack belongs
    offer_id: Optional[str] = offer_id("OfferId", True)

    # The source of the contract
    contract_source: ContractSource = attr(name="ContractSource")

    # Whether we are before gate close or after gate close
    gate_closed: BooleanFlag = attr(name="AfterGC")

    @field_serializer("submission_time")
    def encode_datetime(self, value: DateTime) -> str:
        """Encode the datetime to an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=None).isoformat() if value else ""

    @field_validator("submission_time")
    def decode_datetime(cls, value: DateTime) -> DateTime:  # pylint: disable=no-self-argument
        """Decode the datetime from an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=Timezone("Asia/Tokyo"))


class AwardResult(Payload, tag="AwardResults"):
    """Contains a number of bid rewards associated with a block of time and trade direction."""

    # The start date and time of the block associated with the awards
    start: DateTime = attr(name="StartTime")

    # The end date and time of the block associated with the awards
    end: DateTime = attr(name="EndTime")

    # The direction of the associated trades
    direction: Direction = attr(name="Direction")

    # The bid awards associated with these parameters
    data: List[Award] = element(tag="AwardResultsData", min_length=1)

    @field_serializer("start", "end")
    def encode_datetime(self, value: DateTime) -> str:
        """Encode the datetime to an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=None).isoformat()

    @field_validator("start", "end")
    def decode_datetime(cls, value: DateTime) -> DateTime:  # pylint: disable=no-self-argument
        """Decode the datetime from an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=Timezone("Asia/Tokyo"))


class AwardResponse(AwardQuery, tag="AwardResultsQuery"):
    """Contains the results of a bid award query."""

    # The bid awards associated with the query
    results: Optional[List[AwardResult]] = wrapped(default=None, path="AwardResultsQueryResponse")
