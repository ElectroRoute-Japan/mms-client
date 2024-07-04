"""Contains objects for report data."""

from decimal import Decimal
from enum import StrEnum
from typing import Annotated
from typing import List
from typing import Optional

from pendulum import Timezone as TZ
from pydantic import field_serializer
from pydantic import field_validator
from pydantic_core import PydanticUndefined
from pydantic_extra_types.pendulum_dt import Date
from pydantic_extra_types.pendulum_dt import DateTime
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr
from pydantic_xml import element
from pydantic_xml import wrapped

from mms_client.types.base import Envelope
from mms_client.types.base import Payload
from mms_client.types.enums import AreaCode
from mms_client.types.enums import BaseLineSettingMethod
from mms_client.types.enums import CommandMonitorMethod
from mms_client.types.enums import ContractType
from mms_client.types.enums import RemainingReserveAvailability
from mms_client.types.enums import SignalType
from mms_client.types.fields import company_short_name
from mms_client.types.fields import participant
from mms_client.types.fields import percentage
from mms_client.types.fields import resource_name
from mms_client.types.fields import resource_short_name
from mms_client.types.fields import system_code
from mms_client.types.fields import transaction_id
from mms_client.types.registration import QueryType


def file_name(alias: str, optional: bool = False):
    """Create a field for a file name.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the file name.
    """
    return attr(default=None if optional else PydanticUndefined, name=alias, min_length=0, max_length=60)


def row_number(alias: str, optional: bool = False):
    """Create a field for a row number.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the row number.
    """
    return attr(default=None if optional else PydanticUndefined, name=alias, ge=1, lt=100000000)


class ApplicationType(StrEnum):
    """Represents the type of report to be submitted."""

    MARKET_REPORT = "MARKET_REPORT"


class ReportType(StrEnum):
    """Represents the type of data to be submitted."""

    REGISTRATION = "REGISTRATION"
    MARKET = "MA"
    INTERFACE = "INTERFACE"
    SWITCH = "SWITCH"
    SYSTEM = "SYSTEM"


class ReportSubType(StrEnum):
    """Represents the sub-category of data to be submitted."""

    AWARDS = "AWARDS"
    MERIT_ORDER_LIST = "MOL"
    OFFERS = "OFFERS"
    ADJUSTMENT_PRICES = "BUP"
    RESERVE_REQUIREMENTS = "RESREQ"
    ACCESS = "ACCESS"
    RESOURCES = "RESOURCE"
    REQUESTS = "REQUEST"


class ReportName(StrEnum):
    """Represents the name of a report."""

    TSO_RESOURCE_LIST = "ResourceList"
    BSP_RESOURCE_LIST = "BSP_ResourceList"
    RESOURCE_SETTLEMENT = "ResourceSttl"
    RESOURCE_SETTLEMENT_OTM = "ResourceSttlOTM"
    TSO_OFFERS = "Offers"
    BSP_OFFERS = "BSP_Offers"
    RESERVE_REQUIREMENTS = "ReserveReqs"
    TSO_BUP = "BUP"
    BSP_BUP = "BSP_BUP"
    MERIT_ORDER_LIST = "MOL"
    TSO_AWARDS = "ContractResult"
    BSP_AWARDS = "BSP_ContractResult"
    TSO_BASELINE_AWARDS = "MeasureBaseContractResult"
    BSP_BASELINE_AWARDS = "BSP_MeasureBaseContractResult"
    TSO_AWARDS_AFTER_GC = "ContractResultAfterGC"
    BSP_AWARDS_AFTER_GC = "BSP_ContractResultAfterGC"
    TSO_SWITCH_REQUEST = "SwitchRequest"
    TSO_ACCESS_LOG = "AccessLog"


