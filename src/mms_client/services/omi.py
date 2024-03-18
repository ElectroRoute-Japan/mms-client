"""Contains the client layer for making OMI requests to the MMS server."""

from mms_client.services.base import ServiceConfiguration
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import Interface


class OMIClientMixin:
    """OMI client for the MMS server."""

    # The configuration for the OMI service
    config = ServiceConfiguration(Interface.OMI, Serializer(SchemaType.OMI, "MarketData"))
