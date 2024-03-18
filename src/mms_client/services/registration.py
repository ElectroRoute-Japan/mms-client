"""Contains the client layer for making registration requests to the MMS server."""

from mms_client.services.base import ServiceConfiguration
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import Interface


class RegistrationClientMixin:  # pylint: disable=unused-argument
    """Registration client for the MMS server."""

    # The configuration for the registration service
    config = ServiceConfiguration(Interface.MI, Serializer(SchemaType.REGISTRATION, "RegistrationData"))
