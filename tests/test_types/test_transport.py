"""Tests the functionality in the mms_client.types.transport module."""

from mms_client.types.transport import Attachment
from mms_client.types.transport import MmsRequest
from mms_client.types.transport import MmsResponse
from mms_client.types.transport import RequestDataType
from mms_client.types.transport import RequestType
from mms_client.types.transport import ResponseDataType
from tests.testutils import attachment_verifier
from tests.testutils import verify_mms_request
from tests.testutils import verify_mms_response


def test_mms_request_defaults():
    """Test that the MmsRequest class initializes and converts to a dictionary as we expect."""
    # First, create a new MMS request
    request = MmsRequest(
        requestType=RequestType.INFO,
        requestDataType=RequestDataType.XML,
        requestSignature="FAKE_SIGNATURE",
        requestData="FAKE_PAYLOAD",
    )

    # Next, convert the request to a dictionary
    data = request.to_arguments()

    # Finally, verify that the request was created with the correct parameters
    verify_mms_request(request, RequestType.INFO, RequestDataType.XML, "FAKE_SIGNATURE", "FAKE_PAYLOAD")
    assert data == {
        "requestType": "mp.info",
        "adminRole": False,
        "requestDataCompressed": False,
        "requestDataType": "XML",
        "sendRequestDataOnSuccess": True,
        "sendResponseDataCompressed": False,
        "requestSignature": "FAKE_SIGNATURE",
        "requestData": "FAKE_PAYLOAD",
        "attachmentData": [],
    }


def test_mms_request_full():
    """Test that the MmsRequest class initializes and converts to a dictionary as we expect."""
    # First, create a new MMS request
    request = MmsRequest(
        requestType=RequestType.INFO,
        adminRole=True,
        attachmentData=[Attachment(signature="FAKE_SIGNATURE", name="FAKE_NAME", binaryData="FAKE_DATA")],
        requestDataCompressed=True,
        requestDataType=RequestDataType.JSON,
        sendRequestDataOnSuccess=False,
        sendResponseDataCompressed=True,
        requestSignature="FAKE_SIGNATURE",
        requestData="FAKE_PAYLOAD",
    )

    # Next, convert the request to a dictionary
    data = request.to_arguments()

    # Finally, verify that the request was created with the correct parameters
    verify_mms_request(
        request,
        RequestType.INFO,
        RequestDataType.JSON,
        "FAKE_SIGNATURE",
        "FAKE_PAYLOAD",
        True,
        True,
        False,
        True,
        verifiers=[attachment_verifier("FAKE_NAME", "FAKE_DATA", "FAKE_SIGNATURE")],
    )
    assert data == {
        "requestType": "mp.info",
        "adminRole": True,
        "requestDataCompressed": True,
        "requestDataType": "JSON",
        "sendRequestDataOnSuccess": False,
        "sendResponseDataCompressed": True,
        "requestSignature": "FAKE_SIGNATURE",
        "requestData": "FAKE_PAYLOAD",
        "attachmentData": [{"signature": "FAKE_SIGNATURE", "name": "FAKE_NAME", "binaryData": "FAKE_DATA"}],
    }


def test_mms_response_defaults():
    """Test that the MmsResponse class initializes and converts to a dictionary as we expect."""
    # First, create a new MMS response
    data = {"success": True, "responseDataType": ResponseDataType.CSV, "responseData": b"FAKE_PAYLOAD"}

    # Next, attempt to convert the data to a MmsResponse object
    response = MmsResponse.model_validate(data)

    # Finally, verify that the response was created with the correct parameters
    verify_mms_response(response, True, ResponseDataType.CSV, b"FAKE_PAYLOAD")


def test_mms_response_full():
    """Test that the MmsResponse class initializes and converts to a dictionary as we expect."""
    # First, create a new MMS response
    data = {
        "success": True,
        "responseDataType": ResponseDataType.JSON,
        "responseData": b"FAKE_PAYLOAD",
        "responseFilename": "FAKE_FILENAME",
        "warnings": True,
        "responseBinary": True,
        "responseCompressed": True,
        "attachmentData": [{"signature": "FAKE_SIGNATURE", "name": "FAKE_NAME", "binaryData": "FAKE_DATA"}],
    }

    # Next, attempt to convert the data to a MmsResponse object
    response = MmsResponse.model_validate(data)

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
        verifiers=[attachment_verifier("FAKE_NAME", "FAKE_DATA", "FAKE_SIGNATURE")],
    )
