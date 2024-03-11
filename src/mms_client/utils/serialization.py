"""Contains objects for serialization and deserialization of MMS data."""

from base64 import b64decode
from base64 import b64encode
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Dict
from typing import Tuple
from typing import Type

from pydantic_xml import element
from xmlschema import XMLSchema
from xmlschema import to_dict

from mms_client.types.base import E
from mms_client.types.base import Messages
from mms_client.types.base import MultiResponse
from mms_client.types.base import P
from mms_client.types.base import PayloadBase
from mms_client.types.base import Response
from mms_client.types.base import ResponseCommon
from mms_client.types.base import ResponseData
from mms_client.types.base import SchemaType

# Directory containing all our XML schemas
XSD_DIR = Path(__file__).parent.parent / "schemas" / "xsd"


class Serializer:
    """Contains methods for serializing and deserializing MMS data."""

    def __init__(self, xsd: SchemaType, payload_key: str):
        """Create a new payload configuration with the given XSD schema, payload key, and interface type.

        Arguments:
        xsd (SchemaType):           The XSD schema to use for validation.
        payload_key (str):          The key to use for the payload in the request.
        interface (InterfaceType):  The type of interface to use for the request.
        """
        # Save the configuration for later use
        self._xsd = xsd
        self._payload_key = payload_key

        # Get a reference to the XSD file so we can use it for validation
        self._schema = XMLSchema(XSD_DIR / self._xsd.value)

    @property
    def schema(self) -> SchemaType:
        """Get the schema type for this payload configuration."""
        return self._xsd

    def serialize(self, request_payload: E, request_data: P) -> bytes:
        """Serialize the payload and data to a byte string for sending to the MMS server.

        Arguments:
        request_payload (RequestPayload):   The payload to be serialized.
        request_data (BaseModel):           The data to be serialized.

        Returns:    A byte string containing the XML-formatted data to be sent to the MMS server.
        """
        # First, create our payload class from the payload and data types
        payload_cls = _create_payload_type(
            self._payload_key,
            type(request_payload),  # type: ignore[arg-type]
            type(request_data),  # type: ignore[arg-type]
        )

        # Next, inject the payload and data into the payload class
        payload = payload_cls(request_payload, request_data, self._xsd.value)

        # Now, convert the payload to XML
        xml = payload.to_xml(skip_empty=True, encoding="utf-8")

        # Finally, convert the XML to a base64-encoded byte string and return it
        return b64encode(xml)

    def deserialize(self, data: bytes, payload_type: Type[E], data_type: Type[P]) -> Response[E, P]:
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

    def deserialize_multi(self, data: bytes, payload_type: Type[E], data_type: Type[P]) -> MultiResponse[E, P]:
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

    def _from_dict(self, raw: dict, payload_type: Type[E], data_type: Type[P]) -> Response[E, P]:
        """Convert the raw data to a response object.

        Arguments:
        raw (dict):                             The raw data to be converted.
        payload_type (Type[RequestPayload]):    The type of payload to be constructed.
        data_type (Type[BaseModel]):            The type of data to be constructed.

        Returns:    A response object containing the payload and data extracted from the raw data.
        """
        # First, attempt to extract the response from the raw data; if the key isn't found then we'll raise an error.
        # Otherwise, we'll attempt to construct the response from the raw data.
        if self._payload_key not in raw:
            raise ValueError(f"Expected payload key '{self._payload_key}' not found in response")
        resp = Response[E, P].model_validate(raw[self._payload_key])

        # Next, attempt to extract the payload and data from within the response
        resp.payload, resp.payload_validation = self._from_dict_payload(raw[self._payload_key], payload_type)
        resp.payload_data = self._from_dict_data(raw[self._payload_key][E.__name__], data_type)

        # Now, attempt to extract the messages from within the payload
        self._from_dict_messages(raw[self._payload_key], resp.messages, self._payload_key)

        # Finally, return the response
        return resp

    def _from_dict_multi(self, raw: dict, payload_type: Type[E], data_type: Type[P]) -> MultiResponse[E, P]:
        """Convert the raw data to a multi-response object.

        Arguments:
        raw (dict):                             The raw data to be converted.
        payload_type (Type[RequestPayload]):    The type of payload to be constructed.
        data_type (Type[BaseModel]):            The type of data to be constructed.

        Returns:    A multi-response object containing the payload and data extracted from the raw data.
        """
        # First, attempt to extract the response from the raw data; if the key isn't found then we'll raise an error.
        # Otherwise, we'll attempt to construct the response from the raw data.
        if self._payload_key not in raw:
            raise ValueError(f"Expected payload key '{self._payload_key}' not found in response")
        resp = MultiResponse[E, P].model_validate(raw[self._payload_key])

        # Next, attempt to extract the payload and data from within the response
        resp.payload, resp.payload_validation = self._from_dict_payload(raw[self._payload_key], payload_type)
        resp.payload_data = [self._from_dict_data(item, data_type) for item in raw[self._payload_key][E.__name__]]

        # Now, attempt to extract the messages from within the payload
        self._from_dict_messages(raw[self._payload_key], resp.messages, self._payload_key)

        # Finally, return the response
        return resp

    def _from_dict_payload(self, raw: dict, payload_type: Type[E]) -> Tuple[E, ResponseCommon]:
        """Attempt to extract the payload from within the response.

        Arguments:
        raw (dict):                             The raw data to be converted.
        payload_type (Type[RequestPayload]):    The type of payload to be constructed.

        Returns:
        RequestPayload: The request payload constructed from the raw data.
        ResponseCommon: The validation information for the request payload.
        """
        if E.__name__ not in raw:
            raise ValueError(f"Expected payload type '{E.__name__}' not found in response")
        return (
            payload_type.model_validate(raw[E.__name__]),
            ResponseCommon.model_validate(raw[E.__name__]),
        )

    def _from_dict_data(self, raw: dict, data_type: Type[P]) -> ResponseData[P]:
        """Attempt to extract the data from within the payload.

        Arguments:
        raw (dict):                     The raw data to be converted.
        data_type (Type[BaseModel]):    The type of data to be constructed.

        Returns:
        BaseModel:      The data constructed from the raw data.
        ResponseCommon: The validation information for the data extracted from the response.
        """
        if P.__name__ not in raw:
            raise ValueError(f"Expected data type '{P.__name__}' not found in response")
        return ResponseData[P](
            data_type.model_validate(raw[P.__name__]),
            ResponseCommon.model_validate(raw[P.__name__]),
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


@lru_cache(maxsize=None)
def _create_payload_type(key: str, envelope_type: Type[E], data_type: Type[P]) -> Type[PayloadBase]:
    """Create a new payload type for the given payload and data types.

    This method is intended to save us the overhead of writing a new class for each payload type. Instead, we can
    create a new class at runtime that contains the payload and data types, and use that for serialization.

    Note that this method has been LRU-cached because the operation of creating a new class from data types at
    runtime involves lots of reflection and is quite slow. By caching the results, we can avoid the overhead of
    creating new classes every time we need to serialize or deserialize data.

    Arguments:
    key: str                        The tag to use for the parent element of the payload.
    envelope_type (Type[Envelope]): The type of payload to be constructed.
    data_type (Type[Payload]):      The type of data to be constructed.

    Returns:    A new payload type that can be used for serialization.
    """  # fmt: skip
    # First, create a wrapper for our data type that will be used to store the data in the payload
    class Envelope(envelope_type):
        """Wrapper for the data type that will be used to store the data in the payload."""

        # The data to be stored in the payload
        data: data_type = element(tag=P.__name__)  # type: ignore[valid-type]

        def __init__(self, envelope: envelope_type, data: data_type):  # type: ignore[valid-type]
            """Create a new envelope to store payload data.

            Arguments:
            envelope (Envelope):    The payload to be stored in the data.
            data (Payload):         The data to be stored in the payload.
            """
            super().__init__(**envelope)
            self.data = data

    # Next, create our payload type that actually contains all the XML data
    class Payload(PayloadBase, tag=key):  # type: ignore[call-arg]
        """The payload type that will be used for serialization."""

        # The payload containing our request object and any data
        envelope: Envelope = element(tag=E.__name__)

        def __init__(self, envelope: envelope_type, data: data_type, schema: str):  # type: ignore[valid-type]
            """Create a new payload containing the request object and any data.

            Arguments:
            envelope (Envelope):    The payload to be stored in the data.
            data (Payload):         The data to be stored in the payload.
            schema (str):           The name of the schema file to use for validation.
            """
            super().__init__(location=schema)
            self.envelope = Envelope(envelope, data)

    # Finally, return the payload type so we can instantiate it
    return Payload
