"""Contains the client layer for making report requests to the MMS server."""

from mms_client.services.base import ServiceConfiguration
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import Interface


class ReportClientMixin:
    """Report client for the MMS server."""

    # The configuration for the report service
    config = ServiceConfiguration(Interface.MI, Serializer(SchemaType.REPORT, "MarketReport"))
