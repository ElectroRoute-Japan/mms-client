"""Tests the functionality in the mms_client.types.market module."""

from pendulum import Date

from mms_client.types.market import Defaults
from mms_client.types.market import MarketCancel
from mms_client.types.market import MarketQuery
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType
from tests.testutils import verify_market_cancel
from tests.testutils import verify_market_query
from tests.testutils import verify_market_submit


def test_market_query_defaults():
    """Test that the MarketQuery class initializes and converts to XML as we expect."""
    # First, create a new market query request
    request = MarketQuery(
        date=Date(2019, 8, 30),
        participant="F100",
        user="FAKEUSER",
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_market_query(request, Date(2019, 8, 30), "F100", "FAKEUSER", days=None)
    assert data == b"""<MarketQuery Date="2019-08-30" ParticipantName="F100" UserName="FAKEUSER"/>"""


def test_market_query_full():
    """Test that the MarketQuery class initializes and converts to XML as we expect."""
    # First, create a new market query request
    request = MarketQuery(
        date=Date(2019, 8, 30),
        participant="F100",
        user="FAKEUSER",
        days=4,
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_market_query(request, Date(2019, 8, 30), "F100", "FAKEUSER", 4)
    assert data == b"""<MarketQuery Date="2019-08-30" ParticipantName="F100" UserName="FAKEUSER" NumOfDays="4"/>"""


def test_market_submit_defaults():
    """Test that the MarketSubmit class initializes and converts to a dictionary as we expect."""
    # First, create a new market submit request
    request = MarketSubmit(
        date=Date(2019, 8, 30),
        participant="F100",
        user="FAKEUSER",
    )

    # Next, convert the request to a dictionary
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_market_submit(request, Date(2019, 8, 30), "F100", "FAKEUSER", days=None)
    assert data == b"""<MarketSubmit Date="2019-08-30" ParticipantName="F100" UserName="FAKEUSER"/>"""


def test_market_submit_full():
    """Test that the MarketSubmit class initializes and converts to a dictionary as we expect."""
    # First, create a new market submit request
    request = MarketSubmit(
        date=Date(2019, 8, 30),
        participant="F100",
        user="FAKEUSER",
        market_type=MarketType.COMPOUND,
        days=4,
        defaults=Defaults(is_default=True),
    )

    # Next, convert the request to a dictionary
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_market_submit(request, Date(2019, 8, 30), "F100", "FAKEUSER", MarketType.COMPOUND, 4)
    assert (
        data
        == b"""<MarketSubmit Date="2019-08-30" ParticipantName="F100" UserName="FAKEUSER" MarketType="DCM" NumOfDays="4"><StandingData StandingFlag="true"/></MarketSubmit>"""
    )


def test_market_cancel_defaults():
    """Test that the MarketCancel class initializes and converts to a dictionary as we expect."""
    # First, create a new market cancel request
    request = MarketCancel(
        date=Date(2019, 8, 30),
        participant="F100",
        user="FAKEUSER",
        market_type=MarketType.DAY_AHEAD,
    )

    # Next, convert the request to a dictionary
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_market_cancel(request, Date(2019, 8, 30), "F100", "FAKEUSER", MarketType.DAY_AHEAD)
    assert (
        data
        == b"""<MarketCancel Date="2019-08-30" ParticipantName="F100" UserName="FAKEUSER" MarketType="DAM" NumOfDays="1"/>"""
    )


def test_market_cancel_full():
    """Test that the MarketCancel class initializes and converts to a dictionary as we expect."""
    # First, create a new market cancel request
    request = MarketCancel(
        date=Date(2019, 8, 30),
        participant="F100",
        user="FAKEUSER",
        market_type=MarketType.COMPOUND,
        days=4,
    )

    # Next, convert the request to a dictionary
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    verify_market_cancel(request, Date(2019, 8, 30), "F100", "FAKEUSER", MarketType.COMPOUND, 4)
    assert (
        data
        == b"""<MarketCancel Date="2019-08-30" ParticipantName="F100" UserName="FAKEUSER" MarketType="DCM" NumOfDays="4"/>"""
    )
