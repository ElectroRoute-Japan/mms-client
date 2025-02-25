"""Tests the functionality of the mms_client.types.bup module."""

from decimal import Decimal

from pendulum import DateTime
from pendulum import Timezone

from mms_client.types.bup import AbcBand
from mms_client.types.bup import BalancingUnitPrice
from mms_client.types.bup import BalancingUnitPriceBand
from mms_client.types.bup import BalancingUnitPriceQuery
from mms_client.types.bup import BalancingUnitPriceSubmit
from mms_client.types.bup import Pattern
from mms_client.types.bup import StartupCostBand
from mms_client.types.bup import Status
from mms_client.types.enums import AreaCode
from tests.testutils import abc_band_verifier
from tests.testutils import bup_band_verifier
from tests.testutils import bup_verifier
from tests.testutils import pattern_data_verifier
from tests.testutils import read_request_file
from tests.testutils import startup_cost_band_verifier
from tests.testutils import verify_bup_query
from tests.testutils import verify_bup_submit


def test_bup_submit_defaults():
    """Test that the BalancingUnitPriceSubmit class serializes and converts to XML as we expect."""
    # First, create a new BUP submit request
    request = BalancingUnitPriceSubmit(
        resource_code="FAKE_RESO",
        start=DateTime(2024, 8, 15, 9),
        end=DateTime(2024, 8, 15, 12),
        patterns=[
            Pattern(
                number=1,
                status=Status.ACTIVE,
            )
        ],
    )

    # Now, serialize the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, assert that the XML is as we expect
    assert data == (
        b"""<BupSubmit ResourceName="FAKE_RESO" StartTime="2024-08-15T09:00:00" EndTime="2024-08-15T12:00:00">"""
        b"""<PatternData PatternNo="1" PatternStatus="1"/></BupSubmit>"""
    )
    verify_bup_submit(
        request,
        "FAKE_RESO",
        DateTime(2024, 8, 15, 9, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 8, 15, 12, tzinfo=Timezone("Asia/Tokyo")),
        [pattern_data_verifier(1, Status.ACTIVE)],
    )


def test_bup_submit_full():
    """Test that the BalancingUnitPriceSubmit class serializes and converts to XML as we expect."""
    # First, create a new BUP submit request
    request = BalancingUnitPriceSubmit(
        resource_code="FAKE_RESO",
        start=DateTime(2024, 8, 15, 9),
        end=DateTime(2024, 8, 15, 12),
        participant_name="F100",
        company="偽会社",
        area=AreaCode.TOKYO,
        resource_name="偽電力",
        system_code="FSYS0",
        patterns=[
            Pattern(
                number=1,
                status=Status.ACTIVE,
                remarks="Some remarks",
                balancing_unit_profile=BalancingUnitPrice(
                    v4_unit_price=Decimal("95.95"),
                    bands=[
                        BalancingUnitPriceBand(
                            number=2,
                            from_capacity=Decimal("100"),
                            v1_unit_price=Decimal("200"),
                            v2_unit_price=Decimal("300"),
                        )
                    ],
                ),
                abc=[
                    AbcBand(
                        number=3,
                        from_capacity=Decimal("400"),
                        a=Decimal("400.50"),
                        b=Decimal("400.60"),
                        c=Decimal("400.70"),
                    )
                ],
                startup_costs=[
                    StartupCostBand(
                        number=4,
                        stop_time_hours=90,
                        v3_unit_price=Decimal("500"),
                        remarks="Some more remarks",
                    )
                ],
            )
        ],
    )

    # Now, serialize the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, assert that the XML is as we expect
    assert data == read_request_file("bup_submit_full.xml").encode("utf-8")
    verify_bup_submit(
        request,
        "FAKE_RESO",
        DateTime(2024, 8, 15, 9, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 8, 15, 12, tzinfo=Timezone("Asia/Tokyo")),
        [
            pattern_data_verifier(
                1,
                Status.ACTIVE,
                "Some remarks",
                bup_verifier(Decimal("95.95"), [bup_band_verifier(2, Decimal("100"), Decimal("200"), Decimal("300"))]),
                [abc_band_verifier(3, Decimal("400"), Decimal("400.50"), Decimal("400.60"), Decimal("400.70"))],
                [startup_cost_band_verifier(4, 90, Decimal("500"), "Some more remarks")],
            )
        ],
        participant_name="F100",
        company="偽会社",
        area=AreaCode.TOKYO,
        resource_name="偽電力",
        system_code="FSYS0",
    )


def test_bup_query_defaults():
    """Test that the BalancingUnitPriceQuery class serializes and converts to XML as we expect."""
    # First, create a new BUP query
    request = BalancingUnitPriceQuery(
        resource_code="FAKE_RESO",
        start=DateTime(2024, 8, 15, 9),
        end=DateTime(2024, 8, 15, 12),
    )

    # Now, serialize it to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, check that it matches what we expect
    assert (
        data
        == b"""<BupQuery ResourceName="FAKE_RESO" StartTime="2024-08-15T09:00:00" EndTime="2024-08-15T12:00:00"/>"""
    )
    verify_bup_query(
        request,
        "FAKE_RESO",
        DateTime(2024, 8, 15, 9, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 8, 15, 12, tzinfo=Timezone("Asia/Tokyo")),
    )


def test_bup_query_full():
    """Test that the BalancingUnitPriceQuery class serializes and converts to XML as we expect."""
    # First, create a new BUP query
    request = BalancingUnitPriceQuery(
        resource_code="FAKE_RESO",
        start=DateTime(2024, 8, 15, 9),
        end=DateTime(2024, 8, 15, 12),
        is_default=False,
    )

    # Now, serialize it to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, check that it matches what we expect
    assert (
        data
        == b"""<BupQuery StandingFlag="false" ResourceName="FAKE_RESO" StartTime="2024-08-15T09:00:00" EndTime="2024-08-15T12:00:00"/>"""
    )
    verify_bup_query(
        request,
        "FAKE_RESO",
        DateTime(2024, 8, 15, 9, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 8, 15, 12, tzinfo=Timezone("Asia/Tokyo")),
        False,
    )