class Periodicity(StrEnum):
    """Represents the periodicity of the report data to be generated."""

    YEARLY = "YEARLY"
    MONTHLY = "MONTHLY"
    DAILY = "DAILY"
    HOURLY = "HOURLY"
    HALF_HOURLY = "HALF_HOURLY"
    SUB_HOURLY = "SUB_HOURLY"
    ON_DEMAND = "ON_DEMAND"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ParameterName(StrEnum):
    """Represents the name of a parameter."""

    START_TIME = "START_TIME"
    END_TIME = "END_TIME"
    RESOURCE_NAME = "RESOURCE_NAME"
    MARKET_TYPE = "MARKET_TYPE"
    AREA = "AREA"


class AccessClass(StrEnum):
    """Represents the access class of the report data to be generated."""

    BSP = "BSP"
    TSO = "TSO"
    MO = "MO"


class FileType(StrEnum):
    """Represents the type of file to be returned."""

    CSV = "CSV"
    XML = "XML"


class Timezone(StrEnum):
    """Represents the timezone of the report data to be generated."""

    JST = "JST"


class ReportBase(Envelope, tag="MarketReport"):
    """Represents the base fields for a report request."""

    # The type of application for which the report is being requested
    application_type: ApplicationType = attr(name="ApplicationType")

    # The MMS code of the business entity to which the requesting user belongs, and will be used to track the user who
    # made the request. This value will be checked against the certificate used to make the request.
    participant: str = participant("ParticipantName")


class ReportMetadata(Payload):
    """Represents the base fields for report metadata."""

    # The type of report being requested
    report_type: ReportType = attr(name="ReportType")

    # The sub-type of report being requested
    report_sub_type: ReportSubType = attr(name="ReportSubType")

    # The periodicity of the report data to be returned (this should always be "ON_DEMAND")
    periodicity: Periodicity = attr(name="Periodicity")

    # The name of the report being requested
    name: ReportName = attr(name="ReportName")

    # The target date for the data to be returned
    date: Date = attr(name="Date")


class ReportData(ReportMetadata):
    """Represents the base fields for report data."""

    # The access class of the report data to be returned
    access_class: AccessClass = attr(name="AccessClass")

    # The name of the file to which the report data will be downloaded
    filename: str = file_name("FileName")

    # The type of file to which the report data will be downloaded
    file_type: FileType = attr(name="FileType")


class ReportItem(ReportData):
    """Represents the base fields for report items."""

    # The ID of the report that this item represents
    transaction_id: str = transaction_id("TransactionId")

    # The size of the file to which the report data will be downloaded, in bytes
    file_size: int = attr(name="FileSize", ge=0)

    # Whether the file is binary or not
    is_binary: bool = attr(name="BinaryFile")

    # The date when the report will be deleted
    expiry_date: Date = attr(name="ExpiryDate")

    # The description/title of the report
    description: str = attr(name="Description", max_length=100)


class Parameter(BaseXmlModel):
    """Represents a parameter for a report."""

    # The name of the parameter
    # If the search item is the start date and time, use "START_TIME".
    # If the search item is the end date and time, use "END_TIME".
    # If the search item is related to power supply, use "RESOURCE_NAME".
    # ※ When the ReportSubType is "ADJUSTMENT_PRICES", specifying the power supply is mandatory.
    # If the search item is the target market, use "MARKET_TYPE" (refer to Appendix 3).
    # If the search item is the local area, use "AREA" (refer to Appendix 3).
    # Specifying "START_TIME" and "END_TIME" is mandatory.
    name: ParameterName = attr(name="Name")

    # The value of the parameter
    # If the search item is the start or end date and time, the format is YYYY-MM-DDTHH:MI:SS.
    # If the search item is related to power supply, specify the power supply code.
    # ※ If the Name is "MARKET_TYPE", specify the target market. (Refer to Appendix 1).
    # ※ If the Name is "AREA", specify the local area. (Refer to Appendix 1).
    value: str = attr(name="Value", max_length=200)


