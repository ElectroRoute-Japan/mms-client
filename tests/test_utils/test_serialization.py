"""Tests the functionality in the mms_client.utils.serialization module."""

from datetime import date as Date

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
from mms_client.types.report import ApplicationType
from mms_client.types.report import NewReportRequest
from mms_client.types.report import NewReportResponse
from mms_client.types.report import Parameter
from mms_client.types.report import ParameterName
from mms_client.types.report import Periodicity
from mms_client.types.report import ReportBase
from mms_client.types.report import ReportName
from mms_client.types.report import ReportSubType
from mms_client.types.report import ReportType
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from tests.testutils import messages_verifier
from tests.testutils import offer_stack_verifier
from tests.testutils import parameter_verifier
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import verify_market_submit
from tests.testutils import verify_messages
from tests.testutils import verify_offer_data
from tests.testutils import verify_report_base
from tests.testutils import verify_report_create_request


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

    # Now, create a serializer and serialize the request
    serializer = Serializer(SchemaType.MARKET, "MarketData")
    data = serializer.serialize(request, offer)

    # Finally, verify that the request was serialized as we expect
    assert data.decode("UTF-8") == read_request_file("serialization_2.xml")


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
    assert data.decode("UTF-8") == read_request_file("serialization_2.xml")


def test_serialize_report():
    """Test that the Serializer class serializes report data as we expect."""
    # First, create a new report request
    create_request = NewReportRequest(
        report_type=ReportType.REGISTRATION,
        report_sub_type=ReportSubType.RESOURCES,
        periodicity=Periodicity.ON_DEMAND,
        name=ReportName.BSP_RESOURCE_LIST,
        date=Date(2024, 4, 12),
        parameters=[
            Parameter(name=ParameterName.START_TIME, value="2024-04-12T00:00:00"),
            Parameter(name=ParameterName.END_TIME, value="2024-04-12T23:59:59"),
        ],
    )

    # Next, create a new report envelope
    market_data = ReportBase(
        application_type=ApplicationType.MARKET_REPORT,
        participant="F100",
    )

    # Now, create a serializer and serialize the request
    serializer = Serializer(SchemaType.REPORT, "MarketReport")
    data = serializer.serialize(market_data, create_request, True)

    # Finally, verify that the request was serialized as we expect
    assert data.decode("UTF-8") == read_request_file("create_report_request_full.xml")


def test_deserialize_payload_key_invalid():
    """Test that the deserialize method raises an error when the payload key is invalid."""
    # First, create our serializer
    serialzier = Serializer(SchemaType.MARKET, "ReportData")

    # Next, attempt to deserialize the payload as a market query; this should raise an error
    with pytest.raises(ValueError) as ex_info:
        _ = serialzier.deserialize(read_request_file("serialization_1.xml").encode("UTF-8"), MarketSubmit, OfferData)

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
        _ = serialzier.deserialize(read_request_file("serialization_1.xml").encode("UTF-8"), MarketSubmit, OfferCancel)

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
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
            "MarketData.MarketSubmit.OfferData": messages_verifier(
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
            "MarketData.MarketSubmit.OfferData.OfferStack[0]": messages_verifier(
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
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
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
        },
    )


def test_deserialize_report_works():
    """Test that the deserialize method of the Serializer class works as expected."""
    # First, create our test XML payload
    raw = read_file("create_report_response_full.xml")

    # Next, attempt to deserialize the payload as a report create request
    resp = Serializer(SchemaType.REPORT, "MarketReport").deserialize(raw, ReportBase, NewReportResponse, True)

    # Finally, verify that the response is as we expect
    verify_report_base(resp.envelope, ApplicationType.MARKET_REPORT, "F100")
    verify_response_common(resp.envelope_validation, True, ValidationStatus.PASSED)
    verify_report_create_request(
        resp.data,
        ReportType.REGISTRATION,
        ReportSubType.RESOURCES,
        Periodicity.ON_DEMAND,
        ReportName.BSP_RESOURCE_LIST,
        Date(2024, 4, 12),
        bsp_name="F100",
        verifiers=[
            parameter_verifier(ParameterName.START_TIME, "2024-04-12T00:00:00"),
            parameter_verifier(ParameterName.END_TIME, "2024-04-13T00:00:00"),
        ],
    )
    verify_response_common(resp.payload.data_validation, True, ValidationStatus.PASSED)
    verify_messages(
        resp.messages,
        {
            "MarketReport": messages_verifier(
                [],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
            "MarketReport.ReportCreateRequest": messages_verifier(
                [],
                ["Warning1", "Warning2"],
                [
                    "Info1",
                    "Info2",
                    "Successfully logged request for Report BSP_ResourceList. Please use transaction ID derpderp for further reference.",
                ],
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
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
            "MarketData.MarketSubmit.OfferData[0]": messages_verifier(
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
            "MarketData.MarketSubmit.OfferData[0].OfferStack[0]": messages_verifier(
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
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
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                ["ErrorCode1", "ErrorCode2"],
                ["Warning1", "Warning2"],
                ["Info1", "Info2"],
            ),
        },
    )


def verify_response_common(data: ResponseCommon, success: bool, validation: ValidationStatus):
    """Verify that the response common fields are as we expect."""
    assert data.success == success
    assert data.validation == validation
