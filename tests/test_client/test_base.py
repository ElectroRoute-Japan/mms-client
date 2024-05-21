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
from mms_client.utils.errors import MMSServerError
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
            "z+shp4QJ9WmJG4tmB7FzYVu4TW8QclIF8n9Pp+VIu7Y/O/aySb0M6e4KGKuZrpy4eNiG1hPfM4nL6QXcgXoQFcsLMKyenYVyqW6kJOx9g"
            "uOiVWXlzbK/4d3pjaDR8RbEtEfJNGutAZ94G3rGnmfxg7EMLkOR3MpELZvbdZ0q+uYIeMaqD00jKHnUbF6qdTQO7grvLKaoJK6YODyqZB"
            "9ednzmMeGBuUP8zh1KF6k/p8x7LsM8FPbOvV7Bwuw9bPTxeAWcOnGiPycaBL/wW3iJfzIDX7k9xmd9f8UpgF6kxxAL4KxboF+gyiSezOb"
            "/DhUaTLiFZEw4jr993g2HsuNaV4E64jt6+XksUB8xNwsdtxfav7ItRoi/1/TWgAoHKK4bn9jBxk4hsEGJD3UwPzBxpyJD4flmfdwGZCp2"
            "/huDCItEh3Ej5GcVsUY5OjSglyogV3YwxZBVpWpMflxHRvtiYSGnCC+YCXedhu8nNm1vWwowGb8Pf31fagNT5PB+ghEu/DIe+PEr215FY"
            "2xMxYpmqzp5Vxcyg4aeC6A0XS2rT9XypZRrn+igIln23bCNYVAUpvk5a49CqRwPD+L4GEcGgmH16pCAwfSVvWvqxuzQ41iBsmw8qnXzlN"
            "JC1RFpRUagio2nL3LkRk2sF0iXeE9oi+70NGaDIJSIyPIV93Qg9RY="
        ),
        read_request_file("base_request.xml"),
        read_file("base_response.xml"),
        data_type=data_type,
        compressed=compressed,
        multipart=True,
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
def test_txt_received(mock_certificate):
    """Test that an exception is raised if a TXT response is received."""
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
            "z+shp4QJ9WmJG4tmB7FzYVu4TW8QclIF8n9Pp+VIu7Y/O/aySb0M6e4KGKuZrpy4eNiG1hPfM4nL6QXcgXoQFcsLMKyenYVyqW6kJOx9g"
            "uOiVWXlzbK/4d3pjaDR8RbEtEfJNGutAZ94G3rGnmfxg7EMLkOR3MpELZvbdZ0q+uYIeMaqD00jKHnUbF6qdTQO7grvLKaoJK6YODyqZB"
            "9ednzmMeGBuUP8zh1KF6k/p8x7LsM8FPbOvV7Bwuw9bPTxeAWcOnGiPycaBL/wW3iJfzIDX7k9xmd9f8UpgF6kxxAL4KxboF+gyiSezOb"
            "/DhUaTLiFZEw4jr993g2HsuNaV4E64jt6+XksUB8xNwsdtxfav7ItRoi/1/TWgAoHKK4bn9jBxk4hsEGJD3UwPzBxpyJD4flmfdwGZCp2"
            "/huDCItEh3Ej5GcVsUY5OjSglyogV3YwxZBVpWpMflxHRvtiYSGnCC+YCXedhu8nNm1vWwowGb8Pf31fagNT5PB+ghEu/DIe+PEr215FY"
            "2xMxYpmqzp5Vxcyg4aeC6A0XS2rT9XypZRrn+igIln23bCNYVAUpvk5a49CqRwPD+L4GEcGgmH16pCAwfSVvWvqxuzQ41iBsmw8qnXzlN"
            "JC1RFpRUagio2nL3LkRk2sF0iXeE9oi+70NGaDIJSIyPIV93Qg9RY="
        ),
        read_request_file("base_request.xml"),
        b"Some error message",
        data_type=ResponseDataType.TXT,
        multipart=True,
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
    with pytest.raises(MMSServerError) as exc_info:
        _ = client.request_one(envelope, payload, config)

    # Verify the details of the raised exception
    assert exc_info.value.method == "Test"
    assert exc_info.value.message == "Some error message"
    assert f"Test: Some error message" in str(exc_info.value)


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
            "z+shp4QJ9WmJG4tmB7FzYVu4TW8QclIF8n9Pp+VIu7Y/O/aySb0M6e4KGKuZrpy4eNiG1hPfM4nL6QXcgXoQFcsLMKyenYVyqW6kJOx9g"
            "uOiVWXlzbK/4d3pjaDR8RbEtEfJNGutAZ94G3rGnmfxg7EMLkOR3MpELZvbdZ0q+uYIeMaqD00jKHnUbF6qdTQO7grvLKaoJK6YODyqZB"
            "9ednzmMeGBuUP8zh1KF6k/p8x7LsM8FPbOvV7Bwuw9bPTxeAWcOnGiPycaBL/wW3iJfzIDX7k9xmd9f8UpgF6kxxAL4KxboF+gyiSezOb"
            "/DhUaTLiFZEw4jr993g2HsuNaV4E64jt6+XksUB8xNwsdtxfav7ItRoi/1/TWgAoHKK4bn9jBxk4hsEGJD3UwPzBxpyJD4flmfdwGZCp2"
            "/huDCItEh3Ej5GcVsUY5OjSglyogV3YwxZBVpWpMflxHRvtiYSGnCC+YCXedhu8nNm1vWwowGb8Pf31fagNT5PB+ghEu/DIe+PEr215FY"
            "2xMxYpmqzp5Vxcyg4aeC6A0XS2rT9XypZRrn+igIln23bCNYVAUpvk5a49CqRwPD+L4GEcGgmH16pCAwfSVvWvqxuzQ41iBsmw8qnXzlN"
            "JC1RFpRUagio2nL3LkRk2sF0iXeE9oi+70NGaDIJSIyPIV93Qg9RY="
        ),
        read_request_file("base_request.xml"),
        read_file("base_failed_response.xml"),
        success=False,
        multipart=True,
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
            "z+shp4QJ9WmJG4tmB7FzYVu4TW8QclIF8n9Pp+VIu7Y/O/aySb0M6e4KGKuZrpy4eNiG1hPfM4nL6QXcgXoQFcsLMKyenYVyqW6kJOx9g"
            "uOiVWXlzbK/4d3pjaDR8RbEtEfJNGutAZ94G3rGnmfxg7EMLkOR3MpELZvbdZ0q+uYIeMaqD00jKHnUbF6qdTQO7grvLKaoJK6YODyqZB"
            "9ednzmMeGBuUP8zh1KF6k/p8x7LsM8FPbOvV7Bwuw9bPTxeAWcOnGiPycaBL/wW3iJfzIDX7k9xmd9f8UpgF6kxxAL4KxboF+gyiSezOb"
            "/DhUaTLiFZEw4jr993g2HsuNaV4E64jt6+XksUB8xNwsdtxfav7ItRoi/1/TWgAoHKK4bn9jBxk4hsEGJD3UwPzBxpyJD4flmfdwGZCp2"
            "/huDCItEh3Ej5GcVsUY5OjSglyogV3YwxZBVpWpMflxHRvtiYSGnCC+YCXedhu8nNm1vWwowGb8Pf31fagNT5PB+ghEu/DIe+PEr215FY"
            "2xMxYpmqzp5Vxcyg4aeC6A0XS2rT9XypZRrn+igIln23bCNYVAUpvk5a49CqRwPD+L4GEcGgmH16pCAwfSVvWvqxuzQ41iBsmw8qnXzlN"
            "JC1RFpRUagio2nL3LkRk2sF0iXeE9oi+70NGaDIJSIyPIV93Qg9RY="
        ),
        read_request_file("base_request.xml"),
        read_file("base_failed_response.xml"),
        success=False,
        multipart=True,
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
