"""Tests the functionality in the mms_client.types.transport module."""

from typing import Callable
from typing import List

from mms_client.types.transport import Attachment
from mms_client.types.transport import MmsRequest
from mms_client.types.transport import MmsResponse
from mms_client.types.transport import RequestDataType
from mms_client.types.transport import RequestType
from mms_client.types.transport import ResponseDataType


def test_mms_request_defaults():
    """Test that the MmsRequest class initializes and converts to a dictionary as we expect."""
    # First, create a new MMS request
    request = MmsRequest(
        requestType=RequestType.INFO,
        requestDataType=RequestDataType.XML,
        requestSignature="FAKE_SIGNATURE",
        requestData=b"FAKE_PAYLOAD",
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_mms_request(request, RequestType.INFO, RequestDataType.XML, "FAKE_SIGNATURE", b"FAKE_PAYLOAD")
    assert data == {
        "requestType": RequestType.INFO,
        "requestDataType": RequestDataType.XML,
        "requestSignature": "FAKE_SIGNATURE",
        "requestData": b"FAKE_PAYLOAD",
    }


def test_mms_request_full():
    """Test that the MmsRequest class initializes and converts to a dictionary as we expect."""
    # First, create a new MMS request
    request = MmsRequest(
        requestType=RequestType.INFO,
        adminRole=True,
        attachmentData=[Attachment(signature="FAKE_SIGNATURE", name="FAKE_NAME", binaryData=b"FAKE_DATA")],
        requestDataCompressed=True,
        requestDataType=RequestDataType.JSON,
        sendRequestDataOnSuccess=False,
        sendResponseDataCompressed=True,
        requestSignature="FAKE_SIGNATURE",
        requestData=b"FAKE_PAYLOAD",
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_mms_request(
        request,
        RequestType.INFO,
        RequestDataType.JSON,
        "FAKE_SIGNATURE",
        b"FAKE_PAYLOAD",
        True,
        True,
        False,
        True,
        verifiers=[attachment_verifier("FAKE_NAME", b"FAKE_DATA", "FAKE_SIGNATURE")],
    )
    assert data == {
        "requestType": RequestType.INFO,
        "adminRole": True,
        "requestDataCompressed": True,
        "requestDataType": RequestDataType.JSON,
        "sendRequestDataOnSuccess": False,
        "sendResponseDataCompressed": True,
        "requestSignature": "FAKE_SIGNATURE",
        "requestData": b"FAKE_PAYLOAD",
        "attachmentData": [{"signature": "FAKE_SIGNATURE", "name": "FAKE_NAME", "binaryData": b"FAKE_DATA"}],
    }


def test_mms_response_defaults():
    """Test that the MmsResponse class initializes and converts to a dictionary as we expect."""
    # First, create a new MMS response
    response = MmsResponse(
        success=True,
        responseDataType=ResponseDataType.CSV,
        responseData=b"FAKE_PAYLOAD",
    )

    # Next, convert the response to a dictionary
    data = response.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the response was created with the correct parameters
    verify_mms_response(response, True, ResponseDataType.CSV, b"FAKE_PAYLOAD")
    assert data == {
        "success": True,
        "responseDataType": ResponseDataType.CSV,
        "responseData": b"FAKE_PAYLOAD",
    }


def test_mms_response_full():
    """Test that the MmsResponse class initializes and converts to a dictionary as we expect."""
    # First, create a new MMS response
    response = MmsResponse(
        success=True,
        responseBinary=True,
        responseCompressed=True,
        responseDataType=ResponseDataType.JSON,
        responseFilename="FAKE_FILENAME",
        responseData=b"FAKE_PAYLOAD",
        warnings=True,
        attachmentData=[Attachment(signature="FAKE_SIGNATURE", name="FAKE_NAME", binaryData=b"FAKE_DATA")],
    )

    # Next, convert the response to a dictionary
    data = response.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the response was created with the correct parameters
    verify_mms_response(
        response,
        True,
        ResponseDataType.JSON,
        b"FAKE_PAYLOAD",
        "FAKE_FILENAME",
        True,
        True,
        True,
        verifiers=[attachment_verifier("FAKE_NAME", b"FAKE_DATA", "FAKE_SIGNATURE")],
    )
    assert data == {
        "success": True,
        "warnings": True,
        "responseBinary": True,
        "responseCompressed": True,
        "responseDataType": ResponseDataType.JSON,
        "responseFilename": "FAKE_FILENAME",
        "responseData": b"FAKE_PAYLOAD",
        "attachmentData": [{"signature": "FAKE_SIGNATURE", "name": "FAKE_NAME", "binaryData": b"FAKE_DATA"}],
    }


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
    report_filename: str = "",
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
