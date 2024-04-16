"""Tests the functionality of the mms_client.services.base module."""

from datetime import date as Date

import pytest
import responses
from pendulum import DateTime

from mms_client.services.base import BaseClient
from mms_client.services.base import EndpointConfiguration
from mms_client.services.base import ServiceConfiguration
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferStack
from mms_client.types.transport import RequestType
from mms_client.types.transport import ResponseDataType
from mms_client.utils.errors import MMSClientError
from mms_client.utils.errors import MMSValidationError
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface
from tests.testutils import code_verifier
from tests.testutils import messages_verifier
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import register_mms_request
from tests.testutils import verify_messages


@responses.activate
@pytest.mark.parametrize(
    "data_type,compressed,message",
    [
        (ResponseDataType.JSON, False, "Invalid MMS response data type: JSON. Only XML is supported."),
        (ResponseDataType.XML, True, "Invalid MMS response. Compressed responses are not supported."),
    ],
)
def test_non_xml_received_error(mock_certificate, data_type: ResponseDataType, compressed: bool, message: str):
    """Test that an exception is raised if a non-XML response is received."""
    # First, create our base client and endpoint configuration
    client = BaseClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)
    config = EndpointConfiguration(
        "Test",
        ClientType.BSP,
        ServiceConfiguration(Interface.MI, Serializer(SchemaType.MARKET, "MarketData")),
        RequestType.INFO,
        None,
        None,
    )

    # Next, register our test response with the responses library
    register_mms_request(
        RequestType.INFO,
        (
            "eVnILLetkUevnDGEKTUYwuxgQzOAlH6g8keMr/sP84QXHq7geOaB54Mkdp0Gw3ShYXwhZnzkWQMQK1EuSJEGuauNh3MnJ5VJWI6tCnPIv"
            "5E7cfjH/1OP3Ez0JbjucHUFqqFJrgbJ8dxJxnUuhDX7359oodlmUrFAIXhyzh7XfEjrHLQzhRQsNZV/aa+OgIj0UplHf9Mah62pENa48f"
            "+ZN9+15v/S7Ob2V4ZOFY5oeB2tyuwjydJkdcDL2hkewblkc4wLJwopk4bGfVWBI3m42kH32YdokPCyRx/PoDQNmCH/QDwJ8gKFMiMULHy"
            "/hsvmxcogN3bx7xMeaxun+ROyBYpXX2VCQX2P/x8zSn/uoSRXRZyqbbSd1hYnHp2sN47niteGndHMZv1tqKw/rOIccL2598nkUj8PNqw7"
            "FCpqi9eeHaOkuHOLYLLmexICeE9zhtvz2RWbNLlLaUsMhzcjOYqos2JBUJLOn7uIf+1cZOZVr/9QG62n42pJifZcAjFCraq5k1dlpLCZr"
            "SB7bgP0uterkeTbau1TfVQ+H+iFC7rL9/N7zUHg21KxlQme8p+BQIDGXSEswMucj+TaY3H1VuZAL8bmz+xv0d4L47CbvYf8A1kwOc+2Ed"
            "BvIBTy9QCj+/x92xbopX8knV3/rqUlBJjQR1ZcGIAOn+Yf2DG6iQw="
        ),
        read_request_file("base_request.xml"),
        read_file("base_response.xml"),
        data_type=data_type,
        compressed=compressed,
    )

    # Now, create our request envelope and payload
    envelope = MarketSubmit(
        date=Date(2024, 3, 15), participant="F100", user="FAKEUSER", market_type=MarketType.DAY_AHEAD, days=1
    )
    payload = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        direction=Direction.SELL,
    )

    # Finally, attempt to submit the request; this should fail
    with pytest.raises(MMSClientError) as exc_info:
        _ = client.request_one(envelope, payload, config)

    # Verify the details of the raised exception
    assert exc_info.value.method == "Test"
    assert exc_info.value.message == message
    assert f"Test: {message}" in str(exc_info.value)


