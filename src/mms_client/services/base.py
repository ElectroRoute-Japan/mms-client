"""Contains the client layer for communicating with the MMS server."""

from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Protocol
from typing import Tuple
from typing import Type

from mms_client.security.crypto import Certificate
from mms_client.security.crypto import CryptoWrapper
from mms_client.types.base import E
from mms_client.types.base import MultiResponse
from mms_client.types.base import P
from mms_client.types.base import Response
from mms_client.types.transport import Attachment
from mms_client.types.transport import MmsRequest
from mms_client.types.transport import RequestDataType
from mms_client.types.transport import RequestType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface
from mms_client.utils.web import ZWrapper


@dataclass
class ServiceConfiguration:
    """Configuration for a service on the MMS server."""

    # The interface for the service
    interface: Interface

    # A serializer used to serialize and deserialize the data for the service
    serializer: Serializer


class ClientProto(Protocol):
    """Protocol for the MMS client, allowing for proper typing of the mixins."""

    def participant(self) -> str:
        """Return the MMS code of the business entity to which the requesting user belongs."""

    def user(self) -> str:
        """Return the user name of the person making the request."""

    def verify_audience(self, allowed: Optional[ClientType] = None) -> None:
        """Verify that the client type is allowed.

        Some MMS endpoints are only accessible to certain client types. This method is used to verify that the client
        type is allowed to access the endpoint.

        Arguments:
        allowed (Optional[ClientType]): The allowed client type. If not provided, any client type is allowed.

        Raises:
        ValueError: If the client type is not allowed.
        """

    def request_one(
        self,
        envelope: E,
        data: P,
        service: ServiceConfiguration,
        req_type: RequestType,
        resp_envelope_type: Optional[Type[E]] = None,
        resp_data_type: Optional[Type[P]] = None,
    ) -> Tuple[Response[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the response.

        Arguments:
        envelope (Envelope):            The payload envelope to submit to the MMS server.
        data (Payload):                 The data to submit to the MMS server.
        service (ServiceConfiguration): The service for which to submit the request.
        req_type (RequestType):         The type of request to submit to the MMS server.
        resp_envelope_type (type):      The type of payload to expect in the response. If not provided, the type of the
                                        payload will be used.
        resp_data_type (type):          The type of data to expect in the response. If not provided, the type of the
                                        request data will be used.

        Returns:    The response from the MMS server.
        """

    def request_many(
        self,
        envelope: E,
        data: P,
        service: ServiceConfiguration,
        req_type: RequestType,
        resp_envelope_type: Optional[Type[E]] = None,
        resp_data_type: Optional[Type[P]] = None,
    ) -> Tuple[MultiResponse[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the multi-response.

        Arguments:
        envelope (Envelope):            The payload envelope to submit to the MMS server.
        data (Payload):                 The data to submit to the MMS server.
        service (ServiceConfiguration): The service for which to submit the request.
        req_type (RequestType):         The type of request to submit to the MMS server.
        resp_envelope_type (type):      The type of payload to expect in the response. If not provided, the type of the
                                        payload will be used.
        resp_data_type (type):          The type of data to expect in the response. If not provided, the type of the
                                        request data will be used.

        Returns:    The multi-response from the MMS server.
        """


class BaseClient:  # pylint: disable=too-many-instance-attributes
    """Base end-client for the MMS server.

    This class is used to communicate with the MMS server.
    """

    def __init__(
        self,
        participant: str,
        user: str,
        client_type: ClientType,
        cert: Certificate,
        is_admin: bool = False,
        test: bool = False,
    ):
        """Create a new MMS client with the given participant, user, client type, and authentication.

        Arguments:
        participant (str):          The MMS code of the business entity to which the requesting user belongs.
        user (str):                 The user name of the person making the request.
        client_type (ClientType):   The type of client to use for making requests to the MMS server.
        cert (Certificate):         The certificate to use for signing requests.
        is_admin (bool):            Whether the user is an admin (i.e. is a market operator).
        test (bool):                Whether to use the test server.
        """
        # Save the base field associated with the client
        self._participant = participant
        self._user = user
        self._client_type = client_type
        self._is_admin = is_admin
        self._test = test

        # Save the security-related fields associated with the client
        self._cert = cert
        self._signer = CryptoWrapper(cert)

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

    def verify_audience(self, allowed: Optional[ClientType] = None) -> None:
        """Verify that the client type is allowed.

        Some MMS endpoints are only accessible to certain client types. This method is used to verify that the client
        type is allowed to access the endpoint.

        Arguments:
        allowed (Optional[ClientType]):  The allowed client type. If not provided, any client type is allowed.

        Raises:
        ValueError: If the client type is not allowed.
        """
        if allowed and self._client_type != allowed:
            raise ValueError(
                f"Invalid client type, '{self._client_type.name}' provided. Only '{allowed.name}' is supported.",
            )

    def request_one(
        self,
        envelope: E,
        data: P,
        service: ServiceConfiguration,
        req_type: RequestType,
        resp_envelope_type: Optional[Type[E]] = None,
        resp_data_type: Optional[Type[P]] = None,
    ) -> Tuple[Response[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the response.

        Arguments:
        envelope (Envelope):            The payload envelope to submit to the MMS server.
        data (Payload):                 The data to submit to the MMS server.
        service (ServiceConfiguration): The service for which to submit the request.
        req_type (RequestType):         The type of request to submit to the MMS server.
        resp_envelope_type (type):      The type of payload to expect in the response. If not provided, the type of the
                                        payload will be used.
        resp_data_type (type):          The type of data to expect in the response. If not provided, the type of the
                                        request data will be used.

        Returns:    The response from the MMS server.
        """
        # First, create the MMS request from the payload and data.
        request = self._to_mms_request(req_type, service.serializer.serialize(envelope, data))

        # Next, submit the request to the MMS server and get the response.
        resp = self._get_wrapper(service).submit(request)

        # Now, extract the attachments from the response
        attachments = {a.name: a.data for a in resp.attachments}

        # Finally, deserialize the response and return it.
        return (
            service.serializer.deserialize(
                resp.payload, resp_envelope_type or type(envelope), resp_data_type or type(data)
            ),
            attachments,
        )

    def request_many(
        self,
        envelope: E,
        data: P,
        service: ServiceConfiguration,
        req_type: RequestType,
        resp_envelope_type: Optional[Type[E]] = None,
        resp_data_type: Optional[Type[P]] = None,
    ) -> Tuple[MultiResponse[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the multi-response.

        Arguments:
        envelope (Envelope):            The payload envelope to submit to the MMS server.
        data (Payload):                 The data to submit to the MMS server.
        service (ServiceConfiguration): The service for which to submit the request.
        req_type (RequestType):         The type of request to submit to the MMS server.
        resp_envelope_type (type):      The type of payload to expect in the response. If not provided, the type of the
                                        payload will be used.
        resp_data_type (type):          The type of data to expect in the response. If not provided, the type of the
                                        request data will be used.

        Returns:    The multi-response from the MMS server.
        """
        # First, create the MMS request from the payload and data.
        request = self._to_mms_request(req_type, service.serializer.serialize(envelope, data))

        # Next, submit the request to the MMS server and get the response.
        resp = self._get_wrapper(service).submit(request)

        # Now, extract the attachments from the response
        attachments = {a.name: a.data for a in resp.attachments}

        # Finally, deserialize the response and return it.
        return (
            service.serializer.deserialize_multi(
                resp.payload, resp_envelope_type or type(envelope), resp_data_type or type(data)
            ),
            attachments,
        )

    def _to_mms_request(
        self,
        req_type: RequestType,
        data: bytes,
        return_req: bool = False,
        attachments: Optional[Dict[str, bytes]] = None,
    ) -> MmsRequest:
        """Convert the given data to an MMS request.

        Arguments:
        req_type (RequestType):         The type of request to submit to the MMS server.
        data (bytes):                   The data to submit to the MMS server.
        return_req (bool):              Whether to return the request data in the response. This is False by default.
        attachments (Dict[str, bytes]): The attachments to send with the request.

        Arguments:    The MMS request to submit to the MMS server.
        """
        # Convert the attachments to the correct the MMS format
        attachment_data = (
            [Attachment(signature=self._signer.sign(data), name=name, data=data) for name, data in attachments.items()]
            if attachments
            else []
        )

        # Embed the data and the attachments in the MMS request and return it
        return MmsRequest(
            requestType=req_type,
            adminRole=self._is_admin,
            requestDataType=RequestDataType.XML,
            sendRequestDataOnSuccess=return_req,
            requestSignature=self._signer.sign(data),
            requestData=data,
            attachmentData=attachment_data,
        )

    def _get_wrapper(self, service: ServiceConfiguration) -> ZWrapper:
        """Get the wrapper for the given service.

        Arguments:
        service (ServiceConfiguration):  The service for which to get the wrapper.
        """
        if service.interface not in self._wrappers:
            self._wrappers[service.interface] = ZWrapper(
                self._client_type, service.interface, self._cert.to_adapter(), True, self._test
            )
        return self._wrappers[service.interface]
