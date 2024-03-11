"""Tests the functionality in the mms_client.types.market module."""

from datetime import date as Date
from typing import Optional

from mms_client.types.market import BaseMarketRequest
from mms_client.types.market import MarketCancel
from mms_client.types.market import MarketQuery
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType


def test_market_query_defaults():
    """Test that the MarketQuery class initializes and converts to a dictionary as we expect."""
    # First, create a new market query request
    request = MarketQuery(
        Date=Date(2019, 8, 30),
        ParticipantName="F100",
        UserName="FAKEUSER",
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_market_query(request, Date(2019, 8, 30), "F100", "FAKEUSER")
    assert data == {
        "Date": Date(2019, 8, 30),
        "ParticipantName": "F100",
        "UserName": "FAKEUSER",
    }


def test_market_query_full():
    """Test that the MarketQuery class initializes and converts to a dictionary as we expect."""
    # First, create a new market query request
    request = MarketQuery(
        Date=Date(2019, 8, 30),
        ParticipantName="F100",
        UserName="FAKEUSER",
        MarketType=MarketType.WEEK_AHEAD,
        NumOfDays=4,
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_market_query(request, Date(2019, 8, 30), "F100", "FAKEUSER", MarketType.WEEK_AHEAD, 4)
    assert data == {
        "Date": Date(2019, 8, 30),
        "ParticipantName": "F100",
        "UserName": "FAKEUSER",
        "MarketType": MarketType.WEEK_AHEAD,
        "NumOfDays": 4,
    }


def test_market_submit_defaults():
    """Test that the MarketSubmit class initializes and converts to a dictionary as we expect."""
    # First, create a new market submit request
    request = MarketSubmit(
        Date=Date(2019, 8, 30),
        ParticipantName="F100",
        UserName="FAKEUSER",
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_market_submit(request, Date(2019, 8, 30), "F100", "FAKEUSER")
    assert data == {
        "Date": Date(2019, 8, 30),
        "ParticipantName": "F100",
        "UserName": "FAKEUSER",
    }


def test_market_submit_full():
    """Test that the MarketSubmit class initializes and converts to a dictionary as we expect."""
    # First, create a new market submit request
    request = MarketSubmit(
        Date=Date(2019, 8, 30),
        ParticipantName="F100",
        UserName="FAKEUSER",
        MarketType=MarketType.WEEK_AHEAD,
        NumOfDays=4,
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_market_submit(request, Date(2019, 8, 30), "F100", "FAKEUSER", MarketType.WEEK_AHEAD, 4)
    assert data == {
        "Date": Date(2019, 8, 30),
        "ParticipantName": "F100",
        "UserName": "FAKEUSER",
        "MarketType": MarketType.WEEK_AHEAD,
        "NumOfDays": 4,
    }


def test_market_cancel_defaults():
    """Test that the MarketCancel class initializes and converts to a dictionary as we expect."""
    # First, create a new market cancel request
    request = MarketCancel(
        Date=Date(2019, 8, 30),
        ParticipantName="F100",
        UserName="FAKEUSER",
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_market_cancel(request, Date(2019, 8, 30), "F100", "FAKEUSER")
    assert data == {
        "Date": Date(2019, 8, 30),
        "ParticipantName": "F100",
        "UserName": "FAKEUSER",
    }


def test_market_cancel_full():
    """Test that the MarketCancel class initializes and converts to a dictionary as we expect."""
    # First, create a new market cancel request
    request = MarketCancel(
        Date=Date(2019, 8, 30),
        ParticipantName="F100",
        UserName="FAKEUSER",
        MarketType=MarketType.WEEK_AHEAD,
        NumOfDays=4,
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_market_cancel(request, Date(2019, 8, 30), "F100", "FAKEUSER", MarketType.WEEK_AHEAD, 4)
    assert data == {
        "Date": Date(2019, 8, 30),
        "ParticipantName": "F100",
        "UserName": "FAKEUSER",
        "MarketType": MarketType.WEEK_AHEAD,
        "NumOfDays": 4,
    }


def verify_market_query(
    req: MarketQuery, date: Date, participant: str, user: str, market_type: Optional[MarketType] = None, days: int = 1
):
    """Verify that the MarketQuery was created with the correct parameters."""
    verify_base_market_request(req, date, participant, user, market_type)
    assert req.days == days


def verify_market_submit(
    req: MarketSubmit, date: Date, participant: str, user: str, market_type: Optional[MarketType] = None, days: int = 1
):
    """Verify that the MarketSubmit was created with the correct parameters."""
    verify_base_market_request(req, date, participant, user, market_type)
    assert req.days == days


def verify_market_cancel(
    req: MarketCancel, date: Date, participant: str, user: str, market_type: Optional[MarketType] = None, days: int = 1
):
    """Verify that the MarketCancel was created with the correct parameters."""
    verify_base_market_request(req, date, participant, user, market_type)
    assert req.days == days


def verify_base_market_request(
    req: BaseMarketRequest, date: Date, participant: str, user: str, market_type: Optional[MarketType] = None
):
    """Verify that the BaseMarketRequest was created with the correct parameters."""
    assert req.date == date
    assert req.participant == participant
    assert req.user == user
    assert req.market_type == market_type
