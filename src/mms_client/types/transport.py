"""Contains the base types necessary for communication with the MMS server."""

from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class RequestType(Enum):
    """Represents the type of request to be sent to the MMS server.

    Note that the first four items are valid for the Market Initiator (MI) interface, while the last item is valid for
    the Other Market Initiator (OMI) interface.
    """

    INFO = "mp.info"
    MARKET = "mp.market"
    REGISTRATION = "mp.registration"
    REPORT = "mp.report"
    OMI = "mp.omi"


class RequestDataType(Enum):
    """Represents the type of data to be sent to the MMS server.

    NOTE: JSON is currently not supported and has been left in for future use.
    """

    JSON = "JSON"
    XML = "XML"


class ResponseDataType(Enum):
    """Represents the type of data to be received from the MMS server.

    NOTE: JSON is currently not supported and has been left in for future use.
    """

    XML = "XML"
    HTML = "HTML"
    CSV = "CSV"
    JSON = "JSON"
    TXT = "TXT"


class Attachment(BaseModel):
    """Represents a file attachment to be sent with a request or response."""

    # The signature used to encrypt the attachment
    signature: str = Field(alias="signature")

    # The name of the attachment file
    name: str = Field(alias="name")

    # The attachment file data
    data: str = Field(alias="binaryData")


class MmsRequest(BaseModel):
    """Base class for all MMS requests."""

    # The API subsystem to which the request is sent.
    subsystem: RequestType = Field(alias="requestType")

    # Whether the request is being made as the market operator
    as_admin: bool = Field(default=False, alias="adminRole")

    # Whether the request data is compressed (for future use only)
    compressed: bool = Field(default=False, alias="requestDataCompressed")

    # The type of data to be sent to the MMS server.
    data_type: RequestDataType = Field(alias="requestDataType")

    # Whether to send the request data in the response, on a successful request
    respond_with_request: bool = Field(default=True, alias="sendRequestDataOnSuccess")

    # Wether the response data should be compressed (for future use only)
    response_compressed: bool = Field(default=False, alias="sendResponseDataCompressed")

    # The signature used to encrypt the request payload
    signature: str = Field(alias="requestSignature")

    # The base-64 encoded payload of the request
    payload: str = Field(alias="requestData")

    # Any attached files to be sent with the request. Only 20 of these are allowed for OMI requests. For MI requests,
    # the limit is 40.
    attachments: List[Attachment] = Field(default=[], alias="attachmentData")

    def to_arguments(self) -> dict:
        """Convert the request to a dictionary of arguments for use in the MMS client."""
        # First, convert the type to a dictionary format
        converted = self.model_dump(by_alias=True)

        # Next, convert the enum types to their string representations
        converted["requestType"] = converted["requestType"].value
        converted["requestDataType"] = converted["requestDataType"].value

        # Finally, return the converted dictionary
        return converted


class MmsResponse(BaseModel):
    """Base class for all MMS responses."""

    # Whether the request was successful
    success: bool = Field(alias="success")

    # Whether there were any warnings. This field will only be present if the request was successful.
    warnings: bool = Field(default=False, alias="warnings")

    # Whether the response is binary data.
    is_binary: bool = Field(default=False, alias="responseBinary")

    # Whether the response data is compressed (for future use only)
    compressed: bool = Field(default=False, alias="responseCompressed")

    # The type of data to be received from the MMS server.
    data_type: ResponseDataType = Field(alias="responseDataType")

    # The filename assigned to the response (for pre-generated reports)
    report_filename: Optional[str] = Field(default=None, alias="responseFilename")

    # The base-64 encoded payload of the response
    payload: bytes = Field(alias="responseData")

    # Any attached files to be sent with the response
    attachments: List[Attachment] = Field(default=[], alias="attachmentData")
