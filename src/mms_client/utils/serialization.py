"""Contains objects for serialization and deserialization of MMS data."""

from functools import lru_cache
from io import BytesIO
from logging import getLogger
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union
from typing import get_args
from typing import get_origin

from lxml.etree import XMLSchema
from lxml.etree import _Element as Element
from lxml.etree import parse
from pydantic_xml import element
from pydantic_xml.typedefs import EntityLocation

from mms_client.types.base import E
from mms_client.types.base import Messages
from mms_client.types.base import MultiResponse
from mms_client.types.base import P
from mms_client.types.base import Payload
from mms_client.types.base import PayloadBase
from mms_client.types.base import Response
from mms_client.types.base import ResponseCommon
from mms_client.types.base import ResponseData
from mms_client.types.base import SchemaType

# Directory containing all our XML schemas
XSD_DIR = Path(__file__).parent.parent / "schemas" / "xsd"

# Set the default logger for the MMS client
logger = getLogger(__name__)


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
        with open(XSD_DIR / self._xsd.value, "rb") as f:
            self._schema = XMLSchema(parse(f))

    def serialize(self, request_envelope: E, request_data: P, for_report: bool = False) -> bytes:
        """Serialize the envelope and data to a byte string for sending to the MMS server.

        Arguments:
        request_envelope (Envelope):    The envelope to be serialized.
        request_data (Payload):         The data to be serialized.
        for_report (bool):              If True, the data will be serialized for a report request.

        Returns:    A byte string containing the XML-formatted data to be sent to the MMS server.
        """
        # First, choose the correct payload factory based on the request type
        factory = _create_report_payload_type if for_report else _create_request_payload_type

        # Next, create our payload class from the payload and data types
        payload_cls = factory(
            self._payload_key,
            type(request_envelope),
            type(request_data),
            False,  # type: ignore[arg-type]
        )

        # Now, inject the payload and data into the payload class
        # NOTE: this returns a type that inherits from PayloadBase and the arguments provided to the initializer
        # here are correct, but mypy thinks they are incorrect because it doesn't understand the the inherited type
        payload = payload_cls(request_envelope, request_data, self._xsd.value)  # type: ignore[call-arg, misc]

        # Finally, convert the payload to XML and return it
        # NOTE: we provided the encoding here so this will return bytes, not a string
        return self._to_canoncialized_xml(payload)

    def serialize_multi(
        self, request_envelope: E, request_data: List[P], request_type: Type[P], for_report: bool = False
    ) -> bytes:
        """Serialize the envelope and data to a byte string for sending to the MMS server.

        Arguments:
        request_envelope (Envelope):    The envelope to be serialized.
        request_data (List[Payload]):   The data to be serialized.
        request_type (Type[Payload]):   The type of data to be serialized.
        for_report (bool):              If True, the data will be serialized for a report request.

        Returns:    A byte string containing the XML-formatted data to be sent to the MMS server.
        """
        # First, choose the correct payload factory based on the request type
        factory = _create_report_payload_type if for_report else _create_request_payload_type

        # Next, create our payload class from the payload and data types
        payload_cls = factory(self._payload_key, type(request_envelope), request_type, True)  # type: ignore[arg-type]

        # Now, inject the payload and data into the payload class
        # NOTE: this returns a type that inherits from PayloadBase and the arguments provided to the initializer
        # here are correct, but mypy thinks they are incorrect because it doesn't understand the the inherited type
        payload = payload_cls(request_envelope, request_data, self._xsd.value)  # type: ignore[call-arg, misc]

        # Finally, convert the payload to XML and return it
        # NOTE: we provided the encoding here so this will return bytes, not a string
        return self._to_canoncialized_xml(payload)

    def deserialize(
        self, data: bytes, envelope_type: Type[E], data_type: Type[P], for_report: bool = False
    ) -> Response[E, P]:
        """Deserialize the data to a response object.

        Arguments:
        data (bytes):                   The raw data to be deserialized.
        envelope_type (Type[Envelope]): The type of envelope to be constructed.
        data_type (Type[Payload]):      The type of data to be constructed.
        for_report (bool):              If True, the data will be serialized for a report request.

        Returns:    A response object containing the envelope and data extracted from the raw data.
        """
        tree = self._from_xml(data)
        return self._from_tree(tree, envelope_type, data_type, for_report)

    def deserialize_multi(
        self, data: bytes, envelope_type: Type[E], data_type: Type[P], for_report: bool = False
    ) -> MultiResponse[E, P]:
        """Deserialize the data to a multi-response object.

        Arguments:
        data (bytes):                   The raw data to be deserialized.
        envelope_type (Type[Envelope]): The type of envelope to be constructed.
        data_type (Type[Payload]):      The type of data to be constructed.
        for_report (bool):              If True, the data will be serialized for a report request.

        Returns:    A multi-response object containing the envelope and data extracted from the raw data.
        """
        tree = self._from_xml(data)
        return self._from_tree_multi(tree, envelope_type, data_type, for_report)

    def _to_canoncialized_xml(self, payload: PayloadBase) -> bytes:
        """Convert the payload to a canonicalized XML string.

        Arguments:
        payload (PayloadBase): The payload to be converted.

        Returns:    The canonicalized XML string.
        """
        # First, convert the payload to a raw XML string
        raw: bytes = payload.to_xml(
            skip_empty=True,
            encoding="utf-8",
            xml_declaration=False,
        )  # type: ignore[assignment]

        # Next, parse it back into an XML tree
        unparsed = parse(BytesIO(raw))

        # Finally, convert the XML tree to a canonicalized XML string and return it
        buffer = BytesIO()
        unparsed.write_c14n(buffer)
        buffer.seek(0)
        return buffer.read()

    def _from_tree(self, raw: Element, envelope_type: Type[E], data_type: Type[P], for_report: bool) -> Response[E, P]:
        """Convert the raw data to a response object.

        Arguments:
        raw (Element):                  The raw data to be converted.
        envelope_type (Type[Envelope]): The type of envelope to be constructed.
        data_type (Type[Payload]):      The type of data to be constructed.
        for_report (bool):              If True, the data will be serialized for a report request.

        Returns:    A response object containing the envelope and data extracted from the raw data.
        """
        # First, attempt to extract the response from the raw data; if the key isn't found then we'll raise an error.
        # Otherwise, we'll attempt to construct the response from the raw data.
        if self._payload_key != raw.tag:
            raise ValueError(f"Expected payload key '{self._payload_key}' not found in response")
        cls: Response[E, P] = _create_response_payload_type(  # type: ignore[assignment]
            self._payload_key,
            envelope_type,  # type: ignore[arg-type]
            data_type,  # type: ignore[arg-type]
            False,
        )
        resp = cls.from_xml_tree(raw)  # type: ignore[arg-type]

        # Next, attempt to extract the envelope and data from within the response
        resp.envelope, resp.envelope_validation, envelope_node = self._from_tree_envelope(
            raw, envelope_type, for_report
        )

        # Now, verify that the response doesn't contain an unexpected data type and then retrieve the payload data
        # from within the envelope
        self._verify_tree_data_tag(envelope_node, data_type)
        resp.payload = self._from_tree_data(envelope_node.find(get_tag(data_type)), data_type)

        # Finally, attempt to extract the messages from within the payload
        resp.messages = self._from_tree_messages(
            raw, get_tag(envelope_type), data_type, self._payload_key, False, for_report=for_report
        )

        # Return the response
        return resp

    def _from_tree_multi(
        self, raw: Element, envelope_type: Type[E], data_type: Type[P], for_report: bool
    ) -> MultiResponse[E, P]:
        """Convert the raw data to a multi-response object.

        Arguments:
        raw (Element):                  The raw data to be converted.
        envelope_type (Type[Envelope]): The type of envelope to be constructed.
        data_type (Type[Payload]):      The type of data to be constructed.
        for_report (bool):              If True, the data will be serialized for a report request.

        Returns:    A multi-response object containing the envelope and data extracted from the raw data.
        """
        # First, attempt to extract the response from the raw data; if the key isn't found then we'll raise an error.
        # Otherwise, we'll attempt to construct the response from the raw data.
        if self._payload_key != raw.tag:
            raise ValueError(f"Expected payload key '{self._payload_key}' not found in response")
        cls: MultiResponse[E, P] = _create_response_payload_type(  # type: ignore[assignment]
            self._payload_key,
            envelope_type,  # type: ignore[arg-type]
            data_type,  # type: ignore[arg-type]
            True,
        )
        resp = cls.from_xml_tree(raw)  # type: ignore[arg-type]

        # Next, attempt to extract the envelope from the response
        resp.envelope, resp.envelope_validation, env_node = self._from_tree_envelope(raw, envelope_type, for_report)

        # Now, verify that the response doesn't contain an unexpected data type and then retrieve the payload data
        # from within the envelope
        # NOTE: apparently, mypy doesn't know about setter-getter properties either...
        self._verify_tree_data_tag(env_node, data_type)
        resp.payload = [
            self._from_tree_data(item, data_type) for item in env_node.findall(get_tag(data_type))  # type: ignore[misc]
        ]

        # Finally, attempt to extract the messages from within the payload
        resp.messages = self._from_tree_messages(
            raw, get_tag(envelope_type), data_type, self._payload_key, True, for_report=for_report
        )

        # Return the response
        return resp

    def _from_tree_envelope(
        self, raw: Element, envelope_type: Type[E], for_report: bool
    ) -> Tuple[E, ResponseCommon, Element]:
        """Attempt to extract the envelope from within the response.

        Arguments:
        raw (Element):                  The raw data to be converted.
        envelope_type (Type[Envelope]): The type of envelope to be constructed.
        for_report (bool):              If True, the data will be serialized for a report request.

        Returns:
        Envelope:       The request payload constructed from the raw data.
        ResponseCommon: The validation information for the request payload.
        """
        # First, attempt to extract the envelope from within the response; if the key isn't found then we'll raise an
        # exception to indicate that the envelope wasn't found.
        envelope_tag = get_tag(envelope_type)
        envelope_node = raw if for_report else raw.find(envelope_tag)
        if envelope_node is None or envelope_node.tag != envelope_tag:
            raise ValueError(f"Expected envelope type '{envelope_tag}' not found in response")

        # Next, create a new envelope type that contains the envelope type with the appropriate XML tag. We have to do
        # this because the envelope type doesn't include the ResponseCommon fields, and the tag doesn't match
        # "ResponseCommon", so parsing will fail if we try to separate the envelope and common fields.
        common_cls = _create_response_common_type(envelope_type)  # type: ignore[arg-type]

        # Finally, parse and return the envelope data and validation information
        return (
            envelope_type.from_xml_tree(envelope_node),  # type: ignore[arg-type]
            common_cls.from_xml_tree(envelope_node),  # type: ignore[arg-type]
            envelope_node,
        )

    def _verify_tree_data_tag(self, raw: Element, data_type: Type[P]) -> None:
        """Verify that no types other than the expected data type are present in the response.

        Arguments:
        raw (Element):              The raw data to be converted.
        data_type (Type[Payload]):  The type of data to be constructed.

        Raises:
        ValueError:    If the expected data type is not found in the response.
        """
        data_tags = set(node.tag for node in raw)
        if not data_tags.issubset([data_type.__name__, data_type.__xml_tag__, "ProcessingStatistics", "Messages"]):
            raise ValueError(f"Expected data type '{data_type.__name__}' not found in response")

    def _from_tree_data(self, raw: Optional[Element], data_type: Type[P]) -> Optional[ResponseData[P]]:
        """Attempt to extract the data from within the payload.

        Arguments:
        raw (Element):                  The raw data to be converted.
        data_type (Type[BaseModel]):    The type of data to be constructed.

        Returns:
        BaseModel:      The data constructed from the raw data.
        ResponseCommon: The validation information for the data extracted from the response.
        """
        # First, verify that the data type is present in the response; if it isn't then we'll raise an exception to
        # indicate that the data wasn't found.
        if raw is None:
            return None

        # Next, create a new data type that contains the data type with the appropriate XML tag. We have to do this
        common_cls = _create_response_common_type(data_type)  # type: ignore[arg-type]

        # Finally, parse and return the data and validation information
        return ResponseData[P](
            data_type.from_xml_tree(raw),  # type: ignore[arg-type]
            common_cls.from_xml_tree(raw),  # type: ignore[arg-type]
        )

    def _from_tree_messages(
        self,
        raw: Element,
        envelope_tag: str,
        current_type: Type[P],
        root: str,
        multi: bool,
        wrapped: bool = False,
        for_report: bool = False,
    ) -> Dict[str, Messages]:
        """Attempt to extract the messages from within the payload.

        Note that this method is called recursively to handle nested payloads and data types. It does not iterate over
        the XML tree to determine the structure of the response; instead, it uses the type annotations to determine the
        structure of the response.

        Arguments:
        raw (Element):                  The raw data to be converted.
        envelope_tag (str):             The tag of the envelope being constructed.
        current_type (Type[Payload]):   The type of data being constructed.
        root (str):                     The root of the dictionary, used to create the key for the messages.
        multi (bool):                   Whether we're processing a list of nodes or a single node. If called with the
                                        payload root, this value will determine whether we're processing a multi-
                                        response or a single response.
        wrapped (bool):                 Whether or not this type is referenced from a wrapped field.
        for_report (bool):              If True, the data will be serialized for a report request.
        """
        # First, find the Messages node in the raw data
        message_node = raw.find("Messages")

        # Next, create our dictionary of messages and attempt to extract the messages from the raw data at the current
        # level of the response and set it to the root key
        messages = {}
        if message_node is not None:
            messages[root] = Messages.from_xml_tree(message_node)  # type: ignore[arg-type]

        # Next, we need to call this method recursively, depending on where we are in the response object. If we are
        # at the root of the response, we need to call this method for the envelope type. If we are at the envelope
        # type, we need to call this method for the data type. If we are at the data type, we need to call this method
        # for each field in the data type that is a Payload type.
        if root == self._payload_key and not for_report:
            messages.update(
                self._from_tree_messages(
                    _find_or_fail(raw, envelope_tag),
                    envelope_tag,
                    current_type,
                    f"{root}.{envelope_tag}",
                    multi,
                    False,
                )
            )
        elif root.endswith(envelope_tag) or wrapped:
            messages.update(
                self._from_tree_messages_inner(
                    raw, envelope_tag, current_type, root, get_tag(current_type), multi, False
                )
            )
        else:
            # Iterate over each field on the current type...
            for field in current_type.model_fields.values():

                # First, get the arguments and origin of the field's annotation. Occaisionally, we'll have an optional
                # list. In this case, we'll have to do get_args twice to traverse the type tree.
                arg, multi = _get_field_typing(field.annotation)  # type: ignore[arg-type]

                # Next, check if the annotation is a subclass of Payload or else if it's a collection of Payload. If
                # neither of these is the case, we can skip this field.
                # NOTE: All our fields are annotated so there's no need to check if they're not
                if not issubclass(arg, Payload):
                    continue

                # Finally, call this method recursively for the field and update the messages with the results
                # NOTE: All our fields are annotated as XmlEntityInfo, so they have the "path" and "location" attributes
                print(field)
                messages.update(
                    self._from_tree_messages_inner(
                        raw,
                        envelope_tag,
                        arg,
                        root,
                        field.path,  # type: ignore[attr-defined]
                        multi,
                        field.location == EntityLocation.WRAPPED,  # type: ignore[attr-defined]
                    )
                )

        # Finally, return our dictionary of messages
        return messages

    def _from_tree_messages_inner(
        self,
        raw: Element,
        envelope_tag: str,
        current_type: Type[P],
        root: str,
        tag: str,
        multi: bool,
        wrapped: bool,
    ) -> Dict[str, Messages]:
        """Attempt to extract the messages from within the payload at the current level.

        Arguments:
        raw (Element):                  The raw data to be converted.
        envelope_tag (str):             The tag of the envelope being constructed.
        current_type (Type[Payload]):   The type of data being constructed.
        root (str):                     The root of the dictionary, used to create the key for the messages.
        tag (str):                      The tag of the current node being processed.
        multi (bool):                   If True, the payload will be a multi-response; otherwise, it will be a single
                                        response.
        wrapped (bool):                 Whether or not this field is a wrapped field.

        Returns:    A dictionary mapping messages to where they were found in the response.
        """
        # Construct the new root from the existing root and the tag
        path_base = f"{root}.{tag}"

        # If we are processing a list, we need to iterate over each node and call this method recursively. Otherwise,
        # we can call this method recursively for the node and update the messages with the results.
        if multi:
            # Attempt to find all the nodes with the given tag; if we don't find any then we'll return empty.
            nodes = raw.findall(tag)
            if not nodes:
                return {}

            # Otherwise, we'll call this method recursively for each node and update the messages with the results.
            messages = {}
            for i, node in enumerate(nodes):
                messages.update(
                    self._from_tree_messages(
                        node, envelope_tag, current_type, path_base if wrapped else f"{path_base}[{i}]", True, wrapped
                    )
                )
            return messages

        # If we reached this point then we are processing a single item so find the associated
        child = raw.find(tag)
        return (
            {}
            if child is None
            else self._from_tree_messages(child, envelope_tag, current_type, path_base, False, wrapped)
        )

    def _from_xml(self, data: bytes) -> Element:
        """Parse the XML file, returning the resulting XML tree.

        Arguments:
        data:       The raw XML data to be parsed.

        Returns:    A parsed and validated XML tree containing the data.
        """
        # First, get a file-like reference to the data
        dat_file = BytesIO(data)

        # Next, parse the XML data into an XML element tree
        doc = parse(dat_file)

        # Now, verify that the XML data is valid according to the schema
        self._schema.assertValid(doc)

        # Finally, return the results
        return doc.getroot()


