"""Tests the functionality in the mms_client.types.award module."""

from decimal import Decimal

from pendulum import DateTime
from pendulum import Timezone

from mms_client.types.award import Award
from mms_client.types.award import AwardQuery
from mms_client.types.award import AwardResponse
from mms_client.types.award import AwardResult
from mms_client.types.award import ContractResult
from mms_client.types.award import ContractSource
from mms_client.types.award import SubRequirement
from mms_client.types.enums import AreaCode
from mms_client.types.enums import BooleanFlag
from mms_client.types.enums import CommandMonitorMethod
from mms_client.types.enums import Direction
from mms_client.types.enums import ResourceType
from mms_client.types.market import MarketType
from tests.testutils import award_result_verifier
from tests.testutils import award_verifier
from tests.testutils import read_request_file
from tests.testutils import verify_award_query
from tests.testutils import verify_award_response


def test_award_results_query_defaults():
    """Test that the AwardQuery class initializes and converts to XML as we expect."""
    # First, create a new award results query request
    request = AwardQuery(
        market_type=MarketType.DAY_AHEAD,
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == (
        b"""<AwardResultsQuery MarketType="DAM" StartTime="2024-04-12T15:00:00+09:00" """
        b"""EndTime="2024-04-12T18:00:00+09:00"/>"""
    )
    verify_award_query(
        request,
        MarketType.DAY_AHEAD,
        DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
    )


def test_award_results_query_full():
    """Test that the AwardQuery class initializes and converts to XML as we expect."""
    # First, create a new award results query request
    request = AwardQuery(
        market_type=MarketType.DAY_AHEAD,
        area=AreaCode.TOKYO,
        linked_area=AreaCode.TOHOKU,
        resource="FAKE_RESO",
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        gate_closed=BooleanFlag.YES,
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == (
        b"""<AwardResultsQuery MarketType="DAM" Area="03" LinkedArea="02" ResourceName="FAKE_RESO" """
        b"""StartTime="2024-04-12T15:00:00+09:00" EndTime="2024-04-12T18:00:00+09:00" AfterGC="1"/>"""
    )
    verify_award_query(
        request,
        MarketType.DAY_AHEAD,
        DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        area=AreaCode.TOKYO,
        linked_area=AreaCode.TOHOKU,
        resource="FAKE_RESO",
        gate_closed=BooleanFlag.YES,
    )


def test_award_results_response_defaults():
    """Test that the AwardResponse class initializes and converts to XML as we expect."""
    # First, create a new award results response
    response = AwardResponse(
        market_type=MarketType.DAY_AHEAD,
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
    )

    # Next, convert the response to XML
    data = response.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the response was created with the correct parameters
    assert data == (
        b"""<AwardResultsQuery MarketType="DAM" StartTime="2024-04-12T15:00:00+09:00" """
        b"""EndTime="2024-04-12T18:00:00+09:00"/>"""
    )
    verify_award_response(
        response,
        MarketType.DAY_AHEAD,
        DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
    )


def test_award_results_response_full():
    """Test that the AwardResponse class initializes and converts to XML as we expect."""
    # First, create a new award results response
    response = AwardResponse(
        market_type=MarketType.DAY_AHEAD,
        area=AreaCode.TOKYO,
        linked_area=AreaCode.TOHOKU,
        resource="FAKE_RESO",
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        gate_closed=BooleanFlag.YES,
        results=[
            AwardResult(
                start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
                end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
                direction=Direction.SELL,
                data=[
                    Award(
                        contract_id="156098uqt3qawldefjT",
                        jbms_id=4235230998,
                        area=AreaCode.TOKYO,
                        linked_area=AreaCode.TOHOKU,
                        resource="FAKE_RESO",
                        resource_short_name="偽電力",
                        system_code="FSYS0",
                        resource_type=ResourceType.THERMAL,
                        pattern_number=2,
                        pattern_name="偽パターン",
                        bsp_participant="F100",
                        company_short_name="偽会社",
                        operator="FAKE",
                        primary_secondary_1_control_method=CommandMonitorMethod.OFFLINE,
                        secondary_2_tertiary_control_method=CommandMonitorMethod.SIMPLE_COMMAND,
                        offer_price=Decimal("42.15"),
                        contract_price=Decimal("69.44"),
                        performance_evaluation_coefficient=Decimal("35.79"),
                        corrected_unit_price=Decimal("199.99"),
                        sub_requirement=SubRequirement.PRIAMRY_SECONDARY,
                        primary_offer_qty=5000,
                        secondary_1_offer_qty=6000,
                        secondary_2_offer_qty=7000,
                        tertiary_1_offer_qty=8000,
                        tertiary_2_offer_qty=9000,
                        primary_award_qty=5000,
                        secondary_1_award_qty=5001,
                        secondary_2_award_qty=5002,
                        tertiary_1_award_qty=5003,
                        tertiary_2_award_qty=5004,
                        primary_contract_qty=5000,
                        secondary_1_contract_qty=4000,
                        secondary_2_contract_qty=3000,
                        tertiary_1_contract_qty=2000,
                        tertiary_2_contract_qty=1000,
                        primary_valid_qty=5010,
                        secondary_1_valid_qty=5020,
                        secondary_2_valid_qty=5030,
                        tertiary_1_valid_qty=5040,
                        compound_valid_qty=9001,
                        primary_invalid_qty=4001,
                        secondary_1_invalid_qty=4002,
                        secondary_2_invalid_qty=4003,
                        tertiary_1_invalid_qty=4004,
                        negative_baseload_file="W9_3010_20240411_15_AS490_FAKE_NEG.xml",
                        positive_baseload_file="W9_3010_20240411_15_AS490_FAKE_POS.xml",
                        submission_time=DateTime(2024, 4, 10, 22, 34, 44, tzinfo=Timezone("Asia/Tokyo")),
                        offer_award_level=ContractResult.PARTIAL,
                        offer_id="FAKE_ID",
                        contract_source=ContractSource.SWITCHING,
                        gate_closed=BooleanFlag.YES,
                    )
                ],
            )
        ],
    )

    # Next, convert the response to XML
    data = response.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the response was created with the correct parameters
    assert data == read_request_file("awards_response_full.xml").encode("UTF-8")
    verify_award_response(
        response,
        market_type=MarketType.DAY_AHEAD,
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        area=AreaCode.TOKYO,
        linked_area=AreaCode.TOHOKU,
        resource="FAKE_RESO",
        gate_closed=BooleanFlag.YES,
        result_verifiers=[
            award_result_verifier(
                start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
                end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
                direction=Direction.SELL,
                award_verifiers=[
                    award_verifier(
                        contract_id="156098uqt3qawldefjT",
                        jbms_id=4235230998,
                        area=AreaCode.TOKYO,
                        resource="FAKE_RESO",
                        resource_name="偽電力",
                        system_code="FSYS0",
                        resource_type=ResourceType.THERMAL,
                        bsp_participant="F100",
                        company_name="偽会社",
                        operator="FAKE",
                        offer_price=Decimal("42.15"),
                        contract_price=Decimal("69.44"),
                        eval_coeff=Decimal("35.79"),
                        corrected_price=Decimal("199.99"),
                        result=ContractResult.PARTIAL,
                        source=ContractSource.SWITCHING,
                        gate_closed=BooleanFlag.YES,
                        linked_area=AreaCode.TOHOKU,
                        pattern_number=2,
                        pattern_name="偽パターン",
                        primary_secondary_1_control_method=CommandMonitorMethod.OFFLINE,
                        secondary_2_tertiary_control_method=CommandMonitorMethod.SIMPLE_COMMAND,
                        sub_requirement=SubRequirement.PRIAMRY_SECONDARY,
                        primary_offer_qty=5000,
                        secondary_1_offer_qty=6000,
                        secondary_2_offer_qty=7000,
                        tertiary_1_offer_qty=8000,
                        tertiary_2_offer_qty=9000,
                        primary_award_qty=5000,
                        secondary_1_award_qty=5001,
                        secondary_2_award_qty=5002,
                        tertiary_1_award_qty=5003,
                        tertiary_2_award_qty=5004,
                        primary_contract_qty=5000,
                        secondary_1_contract_qty=4000,
                        secondary_2_contract_qty=3000,
                        tertiary_1_contract_qty=2000,
                        tertiary_2_contract_qty=1000,
                        primary_valid_qty=5010,
                        secondary_1_valid_qty=5020,
                        secondary_2_valid_qty=5030,
                        tertiary_1_valid_qty=5040,
                        compound_valid_qty=9001,
                        primary_invalid_qty=4001,
                        secondary_1_invalid_qty=4002,
                        secondary_2_invalid_qty=4003,
                        tertiary_1_invalid_qty=4004,
                        negative_baseload_file="W9_3010_20240411_15_AS490_FAKE_NEG.xml",
                        positive_baseload_file="W9_3010_20240411_15_AS490_FAKE_POS.xml",
                        submission_time=DateTime(2024, 4, 10, 22, 34, 44, tzinfo=Timezone("Asia/Tokyo")),
                        offer_id="FAKE_ID",
                    )
                ],
            ),
        ],
    )
