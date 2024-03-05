"""Includes unit tests for the mms_client.web module."""

import pytest

from mms_client.objects.base import MmsRequest
from mms_client.objects.base import MmsResponse
from mms_client.objects.base import RequestType
from mms_client.objects.base import ResponseDataType
from mms_client.web import MI_WEBSERVICE_PORT
from mms_client.web import OMI_WEBSERVICE_PORT
from mms_client.web import URLS
from mms_client.web import ClientType
from mms_client.web import InterfaceType
from mms_client.web import ZWrapper


@pytest.mark.parametrize(
    "client, interface, error, test, expected",
    [
        ("bsp", "mi", False, False, "https://www2.tdgc.jp/axis2/services/MiWebService"),
        ("bsp", "mi", True, False, "https://www3.tdgc.jp/axis2/services/MiWebService"),
        ("bsp", "mi", False, True, "https://www4.tdgc.jp/axis2/services/MiWebService"),
        ("bsp", "omi", False, False, "https://www5.tdgc.jp/axis2/services/OmiWebService"),
        ("bsp", "omi", True, False, "https://www6.tdgc.jp/axis2/services/OmiWebService"),
        ("bsp", "omi", False, True, "https://www7.tdgc.jp/axis2/services/OmiWebService"),
        ("tso", "mi", False, False, "https://maiwlba103v03.tdgc.jp/axis2/services/MiWebService"),
        ("tso", "mi", True, False, "https://mbiwlba103v03.tdgc.jp/axis2/services/MiWebService"),
        ("tso", "mi", False, True, "https://mbiwlba103v06.tdgc.jp/axis2/services/MiWebService"),
        ("tso", "omi", False, False, "https://maiwlba103v07.tdgc.jp/axis2/services/OmiWebService"),
        ("tso", "omi", True, False, "https://mbiwlba103v07.tdgc.jp/axis2/services/OmiWebService"),
        ("tso", "omi", False, True, "https://mbiwlba103v08.tdgc.jp/axis2/services/OmiWebService"),
    ],
)
def test_service_endpoint_select_works(
    client: ClientType, interface: InterfaceType, error: bool, test: bool, expected: str
):
    """Test that the select method of the ServiceEndpoint class works as expected."""
    endpoint = URLS[client][interface]
    endpoint.select(error=error, test=test)
    assert endpoint.selected == expected


def test_zwrapper_client_invalid(mocker):
    """Test that the ZWrapper constructor raises an error when the given client is invalid."""
    with pytest.raises(ValueError) as exc_info:
        _ = ZWrapper("invalid", "omi", mocker.MagicMock())
    assert str(exc_info.value) == "Invalid client, 'invalid'. Only 'bsp' and 'tso' are supported."


def test_zwrapper_interface_invalid(mocker):
    """Test that the ZWrapper constructor raises an error when the given interface is invalid."""
    with pytest.raises(ValueError) as exc_info:
        _ = ZWrapper("bsp", "invalid", mocker.MagicMock())
    assert str(exc_info.value) == "Invalid interface, 'invalid'. Only 'mi' and 'omi' are supported."


def test_zwrapper_client_interface_valid(mocker):
    """Test that the ZWrapper constructor does not raise an error when the given client and interface are valid."""
    mock_cert = mocker.MagicMock()
    zmi = ZWrapper("bsp", "mi", mock_cert)
    assert zmi._service_port == MI_WEBSERVICE_PORT
    zomi = ZWrapper("tso", "omi", mock_cert)
    assert zomi._service_port == OMI_WEBSERVICE_PORT


@pytest.mark.parametrize(
    "test, expected",
    [
        (False, "https://www2.tdgc.jp/axis2/services/MiWebService"),
        (True, "https://www4.tdgc.jp/axis2/services/MiWebService"),
    ],
)
def test_zwrapper_client_instantiation(mocker, test: bool, expected: str):
    """Test that the ZWrapper constructor instantiates the correct client."""
    z = ZWrapper("bsp", "mi", mocker.MagicMock(), test=test)
    assert z._endpoint == URLS["bsp"]["mi"]
    assert z._endpoint.selected == expected


def test_zwrapper_submit_works(mocker):
    """Test that the submit method of the ZWrapper class works as expected."""
    # First, create our mock client and set it as the client for the ZWrapper object.
    mock_client = mocker.MagicMock()
    mock_client.service["MiWebService"].return_value = {
        "success": True,
        "responseDataType": "TXT",
        "responseData": b"derp",
    }
    z = ZWrapper("bsp", "mi", mocker.MagicMock())
    z._client = mock_client

    # Next, attempt to submit a request and retrieve the response
    resp = z.submit(MmsRequest(requestType=RequestType.INFO, requestSignature="test", requestData=b"derp"))

    # Finally, assert that the response is of the correct type and that the client was called once.
    assert isinstance(resp, MmsResponse)
    assert mock_client.service["MiWebService"].call_count == 1