# Create the response payload type
PayloadType = Type[Union[Response[E, P], MultiResponse[E, P]]]


@lru_cache(maxsize=None)
def _create_response_payload_type(key: str, envelope_type: Type[E], data_type: Type[P], multi: bool) -> PayloadType:
    """Create a new payload type for the given envelope and data types.

    This method is intended to save us the overhead of writing a new class for each payload type. Instead, we can
    create a new class at runtime that contains the envelope and data types, and use that for deserialization.

    Note that this method has been LRU-cached because the operation of creating a new class from data types at
    runtime involves lots of reflection and is quite slow. By caching the results, we can avoid the overhead of
    creating new classes every time we need to deserialize data.

    Arguments:
    key (str):                      The tag to use for the parent element of the payload.
    envelope_type (Type[Envelope]): The type of envelope to be constructed.
    data_type (Type[Payload]):      The type of data to be constructed.
    multi (bool):                   If True, the payload will be a multi-response; otherwise, it will be a single
                                    response.

    Returns:    The base response type that will be used for deserialization.
    """
    # First, create our base response type depending on whether we are creating a multi-response or not
    base_type: PayloadType = Response[envelope_type, data_type]  # type: ignore[valid-type]
    if multi:
        base_type = MultiResponse[envelope_type, data_type]  # type: ignore[valid-type]

    # Next, create a new payload type that contains the envelope and data types with the appropriate XML tag
    class RSPayload(base_type, tag=key):  # type: ignore[call-arg, valid-type, misc]
        """Wrapper for the response payload type that will be used for serialization."""

    # Finally, return the payload type so we can instantiate it
    return RSPayload


