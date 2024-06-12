"""Contains the base types necessary for communication with the MMS server."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from lxml.etree import _Element as Element
from pydantic import PrivateAttr
from pydantic_extra_types.pendulum_dt import DateTime
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr
from pydantic_xml import computed_element
from pydantic_xml import element

from mms_client.types.fields import transaction_id


class ValidationStatus(Enum):
    """Represents the status of the validation check done on an element."""

    PASSED = "PASSED"  # The validation check for all data within the element has succeeded.
    WARNING = "WARNING"  # There are data within the element that have triggered warnings during the validation check.
    PASSED_PARTIAL = "PASSED_PARTIAL"  # Some data within the element has failed the validation check.
    FAILED = "FAILED"  # The data inside the element failed the validation check.
    NOT_DONE = "NOT_DONE"  # There are data with incomplete validation checks within the element.


class Message(BaseXmlModel):
    """Represents a message returned with a payload."""

    # The message text. Not sure why this is called code in the XML.
    code: str = attr(default="", name="Code", min_length=2, max_length=50, pattern=r"^[a-zA-Z_0-9\-]*$")


class Messages(BaseXmlModel, search_mode="unordered", arbitrary_types_allowed=True):
    """Represents a collection of messages returned with a payload."""

    # The raw information messages returned with a payload
    information_raw: List[Element] = element(default=[], tag="Information", nillable=True, exclude=True)

    # The raw warning messages returned with a payload
    warnings_raw: List[Element] = element(default=[], tag="Warning", nillable=True, exclude=True)

    # The raw error messages returned with a payload
    errors_raw: List[Element] = element(default=[], tag="Error", nillable=True, exclude=True)

    @computed_element
    def information(self) -> List[str]:
        """Return the information messages."""
        return self._parse_messages(self.information_raw)

    @computed_element
    def warnings(self) -> List[str]:
        """Return the warning messages."""
        return self._parse_messages(self.warnings_raw)

    @computed_element
    def errors(self) -> List[str]:
        """Return the error messages."""
        return self._parse_messages(self.errors_raw)

    def _parse_messages(self, raw: List[Element]) -> List[str]:
        """Parse the messages from the XML tree.

        Arguments:
        raw (List[Element]): The raw XML tree to parse.

        Returns:    A list of message codes.
        """
        messages = []
        for item in raw:
            if message := item.attrib.get("Code"):
                messages.append(message)
            else:
                messages.append(item.text or "")
        return messages


class ProcessingStatistics(BaseXmlModel):
    """Represents the statistics returned with a payload."""

    # The number of objects received with the request
    received: Optional[int] = attr(default=None, name="Received")

    # The number of objects that passed validation
    valid: Optional[int] = attr(default=None, name="Valid")

    # The number of objects that failed validation
    invalid: Optional[int] = attr(default=None, name="Invalid")

    # The number of objects that were successfully processed
    successful: Optional[int] = attr(default=None, name="Successful")

    # The number of objects that were unsuccessfully processed
    unsuccessful: Optional[int] = attr(default=None, name="Unsuccessful")

    # The amount of time it took to process the request in milliseconds
    time_ms: Optional[int] = attr(default=None, name="ProcessingTimeMs")

    # The transaction ID of the request
    transaction_id: Optional[str] = transaction_id("TransactionId", True)

    # When the request was received, in the format "DDD MMM DD HH:MM:SS TZ YYYY"
    timestamp: str = attr(default="", name="TimeStamp")

    # When the request was received, in the format "YYYY-MM-DD HH:MM:SSZ"
    timestamp_xml: Optional[DateTime] = attr(default=None, name="XmlTimeStamp")


class ResponseCommon(BaseXmlModel, search_mode="unordered"):
    """Contains fields common to many (but not all) market DTOs."""

    # Whether the request was successful. This field will certainly be present in responses, but should not be present
    # in requests.
    success: bool = attr(default=True, name="Success")

    # The status of the validation check done on the element. This field is not required for requests, and will be
    # populated in responses. For responses, the default value is "NOT_DONE".
    base_validation: Optional[ValidationStatus] = attr(default=None, name="Validation")

    # The status of the validation check done on the element, specifically for reports. This field is not required for
    # requests, and will be populated in responses. For responses, the default value is "NOT_DONE".
    report_validation: Optional[ValidationStatus] = attr(default=None, name="ValidationStatus")

    @property
    def validation(self) -> ValidationStatus:
        """Return the validation status of the element."""
        return self.base_validation or self.report_validation or ValidationStatus.NOT_DONE


class Payload(BaseXmlModel, search_mode="unordered"):
    """Represents the base fields for MMS request data."""


# Define a generic type used to identify the data type. This type will be used to create the MarketData class.
P = TypeVar("P", bound=Payload)


class Envelope(BaseXmlModel):
    """Represents the base fields for an MMS request data envelope."""


# Define a generic type used to identify the payload type. This type will be used to create the MarketData class.
E = TypeVar("E", bound=Envelope)


class SchemaType(Enum):
    """Represents the type of schema to be used for validation."""

    MARKET = "mi-market.xsd"
    REPORT = "mi-report.xsd"
    REPORT_RESPONSE = "mi-outbnd-reports.xsd"
    REGISTRATION = "mpr.xsd"
    OMI = "omi.xsd"


class PayloadBase(BaseXmlModel):
    """Represents the base fields for an MMS request payload."""


class BaseResponse(BaseXmlModel, Generic[E], tag="BaseResponse"):
    """Contains the base data extracted from the MMS response in a format we can use."""

    # The processing statistics returned with the payload. This will not be present in requests, and will be populated
    # in responses.
    statistics: Optional[ProcessingStatistics] = element(default=None, tag="ProcessingStatistics")

    # The request payload, containing the request data
    _envelope: E = PrivateAttr()

    # The validation information for the request payload
    _envelope_validation: ResponseCommon = PrivateAttr()

    # The messages returned with the payload. Each object will likely have its own so these
    # will be parsed separately.
    _messages: Dict[str, Messages] = PrivateAttr()

    def __init__(self, **data):
        """Create a new BaseResponse object.

        Arguments:
        **data:    The data to use to create the object.
        """
        super().__init__(**data)
        self._envelope = None
        self._envelope_validation = None
        self._messages = {}

    @property
    def envelope(self) -> E:
        """Return the request payload."""
        return self._envelope

    @envelope.setter
    def envelope(self, value: E) -> None:
        """Set the request payload.

        Arguments:
        value (E):    The request payload.
        """
        self._envelope = value

    @property
    def envelope_validation(self) -> ResponseCommon:
        """Return the validation information for the request payload."""
        return self._envelope_validation

    @envelope_validation.setter
    def envelope_validation(self, value: ResponseCommon) -> None:
        """Set the validation information for the request payload.

        Arguments:
        value (ResponseCommon):    The validation information for the request payload.
        """
        self._envelope_validation = value

    @property
    def messages(self) -> Dict[str, Messages]:
        """Return the messages returned with the payload."""
        return self._messages

    @messages.setter
    def messages(self, value: Dict[str, Messages]) -> None:
        """Set the messages returned with the payload.

        Arguments:
        value (Dict[str, Messages]):    The messages returned with the payload.
        """
        self._messages = value


@dataclass
class ResponseData(Generic[P]):
    """Contains the actual payload data extracted from the MMS response in a format we can use."""

    # The data extracted from the response
    data: P

    # The validation information for the data extracted from the response
    data_validation: ResponseCommon


class Response(BaseResponse[E], Generic[E, P]):
    """Contains all the data extracted from the MMS response in a format we can use."""

    # The payload data extracted from the response
    _payload_data: Optional[ResponseData[P]] = PrivateAttr()

    def __init__(self, **data):
        """Create a new Response object.

        Arguments:
        **data:    The data to use to create the object.
        """
        super().__init__(**data)
        self._payload_data = None

    @property
    def data(self) -> Optional[P]:
        """Return the data extracted from the response."""
        return self._payload_data.data if self._payload_data else None  # pylint: disable=no-member

    @property
    def payload(self) -> Optional[ResponseData[P]]:
        """Return the response payload."""
        return self._payload_data

    @payload.setter
    def payload(self, value: Optional[ResponseData[P]]) -> None:
        """Set the payload extracted from the response.

        Arguments:
        value (ResponseData[P]):    The payload extracted from the response.
        """
        self._payload_data = value


class MultiResponse(BaseResponse[E], Generic[E, P]):
    """Contains all the data extracted from the MMS response in a format we can use."""

    # The payload data extracted from the response
    _payload_data: List[ResponseData[P]] = PrivateAttr()

    def __init__(self, **data):
        """Create a new MultiResponse object.

        Arguments:
        **data:    The data to use to create the object.
        """
        super().__init__(**data)
        self._payload_data = []

    @property
    def data(self) -> List[P]:
        """Return the data extracted from the response."""
        return [response.data for response in self._payload_data]  # pylint: disable=not-an-iterable

    @property
    def payload(self) -> List[ResponseData[P]]:
        """Return the response payload."""
        return self._payload_data

    @payload.setter
    def payload(self, values: List[Optional[ResponseData[P]]]) -> None:
        """Set the payload extracted from the response.

        Arguments:
        values (List[ResponseData[P]]): The payload extracted from the response.
        """
        self._payload_data = [value for value in values if value]
