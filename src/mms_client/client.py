"""Contains the client layer for communicating with the MMS server."""

from logging import getLogger

from mms_client.services.base import BaseClient
from mms_client.services.market import MarketClientMixin
from mms_client.services.omi import OMIClientMixin
from mms_client.services.registration import RegistrationClientMixin
from mms_client.services.report import ReportClientMixin

# Set the default logger for the MMS client
logger = getLogger(__name__)


class MmsClient(BaseClient, MarketClientMixin, RegistrationClientMixin, ReportClientMixin, OMIClientMixin):
    """User client for the MMS server.

    This class is used to communicate with the MMS server.
    """
