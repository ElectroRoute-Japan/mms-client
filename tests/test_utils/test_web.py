"""Includes unit tests for the mms_client.utils.web module."""

from logging import getLogger

import pytest
import responses
from zeep.exceptions import TransportError

from mms_client.types.transport import MmsRequest
from mms_client.types.transport import RequestDataType
from mms_client.types.transport import RequestType
from mms_client.types.transport import ResponseDataType
from mms_client.utils.web import URLS
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface
from mms_client.utils.web import ZWrapper
from tests.testutils import register_mms_request
from tests.testutils import verify_mms_response


@pytest.mark.parametrize(
    "client, interface, error, test, expected",
    [
        (ClientType.BSP, Interface.MI, False, False, "https://www2.tdgc.jp/axis2/services/MiWebService"),
        (ClientType.BSP, Interface.MI, True, False, "https://www3.tdgc.jp/axis2/services/MiWebService"),
        (ClientType.BSP, Interface.MI, False, True, "https://www4.tdgc.jp/axis2/services/MiWebService"),
        (ClientType.BSP, Interface.OMI, False, False, "https://www5.tdgc.jp/axis2/services/OmiWebService"),
        (ClientType.BSP, Interface.OMI, True, False, "https://www6.tdgc.jp/axis2/services/OmiWebService"),
        (ClientType.BSP, Interface.OMI, False, True, "https://www7.tdgc.jp/axis2/services/OmiWebService"),
        (ClientType.TSO, Interface.MI, False, False, "https://maiwlba103v03.tdgc.jp/axis2/services/MiWebService"),
        (ClientType.TSO, Interface.MI, True, False, "https://mbiwlba103v03.tdgc.jp/axis2/services/MiWebService"),
        (ClientType.TSO, Interface.MI, False, True, "https://mbiwlba103v06.tdgc.jp/axis2/services/MiWebService"),
        (ClientType.TSO, Interface.OMI, False, False, "https://maiwlba103v07.tdgc.jp/axis2/services/OmiWebService"),
        (ClientType.TSO, Interface.OMI, True, False, "https://mbiwlba103v07.tdgc.jp/axis2/services/OmiWebService"),
        (ClientType.TSO, Interface.OMI, False, True, "https://mbiwlba103v08.tdgc.jp/axis2/services/OmiWebService"),
    ],
)
def test_service_endpoint_select_works(
    client: ClientType, interface: Interface, error: bool, test: bool, expected: str
):
    """Test that the select method of the ServiceEndpoint class works as expected."""
    endpoint = URLS[client][interface]
    endpoint.select(error=error, test=test)
    assert endpoint.selected == expected


def test_zwrapper_client_invalid(mocker):
    """Test that the ZWrapper constructor raises an error when the given client is invalid."""
    with pytest.raises(ValueError) as exc_info:
        _ = ZWrapper("invalid", Interface.OMI, mocker.MagicMock(), getLogger())
    assert str(exc_info.value) == "Invalid client, 'invalid'. Only 'bsp' and 'tso' are supported."


def test_zwrapper_interface_invalid(mocker):
    """Test that the ZWrapper constructor raises an error when the given interface is invalid."""
    with pytest.raises(ValueError) as exc_info:
        _ = ZWrapper(ClientType.BSP, "invalid", mocker.MagicMock(), getLogger())
    assert str(exc_info.value) == "Invalid interface, 'invalid'. Only 'mi' and 'omi' are supported."


@pytest.mark.parametrize(
    "interface, addr",
    [
        (Interface.MI, "https://www2.tdgc.jp/axis2/services/MiWebService"),
        (Interface.OMI, "https://www5.tdgc.jp/axis2/services/OmiWebService"),
    ],
)
def test_zwrapper_client_interface_valid(mocker, interface: Interface, addr: str):
    """Test that the ZWrapper constructor does not raise an error when the given client and interface are valid."""
    mock_cert = mocker.MagicMock()
    zmi = ZWrapper(ClientType.BSP, interface, mock_cert, getLogger())
    assert zmi._service._binding_options["address"] == addr


@pytest.mark.parametrize(
    "test, expected",
    [
        (False, "https://www2.tdgc.jp/axis2/services/MiWebService"),
        (True, "https://www4.tdgc.jp/axis2/services/MiWebService"),
    ],
)
def test_zwrapper_client_instantiation(mocker, test: bool, expected: str):
    """Test that the ZWrapper constructor instantiates the correct client."""
    z = ZWrapper(ClientType.BSP, Interface.MI, mocker.MagicMock(), getLogger(), test=test)
    assert z._endpoint == URLS[ClientType.BSP][Interface.MI]
    assert z._endpoint.selected == expected


@responses.activate
def test_zwrapper_submit_server_error(mock_certificate):
    """Test that the submit method of the ZWrapper class handles server errors as expected."""
    # First, register our test responses with the responses library
    register_mms_request(RequestType.INFO, "test", b"derp", b"", 500)
    register_mms_request(
        RequestType.INFO, "test", b"derp", b"derp", url="https://www3.tdgc.jp/axis2/services/MiWebService"
    )

    # Next, create our Zeep client
    z = ZWrapper(ClientType.BSP, Interface.MI, mock_certificate.to_adapter(), getLogger())

    # Next, attempt to submit a request and retrieve the response
    resp = z.submit(
        MmsRequest(
            requestType=RequestType.INFO,
            requestDataType=RequestDataType.XML,
            requestSignature="test",
            requestData=b"derp",
            sendRequestDataOnSuccess=False,
        )
    )

    # Finally, verify that the response is as expected
    verify_mms_response(resp, True, ResponseDataType.XML, b"derp")


@responses.activate
def test_zwrapper_unrecoverable_error(mock_certificate):
    """Test that, in the event of a 4xx error, the ZWrapper class raises an exception."""
    # First, register our test responses with the responses library
    register_mms_request(RequestType.INFO, "test", b"derp", b"", 400)

    # Next, create our Zeep client
    z = ZWrapper(ClientType.BSP, Interface.MI, mock_certificate.to_adapter(), getLogger())

    # Now, attempt to submit a request and retrieve the response; this should fail
    with pytest.raises(TransportError) as exc_info:
        _ = z.submit(
            MmsRequest(
                requestType=RequestType.INFO,
                requestDataType=RequestDataType.XML,
                requestSignature="test",
                requestData=b"derp",
                sendRequestDataOnSuccess=False,
            )
        )

    # Finally, verify the details of the raised exception
    assert exc_info.value.status_code == 400
    assert exc_info.value.message == "Server returned HTTP status 400 (no content available)"


@responses.activate
def test_zwrapper_submit_works(mock_certificate):
    """Test that the submit method of the ZWrapper class works as expected."""
    # First, register our test response with the responses library
    register_mms_request(RequestType.INFO, "test", b"derp", b"derp")

    # Next, create our Zeep client
    z = ZWrapper(ClientType.BSP, Interface.MI, mock_certificate.to_adapter(), getLogger())

    # Now, attempt to submit a request and retrieve the response
    resp = z.submit(
        MmsRequest(
            requestType=RequestType.INFO,
            requestDataType=RequestDataType.XML,
            requestSignature="test",
            requestData=b"derp",
            sendRequestDataOnSuccess=False,
        )
    )

    # Finally, verify that the response is as expected
    verify_mms_response(resp, True, ResponseDataType.XML, b"derp")