@lru_cache(maxsize=None)
def _create_response_common_type(tag_type: Type[Union[E, P]]) -> Type[ResponseCommon]:
    """Create a new wrapper for the ResponseCommon type with the given tag.

    This method is intended to save us the overhead of writing a new class for each tag type. Instead, we can
    create a new class at runtime that contains the ResponseCommon type, and use that for deserialization.

    Arguments:
    tag_type (Type):    The type of tag to use for the wrapper.

    Returns:    The wrapper type that will be used for deserialization.
    """  # fmt: skip
    # First, create a new wrapper type that contains the ResponseCommon type with the appropriate XML tag
    class Wrapper(ResponseCommon, tag=get_tag(tag_type)):  # type: ignore[call-arg]
        """Wrapper for the validation object with the proper XML tag."""

    # Finally, return the wrapper type so we can instantiate it
    return Wrapper


@lru_cache(maxsize=None)
def _create_request_payload_type(
    key: str,
    envelope_type: Type[E],
    data_type: Type[P],
    multi: bool,
) -> Type[PayloadBase]:
    """Create a new payload type for the given payload and data types.

    This method is intended to save us the overhead of writing a new class for each payload type. Instead, we can
    create a new class at runtime that contains the payload and data types, and use that for serialization.

    Note that this method has been LRU-cached because the operation of creating a new class from data types at
    runtime involves lots of reflection and is quite slow. By caching the results, we can avoid the overhead of
    creating new classes every time we need to serialize data.

    Arguments:
    key: str                        The tag to use for the parent element of the payload.
    envelope_type (Type[Envelope]): The type of payload to be constructed.
    data_type (Type[Payload]):      The type of data to be constructed.
    multi (bool):                   If True, the payload will be a list; otherwise, it will be a singleton.

    Returns:    A new payload type that can be used for serialization.
    """  # fmt: skip
    # First, create our data type
    payload_type = List[data_type] if multi else data_type  # type: ignore[valid-type]

    # Next, create a wrapper for our data type that will be used to store the data in the payload
    class Envelope(envelope_type):  # type: ignore[valid-type, misc]
        """Wrapper for the data type that will be used to store the data in the payload."""

        # The data to be stored in the payload
        data: payload_type = element(tag=get_tag(data_type))  # type: ignore[valid-type, type-var]

        def __init__(self, envelope: envelope_type, data: payload_type):  # type: ignore[valid-type]
            """Create a new envelope to store payload data.

            Arguments:
            envelope (Envelope):    The payload to be stored in the data.
            data (Payload):         The data to be stored in the payload.
            """
            obj = dict(envelope)
            obj["data"] = data
            super().__init__(**obj)

    # Now, create our payload type that actually contains all the XML data
    class RQPayload(PayloadBase, tag=key):  # type: ignore[call-arg]
        """The payload type that will be used for serialization."""

        # The payload containing our request object and any data
        envelope: Envelope = element(tag=envelope_type.__name__)

        def __init__(self, envelope: envelope_type, data: payload_type, schema: str):  # type: ignore[valid-type]
            """Create a new payload containing the request object and any data.

            Arguments:
            envelope (Envelope):    The payload to be stored in the data.
            data (Payload):         The data to be stored in the payload.
            schema (str):           The name of the schema file to use for validation.
            """
            super().__init__(location=schema, envelope=Envelope(envelope, data))

    # Finally, return the payload type so we can instantiate it
    return RQPayload


