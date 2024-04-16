"""Tests the functionality in the mms_client.utils.serialization module."""

from base64 import b64encode
from datetime import date as Date
from typing import Dict

import pytest
from pendulum import DateTime
from pendulum import Timezone

from mms_client.types.base import ResponseCommon
from mms_client.types.base import ValidationStatus
from mms_client.types.enums import AreaCode
from mms_client.types.market import MarketQuery
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferStack
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from tests.testutils import code_verifier
from tests.testutils import messages_verifier
from tests.testutils import offer_stack_verifier
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import verify_market_submit
from tests.testutils import verify_messages
from tests.testutils import verify_offer_data


def test_serialize_data():
    """Test that the Serializer class serializes data as we expect."""
    # First, create a new offer data object
    offer = OfferData(
        stack=[
            OfferStack(
                number=1,
                minimum_quantity_kw=100,
                primary_qty_kw=150,
                secondary_1_qty_kw=200,
                secondary_2_qty_kw=250,
                tertiary_1_qty_kw=300,
                tertiary_2_qty_kw=350,
                unit_price=100,
                id="FAKE_ID",
            )
        ],
        resource="FAKE_RESO",
        start=DateTime(2019, 8, 30, 3, 24, 15),
        end=DateTime(2019, 8, 30, 11, 24, 15),
        direction=Direction.SELL,
        pattern_number=12,
        bsp_participant="F100",
        company_short_name="偽会社",
        operator="FAKE",
        area=AreaCode.CHUBU,
        resource_short_name="偽電力",
        system_code="FSYS0",
        submission_time=DateTime(2019, 8, 29, 3, 24, 15),
    )

    # Next, create an associated market submit request
    request = MarketSubmit(
        date=Date(2019, 8, 29),
        market_type=MarketType.DAY_AHEAD,
        participant="F100",
        user="FAKEUSER",
        days=1,
    )

    serializer = Serializer(SchemaType.MARKET, "MarketData")
    data = serializer.serialize(request, offer)

    # Finally, verify that the request was serialized as we expect
    assert data == read_request_file("serialization_2.xml")


def test_serialize_multi_data():
    """Test that the Serializer class serializes data as we expect, when provided with a list."""
    # First, create a new offer data object
    offer = OfferData(
        stack=[
            OfferStack(
                number=1,
                minimum_quantity_kw=100,
                primary_qty_kw=150,
                secondary_1_qty_kw=200,
                secondary_2_qty_kw=250,
                tertiary_1_qty_kw=300,
                tertiary_2_qty_kw=350,
                unit_price=100,
                id="FAKE_ID",
            )
        ],
        resource="FAKE_RESO",
        start=DateTime(2019, 8, 30, 3, 24, 15),
        end=DateTime(2019, 8, 30, 11, 24, 15),
        direction=Direction.SELL,
        pattern_number=12,
        bsp_participant="F100",
        company_short_name="偽会社",
        operator="FAKE",
        area=AreaCode.CHUBU,
        resource_short_name="偽電力",
        system_code="FSYS0",
        submission_time=DateTime(2019, 8, 29, 3, 24, 15),
    )

    # Next, create an associated market submit request
    request = MarketSubmit(
        date=Date(2019, 8, 29),
        market_type=MarketType.DAY_AHEAD,
        participant="F100",
        user="FAKEUSER",
        days=1,
    )

    serializer = Serializer(SchemaType.MARKET, "MarketData")
    data = serializer.serialize_multi(request, [offer], OfferData)

    # Finally, verify that the request was serialized as we expect
    assert data == read_request_file("serialization_2.xml")


def test_deserialize_payload_key_invalid():
    """Test that the deserialize method raises an error when the payload key is invalid."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "ReportData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize(read_request_file("serialization_1.xml", False), MarketSubmit, OfferData)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected payload key 'ReportData' not found in response"


def test_deserialize_envelope_type_invalid():
    """Test that the deserialize method raises an error when the envelope type doesn't match the XML payload."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize(read_file("serialization_1.xml"), MarketQuery, OfferData)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected envelope type 'MarketQuery' not found in response"


