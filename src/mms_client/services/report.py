"""Contains the client layer for making report requests to the MMS server."""

from logging import getLogger

from mms_client.services.base import ServiceConfiguration
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import Interface

# Set the default logger for the MMS client
logger = getLogger(__name__)


class ReportClientMixin:  # pylint: disable=unused-argument
    """Report client for the MMS server."""

    # The configuration for the report service
    config = ServiceConfiguration(Interface.MI, Serializer(SchemaType.REPORT, "MarketReport"))
