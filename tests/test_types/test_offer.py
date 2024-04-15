"""Tests the functionality in the mms_client.types.offer module."""

from pendulum import DateTime

from mms_client.types.enums import AreaCode
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferQuery
from mms_client.types.offer import OfferStack
from tests.testutils import offer_stack_verifier
from tests.testutils import verify_offer_cancel
from tests.testutils import verify_offer_data
from tests.testutils import verify_offer_query


def test_offer_submit_defaults():
    """Test that the OfferData class initializes and converts to XML as we expect."""
    # First, create a new offer data request
    request = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2019, 8, 30, 3, 24, 15),
        end=DateTime(2019, 9, 30, 3, 24, 15),
        direction=Direction.SELL,
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_offer_data(
        request,
        [offer_stack_verifier(1, 100, 100)],
        "FAKE_RESO",
        DateTime(2019, 8, 30, 3, 24, 15),
        DateTime(2019, 9, 30, 3, 24, 15),
        Direction.SELL,
    )
    assert (
        data
        == b"""<OfferData ResourceName="FAKE_RESO" StartTime="2019-08-30T03:24:15" EndTime="2019-09-30T03:24:15" Direction="1"><OfferStack StackNumber="1" MinimumQuantityInKw="100" OfferUnitPrice="100"/></OfferData>"""
    )


def test_offer_submit_full():
    """Test that the OfferData class initializes and converts to XML as we expect."""
    # First, create a new offer data request
    request = OfferData(
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
        end=DateTime(2019, 9, 30, 3, 24, 15),
        direction=Direction.SELL,
        pattern_number=12,
        bsp_participant="F100",
        company_short_name="偽会社",
        operator="FAKE",
        area=AreaCode.CHUBU,
        resource_short_name="偽電力",
        system_code="FSYS0",
        submission_time=DateTime(2019, 8, 30, 3, 24, 15),
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_offer_data(
        request,
        [offer_stack_verifier(1, 100, 100, 150, 200, 250, 300, 350, "FAKE_ID")],
        "FAKE_RESO",
        DateTime(2019, 8, 30, 3, 24, 15),
        DateTime(2019, 9, 30, 3, 24, 15),
        Direction.SELL,
        12,
        "F100",
        "偽会社",
        "FAKE",
        AreaCode.CHUBU,
        "偽電力",
        "FSYS0",
        DateTime(2019, 8, 30, 3, 24, 15),
    )
    assert data == (
        """<OfferData ResourceName="FAKE_RESO" StartTime="2019-08-30T03:24:15" EndTime="2019-09-30T03:24:15" """
        """Direction="1" DrPatternNumber="12" BspParticipantName="F100" CompanyShortName="偽会社" OperatorCode="FAKE" """
        """Area="04" ResourceShortName="偽電力" SystemCode="FSYS0" SubmissionTime="2019-08-30T03:24:15"><OfferStack """
        """StackNumber="1" MinimumQuantityInKw="100" PrimaryOfferQuantityInKw="150" Secondary1OfferQuantityInKw="200" """
        """Secondary2OfferQuantityInKw="250" Tertiary1OfferQuantityInKw="300" Tertiary2OfferQuantityInKw="350" """
        """OfferUnitPrice="100" OfferId="FAKE_ID"/></OfferData>"""
    ).encode("UTF-8")


def test_offer_cancel():
    """Test that the OfferCancel class initializes and converts to XML as we expect."""
    # First, create a new offer cancel request
    request = OfferCancel(
        resource="FAKE_RESO",
        start=DateTime(2019, 8, 30, 3, 24, 15),
        end=DateTime(2019, 9, 30, 3, 24, 15),
        market_type=MarketType.WEEK_AHEAD,
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_offer_cancel(
        request, "FAKE_RESO", DateTime(2019, 8, 30, 3, 24, 15), DateTime(2019, 9, 30, 3, 24, 15), MarketType.WEEK_AHEAD
    )
    assert data == (
        b"""<OfferCancel ResourceName="FAKE_RESO" StartTime="2019-08-30T03:24:15" EndTime="2019-09-30T03:24:15" """
        b"""MarketType="WAM"/>"""
    )


def test_offer_query_defaults():
    """Test that the OfferQuery class initializes and converts to XML as we expect."""
    # First, create a new offer query request
    request = OfferQuery(market_type=MarketType.WEEK_AHEAD)

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_offer_query(request, MarketType.WEEK_AHEAD)
    assert data == b"""<OfferQuery MarketType="WAM"/>"""


def test_offer_query_full():
    """Test that the OfferQuery class initializes and converts to XML as we expect."""
    # First, create a new offer query request
    request = OfferQuery(market_type=MarketType.WEEK_AHEAD, area=AreaCode.CHUBU, resource="FAKE_RESO")

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_offer_query(request, MarketType.WEEK_AHEAD, AreaCode.CHUBU, "FAKE_RESO")
    assert data == b"""<OfferQuery MarketType="WAM" ResourceName="FAKE_RESO" Area="04"/>"""