@responses.activate
def test_request_one_response_invalid(mock_certificate):
    """Test that an exception is raised if the response is invalid."""
    # First, create our base client and endpoint configuration
    client = BaseClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)
    config = EndpointConfiguration(
        "Test",
        ClientType.BSP,
        ServiceConfiguration(Interface.MI, Serializer(SchemaType.MARKET, "MarketData")),
        RequestType.INFO,
        None,
        None,
    )

    # Next, register our test response with the responses library
    register_mms_request(
        RequestType.INFO,
        (
            "eVnILLetkUevnDGEKTUYwuxgQzOAlH6g8keMr/sP84QXHq7geOaB54Mkdp0Gw3ShYXwhZnzkWQMQK1EuSJEGuauNh3MnJ5VJWI6tCnPIv"
            "5E7cfjH/1OP3Ez0JbjucHUFqqFJrgbJ8dxJxnUuhDX7359oodlmUrFAIXhyzh7XfEjrHLQzhRQsNZV/aa+OgIj0UplHf9Mah62pENa48f"
            "+ZN9+15v/S7Ob2V4ZOFY5oeB2tyuwjydJkdcDL2hkewblkc4wLJwopk4bGfVWBI3m42kH32YdokPCyRx/PoDQNmCH/QDwJ8gKFMiMULHy"
            "/hsvmxcogN3bx7xMeaxun+ROyBYpXX2VCQX2P/x8zSn/uoSRXRZyqbbSd1hYnHp2sN47niteGndHMZv1tqKw/rOIccL2598nkUj8PNqw7"
            "FCpqi9eeHaOkuHOLYLLmexICeE9zhtvz2RWbNLlLaUsMhzcjOYqos2JBUJLOn7uIf+1cZOZVr/9QG62n42pJifZcAjFCraq5k1dlpLCZr"
            "SB7bgP0uterkeTbau1TfVQ+H+iFC7rL9/N7zUHg21KxlQme8p+BQIDGXSEswMucj+TaY3H1VuZAL8bmz+xv0d4L47CbvYf8A1kwOc+2Ed"
            "BvIBTy9QCj+/x92xbopX8knV3/rqUlBJjQR1ZcGIAOn+Yf2DG6iQw="
        ),
        read_request_file("base_request.xml"),
        read_file("base_failed_response.xml"),
        success=False,
    )

    # Now, create our request envelope and payload
    envelope = MarketSubmit(
        date=Date(2024, 3, 15), participant="F100", user="FAKEUSER", market_type=MarketType.DAY_AHEAD, days=1
    )
    payload = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        direction=Direction.SELL,
    )

    # Finally, attempt to submit the request; this should fail
    with pytest.raises(MMSValidationError) as exc_info:
        _ = client.request_one(envelope, payload, config)

    # Verify the details of the raised exception
    assert exc_info.value.method == "Test"
    verify_messages(
        exc_info.value.messages,
        {
            "MarketData": messages_verifier(
                [code_verifier("Error1")],
                [code_verifier("Warning2"), code_verifier("Warning1")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                [code_verifier("Error1")],
                [code_verifier("Warning2"), code_verifier("Warning1")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData": messages_verifier(
                [],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData.OfferStack[0]": messages_verifier(
                [],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
        },
    )


@responses.activate
def test_request_many_response_invalid(mock_certificate):
    """Test that an exception is raised if the response is invalid."""
    # First, create our base client and endpoint configuration
    client = BaseClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)
    config = EndpointConfiguration(
        "Test",
        ClientType.BSP,
        ServiceConfiguration(Interface.MI, Serializer(SchemaType.MARKET, "MarketData")),
        RequestType.INFO,
        None,
        None,
    )

    # Next, register our test response with the responses library
    register_mms_request(
        RequestType.INFO,
        (
            "eVnILLetkUevnDGEKTUYwuxgQzOAlH6g8keMr/sP84QXHq7geOaB54Mkdp0Gw3ShYXwhZnzkWQMQK1EuSJEGuauNh3MnJ5VJWI6tCnPIv"
            "5E7cfjH/1OP3Ez0JbjucHUFqqFJrgbJ8dxJxnUuhDX7359oodlmUrFAIXhyzh7XfEjrHLQzhRQsNZV/aa+OgIj0UplHf9Mah62pENa48f"
            "+ZN9+15v/S7Ob2V4ZOFY5oeB2tyuwjydJkdcDL2hkewblkc4wLJwopk4bGfVWBI3m42kH32YdokPCyRx/PoDQNmCH/QDwJ8gKFMiMULHy"
            "/hsvmxcogN3bx7xMeaxun+ROyBYpXX2VCQX2P/x8zSn/uoSRXRZyqbbSd1hYnHp2sN47niteGndHMZv1tqKw/rOIccL2598nkUj8PNqw7"
            "FCpqi9eeHaOkuHOLYLLmexICeE9zhtvz2RWbNLlLaUsMhzcjOYqos2JBUJLOn7uIf+1cZOZVr/9QG62n42pJifZcAjFCraq5k1dlpLCZr"
            "SB7bgP0uterkeTbau1TfVQ+H+iFC7rL9/N7zUHg21KxlQme8p+BQIDGXSEswMucj+TaY3H1VuZAL8bmz+xv0d4L47CbvYf8A1kwOc+2Ed"
            "BvIBTy9QCj+/x92xbopX8knV3/rqUlBJjQR1ZcGIAOn+Yf2DG6iQw="
        ),
        read_request_file("base_request.xml"),
        read_file("base_failed_response.xml"),
        success=False,
    )

    # Now, create our request envelope and payload
    envelope = MarketSubmit(
        date=Date(2024, 3, 15), participant="F100", user="FAKEUSER", market_type=MarketType.DAY_AHEAD, days=1
    )
    payload = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        direction=Direction.SELL,
    )

    # Finally, attempt to submit the request; this should fail
    with pytest.raises(MMSValidationError) as exc_info:
        _ = client.request_many(envelope, payload, config)

    # Verify the details of the raised exception
    assert exc_info.value.method == "Test"
    verify_messages(
        exc_info.value.messages,
        {
            "MarketData": messages_verifier(
                [code_verifier("Error1")],
                [code_verifier("Warning2"), code_verifier("Warning1")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                [code_verifier("Error1")],
                [code_verifier("Warning2"), code_verifier("Warning1")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData[0]": messages_verifier(
                [],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData[0].OfferStack[0]": messages_verifier(
                [],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
        },
    )
