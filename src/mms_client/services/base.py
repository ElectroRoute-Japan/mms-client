"""Contains the client layer for communicating with the MMS server."""

from typing import Dict
from typing import Optional
from typing import Tuple

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
from mms_client.utils.web import ZWrapper


class BaseClient:  # pylint: disable=too-many-instance-attributes
    """Base end-client for the MMS server.

    This class is used to communicate with the MMS server.
    """

    def __init__(
        self,
        client_type: ClientType,
        wrapper: ZWrapper,
        signer: CryptoWrapper,
        serializer: Serializer,
        is_admin: bool = False,
    ):
        """Create a new MMS client with the given participant, user, client type, and authentication.

        Arguments:
        client_type (ClientType):       The type of client to use for making requests to the MMS server.
        wrapper (ZWrapper):             The Zeep client to use for making requests to the MMS server.
        signer (CryptoWrapper):         The signer to use for signing requests.
        serializer (Serializer):        The serializer to use for the requests and responses.
        is_admin (bool):                Whether the user is an admin (i.e. is a market operator).
        """
        self._client_type = client_type
        self._is_admin = is_admin
        self._signer = signer
        self._serializer = serializer
        self._wrapper = wrapper

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
        req_type: RequestType,
        resp_envelope_type: Optional[type] = None,
    ) -> Tuple[Response[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the response.

        Arguments:
        envelope (E):               The payload envelope to submit to the MMS server.
        data (P):                   The data to submit to the MMS server.
        req_type (RequestType):     The type of request to submit to the MMS server.
        resp_envelope_type (type):  The type of payload to expect in the response. If not provided, the type of the
                                    payload will be used.

        Returns:    The response from the MMS server.
        """
        # First, create the MMS request from the payload and data.
        request = self._to_mms_request(req_type, self._serializer.serialize(envelope, data))

        # Next, submit the request to the MMS server and get the response.
        resp = self._wrapper.submit(request)

        # Now, extract the attachments from the response
        attachments = {a.name: a.data for a in resp.attachments}

        # Finally, deserialize the response and return it.
        return self._serializer.deserialize(resp.payload, resp_envelope_type or type(envelope), type(data)), attachments

    def request_many(
        self,
        envelope: E,
        data: P,
        req_type: RequestType,
        resp_envelope_type: Optional[type] = None,
    ) -> Tuple[MultiResponse[E, P], Dict[str, bytes]]:
        """Submit a request to the MMS server and return the multi-response.

        Arguments:
        envelope (PQ):              The payload envelope to submit to the MMS server.
        data (D):                   The data to submit to the MMS server.
        req_type (RequestType):     The type of request to submit to the MMS server.
        resp_envelope_type (type):  The type of payload to expect in the response. If not provided, the type of the
                                    payload will be used.

        Returns:    The multi-response from the MMS server.
        """
        # First, create the MMS request from the payload and data.
        request = self._to_mms_request(req_type, self._serializer.serialize(envelope, data))

        # Next, submit the request to the MMS server and get the response.
        resp = self._wrapper.submit(request)

        # Now, extract the attachments from the response
        attachments = {a.name: a.data for a in resp.attachments}

        # Finally, deserialize the response and return it.
        return (
            self._serializer.deserialize_multi(resp.payload, resp_envelope_type or type(envelope), type(data)),
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
