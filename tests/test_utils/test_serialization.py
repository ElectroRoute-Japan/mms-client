"""Tests the functionality in the mms_client.utils.serialization module."""

from base64 import b64decode
from base64 import b64encode
from datetime import date as Date
from typing import Dict

import pytest
from pendulum import DateTime
from pendulum import Timezone

from mms_client.types.base import Message
from mms_client.types.base import Messages
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
from tests.test_types.test_market import verify_market_submit
from tests.test_types.test_offer import offer_stack_verifier
from tests.test_types.test_offer import verify_offer_data

# Test base-64 encoded XML payload
TEST_XML_ENCODED = b"PD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0ndXRmLTgnPz4KPE1hcmtldERhdGEgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYSI+PFByb2Nlc3NpbmdTdGF0aXN0aWNzIFJlY2VpdmVkPSIxIiBWYWxpZD0iMSIgSW52YWxpZD0iMCIgU3VjY2Vzc2Z1bD0iMSIgVW5zdWNjZXNzZnVsPSIwIiBQcm9jZXNzaW5nVGltZU1zPSIxODciIFRyYW5zYWN0aW9uSWQ9ImRlcnBkZXJwIiBUaW1lU3RhbXA9IlR1ZSBNYXIgMTIgMTE6NDM6MzcgSlNUIDIwMjQiIFhtbFRpbWVTdGFtcD0iMjAyNC0wMy0xMlQxMTo0MzozNyIgLz48TWVzc2FnZXM+PEVycm9yIENvZGU9IkVycm9yQ29kZTEiIC8+PEVycm9yIENvZGU9IkVycm9yQ29kZTIiIC8+PFdhcm5pbmcgQ29kZT0iV2FybmluZzEiIC8+PFdhcm5pbmcgQ29kZT0iV2FybmluZzIiIC8+PEluZm9ybWF0aW9uIENvZGU9IkluZm8xIiAvPjxJbmZvcm1hdGlvbiBDb2RlPSJJbmZvMiIgLz48L01lc3NhZ2VzPjxNYXJrZXRTdWJtaXQgRGF0ZT0iMjAxOS0wOC0yOSIgUGFydGljaXBhbnROYW1lPSJGMTAwIiBVc2VyTmFtZT0iRkFLRVVTRVIiIE1hcmtldFR5cGU9IkRBTSIgTnVtT2ZEYXlzPSIxIiBWYWxpZGF0aW9uPSJQQVNTRUQiIFN1Y2Nlc3M9InRydWUiPjxNZXNzYWdlcz48RXJyb3IgQ29kZT0iRXJyb3JDb2RlMSIgLz48RXJyb3IgQ29kZT0iRXJyb3JDb2RlMiIgLz48V2FybmluZyBDb2RlPSJXYXJuaW5nMSIgLz48V2FybmluZyBDb2RlPSJXYXJuaW5nMiIgLz48SW5mb3JtYXRpb24gQ29kZT0iSW5mbzEiIC8+PEluZm9ybWF0aW9uIENvZGU9IkluZm8yIiAvPjwvTWVzc2FnZXM+PE9mZmVyRGF0YSBSZXNvdXJjZU5hbWU9IkZBS0VfUkVTTyIgU3RhcnRUaW1lPSIyMDE5LTA4LTMwVDAzOjI0OjE1IiBFbmRUaW1lPSIyMDE5LTA4LTMwVDExOjI0OjE1IiBEaXJlY3Rpb249IjEiIERyUGF0dGVybk51bWJlcj0iMTIiIEJzcFBhcnRpY2lwYW50TmFtZT0iRjEwMCIgQ29tcGFueVNob3J0TmFtZT0i5YG95Lya56S+IiBPcGVyYXRvckNvZGU9IkZBS0UiIEFyZWE9IjA0IiBSZXNvdXJjZVNob3J0TmFtZT0i5YG96Zu75YqbIiBTeXN0ZW1Db2RlPSJGU1lTMCIgU3VibWlzc2lvblRpbWU9IjIwMTktMDgtMjlUMDM6MjQ6MTUiIFZhbGlkYXRpb249IlBBU1NFRCIgU3VjY2Vzcz0idHJ1ZSI+PE1lc3NhZ2VzPjxFcnJvciBDb2RlPSJFcnJvckNvZGUxIiAvPjxFcnJvciBDb2RlPSJFcnJvckNvZGUyIiAvPjxXYXJuaW5nIENvZGU9Ildhcm5pbmcxIiAvPjxXYXJuaW5nIENvZGU9Ildhcm5pbmcyIiAvPjxJbmZvcm1hdGlvbiBDb2RlPSJJbmZvMSIgLz48SW5mb3JtYXRpb24gQ29kZT0iSW5mbzIiIC8+PC9NZXNzYWdlcz48T2ZmZXJTdGFjayBTdGFja051bWJlcj0iMSIgTWluaW11bVF1YW50aXR5SW5Ldz0iMTAwIiBQcmltYXJ5T2ZmZXJRdWFudGl0eUluS3c9IjE1MCIgU2Vjb25kYXJ5MU9mZmVyUXVhbnRpdHlJbkt3PSIyMDAiIFNlY29uZGFyeTJPZmZlclF1YW50aXR5SW5Ldz0iMjUwIiBUZXJ0aWFyeTFPZmZlclF1YW50aXR5SW5Ldz0iMzAwIiBUZXJ0aWFyeTJPZmZlclF1YW50aXR5SW5Ldz0iMzUwIiBPZmZlclVuaXRQcmljZT0iMTAwIiBPZmZlcklkPSJGQUtFX0lEIj48TWVzc2FnZXM+PEVycm9yIENvZGU9IkVycm9yQ29kZTEiIC8+PEVycm9yIENvZGU9IkVycm9yQ29kZTIiIC8+PFdhcm5pbmcgQ29kZT0iV2FybmluZzEiIC8+PFdhcm5pbmcgQ29kZT0iV2FybmluZzIiIC8+PEluZm9ybWF0aW9uIENvZGU9IkluZm8xIiAvPjxJbmZvcm1hdGlvbiBDb2RlPSJJbmZvMiIgLz48L01lc3NhZ2VzPjwvT2ZmZXJTdGFjaz48L09mZmVyRGF0YT48L01hcmtldFN1Ym1pdD48L01hcmtldERhdGE+"


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
    assert b64decode(data) == (
        """<?xml version='1.0' encoding='utf-8'?>\n<MarketData xmlns:xsi="http://www.w3.org/2001/XMLSchema" """
        """xsi:noNamespaceSchemaLocation="mi-market.xsd"><MarketSubmit Date="2019-08-29" ParticipantName="F100" """
        """UserName="FAKEUSER" MarketType="DAM" NumOfDays="1"><OfferData ResourceName="FAKE_RESO" """
        """StartTime="2019-08-30T03:24:15" EndTime="2019-08-30T11:24:15" Direction="1" DrPatternNumber="12" """
        """BspParticipantName="F100" CompanyShortName="偽会社" OperatorCode="FAKE" Area="04" ResourceShortName="偽電力" """
        """SystemCode="FSYS0" SubmissionTime="2019-08-29T03:24:15"><OfferStack StackNumber="1" """
        """MinimumQuantityInKw="100" PrimaryOfferQuantityInKw="150" Secondary1OfferQuantityInKw="200" """
        """Secondary2OfferQuantityInKw="250" Tertiary1OfferQuantityInKw="300" Tertiary2OfferQuantityInKw="350" """
        """OfferUnitPrice="100" OfferId="FAKE_ID"/></OfferData></MarketSubmit></MarketData>"""
    ).encode("UTF-8")