class NewReportRequest(ReportMetadata, tag="ReportCreateRequest"):
    """Represents the base fields for a new report request.

    For report generation requests, the search criteria related to start date and time and end date and time are as
    follows:
        If the target of creation is a daily report, then the time part of the specified start date and time and end
        date and time is not used for the search.
        If the target of creation is an hourly report, then reports are created for the records spanning from the
        specified start date and time to the end date and time. For example, if start date and time is
        2021-05-01T05:10:00 and end date and time is 2021-05-01T06:10:00, and a report with 30-minute intervals is
        requested, reports for "05:00:00-05:30:00", "05:30:00-06:00:00", and "06:00:00-06:30:00" of May 1, 2021, will
        be created. If start date and time is 2021-05-01T05:00:00 and end date and time is 2021-05-01T06:00:00, and a
        report with 30-minute intervals is requested, reports for "05:00:00-05:30:00" and "05:30:00-06:00:00" of May 1,
        2021, will be created.

    The created reports are saved for 2 days and then deleted. The period during which the created reports are saved
    prevents the re-creation of reports under the same conditions. Even a slight difference in the specified conditions
    allows for the re-creation of reports.

    Report generation requests should be executed one by one, ensuring that the Transaction ID is returned before
    proceeding to the next request.
    """

    # The name of the BSP for which the report is being created
    bsp_name: Optional[str] = participant("BSPName", True)

    # Parameters to be use when configuring the report
    parameters: List[Parameter] = element(tag="Param", max_length=5)


class NewReportResponse(NewReportRequest, tag="ReportCreateRequest"):
    """Represents the base fields for a new report response."""

    # The transaction ID of the request
    transaction_id: str = attr(default="")


class ListReportRequest(ReportMetadata, tag="ReportListRequest"):
    """Represents the base fields for a list report request."""


class ListReportResponse(ListReportRequest, tag="ReportListRequest"):
    """Represents the base fields for a list report response."""

    # The list of reports that match the query
    reports: List[ReportItem] = wrapped(path="ReportListResponse", entity=element(tag="ReportItem"))


class ReportDownloadRequest(ReportData):
    """Represents the base fields for a report download request.

    This is used when the Transaction ID obtained as a response to the report generation request is unknown while
    downloading the report. If the requested report exists, the content of the report will be provided as a response. If
    the requested report does not exist, the response described on this page will be provided. Report download requests
    should be made one file at a time, ensuring that each download is completed before making the next request.
    """


class ReportDownloadRequestTrnID(Payload):
    """Represents the base fields for a report download request.

    This is used when the Transaction ID obtained as a response to the report generation request is known when
    downloading the report. If the requested report exists, the content of the report will be provided as a response. If
    the requested report does not exist, the response described on this page will be provided. Report download requests
    should be made one file at a time, ensuring that each download is completed before making the next request.
    """

    # The transaction ID of the request
    transaction_id: str = transaction_id("TransactionId")