def test_deserialize_data_type_invalid():
    """Test that the deserialize method raises an error when the data type doesn't match the XML payload."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize(read_request_file("serialization_1.xml"), MarketSubmit, OfferCancel)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected data type 'OfferCancel' not found in response"


def test_deserialize_works():
    """Test that, if no errors occur, then the deserialize method will return the expected data."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market submit request and offer data
    resp = serialzier.deserialize(read_file("serialization_1.xml"), MarketSubmit, OfferData)

    # Finally, verify that the response is as we expect
    verify_offer_data(
        resp.data,
        [offer_stack_verifier(1, 100, 100, 150, 200, 250, 300, 350, "FAKE_ID")],
        "FAKE_RESO",
        DateTime(2019, 8, 30, 3, 24, 15, tzinfo=Timezone("UTC")),
        DateTime(2019, 8, 30, 11, 24, 15, tzinfo=Timezone("UTC")),
        Direction.SELL,
        12,
        "F100",
        "偽会社",
        "FAKE",
        AreaCode.CHUBU,
        "偽電力",
        "FSYS0",
        DateTime(2019, 8, 29, 3, 24, 15, tzinfo=Timezone("UTC")),
    )
    verify_response_common(resp.payload.data_validation, True, ValidationStatus.PASSED)
    verify_market_submit(resp.envelope, Date(2019, 8, 29), "F100", "FAKEUSER", MarketType.DAY_AHEAD, 1)
    verify_response_common(resp.envelope_validation, True, ValidationStatus.PASSED)
    verify_messages(
        resp.messages,
        {
            "MarketData": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData.OfferStack[0]": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
        },
    )


def test_deserialize_no_data_works():
    """Test that the deserialize method works when there is no data to return."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Create our test XML payload
    encoded_data = read_file("serialization_3.xml")

    # Next, attempt to deserialize the payload as a market submit request and offer data
    resp = serialzier.deserialize(encoded_data, MarketSubmit, OfferData)

    # Finally, verify that the response is as we expect
    assert not resp.data
    verify_market_submit(resp.envelope, Date(2019, 8, 29), "F100", "FAKEUSER", MarketType.DAY_AHEAD, 1)
    verify_response_common(resp.envelope_validation, True, ValidationStatus.PASSED)
    verify_messages(
        resp.messages,
        {
            "MarketData": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
        },
    )


def test_deserialize_multi_payload_key_invalid():
    """Test that the deserialize_multi method raises an error when the payload key is invalid."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "ReportData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize_multi(read_file("serialization_1.xml"), MarketSubmit, OfferData)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected payload key 'ReportData' not found in response"


def test_deserialize_multi_envelope_type_invalid():
    """Test that the deserialize_multi method raises an error when the envelope type doesn't match the XML payload."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize_multi(read_file("serialization_1.xml"), MarketQuery, OfferData)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected envelope type 'MarketQuery' not found in response"


def test_deserialize_multi_data_type_invalid():
    """Test that the deserialize_multi method raises an error when the data type doesn't match the XML payload."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize_multi(read_file("serialization_1.xml"), MarketSubmit, OfferCancel)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected data type 'OfferCancel' not found in response"


def test_deserialize_multi_works():
    """Test that, if no errors occur, then the deserialize_multi method will return the expected data."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market submit request and offer data
    resp = serialzier.deserialize_multi(read_file("serialization_1.xml"), MarketSubmit, OfferData)

    # Finally, verify that the response is as we expect
    assert len(resp.data) == 1
    verify_offer_data(
        resp.data[0],
        [offer_stack_verifier(1, 100, 100, 150, 200, 250, 300, 350, "FAKE_ID")],
        "FAKE_RESO",
        DateTime(2019, 8, 30, 3, 24, 15, tzinfo=Timezone("UTC")),
        DateTime(2019, 8, 30, 11, 24, 15, tzinfo=Timezone("UTC")),
        Direction.SELL,
        12,
        "F100",
        "偽会社",
        "FAKE",
        AreaCode.CHUBU,
        "偽電力",
        "FSYS0",
        DateTime(2019, 8, 29, 3, 24, 15, tzinfo=Timezone("UTC")),
    )
    verify_response_common(resp.payload[0].data_validation, True, ValidationStatus.PASSED)
    verify_market_submit(resp.envelope, Date(2019, 8, 29), "F100", "FAKEUSER", MarketType.DAY_AHEAD, 1)
    verify_response_common(resp.envelope_validation, True, ValidationStatus.PASSED)
    verify_messages(
        resp.messages,
        {
            "MarketData": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData[0]": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData[0].OfferStack[0]": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
        },
    )


def test_deserialize_multi_no_data_works():
    """Test that the deserialize_multi method works when there is no data to return."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Create our test XML payload
    encoded_data = read_file("serialization_3.xml")

    # Next, attempt to deserialize the payload as a market submit request and offer data
    resp = serialzier.deserialize_multi(encoded_data, MarketSubmit, OfferData)

    # Finally, verify that the response is as we expect
    assert len(resp.data) == 0
    verify_market_submit(resp.envelope, Date(2019, 8, 29), "F100", "FAKEUSER", MarketType.DAY_AHEAD, 1)
    verify_response_common(resp.envelope_validation, True, ValidationStatus.PASSED)
    verify_messages(
        resp.messages,
        {
            "MarketData": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                [code_verifier("ErrorCode1"), code_verifier("ErrorCode2")],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
        },
    )


def verify_response_common(data: ResponseCommon, success: bool, validation: ValidationStatus):
    """Verify that the response common fields are as we expect."""
    assert data.success == success
    assert data.validation == validation