@lru_cache(maxsize=None)
def _create_report_payload_type(key: str, envelope_type: Type[E], data_type: Type[P], multi: bool) -> Type[PayloadBase]:
    """Create a new payload type for the given report data request.

    Arguments:
    key: str                        The tag to use for the parent element of the payload.
    envelope_type (Type[Envelope]): The type of payload to be used for the envelope.
    data_type (Type[Payload]):      The type of payload to be used for the data.
    multi (bool):                   If True, the payload will be a list; otherwise, it will be a singleton.

    Returns:    The base payload type that will be used for serialization.
    """
    # First, create our data type
    payload_type = List[data_type] if multi else data_type  # type: ignore[valid-type]

    # Next, create a wrapper for our data type that will be used to store the data in the payload
    class Envelope(PayloadBase, envelope_type, tag=key):  # type: ignore[valid-type, misc]
        """Wrapper for the data type that will be used to store the data in the payload."""

        # The data to be stored in the payload
        data: payload_type = element(tag=get_tag(data_type))  # type: ignore[valid-type]

        def __init__(self, envelope: envelope_type, data: payload_type, schema: str):  # type: ignore[valid-type]
            """Create a new envelope to store payload data.

            Arguments:
            envelope (Envelope):    The payload to be stored in the data.
            data (Payload):         The data to be stored in the payload.
            schema (str):           The name of the schema file to use for validation.
            """
            obj = dict(envelope)
            obj["data"] = data
            obj["location"] = schema
            super().__init__(**obj)

    # Finally, return the payload type so we can instantiate it
    return Envelope


