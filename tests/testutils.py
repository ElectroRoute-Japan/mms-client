"""Contains utility functions for testing the MMS client."""

from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple

import responses
from requests import PreparedRequest
from responses.matchers import header_matcher

from mms_client.types.transport import Attachment
from mms_client.types.transport import MmsRequest
from mms_client.types.transport import MmsResponse
from mms_client.types.transport import RequestDataType
from mms_client.types.transport import RequestType
from mms_client.types.transport import ResponseDataType


def verify_mms_request(
    request: MmsRequest,
    subsystem: RequestType,
    data_type: RequestDataType,
    signature: str,
    data: bytes,
    as_admin: bool = False,
    compressed: bool = False,
    send_request: bool = True,
    resp_compressed: bool = False,
    verifiers: List[Callable] = [],
):
    """Verify that the given MMS request was created with the correct parameters."""
    assert request.as_admin == as_admin
    assert request.compressed == compressed
    assert request.data_type == data_type
    assert request.payload == data
    assert request.respond_with_request == send_request
    assert request.response_compressed == resp_compressed
    assert request.signature == signature
    assert request.subsystem == subsystem
    verify_attachments(request.attachments, verifiers)


def verify_mms_response(
    response: MmsResponse,
    success: bool,
    data_type: ResponseDataType,
    payload: bytes,
    report_filename: Optional[str] = None,
    binary: bool = False,
    compressed: bool = False,
    warnings: bool = False,
    verifiers: List[Callable] = [],
):
    """Verify that the given MMS response was created with the correct parameters."""
    assert response.success == success
    assert response.data_type == data_type
    assert response.payload == payload
    assert response.report_filename == report_filename
    assert response.is_binary == binary
    assert response.compressed == compressed
    assert response.warnings == warnings
    verify_attachments(response.attachments, verifiers)


def verify_attachments(attachments: List[Attachment], verifiers: List[Callable]):
    """Verify that the given attachments were created with the correct parameters."""
    assert len(attachments) == len(verifiers)
    for i, verifier in enumerate(verifiers):
        verifier(attachments[i])


def attachment_verifier(name: str, data: bytes, signature: str):
    """Verify that the given attachment was created with the correct parameters."""

    def inner(att: Attachment):
        assert att.data == data
        assert att.name == name
        assert att.signature == signature

    return inner


def register_mms_request(
    request: bytes, response: bytes, status: int = 200, url: str = "https://www2.tdgc.jp/axis2/services/MiWebService"
):
    """Register a new MMS request and response with the responses library."""
    responses.add(
        responses.Response(
            method="POST",
            url=url,
            body=response,
            status=status,
            content_type="text/xml; charset=utf-8",
            auto_calculate_content_length=True,
            match=[PayloadMatcher(request), header_matcher({"Content-Type": "text/xml; charset=utf-8"})],
        )
    )


class PayloadMatcher:
    """A custom matcher for comparing XML payloads."""

    def __init__(self, expected: bytes):
        """Create a new XML payload matcher with the given expected XML payload."""
        self.expected = expected

    def __call__(self, request: PreparedRequest) -> Tuple[bool, str]:
        """Return True if the request's body matches the expected XML payload."""

        # First, parse the request body and the expected XML payload
        actual = request.body

        # Next, compare the two payloads and return the result
        return actual == self.expected, "XML payloads do not match"
