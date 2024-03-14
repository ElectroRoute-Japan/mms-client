"""Contains the client layer for making registration requests to the MMS server."""

from mms_client.security.certs import Certificate
from mms_client.security.crypto import CryptoWrapper
from mms_client.services.base import BaseClient
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface
from mms_client.utils.web import ZWrapper


class RegistrationClient:
    """Registration client for the MMS server."""

    def __init__(
        self,
        participant: str,
        user: str,
        client_type: ClientType,
        cert: Certificate,
        is_admin: bool = False,
        test: bool = False,
    ):
        """Create a new MMS registration client with the given participant, user, client type, and authentication.

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

        # First, create a new Zeep wrapper for the given client type and certificate
        wrapper = ZWrapper(client_type, Interface.MI, cert.to_adapter(), True, test)

        # Next, create a new signer for the given certificate
        signer = CryptoWrapper(cert)

        # Now, create a new serializer for the registration schema
        serializer = Serializer(SchemaType.REGISTRATION, "RegistrationData")

        # Finally, create the MMS client
        self._client = BaseClient(client_type, wrapper, signer, serializer, is_admin)
