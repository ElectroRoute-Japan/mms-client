"""Contains the client layer for communicating with the MMS server."""

from base64 import b64decode
from dataclasses import dataclass
from logging import getLogger
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Protocol
from typing import Tuple
from typing import Type
from typing import Union

from mms_client.security.crypto import Certificate
from mms_client.security.crypto import CryptoWrapper
from mms_client.types.base import BaseResponse
from mms_client.types.base import E
from mms_client.types.base import MultiResponse
from mms_client.types.base import P
from mms_client.types.base import Response
from mms_client.types.base import ResponseCommon
from mms_client.types.base import ValidationStatus
from mms_client.types.transport import Attachment
from mms_client.types.transport import MmsRequest
from mms_client.types.transport import MmsResponse
from mms_client.types.transport import RequestDataType
from mms_client.types.transport import RequestType
from mms_client.types.transport import ResponseDataType
from mms_client.utils.errors import AudienceError
from mms_client.utils.errors import MMSClientError
from mms_client.utils.errors import MMSServerError
from mms_client.utils.errors import MMSValidationError
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface
from mms_client.utils.web import Plugin
from mms_client.utils.web import ZWrapper

# Set the default logger for the MMS client
logger = getLogger(__name__)


@dataclass
class ServiceConfiguration:
    """Configuration for a service on the MMS server."""

    # The interface for the service
    interface: Interface

    # A serializer used to serialize and deserialize the data for the service
    serializer: Serializer


@dataclass
class EndpointConfiguration(Generic[E, P]):  # pylint: disable=too-many-instance-attributes
    """Configuration for an endpoint on the MMS server."""

    # The name of the endpoint
    name: str

    # The service for the endpoint
    service: ServiceConfiguration

    # The type of request to submit to the MMS server
    request_type: RequestType

    # The allowed client types for the endpoint
    allowed_clients: Optional[List[ClientType]] = None

    # The type of payload to expect in the response
    response_envelope_type: Optional[Type[E]] = None

    # The type of data to expect in the response
    response_data_type: Optional[Type[P]] = None

    # Whether the endpoint is for a report request
    for_report: bool = False

    # An optional serializer used to deserialize the response data for the service. This is only used for report
    # requests because they have a separate XSD file for responses.
    serializer: Optional[Serializer] = None


