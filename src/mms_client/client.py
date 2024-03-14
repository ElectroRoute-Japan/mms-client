"""Contains the client layer for communicating with the MMS server."""

from mms_client.services.market import MarketClient
from mms_client.services.omi import OMIClient
from mms_client.services.registration import RegistrationClient
from mms_client.services.report import ReportClient


class MmsClient(MarketClient, RegistrationClient, ReportClient, OMIClient):
    """User client for the MMS server.

    This class is used to communicate with the MMS server.
    """
