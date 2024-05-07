"""Contains error classes for the MMS client."""

from logging import getLogger
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from mms_client.types.base import E
from mms_client.types.base import Messages
from mms_client.types.base import P
from mms_client.utils.web import ClientType

# Set the default logger for the MMS client
logger = getLogger(__name__)


class AudienceError(ValueError):
    """Error raised when an invalid audience is provided."""

    def __init__(self, method: str, allowed: List[ClientType], audience: ClientType):
        """Initialize the error.

        Arguments:
        method (str):   The method that caused the error.
        allowed (str):  The allowed audience.
        audience (str): The invalid audience.
        """
        inner = (
            f"'{allowed[0].name}' is"
            if len(allowed) == 1
            else f"""{" or ".join([f"'{a.name}'" for a in allowed])} are"""
        )
        self.method = method
        self.message = f"{method}: Invalid client type, '{audience.name}' provided. Only {inner} supported."
        self.allowed = allowed
        self.audience = audience
        super().__init__(self.message)


class MMSServerError(RuntimeError):
    """Error raised when the MMS server returns an error."""

    def __init__(self, method: str, message: str):
        """Initialize the error.

        Arguments:
        method (str):   The method that caused the error.
        message (str):  The error message.
        """
        super().__init__(f"{method}: {message}")
        self.message = message
        self.method = method


class MMSClientError(RuntimeError):
    """Base class for MMS client errors."""

    def __init__(self, method: str, message: str):
        """Initialize the error.

        Arguments:
        method (str):   The method that caused the error.
        message (str):  The error message.
        """
        super().__init__(f"{method}: {message}")
        self.message = message
        self.method = method


class MMSValidationError(RuntimeError):
    """Error raised when a request fails validation."""

    def __init__(self, method: str, envelope: E, request: Optional[Union[P, List[P]]], messages: Dict[str, Messages]):
        """Initialize the validation error.

        Arguments:
        method (str):                   The method that caused the error.
        message (str):                  The error message.
        envelope (E):                   The request envelope.
        request (P):                    The request data.
        messages (Dict[str, Messages]): The messages returned with the payload.
        """
        self.message = (
            f"{method}: Request of type {type(envelope).__name__} containing data {type(request).__name__} "
            f"failed validation. See the logs for more information."
        )
        self.method = method
        self.messages = messages
        super().__init__(self.message)