def _find_or_fail(node: Element, tag: str) -> Element:
    """Find the node with the given tag, or raise an error if it isn't found.

    Arguments:
    node (Element):     The node to search for the tag.
    tag (str):          The tag to search for in the node.

    Returns:    The node with the given tag.

    Raises:     ValueError if the tag isn't found in the node.
    """
    found = node.find(tag)
    if found is None:
        raise ValueError(f"Expected tag '{tag}' not found in node")  # pragma: no cover
    return found


def _get_field_typing(typ: Type) -> Tuple[Type, bool]:
    """Retrieve the field's actual type and whether or not the field is a collection.

    This method is designed to find the inner type of fields in the following cases:
    1. Fundamental types and classes (e.g. int, str, Award, Offer, etc.)
    2. Nullable fundamental types and classes
    3. Collections of fundamental types and classes
    4. Nullable collections of fundamental types and classes

    Arguments:
    typ (Type): The type of the field to retrieve the inner type for.

    Returns:
    Type:   The inner type of the field.
    bool:   Whether or not the field is a collection.
    """
    # First, check for the case where we have a fundamental type. If we do then we can return the type and False.
    init = get_args(typ)
    if len(init) == 0:
        return typ, False

    # Next, iterate over the type hierarchy and repeat the operation until we find the leaf type.
    args = [get_args(typ)]
    while len(args[-1]) > 1:
        temp = get_args(args[-1][0])
        if len(temp) == 0:
            break
        args.append(temp)

    # Now, find the origin type of the field. This will be the lowest type in the hierarchy that isn't a multi-type.
    # If there aren't any of these, then we'll just use the original type.
    origin_type = next(
        filter(lambda x: x is not None, map(lambda arg: arg[0] if len(arg) > 1 else None, reversed(args))), typ
    )

    # Finally, return the inner type and whether or not the origin type is a list
    return args[-1][0] if len(args) > 0 else typ, get_origin(origin_type) is list  # typing: ignore[return-value]


def get_tag(data_type: Union[Type[P], Type[E]]) -> str:
    """Get the tag for the given data type.

    Arguments:
    data_type (Type[Payload]):  The data type to get the tag for.

    Returns:    The tag for the given data type.
    """
    return data_type.__xml_tag__ or data_type.__name__