class ClientProto(Protocol):
    """Protocol for the MMS client, allowing for proper typing of the mixins."""

    @property
    def participant(self) -> str:
        """Return the MMS code of the business entity to which the requesting user belongs."""

    @property
    def user(self) -> str:
        """Return the user name of the person making the request."""

    @property
    def client_type(self) -> ClientType:
        """Return the type of client to use for making requests to the MMS server."""

    def verify_audience(self, config: EndpointConfiguration) -> None:
        """Verify that the client type is allowed.

        Some MMS endpoints are only accessible to certain client types. This method is used to verify that the client
        type is allowed to access the endpoint.

        Arguments:
        config (EndpointConfiguration): The configuration for the endpoint.

        Raises:
        ValueError: If the client type is not allowed.
        """

    def request_one(
        self,
        envelope: E,
        data: P,
        config: EndpointConfiguration,
    ) -> Tuple[Response[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the response.

        Arguments:
        envelope (Envelope):            The payload envelope to submit to the MMS server.
        data (Payload):                 The data to submit to the MMS server.
        config (EndpointConfiguration): The configuration for the endpoint.

        Returns:    The response from the MMS server.
        """

    def request_many(
        self,
        envelope: E,
        data: Union[P, List[P]],
        config: EndpointConfiguration,
    ) -> Tuple[MultiResponse[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the multi-response.

        Arguments:
        envelope (Envelope):            The payload envelope to submit to the MMS server.
        data (Payload):                 The data to submit to the MMS server.
        config (EndpointConfiguration): The configuration for the endpoint.

        Returns:    The multi-response from the MMS server.
        """


def mms_endpoint(**kwargs):
    """Create a decorator for an MMS endpoint.

    This decorator is used to mark a method as an MMS endpoint. It will add the endpoint configuration to the function
    and submit the request to the MMS server when the function is called. The response will be extracted and returned.
    Decorated functions will only be responsible for creating the payload envelope to submit to the MMS server.

    Arguments:
    name (str):                         The name of the endpoint.
    service (ServiceConfiguration):     The configuration for the service.
    request_type (RequestType):         The type of request to submit to the MMS server.
    allowed_clients (List[ClientType]): The types of clients that are allowed to access the endpoint. If this is not
                                        provided, then any client will be allowed.
    response_envelope_type (Type[E]):   The type of payload to expect in the response. If this is not provided, then the
                                        response envelope will be assumed to have the same type as the request envelope.
    response_data_type (Type[P]):       The type of data to expect in the response. If this is not provided, then the
                                        response data will be assumed to have the same type as the request data.
    for_report (bool):                  If True, the endpoint is for a report request.
    serializer (Serializer):            The serializer to use for responses from the endpoint. Overrides the default
                                        serializer for the service.
    """
    # First, create the endpoint configuration from the given parameters
    config = EndpointConfiguration(**kwargs)

    # Next, create a decorator that will add the endpoint configuration to the function
    def decorator(func):
        def wrapper(self: ClientProto, *args, **kwargs) -> Optional[P]:
            logger.info(f"{config.name}: Called with args: {args[1:]}...")

            # First, verify that the client type is allowed
            self.verify_audience(config)

            # Next, call the wrapped function to get the envelope
            result = func(self, *args, **kwargs)
            if isinstance(result, tuple):
                envelope, callback = result
            else:
                envelope, callback = result, None

            # Now, submit the request to the MMS server and get the response
            resp, attachments = self.request_one(envelope, args[0], config)

            # Call the callback function if it was provided
            if callback:
                callback(resp, attachments)

            # Finally, extract the data from the response and return it
            logger.info(f"{config.name}: Returning {type(resp.data).__name__} data.")
            return resp.data

        return wrapper

    # Finally, return the decorator
    return decorator


def mms_multi_endpoint(**kwargs):
    """Create a decorator for an MMS multi-response endpoint.

    This decorator is used to mark a method as an MMS multi-response endpoint. It will add the endpoint configuration to
    the function and submit the request to the MMS server when the function is called. The multi-response will be
    extracted and returned. Decorated functions will only be responsible for creating the payload envelope to submit to
    the MMS server.

    Arguments:
    name (str):                         The name of the endpoint.
    service (ServiceConfiguration):     The configuration for the service.
    request_type (RequestType):         The type of request to submit to the MMS server.
    allowed_clients (List[ClientType]): The types of clients that are allowed to access the endpoint. If this is not
                                        provided, then any client will be allowed.
    response_envelope_type (Type[E]):   The type of payload to expect in the response. If this is not provided, then
                                        the response envelope will be assumed to have the same type as the request
                                        envelope.
    response_data_type (Type[P]):       The type of data to expect in the response. If this is not provided, then the
                                        response data will be assumed to have the same type as the request data. Note,
                                        that this is not intended to account for the expected sequence type of the
                                        response data. That is already handled in the wrapped function, so this should
                                        only be set if the inner data type being returned differs from what was sent.
    for_report (bool):                  If True, the endpoint is for a report request.
    serializer (Serializer):            The serializer to use for responses from the endpoint. Overrides the default
                                        serializer for the service.
    """
    # First, create the endpoint configuration from the given parameters
    config = EndpointConfiguration(**kwargs)

    # Next, create a decorator that will add the endpoint configuration to the function
    def decorator(func):
        def wrapper(self: ClientProto, *args, **kwargs) -> List[P]:
            logger.info(f"{config.name}: Called with args: {args[1:]}...")

            # First, verify that the client type is allowed
            self.verify_audience(config)

            # Next, call the wrapped function to get the envelope
            result = func(self, *args, **kwargs)
            if isinstance(result, tuple):
                envelope, callback = result  # pragma: no cover
            else:
                envelope, callback = result, None

            # Now, submit the request to the MMS server and get the response
            resp, attachments = self.request_many(envelope, args[0], config)

            # Call the callback function if it was provided
            if callback:
                callback(resp, attachments)  # pragma: no cover

            # Finally, extract the data from the response and return it
            logger.info(f"{config.name}: Returning {len(resp.data)} item(s).")
            return resp.data

        return wrapper

    # Finally, return the decorator
    return decorator


class BaseClient:  # pylint: disable=too-many-instance-attributes
    """Base end-client for the MMS server.

    This class is used to communicate with the MMS server.
    """

    def __init__(
        self,
        domain: str,
        participant: str,
        user: str,
        client_type: ClientType,
        cert: Certificate,
        plugins: Optional[List[Plugin]] = None,
        is_admin: bool = False,
        test: bool = False,
    ):
        """Create a new MMS client with the given participant, user, client type, and authentication.

        Arguments:
        domain (str):               The domain to use when signing the content ID to MTOM attachments.
        participant (str):          The MMS code of the business entity to which the requesting user belongs.
        user (str):                 The user name of the person making the request.
        client_type (ClientType):   The type of client to use for making requests to the MMS server.
        cert (Certificate):         The certificate to use for signing requests.
        plugins (List[Plugin]):     A list of plugins to add to the Zeep client. This can be useful for auditing or
                                    other purposes.
        is_admin (bool):            Whether the user is an admin (i.e. is a market operator).
        test (bool):                Whether to use the test server.
        """
        # First, save the base field associated with the client
        self._domain = domain
        self._participant = participant
        self._user = user
        self._client_type = client_type
        self._is_admin = is_admin
        self._test = test

        # Next, save the security-related fields associated with the client
        self._cert = cert
        self._signer = CryptoWrapper(cert)

        # Now, set the plugins we'll inject into the Zeep client
        self._plugins = plugins or []

        # Finally, create a list of wrappers for the different interfaces
        self._wrappers: Dict[Interface, ZWrapper] = {}

    @property
    def participant(self) -> str:
        """Return the MMS code of the business entity to which the requesting user belongs."""
        return self._participant

    @property
    def user(self) -> str:
        """Return the user name of the person making the request."""
        return self._user

    @property
    def client_type(self) -> ClientType:
        """Return the type of client to use for making requests to the MMS server."""
        return self._client_type

    def verify_audience(self, config: EndpointConfiguration) -> None:
        """Verify that the client type is allowed.

        Some MMS endpoints are only accessible to certain client types. This method is used to verify that the client
        type is allowed to access the endpoint.

        Arguments:
        config (EndpointConfiguration): The configuration for the endpoint.

        Raises:
        ValueError: If the client type is not allowed.
        """
        logger.debug(
            f"{config.name}: Verifying audience. Allowed clients: "
            f"{config.allowed_clients if config.allowed_clients else 'Any'}."
        )
        if config.allowed_clients and (self._client_type not in config.allowed_clients):
            raise AudienceError(config.name, config.allowed_clients, self._client_type)

    def request_one(
        self,
        envelope: E,
        payload: P,
        config: EndpointConfiguration[E, P],
    ) -> Tuple[Response[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the response.

        Arguments:
        envelope (Envelope):            The payload envelope to submit to the MMS server.
        payload (Payload):              The data to submit to the MMS server.
        config (EndpointConfiguration): The configuration for the endpoint.

        Returns:    The response from the MMS server.
        """
        # Create a new ZWrapper for the given service
        wrapper = self._get_wrapper(config.service)

        # First, create the MMS request from the payload and data.
        logger.debug(
            f"{config.name}: Starting request. Envelope: {type(envelope).__name__}, Data: {type(payload).__name__}",
        )
        request = self._to_mms_request(
            wrapper,
            config.name,
            config.request_type,
            config.service.serializer.serialize(envelope, payload, config.for_report),
        )

        # Next, submit the request to the MMS server and get and verify the response.
        resp = wrapper.submit(request)
        self._verify_mms_response(resp, config)

        # Now, extract the attachments from the response
        attachments = {a.name: b64decode(a.data) for a in resp.attachments}

        # Finally, deserialize and verify the response
        envelope_type = config.response_envelope_type or type(envelope)
        data_type = config.response_data_type or type(payload)
        deserializer = config.serializer or config.service.serializer
        data: Response[E, P] = deserializer.deserialize(resp.payload, envelope_type, data_type, config.for_report)
        self._verify_response(data, config)

        # Return the response data and any attachments
        logger.debug(
            f"{config.name}: Returning response. Envelope: {envelope_type.__name__}, Data: {data_type.__name__}",
        )
        return data, attachments

    def request_many(
        self,
        envelope: E,
        payload: Union[P, List[P]],
        config: EndpointConfiguration[E, P],
    ) -> Tuple[MultiResponse[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the multi-response.

        Arguments:
        envelope (Envelope):            The payload envelope to submit to the MMS server.
        payload (Payload):              The data to submit to the MMS server.
        config (EndpointConfiguration): The configuration for the endpoint.

        Returns:    The multi-response from the MMS server.
        """
        # Create a new ZWrapper for the given service
        wrapper = self._get_wrapper(config.service)

        # First, create the MMS request from the payload and data.
        is_list = isinstance(payload, list)
        data_type = type(payload[0]) if is_list else type(payload)  # type: ignore[index]
        logger.debug(
            (
                f"{config.name}: Starting multi-request. Envelope: {type(envelope).__name__}, "
                f"Data: {data_type.__name__}"
            ),
        )
        serialized = (
            config.service.serializer.serialize_multi(
                envelope, payload, data_type, config.for_report  # type: ignore[arg-type]
            )
            if is_list
            else config.service.serializer.serialize(envelope, payload, config.for_report)  # type: ignore[type-var]
        )
        request = self._to_mms_request(wrapper, config.name, config.request_type, serialized)

        # Next, submit the request to the MMS server and get and verify the response.
        resp = wrapper.submit(request)
        self._verify_mms_response(resp, config)

        # Now, extract the attachments from the response
        attachments = {a.name: b64decode(a.data) for a in resp.attachments}

        # Finally, deserialize and verify the response
        envelope_type = config.response_envelope_type or type(envelope)
        data_type = config.response_data_type or data_type
        deserializer = config.serializer or config.service.serializer
        data: MultiResponse[E, P] = deserializer.deserialize_multi(
            resp.payload,
            envelope_type,
            data_type,  # type: ignore[arg-type]
            config.for_report,
        )
        self._verify_multi_response(data, config)

        # Return the response data and any attachments
        logger.debug(
            f"{config.name}: Returning multi-response. Envelope: {envelope_type.__name__}, Data: {data_type.__name__}",
        )
        return data, attachments

    def _to_mms_request(
        self,
        client: ZWrapper,
        operation: str,
        req_type: RequestType,
        data: bytes,
        return_req: bool = False,
        attachments: Optional[Dict[str, bytes]] = None,
    ) -> MmsRequest:
        """Convert the given data to an MMS request.

        Arguments:
        client (ZWrapper):              The Zeep client to use for submitting the request.
        operation (str):                The name of the MMS function being called.
        req_type (RequestType):         The type of request to submit to the MMS server.
        data (bytes):                   The data to submit to the MMS server.
        return_req (bool):              Whether to return the request data in the response. This is False by default.
        attachments (Dict[str, bytes]): The attachments to send with the request.

        Arguments:    The MMS request to submit to the MMS server.
        """
        # First, convert the attachments to the correct the MMS format
        attachment_data = (
            [self._to_mms_attachment(client, operation, name, data) for name, data in attachments.items()]
            if attachments
            else []
        )

        # Next, convert the payload to a base-64 string
        tag, signature = self._register_and_sign(client, operation, "payload", data)

        # Embed the data and the attachments in the MMS request and return it
        logger.debug(
            f"Creating MMS request of type {req_type.name} to send {len(data)} bytes of data and "
            f"{len(attachment_data)} attachments."
        )
        return MmsRequest(
            requestType=req_type,
            adminRole=self._is_admin,
            requestDataType=RequestDataType.XML,
            sendRequestDataOnSuccess=return_req,
            requestSignature=signature,
            requestData=tag,
            attachmentData=attachment_data,
        )

    def _to_mms_attachment(
        self, client: ZWrapper, operation: str, name: str, data: bytes
    ) -> Attachment:  # pragma: no cover
        """Convert the given data to an MMS attachment.

        Arguments:
        client (ZWrapper):  The Zeep client to use for submitting the request.
        operation (str):    The name of the operation.
        name (str):         The name of the attachment.
        data (bytes):       The data to be attached.

        Returns:    The MMS attachment.
        """
        # Convert the data to a base-64 string
        tag, signature = self._register_and_sign(client, operation, name, data)

        # Create the MMS attachment and return it
        return Attachment(signature=signature, name=name, binaryData=tag)

    def _register_and_sign(self, client: ZWrapper, operation: str, name: str, data: bytes) -> Tuple[str, str]:
        """Register an attachment and sign the data.

        Arguments:
        client (ZWrapper):  The Zeep client to use for submitting the request.
        operation (str):    The name of the operation.
        name (str):         The name of the attachment.
        data (bytes):       The data to be attached.

        Returns:    The content ID of the attachment, which should be used in place of the attachment data.
        """
        # First, register the attachment
        tag = client.register_attachment(operation, name, data)

        # Next, sign the data
        signature = self._signer.sign(data)

        # Finally, convert the encoded data to a string and return it and the signature
        return tag, signature.decode("UTF-8")

    def _verify_mms_response(self, resp: MmsResponse, config: EndpointConfiguration) -> None:
        """Verify that the given MMS response is valid.

        Arguments:
        resp (MmsResponse):     The MMS response to verify.

        Raises:
        MMSClientError: If the response is not valid.
        """
        # Verify that the response is in the correct format. If it's not, raise an error.
        # NOTE: We're disabling the no-else-raise rule here because both comparisons are on the same enum so if one is
        # removed then the other will raise an error. This is a false positive.
        if resp.data_type == ResponseDataType.TXT:  # pylint: disable=no-else-raise
            raise MMSServerError(config.name, resp.payload.decode("UTF-8"))
        elif resp.data_type != ResponseDataType.XML:
            raise MMSClientError(
                config.name,
                f"Invalid MMS response data type: {resp.data_type.name}. Only XML is supported.",
            )
        if resp.compressed:
            raise MMSClientError(config.name, "Invalid MMS response. Compressed responses are not supported.")

        # Check the response status flags and log any warnings or errors
        if resp.warnings:
            logger.warning(f"{config.name}: MMS response contained warnings.")
        if not resp.success:
            logger.error(f"{config.name}: MMS response was unsuccessful.")

    def _verify_response(self, resp: Response[E, P], config: EndpointConfiguration) -> None:
        """Verify that the given response is valid.

        Arguments:
        resp (Response):    The response to verify.

        Raises:
        MMSValidationError: If the response is not valid.
        """
        # First, verify the base response data to make sure we haven't missed some request details
        valid = self._verify_base_response(resp, config)

        # Next, if we received data back with the request then verify that it's valid
        if resp.payload:
            valid = valid and self._verify_response_common(config, type(resp.data), resp.payload.data_validation)

        # Now, log any messages that were returned with the response
        self._verify_messages(config, resp)

        # Finally, if the response is not valid, raise an error
        if not valid:
            raise MMSValidationError(config.name, resp.envelope, resp.data, resp.messages)

    def _verify_multi_response(self, resp: MultiResponse[E, P], config: EndpointConfiguration) -> None:
        """Verify that the given multi-response is valid.

        Arguments:
        resp (MultiResponse):   The multi-response to verify.

        Raises:
        MMSValidationError: If the response is not valid.
        """
        # First, verify the base response data to make sure we haven't missed some request details
        valid = self._verify_base_response(resp, config)

        # Next, if we received data back with the request then verify that it's valid
        if resp.payload:
            valid = valid and all(
                self._verify_response_common(config, type(data), resp.payload[i].data_validation, i)
                for i, data in enumerate(resp.data)
            )

        # Now, log any messages that were returned with the response
        self._verify_messages(config, resp)

        # Finally, if the response is not valid, raise an error
        if not valid:
            raise MMSValidationError(config.name, resp.envelope, resp.data, resp.messages)

    def _verify_base_response(self, resp: BaseResponse[E], config: EndpointConfiguration) -> bool:
        """Verify that the given base response is valid.

        Arguments:
        resp (BaseResponse):            The base response to verify.
        config (EndpointConfiguration): The configuration for the endpoint.

        Returns:    True to indicate that the response is valid, False otherwise.
        """
        # Log the request's processing statistics
        if resp.statistics is not None:
            logger.info(
                f"{config.name} ({resp.statistics.timestamp_xml}): Recieved {resp.statistics.received}, "
                f"Valid: {resp.statistics.valid}, Invalid: {resp.statistics.invalid}, "
                f"Successful: {resp.statistics.successful}, Unsuccessful: {resp.statistics.unsuccessful} "
                f"in {resp.statistics.time_ms}ms"
            )

        # Check if the response is invalid and if the envelope had any validation issues. If not, then we have a
        # valid base response so return True. Otherwise, return False.
        is_invalid = resp.statistics is not None and resp.statistics.invalid
        return not is_invalid and self._verify_response_common(config, type(resp.envelope), resp.envelope_validation)

    def _verify_messages(self, config: EndpointConfiguration, resp: BaseResponse[E]) -> None:
        """Verify the messages in the given response.

        Arguments:
        config (EndpointConfiguration): The configuration for the endpoint.
        resp (BaseResponse):            The response to verify.
        """
        for path, messages in resp.messages.items():
            for info in messages.information:  # type: ignore[union-attr]
                logger.info(f"{config.name} - {path}: {info}")
            for warning in messages.warnings:  # type: ignore[union-attr]
                logger.warning(f"{config.name} - {path}: {warning}")
            for error in messages.errors:  # type: ignore[union-attr]
                logger.error(f"{config.name} - {path}: {error}")

    def _verify_response_common(
        self, config: EndpointConfiguration, payload_type: type, resp: ResponseCommon, index: Optional[int] = None
    ) -> bool:
        """Verify the common response data in the given response.

        Arguments:
        config (EndpointConfiguration): The configuration for the endpoint.
        payload_type (type):            The type of payload that was sent with the request.
        resp (ResponseCommon):          The common response data to verify.
        index (int):                    The index of the response in the multi-response. This is None for single
                                        responses.

        Returns:    True to indicate that the response is valid, False otherwise.
        """
        # Log the status of the response validation
        logger.info(
            f"{config.name}: {payload_type.__name__}{f'[{index}]' if index is not None else ''} was valid? "
            f"{resp.success} ({resp.validation.value})",
        )

        # Verify that the response was successful and that the validation status is not a failed status
        return resp.success and (resp.validation not in (ValidationStatus.FAILED, ValidationStatus.PASSED_PARTIAL))

    def _get_wrapper(self, service: ServiceConfiguration) -> ZWrapper:
        """Get the wrapper for the given service.

        Arguments:
        service (ServiceConfiguration):  The service for which to get the wrapper.
        """
        if service.interface not in self._wrappers:
            logger.debug(f"Creating wrapper for {service.interface.name} interface.")
            self._wrappers[service.interface] = ZWrapper(
                self._domain,
                self._client_type,
                service.interface,
                self._cert.to_adapter(),
                self._plugins,
                True,
                self._test,
            )
        return self._wrappers[service.interface]
