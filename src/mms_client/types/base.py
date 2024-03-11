"""Contains the base types necessary for communication with the MMS server."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from pydantic import PrivateAttr
from pydantic_extra_types.pendulum_dt import DateTime
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr
from pydantic_xml import element

from mms_client.types.enums import ValidationStatus


class Message(BaseXmlModel):
    """Represents a message returned with a payload."""

    # The message text. Not sure why this is called code in the XML.
    code: str = attr(default="", name="Code", min_length=2, max_length=50, pattern=r"^[a-zA-Z_0-9\-]*$")


class Messages(BaseXmlModel):
    """Represents a collection of messages returned with a payload."""

    # A list of information messages returned with a payload
    information: List[Message] = element(default=[], tag="Information")

    # A list of warning messages returned with a payload
    warnings: List[Message] = element(default=[], tag="Warning")

    # A list of error messages returned with a payload
    errors: List[Message] = element(default=[], tag="Error")


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
    transaction_id: Optional[str] = attr(default=None, name="TransactionID", min_length=8, max_length=10)

    # When the request was received, in the format "DDD MMM DD HH:MM:SS TZ YYYY"
    timestamp: str = attr(default="", name="TimeStamp")

    # When the request was received, in the format "YYYY-MM-DD HH:MM:SSZ"
    timestamp_xml: Optional[DateTime] = attr(default=None, name="XmlTimeStamp")


class ResponseCommon(BaseXmlModel):
    """Contains fields common to many (but not all) market DTOs."""

    # Whether the request was successful. This field will certainly be present in responses, but should not be present
    # in requests.
    success: Optional[bool] = attr(default=None, name="Success")

    # The status of the validation check done on the element. This field is not required for requests, and will be
    # populated in responses. For responses, the default value is "NOT_DONE".
    validation: Optional[ValidationStatus] = attr(default=None, name="ValidationStatus")


class Payload(BaseXmlModel):
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
    REGISTRATION = "mpr.xsd"
    OMI = "omi.xsd"


class PayloadBase(BaseXmlModel, nsmap={"xsi": "http://www.w3.org/2001/XMLSchema"}):
    """Represents the base fields for an MMS request payload."""

    # The XML schema to use for validation
    location: SchemaType = attr(name="noNamespaceSchemaLocation", ns="xsi")


class BaseResponse(PayloadBase, Generic[E], tag="BaseResponse"):
    """Contains the base data extracted from the MMS response in a format we can use."""

    # The processing statistics returned with the payload. This will not be present in requests, and will be populated
    # in responses.
    statistics: ProcessingStatistics = element(tag="ProcessingStatistics")

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

    def set_envelope(self, value: E) -> None:
        """Set the request payload.

        Arguments:
        value (E):    The request payload.
        """
        self._envelope = value

    @property
    def envelope_validation(self) -> ResponseCommon:
        """Return the validation information for the request payload."""
        return self._envelope_validation

    def set_envelope_validation(self, value: ResponseCommon) -> None:
        """Set the validation information for the request payload.

        Arguments:
        value (ResponseCommon):    The validation information for the request payload.
        """
        self._envelope_validation = value

    @property
    def messages(self) -> Dict[str, Messages]:
        """Return the messages returned with the payload."""
        return self._messages

    def set_messages(self, value: Dict[str, Messages]) -> None:
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
    _payload_data: ResponseData[P] = PrivateAttr()

    @property
    def data(self) -> P:
        """Return the data extracted from the response."""
        return self._payload_data.data  # pylint: disable=no-member

    @data.setter
    def data(self, value: ResponseData[P]) -> None:
        """Set the data extracted from the response.

        Arguments:
        value (ResponseData[P]):    The data extracted from the response.
        """
        self._payload_data = value


class MultiResponse(BaseResponse[E], Generic[E, P]):
    """Contains all the data extracted from the MMS response in a format we can use."""

    # The payload data extracted from the response
    _payload_data: List[ResponseData[P]] = PrivateAttr()

    @property
    def data(self) -> List[P]:
        """Return the data extracted from the response."""
        return [response.data for response in self._payload_data]  # pylint: disable=not-an-iterable

    @data.setter
    def data(self, value: List[ResponseData[P]]) -> None:
        """Set the data extracted from the response.

        Arguments:
        value (List[ResponseData[P]]):    The data extracted from the response.
        """
        self._payload_data = value[:]
