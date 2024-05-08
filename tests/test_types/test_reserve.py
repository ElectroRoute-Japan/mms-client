"""Tests the functionality in the mms_client.types.reserve module."""

from pydantic_extra_types.pendulum_dt import DateTime

from mms_client.types.enums import AreaCode
from mms_client.types.enums import Direction
from mms_client.types.market import MarketType
from mms_client.types.reserve import Requirement
from mms_client.types.reserve import ReserveRequirement
from mms_client.types.reserve import ReserveRequirementQuery
from tests.testutils import read_request_file
from tests.testutils import requirement_verifier
from tests.testutils import verify_reserve_requirement
from tests.testutils import verify_reserve_requirement_query


def test_reserve_requirement_query_defaults():
    """Test that the ReserveRequirementQuery class initializes and converts to XML as expected."""
    # First, create a new reserve requirement query request
    request = ReserveRequirementQuery(
        market_type=MarketType.DAY_AHEAD,
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<ReserveRequirementQuery MarketType="DAM"/>"""
    verify_reserve_requirement_query(request, MarketType.DAY_AHEAD)


def test_reserve_requirement_query_full():
    """Test that the ReserveRequirementQuery class initializes and converts to XML as expected."""
    # First, create a new reserve requirement query request
    request = ReserveRequirementQuery(
        market_type=MarketType.DAY_AHEAD,
        area=AreaCode.TOKYO,
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<ReserveRequirementQuery MarketType="DAM" Area="03"/>"""
    verify_reserve_requirement_query(request, MarketType.DAY_AHEAD, AreaCode.TOKYO)


def test_reserve_requirement_defaults():
    """Test that the ReserveRequirement class initializes and converts to XML as expected."""
    # First, create a new reserve requirement request
    request = ReserveRequirement(
        area=AreaCode.TOKYO,
        requirements=[
            Requirement(
                start=DateTime(2024, 4, 12, 15),
                end=DateTime(2024, 4, 12, 18),
                direction=Direction.SELL,
            ),
        ],
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == (
        b"""<ReserveRequirement Area="03"><Requirement StartTime="2024-04-12T15:00:00" EndTime="2024-04-12T18:00:00" """
        b"""Direction="1"/></ReserveRequirement>"""
    )
    verify_reserve_requirement(
        request, AreaCode.TOKYO, [requirement_verifier(DateTime(2024, 4, 12, 15), DateTime(2024, 4, 12, 18))]
    )


def test_reserve_requirement_full():
    """Test that the ReserveRequirement class initializes and converts to XML as expected."""
    # First, create a new reserve requirement request
    request = ReserveRequirement(
        area=AreaCode.TOKYO,
        requirements=[
            Requirement(
                start=DateTime(2024, 4, 12, 15),
                end=DateTime(2024, 4, 12, 18),
                direction=Direction.SELL,
                primary_qty_kw=100,
                secondary_1_qty_kw=200,
                secondary_2_qty_kw=300,
                tertiary_1_qty_kw=400,
                tertiary_2_qty_kw=500,
                primary_secondary_1_qty_kw=600,
                primary_secondary_2_qty_kw=700,
                primary_tertiary_1_qty_kw=800,
            ),
        ],
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == read_request_file("reserve_requirement_full.xml", False)
    verify_reserve_requirement(
        request,
        AreaCode.TOKYO,
        [
            requirement_verifier(
                DateTime(2024, 4, 12, 15), DateTime(2024, 4, 12, 18), 100, 200, 300, 400, 500, 600, 700, 800
            )
        ],
    )
