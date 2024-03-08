"""Contains the base types necessary for communication with the MMS server."""

from dataclasses import dataclass
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from pendulum import DateTime
from pydantic import BaseModel
from pydantic import Field

from mms_client.types.enums import ValidationStatus

# Type that will be used inside the various request/response types
P = TypeVar("P", bound=BaseModel)


class Message(BaseModel):
    """Represents a message returned with a payload."""

    # The message text. Not sure why this is called code in the XML.
    code: str = Field(default="", alias="Code", min_length=2, max_length=50, pattern=r"^[a-zA-Z_0-9\-]*$")


class Messages(BaseModel):
    """Represents a collection of messages returned with a payload."""

    # A list of information messages returned with a payload
    information: List[Message] = Field(default=[], alias="Information")

    # A list of warning messages returned with a payload
    warnings: List[Message] = Field(default=[], alias="Warning")

    # A list of error messages returned with a payload
    errors: List[Message] = Field(default=[], alias="Error")


class ProcessingStatistics(BaseModel):
    """Represents the statistics returned with a payload."""

    # The number of objects received with the request
    received: Optional[int] = Field(default=None, alias="Received")

    # The number of objects that passed validation
    valid: Optional[int] = Field(default=None, alias="Valid")

    # The number of objects that failed validation
    invalid: Optional[int] = Field(default=None, alias="Invalid")

    # The number of objects that were successfully processed
    successful: Optional[int] = Field(default=None, alias="Successful")

    # The number of objects that were unsuccessfully processed
    unsuccessful: Optional[int] = Field(default=None, alias="Unsuccessful")

    # The amount of time it took to process the request in milliseconds
    time_ms: Optional[int] = Field(default=None, alias="ProcessingTimeMs")

    # The transaction ID of the request
    transaction_id: Optional[str] = Field(default=None, alias="TransactionID", min_length=8, max_length=10)

    # When the request was received, in the format "DDD MMM DD HH:MM:SS TZ YYYY"
    timestamp: str = Field(default="", alias="TimeStamp")

    # When the request was received, in the format "YYYY-MM-DD HH:MM:SSZ"
    timestamp_xml: Optional[DateTime] = Field(default=None, alias="XmlTimeStamp")


class ResponseCommon(BaseModel):
    """Contains fields common to many (but not all) market DTOs."""

    # Whether the request was successful. This field will certainly be present in responses, but should not be present
    # in requests.
    success: Optional[bool] = Field(default=None, alias="Success")

    # The status of the validation check done on the element. This field is not required for requests, and will be
    # populated in responses. For responses, the default value is "NOT_DONE".
    validation: Optional[ValidationStatus] = Field(default=None, alias="ValidationStatus")


class RequestPayload(BaseModel):
    """Represents the base fields for an MMS request payload."""


# Define a generic type used to identify the payload type. This type will be used to create the MarketData class.
PQ = TypeVar("PQ", bound=RequestPayload)

# Define a generic type used to identify the data type. This type will be used to create the MarketData class.
D = TypeVar("D", bound=BaseModel)


class BaseResponse(BaseModel, Generic[PQ]):
    """Contains the base data extracted from the MMS response in a format we can use."""

    # The processing statistics returned with the payload. This will not be present in requests, and will be populated
    # in responses.
    statistics: ProcessingStatistics = Field(alias="ProcessingStatistics")

    # The request payload, containing the request data
    payload: PQ = Field(exclude=True)

    # The validation information for the request payload
    payload_validation: ResponseCommon = Field(exclude=True)

    # The messages returned with the payload. Each object will likely have its own so these
    # will be parsed separately.
    messages: Dict[str, Messages] = Field(exclude=True)


@dataclass
class ResponseData(Generic[D]):
    """Contains the actual payload data extracted from the MMS response in a format we can use."""

    # The data extracted from the response
    data: D

    # The validation information for the data extracted from the response
    data_validation: ResponseCommon


class Response(BaseResponse, Generic[D]):
    """Contains all the data extracted from the MMS response in a format we can use."""

    # The payload data extracted from the response
    payload_data: ResponseData[D] = Field(exclude=True)

    @property
    def data(self) -> D:
        """Return the data extracted from the response."""
        return self.payload_data.data  # pylint: disable=no-member


class MultiResponse(BaseResponse, Generic[D]):
    """Contains all the data extracted from the MMS response in a format we can use."""

    # The payload data extracted from the response
    payload_data: List[ResponseData[D]] = Field(exclude=True)

    @property
    def data(self) -> List[D]:
        """Return the data extracted from the response."""
        return [response.data for response in self.payload_data]  # pylint: disable=not-an-iterable