class OutboundData(Envelope):
    """Represents the base fields for actual report data."""

    # The name of the dataset to be returned
    dataset_name: Optional[ReportName] = attr(default=None, name="DatasetName")

    # The type of dataset to be returned
    dataset_type: Optional[Periodicity] = attr(default=None, name="DatasetType")

    # The date for which the dataset is being returned
    date: Optional[Date] = attr(default=None, name="Date")

    # The type of date for which the dataset is being returned
    date_type: Optional[QueryType] = attr(default=None, name="DateType")

    # The timezone for which the dataset is being returned
    timezone: Optional[Timezone] = attr(default=None, name="DateTimeIndicator")

    # The time the report was published
    publish_time: Optional[DateTime] = attr(default=None, name="PublishTime")

    @field_serializer("publish_time")
    def encode_datetime(self, value: DateTime) -> str:
        """Encode the datetime to an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=None).isoformat() if value else ""

    @field_validator("publish_time")
    def decode_datetime(cls, value: DateTime) -> DateTime:  # pylint: disable=no-self-argument
        """Decode the datetime from an MMS-compliant ISO 8601 string."""
        return value.replace(tzinfo=TZ("Asia/Tokyo"))


class ReportLineBase(Payload):
    """Represents the base fields for a report line item."""

    # The row number of the report line item
    row_number: Optional[int] = row_number("ROW", True)


class BSPResourceListItem(ReportLineBase, tag="BSP_ResourceList"):
    """Represents the base fields for a BSP resource report line item."""

    # The MMS code of the business entity to which the registration applies
    participant: str = participant("ParticipantName")

    # Abbrevated name of the business entity to which the registration applies
    company_short_name: str = company_short_name("CompanyShortName")

    # The date from which the power generation unit is available to trade
    start: Date = attr(name="StartDate")

    # The date until which the power generation unit is available to trade
    end: Optional[Date] = attr(default=None, name="EndDate")

    # An abbreviated name for the power generation unit
    short_name: str = resource_short_name("ResourceShortName")

    # The full name for the power generation unit
    full_name: str = resource_name("ResourceName")

    # The grid code of the power generation unit
    system_code: str = system_code("SystemCode")

    # The region in which the power generation unit is located and in which its energy will be traded
    area: AreaCode = attr(name="Area")

    # Whether or not the resource is primary control power. Refers to the ability of a power generation unit or system
    # to rapidly adjust its output in response to fluctuations in demand or supply within the electrical grid. This
    # primary control power is essential for maintaining the stability and frequency of the grid, especially during
    # sudden changes in load or generation. Typically, primary control power is provided by resources such as
    # hydroelectric plants, natural gas turbines, or other fast-responding power generation assets. If you want to
    # allow market participation for the specified product category, you should set this to True.
    has_primary: Optional[bool] = attr(default=None, name="Pri")

    # Whether or not the resource is secondary 1 control power. Secondary control power, also known as secondary reserve
    # or frequency containment reserve, refers to a type of reserve power that is used to stabilize the grid frequency
    # in the event of sudden changes in supply or demand. It is one of the mechanisms used in the regulation of grid
    # frequency and is typically provided by power plants or other sources that can quickly adjust their output in
    # response to frequency deviations. The secondary control power is activated automatically and rapidly in response
    # to frequency deviations detected by the grid's control system. If you want to allow market participation for the
    # specified product category, you should set this to True.
    has_secondary_1: Optional[bool] = attr(default=None, name="Sec1")

    # Whether or not the resource is secondary 2 control power. Secondary control power, also known as secondary reserve
    # or frequency containment reserve, refers to a type of reserve power that is used to stabilize the grid frequency
    # in the event of sudden changes in supply or demand. It is one of the mechanisms used in the regulation of grid
    # frequency and is typically provided by power plants or other sources that can quickly adjust their output in
    # response to frequency deviations. The secondary control power is activated automatically and rapidly in response
    # to frequency deviations detected by the grid's control system. If you want to allow market participation for the
    # specified product category, you should set this to True.
    has_secondary_2: Optional[bool] = attr(default=None, name="Sec2")

    # Whether or not the resource is tertairy 1 control power. Tertiary control power refers to the capacity of a
    # power generation unit or system to provide regulation services at the tertiary level of frequency control in
    # an electrical grid. In an electrical grid, frequency regulation is typically categorized into primary, secondary,
    # and tertiary control levels, each serving a specific role in maintaining grid stability. Tertiary control,
    # also known as frequency containment reserve (FCR), operates on a slower timescale compared to primary and
    # secondary control. It helps to fine-tune grid frequency over longer periods, usually several minutes to hours,
    # by adjusting the output of power generation units. The tertiary control power is often provided by power plants
    # that can adjust their output relatively quickly but are not as fast as those providing primary and secondary
    # control. This control level helps to ensure that the grid frequency remains within acceptable limits, thus
    # maintaining grid stability and reliability.If you want to allow market participation for the specified product
    # category, you should set this to True.
    has_tertiary_1: Optional[bool] = attr(default=None, name="Ter1")

    # Whether or not the resource is tertairy 2 control power. Tertiary control power refers to the capacity of a
    # power generation unit or system to provide regulation services at the tertiary level of frequency control in
    # an electrical grid. In an electrical grid, frequency regulation is typically categorized into primary, secondary,
    # and tertiary control levels, each serving a specific role in maintaining grid stability. Tertiary control,
    # also known as frequency containment reserve (FCR), operates on a slower timescale compared to primary and
    # secondary control. It helps to fine-tune grid frequency over longer periods, usually several minutes to hours,
    # by adjusting the output of power generation units. The tertiary control power is often provided by power plants
    # that can adjust their output relatively quickly but are not as fast as those providing primary and secondary
    # control. This control level helps to ensure that the grid frequency remains within acceptable limits, thus
    # maintaining grid stability and reliability.If you want to allow market participation for the specified product
    # category, you should set this to True.
    has_tertiary_2: Optional[bool] = attr(default=None, name="Ter2")

    # How the power generation unit is used in the market
    contract_type: Optional[ContractType] = attr(default=None, name="ContractType")

    # Primary-Secondary 1 command-and-control and monitoring method. Refers to the methodology or system utilized for
    # regulating and overseeing power generation units' operations in response to external commands or signals. This
    # method encompasses the process by which instructions are transmitted to power generation units, and their
    # performance is monitored to ensure compliance with these instructions. If has_secondary_1 is set to True, then
    # it must be set to DEDICATED_LINE. At least one of the following combinations must be set:
    #   primary_secondary_1_control_method
    #   secondary_2_tertiary_control_method
    primary_secondary_1_control_method: Optional[CommandMonitorMethod] = attr(
        default=None, name="PriSec1CommandOperationMethod"
    )

    # Secondary 2-Tertiary command-and-control and monitoring method. Refers to the methodology or system utilized for
    # regulating and overseeing power generation units' operations in response to external commands or signals. This
    # method encompasses the process by which instructions are transmitted to power generation units, and their
    # performance is monitored to ensure compliance with these instructions.
    secondary_2_tertiary_control_method: Optional[CommandMonitorMethod] = attr(
        default=None, name="Sec2Ter1Ter2CommandOperationMethod"
    )

    # Adjustment Coefficient (α) (Tertiary Adjustment Power ②). If this is not set for a power supply, it is treated as
    # "1" during the execution process but will not be output when retrieving this report.
    tertiary_2_adjustment_coefficient: Annotated[Decimal, percentage("CoefficientTR2", True)]

    # Method determinining how the baseline is set for a power generation unit. The setting method is available when
    # the contract type is not ONLY_POWER_SUPPLY_1 and at least one of the following is True: has_primary,
    # has_secondary_1, has_secondary_2 or has_tertiary_1. Additionally, it can only be set when resource_type is
    # VPP_GEN, VPP_GEN_AND_DEM or VPP_DEM. It's mandatory in these cases and cannot be set for other power sources.
    baseline_setting_method: Optional[BaseLineSettingMethod] = attr(default=None, name="BaselineSettingsMethod")

    # The signal type for the power generation unit
    signal_type: SignalType = attr("SignalType")

    # How the surplus capacity of a power generation unit can be utilized. For contract_type MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    primary_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="PriRemResvUtilization")

    # How the surplus capacity of a power generation unit can be utilized. For contract_type of MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    secondary_1_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Sec1RemResvUtilization")

    # How the surplus capacity of a power generation unit can be utilized. For contract_type of MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    secondary_2_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Sec2RemResvUtilization")

    # How the surplus capacity of a power generation unit can be utilized. For contract_type of MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    tertiary_1_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Ter1RemResvUtilization")

    # How the surplus capacity of a power generation unit can be utilized. For contract_type of MARKET, POWER_SUPPLY_2,
    # and ONLY_POWER_SUPPLY_1, this field must be set to NOT_AVAILABLE.
    tertiary_2_remaining_reserve_utilization: RemainingReserveAvailability = attr(name="Ter2RemResvUtilization")
