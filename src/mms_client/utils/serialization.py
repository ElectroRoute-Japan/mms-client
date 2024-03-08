"""Contains objects for serialization and deserialization of MMS data."""

from base64 import b64decode
from base64 import b64encode
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Dict
from typing import Tuple
from typing import Type

from dicttoxml import dicttoxml
from xmlschema import XMLSchema
from xmlschema import to_dict

from mms_client.types.base import PQ
from mms_client.types.base import D
from mms_client.types.base import Messages
from mms_client.types.base import MultiResponse
from mms_client.types.base import Response
from mms_client.types.base import ResponseCommon
from mms_client.types.base import ResponseData
from mms_client.utils.web import InterfaceType


class SchemaType(Enum):
    """Represents the type of schema to be used for validation."""

    MARKET = "mi-market.xsd"
    REPORT = "mi-report.xsd"
    REGISTRATION = "mpr.xsd"
    OMI = "omi.xsd"


class PayloadConfig:
    """Represents the configuration for a payload."""

    def __init__(self, xsd: SchemaType, payload_key: str, interface: InterfaceType):
        """Create a new payload configuration with the given XSD schema, payload key, and interface type.

        Arguments:
        xsd (SchemaType):           The XSD schema to use for validation.
        payload_key (str):          The key to use for the payload in the request.
        interface (InterfaceType):  The type of interface to use for the request.
        """
        # Save the configuration for later use
        self.xsd = xsd
        self.payload_key = payload_key
        self.interface = interface

        # Get a reference to the XSD file so we can use it for validation
        self._schema = XMLSchema(Path(__file__).parent / "schemas" / "xsd" / self.xsd.value)

    def serialize(self, request_payload: PQ, request_data: D) -> bytes:
        """Serialize the payload and data to a byte string for sending to the MMS server.

        Arguments:
        request_payload (RequestPayload):   The payload to be serialized.
        request_data (BaseModel):           The data to be serialized.

        Returns:    A byte string containing the XML-formatted data to be sent to the MMS server.
        """
        xml = dicttoxml(
            self._to_dict(request_payload, request_data),
            custom_root=self.payload_key,
            attr_type=False,
            encoding="UTF-8",
        )
        return b64encode(xml)

    def deserialize(self, data: bytes, payload_type: Type[PQ], data_type: Type[D]) -> Response[PQ, D]:
        """Deserialize the data to a response object.

        Arguments:
        data (bytes):                           The raw data to be deserialized.
        payload_type (Type[RequestPayload]):    The type of payload to be constructed.
        data_type (Type[BaseModel]):            The type of data to be constructed.

        Returns:    A response object containing the payload and data extracted from the raw data.
        """
        # First, decode the base64-encoded data
        xml = b64decode(data)

        # Next, convert the raw XML data to a dictionary for conversion
        as_dict = self._from_xml(xml)

        # Finally, extract the response, payload, and data from the dictionary and return them
        return self._from_dict(as_dict, payload_type, data_type)

    def deserialize_multi(self, data: bytes, payload_type: Type[PQ], data_type: Type[D]) -> MultiResponse[PQ, D]:
        """Deserialize the data to a multi-response object.

        Arguments:
        data (bytes):                           The raw data to be deserialized.
        payload_type (Type[RequestPayload]):    The type of payload to be constructed.
        data_type (Type[BaseModel]):            The type of data to be constructed.

        Returns:    A multi-response object containing the payload and data extracted from the raw data.
        """
        # First, decode the base64-encoded data
        xml = b64decode(data)

        # Next, convert the raw XML data to a dictionary for conversion
        as_dict = self._from_xml(xml)

        # Finally, extract the response, payload, and data from the dictionary and return them
        return self._from_dict_multi(as_dict, payload_type, data_type)

    def _to_dict(self, request_payload: PQ, request_data: D) -> dict:
        """Convert the payload and data to a dictionary for serialization.

        Arguments:
        request_payload (RequestPayload):   The payload to be serialized.
        request_data (BaseModel):           The data to be serialized.

        Returns:    A dictionary representation of the payload and data for serialization.
        """
        # First, validate the payload and data we'll be sending; if this fails then a Pydantic validation error will be
        # raised. We will not catch this as it is the user's responsibility to ensure the data is valid before sending.
        request_payload.model_validate(strict=True, from_attributes=True)
        request_data.model_validate(strict=True, from_attributes=True)

        # Next, convert the payload and data to a dictionary for serialization. We will exclude any unset or None
        # values from the serialization, as these represent optional fields that were not set.
        payload_dict = request_payload.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

        # Now, convert the data to a dictionary and add it to the payload dictionary. Again, we will exclude any unset
        # or None values from the serialization, as these represent optional fields that were not set.
        payload_dict[D.__name__] = request_data.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

        # Finally, return the dictionary representation of the payload and data for serialization.
        return {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema",
            "xsi:noNamespaceSchemaLocation": self.xsd,
            PQ.__name__: payload_dict,
        }

    def _from_dict(self, raw: dict, payload_type: Type[PQ], data_type: Type[D]) -> Response[PQ, D]:
        """Convert the raw data to a response object.

        Arguments:
        raw (dict):                             The raw data to be converted.
        payload_type (Type[RequestPayload]):    The type of payload to be constructed.
        data_type (Type[BaseModel]):            The type of data to be constructed.

        Returns:    A response object containing the payload and data extracted from the raw data.
        """
        # First, attempt to extract the response from the raw data; if the key isn't found then we'll raise an error.
        # Otherwise, we'll attempt to construct the response from the raw data.
        if self.payload_key not in raw:
            raise ValueError(f"Expected payload key '{self.payload_key}' not found in response")
        resp = Response[PQ, D].model_validate(raw[self.payload_key])

        # Next, attempt to extract the payload and data from within the response
        resp.payload, resp.payload_validation = self._from_dict_payload(raw[self.payload_key], payload_type)
        resp.payload_data = self._from_dict_data(raw[self.payload_key][PQ.__name__], data_type)

        # Now, attempt to extract the messages from within the payload
        self._from_dict_messages(raw[self.payload_key], resp.messages, self.payload_key)

        # Finally, return the response
        return resp

    def _from_dict_multi(self, raw: dict, payload_type: Type[PQ], data_type: Type[D]) -> MultiResponse[PQ, D]:
        """Convert the raw data to a multi-response object.

        Arguments:
        raw (dict):                             The raw data to be converted.
        payload_type (Type[RequestPayload]):    The type of payload to be constructed.
        data_type (Type[BaseModel]):            The type of data to be constructed.

        Returns:    A multi-response object containing the payload and data extracted from the raw data.
        """
        # First, attempt to extract the response from the raw data; if the key isn't found then we'll raise an error.
        # Otherwise, we'll attempt to construct the response from the raw data.
        if self.payload_key not in raw:
            raise ValueError(f"Expected payload key '{self.payload_key}' not found in response")
        resp = MultiResponse[PQ, D].model_validate(raw[self.payload_key])

        # Next, attempt to extract the payload and data from within the response
        resp.payload, resp.payload_validation = self._from_dict_payload(raw[self.payload_key], payload_type)
        resp.payload_data = [self._from_dict_data(item, data_type) for item in raw[self.payload_key][PQ.__name__]]

        # Now, attempt to extract the messages from within the payload
        self._from_dict_messages(raw[self.payload_key], resp.messages, self.payload_key)

        # Finally, return the response
        return resp

    def _from_dict_payload(self, raw: dict, payload_type: Type[PQ]) -> Tuple[PQ, ResponseCommon]:
        """Attempt to extract the payload from within the response.

        Arguments:
        raw (dict):                             The raw data to be converted.
        payload_type (Type[RequestPayload]):    The type of payload to be constructed.

        Returns:
        RequestPayload: The request payload constructed from the raw data.
        ResponseCommon: The validation information for the request payload.
        """
        if PQ.__name__ not in raw:
            raise ValueError(f"Expected payload type '{PQ.__name__}' not found in response")
        return (
            payload_type.model_validate(raw[PQ.__name__]),
            ResponseCommon.model_validate(raw[PQ.__name__]),
        )

    def _from_dict_data(self, raw: dict, data_type: Type[D]) -> ResponseData[D]:
        """Attempt to extract the data from within the payload.

        Arguments:
        raw (dict):                     The raw data to be converted.
        data_type (Type[BaseModel]):    The type of data to be constructed.

        Returns:
        BaseModel:      The data constructed from the raw data.
        ResponseCommon: The validation information for the data extracted from the response.
        """
        if D.__name__ not in raw:
            raise ValueError(f"Expected data type '{D.__name__}' not found in response")
        return ResponseData[D](
            data_type.model_validate(raw[D.__name__]),
            ResponseCommon.model_validate(raw[D.__name__]),
        )

    def _from_dict_messages(self, raw: dict, messages: Dict[str, Messages], root="") -> None:
        """Attempt to extract the messages from within the payload.

        Arguments:
        raw (dict):                     The raw data to be converted.
        messages (Dict[str, Messages]): A dictionary of messages that will be populated with the messages from the raw
                                        data, as the messages are parsed.
        root (str):                     The root of the dictionary, used to create the key for the messages.
        """
        # First, check if the "Messages" key is present in the raw data. If it's not, then we are at a leaf node and
        # will have no messages to parse, so we can return early.
        if "Messages" not in raw:
            return

        # Next, attempt to extract the messages from the raw data and add them to the messages dictionary. We will use
        # the root of the dictionary to create the key for the messages.
        messages[root] = Messages.model_validate(raw["Messages"])

        # Finally, iterate over the raw data and attempt to extract messages from any nested dictionaries. We will use
        # the root of the dictionary to create the key for the messages.
        for key, value in raw.items():
            if isinstance(value, dict) and key != "Messages":
                self._from_dict_messages(value, messages, f"{root}.{key}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._from_dict_messages(item, messages, f"{root}.{key}[{i}]")

    def _from_xml(self, data: bytes) -> dict:
        """Parse the XML file, returning the resulting dictionary.

        Arguments:
        data:       The raw XML data
        schema:     The Name the file containing the XML schema determining how this XML
                    data should be parsed.
        """
        # First, get a file-like reference to the data
        dat_file = BytesIO(data)

        # Now, attempt to extract the XML data into a dictionary for conversion; if this
        # fails then we should get a list of errors rather than a dictionary
        results = to_dict(dat_file, self._schema)
        if not isinstance(results, dict):
            raise RuntimeError(
                "xmlschema.to_dict should have returned a dictionary; it may not have been setup properly",
            )

        # Finally, return the results
        return results