def test_deserialize_payload_key_invalid():
    """Test that the deserialize method raises an error when the payload key is invalid."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "ReportData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize(TEST_XML_ENCODED, MarketSubmit, OfferData)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected payload key 'ReportData' not found in response"


def test_deserialize_envelope_type_invalid():
    """Test that the deserialize method raises an error when the envelope type doesn't match the XML payload."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize(TEST_XML_ENCODED, MarketQuery, OfferData)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected envelope type 'MarketQuery' not found in response"


def test_deserialize_data_type_invalid():
    """Test that the deserialize method raises an error when the data type doesn't match the XML payload."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize(TEST_XML_ENCODED, MarketSubmit, OfferCancel)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected data type 'OfferCancel' not found in response"


def test_deserialize_works():
    """Test that, if no errors occur, then the deserialize method will return the expected data."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market submit request and offer data
    resp = serialzier.deserialize(TEST_XML_ENCODED, MarketSubmit, OfferData)

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


def test_deserialize_multi_payload_key_invalid():
    """Test that the deserialize_multi method raises an error when the payload key is invalid."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "ReportData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize_multi(TEST_XML_ENCODED, MarketSubmit, OfferData)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected payload key 'ReportData' not found in response"


def test_deserialize_multi_envelope_type_invalid():
    """Test that the deserialize_multi method raises an error when the envelope type doesn't match the XML payload."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize_multi(TEST_XML_ENCODED, MarketQuery, OfferData)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected envelope type 'MarketQuery' not found in response"


