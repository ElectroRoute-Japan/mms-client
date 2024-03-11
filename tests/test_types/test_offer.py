"""Tests the functionality in the mms_client.types.offer module."""

from typing import Optional

from pendulum import DateTime

from mms_client.types.enums import AreaCode
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferQuery
from mms_client.types.offer import OfferStack


def test_offer_submit_defaults():
    """Test that the OfferData class initializes and converts to a dictionary as we expect."""
    # First, create a new offer data request
    request = OfferData(
        OfferStack=[OfferStack(StackNumber=1, OfferUnitPrice=100, MinimumQuantityInKw=100)],
        ResourceName="FAKE_RESO",
        StartTime=DateTime(2019, 8, 30, 3, 24, 15),
        EndTime=DateTime(2019, 9, 30, 3, 24, 15),
        Direction=Direction.BUY,
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_offer_data(
        request,
        [offer_stack_verifier(1, 100, 100)],
        "FAKE_RESO",
        DateTime(2019, 8, 30, 3, 24, 15),
        DateTime(2019, 9, 30, 3, 24, 15),
        Direction.BUY,
    )
    assert data == {
        "OfferStack": [{"StackNumber": 1, "OfferUnitPrice": 100, "MinimumQuantityInKw": 100}],
        "ResourceName": "FAKE_RESO",
        "StartTime": DateTime(2019, 8, 30, 3, 24, 15),
        "EndTime": DateTime(2019, 9, 30, 3, 24, 15),
        "Direction": Direction.BUY,
    }


def test_offer_submit_full():
    """Test that the OfferData class initializes and converts to a dictionary as we expect."""
    # First, create a new offer data request
    request = OfferData(
        OfferStack=[
            OfferStack(
                StackNumber=1,
                MinimumQuantityInKw=100,
                PrimaryOfferQuantityInKw=150,
                Secondary1OfferQuantityInKw=200,
                Secondary2OfferQuantityInKw=250,
                Tertiary1OfferQuantityInKw=300,
                Tertiary2OfferQuantityInKw=350,
                OfferUnitPrice=100,
                OfferId="FAKE_ID",
            )
        ],
        ResourceName="FAKE_RESO",
        StartTime=DateTime(2019, 8, 30, 3, 24, 15),
        EndTime=DateTime(2019, 9, 30, 3, 24, 15),
        Direction=Direction.BUY,
        DrPatternNumber=12,
        BspParticipantName="F100",
        CompanyShortName="偽会社",
        OperatorCode="FAKE",
        Area=AreaCode.CHUBU,
        ResourceShortName="偽電力",
        SystemCode="FSYS0",
        SubmissionTime=DateTime(2019, 8, 30, 3, 24, 15),
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_offer_data(
        request,
        [offer_stack_verifier(1, 100, 100, 150, 200, 250, 300, 350, "FAKE_ID")],
        "FAKE_RESO",
        DateTime(2019, 8, 30, 3, 24, 15),
        DateTime(2019, 9, 30, 3, 24, 15),
        Direction.BUY,
        12,
        "F100",
        "偽会社",
        "FAKE",
        AreaCode.CHUBU,
        "偽電力",
        "FSYS0",
        DateTime(2019, 8, 30, 3, 24, 15),
    )
    assert data == {
        "OfferStack": [
            {
                "StackNumber": 1,
                "MinimumQuantityInKw": 100,
                "PrimaryOfferQuantityInKw": 150,
                "Secondary1OfferQuantityInKw": 200,
                "Secondary2OfferQuantityInKw": 250,
                "Tertiary1OfferQuantityInKw": 300,
                "Tertiary2OfferQuantityInKw": 350,
                "OfferUnitPrice": 100,
                "OfferId": "FAKE_ID",
            }
        ],
        "ResourceName": "FAKE_RESO",
        "StartTime": DateTime(2019, 8, 30, 3, 24, 15),
        "EndTime": DateTime(2019, 9, 30, 3, 24, 15),
        "Direction": Direction.BUY,
        "DrPatternNumber": 12,
        "BspParticipantName": "F100",
        "CompanyShortName": "偽会社",
        "OperatorCode": "FAKE",
        "Area": AreaCode.CHUBU,
        "ResourceShortName": "偽電力",
        "SystemCode": "FSYS0",
        "SubmissionTime": DateTime(2019, 8, 30, 3, 24, 15),
    }


def test_offer_cancel():
    """Test that the OfferCancel class initializes and converts to a dictionary as we expect."""
    # First, create a new offer cancel request
    request = OfferCancel(
        ResourceName="FAKE_RESO",
        StartTime=DateTime(2019, 8, 30, 3, 24, 15),
        EndTime=DateTime(2019, 9, 30, 3, 24, 15),
        MarketType=MarketType.WEEK_AHEAD,
    )

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    assert request.resource == "FAKE_RESO"
    assert request.start == DateTime(2019, 8, 30, 3, 24, 15)
    assert request.end == DateTime(2019, 9, 30, 3, 24, 15)
    assert request.market_type == MarketType.WEEK_AHEAD
    assert data == {
        "ResourceName": "FAKE_RESO",
        "StartTime": DateTime(2019, 8, 30, 3, 24, 15),
        "EndTime": DateTime(2019, 9, 30, 3, 24, 15),
        "MarketType": MarketType.WEEK_AHEAD,
    }


def test_offer_query_defaults():
    """Test that the OfferQuery class initializes and converts to a dictionary as we expect."""
    # First, create a new offer query request
    request = OfferQuery(MarketType=MarketType.WEEK_AHEAD)

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_offer_query(request, MarketType.WEEK_AHEAD)
    assert data == {
        "MarketType": MarketType.WEEK_AHEAD,
    }


def test_offer_query_full():
    """Test that the OfferQuery class initializes and converts to a dictionary as we expect."""
    # First, create a new offer query request
    request = OfferQuery(MarketType=MarketType.WEEK_AHEAD, Area=AreaCode.CHUBU, ResourceName="FAKE_RESO")

    # Next, convert the request to a dictionary
    data = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    # Finally, verify that the request was created with the correct parameters
    verify_offer_query(request, MarketType.WEEK_AHEAD, AreaCode.CHUBU, "FAKE_RESO")
    assert data == {
        "MarketType": MarketType.WEEK_AHEAD,
        "Area": AreaCode.CHUBU,
        "ResourceName": "FAKE_RESO",
    }


def verify_offer_data(
    request: OfferData,
    stack_verifiers: list,
    resource: str,
    start: DateTime,
    end: DateTime,
    direction: Direction,
    pattern: Optional[int] = None,
    bsp_participant: Optional[str] = None,
    company_short_name: Optional[str] = None,
    operator: Optional[str] = None,
    area: Optional[AreaCode] = None,
    resource_short_name: Optional[str] = None,
    system_code: Optional[str] = None,
    submission_time: Optional[DateTime] = None,
):
    """Verify that the given offer data request has the expected parameters."""
    assert request.resource == resource
    assert request.start == start
    assert request.end == end
    assert request.direction == direction
    assert len(request.stack) == len(stack_verifiers)
    for stack, verifier in zip(request.stack, stack_verifiers):
        verifier(stack)
    verify_offer_data_optional(
        request,
        pattern_number=pattern,
        bsp_participant=bsp_participant,
        company_short_name=company_short_name,
        operator=operator,
        area=area,
        resource_short_name=resource_short_name,
        system_code=system_code,
        submission_time=submission_time,
    )


def verify_offer_data_optional(request: OfferData, **kwargs):
    """Verify that the given offer data request has the expected parameters."""
    for field, info in request.model_fields.items():
        if not info.is_required():
            if field in kwargs:
                assert getattr(request, field) == kwargs[field]
            else:
                assert getattr(request, field) is None


def offer_stack_verifier(
    number: int,
    price: float,
    quantity: float,
    primary: Optional[float] = None,
    seconday_1: Optional[float] = None,
    secondary_2: Optional[float] = None,
    tertiary_1: Optional[float] = None,
    tertiary_2: Optional[float] = None,
    id: Optional[str] = None,
):
    """Verify that the given offer stack has the expected parameters."""

    def inner(stack: OfferStack):
        assert stack.stack_number == number
        assert stack.unit_price == price
        assert stack.minimum_quantity_kw == quantity
        assert stack.primary_qty_kw == primary
        assert stack.secondary_1_qty_kw == seconday_1
        assert stack.secondary_2_qty_kw == secondary_2
        assert stack.tertiary_1_qty_kw == tertiary_1
        assert stack.tertiary_2_qty_kw == tertiary_2
        assert stack.id == id

    return inner


def verify_offer_query(
    req: OfferQuery, market_type: MarketType, area: Optional[AreaCode] = None, resource: Optional[str] = None
):
    """Verify that the OfferQuery was created with the correct parameters."""
    assert req.market_type == market_type
    assert req.area == area
    assert req.resource == resource
