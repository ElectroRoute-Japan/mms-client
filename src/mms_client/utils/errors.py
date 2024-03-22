"""Contains error classes for the MMS client."""

from typing import Dict

from mms_client.types.base import E
from mms_client.types.base import Messages
from mms_client.types.base import P
from mms_client.utils.web import ClientType


class AudienceError(ValueError):
    """Error raised when an invalid audience is provided."""

    def __init__(self, method: str, allowed: ClientType, audience: ClientType):
        """Initialize the error.

        Arguments:
        method (str):   The method that caused the error.
        allowed (str):  The allowed audience.
        audience (str): The invalid audience.
        """
        self.method = method
        self.message = f"{method}: Invalid client type, '{audience.name}' provided. Only '{allowed.name}' is supported."
        self.allowed = allowed
        self.audience = audience
        super().__init__(self.message)


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

    def __init__(self, method: str, envelope: E, request: P, messages: Dict[str, Messages]):
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