def test_deserialize_multi_data_type_invalid():
    """Test that the deserialize_multi method raises an error when the data type doesn't match the XML payload."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize_multi(TEST_XML_ENCODED, MarketSubmit, OfferCancel)

    # Finally, verify that the error message is as we expect
    assert str(ex_info.value) == "Expected data type 'OfferCancel' not found in response"


def test_deserialize_multi_works():
    """Test that, if no errors occur, then the deserialize_multi method will return the expected data."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Next, attempt to deserialize the payload as a market submit request and offer data
    resp = serialzier.deserialize_multi(TEST_XML_ENCODED, MarketSubmit, OfferData)

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
    """Test that, if no errors occur, then the deserialize_multi method will return the expected data."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "MarketData")

    # Create our test XML payload
    encoded_data = b64encode(
        (
            """<?xml version='1.0' encoding='utf-8'?>\n<MarketData xmlns:xsi="http://www.w3.org/2001/XMLSchema">"""
            """<ProcessingStatistics Received="1" Valid="1" Invalid="0" Successful="1" Unsuccessful="0" """
            """ProcessingTimeMs="187" TransactionId="derpderp" TimeStamp="Tue Mar 12 11:43:37 JST 2024" """
            """XmlTimeStamp="2024-03-12T11:43:37" /><Messages><Error Code="ErrorCode1" /><Error Code="ErrorCode2" />"""
            """<Warning Code="Warning1" /><Warning Code="Warning2" /><Information Code="Info1" /><Information """
            """Code="Info2" /></Messages><MarketSubmit Date="2019-08-29" ParticipantName="F100" UserName="FAKEUSER" """
            """MarketType="DAM" NumOfDays="1" Validation="PASSED" Success="true"><Messages><Error Code="ErrorCode1" />"""
            """<Error Code="ErrorCode2" /><Warning Code="Warning1" /><Warning Code="Warning2" /><Information """
            """Code="Info1" /><Information Code="Info2" /></Messages></MarketSubmit></MarketData>"""
        ).encode("UTF-8")
    )

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


def code_verifier(code: str):
    """Return a function that verifies a message has the expected code."""

    def inner(message: Message):
        assert message.code == code

    return inner


def messages_verifier(errors: list, warnings: list, infos: list):
    """Return a function that verifies that a message has the expected errors, warnings, and information."""

    def inner(messages: Messages):
        assert len(messages.errors) == len(errors)
        assert len(messages.warnings) == len(warnings)
        assert len(messages.information) == len(infos)
        for i, error in enumerate(errors):
            error(messages.errors[i])
        for i, warning in enumerate(warnings):
            warning(messages.warnings[i])
        for i, info in enumerate(infos):
            info(messages.information[i])

    return inner


def verify_messages(messages: Dict[str, Messages], verifiers: dict):
    """Verify that the messages are as we expect."""
    assert len(messages) == len(verifiers)
    print(messages)
    for key, verifier in verifiers.items():
        verifier(messages[key])