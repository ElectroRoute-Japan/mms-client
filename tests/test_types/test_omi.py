"""Tests the functionality of the mms_client.types.omi module."""

from pendulum import Date

from mms_client.types.omi import MarketQuery
from mms_client.types.omi import MarketSubmit
from tests.testutils import verify_omi_market_query
from tests.testutils import verify_omi_market_submit


def test_market_submit_defaults():
    """Test that the MarketSubmit class initializes and converts to XML as we expect."""
    # First, create a new market submit request
    request = MarketSubmit(
        date=Date(2019, 8, 30),
        participant="F100",
        user="FAKEUSER",
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<MarketSubmit Date="2019-08-30" ParticipantName="F100" UserName="FAKEUSER"/>"""
    verify_omi_market_submit(request, Date(2019, 8, 30), "F100", "FAKEUSER")


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
    assert data == b"""<MarketQuery Date="2019-08-30" ParticipantName="F100" UserName="FAKEUSER"/>"""
    verify_omi_market_query(request, Date(2019, 8, 30), "F100", "FAKEUSER")
