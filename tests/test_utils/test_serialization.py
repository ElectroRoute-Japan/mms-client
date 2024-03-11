"""Tests the functionality in the mms_client.utils.serialization module."""

from base64 import b64decode
from datetime import date as Date

from pendulum import DateTime

from mms_client.types.enums import AreaCode
from mms_client.types.market import MarketCancel
from mms_client.types.market import MarketQuery
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferQuery
from mms_client.types.offer import OfferStack
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer


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
        direction=Direction.BUY,
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
        Date=Date(2019, 8, 29),
        MarketType=MarketType.DAY_AHEAD,
        ParticipantName="F100",
        UserName="FAKEUSER",
        NumOfDays=1,
    )

    serializer = Serializer(SchemaType.MARKET, "MarketData")
    data = serializer.serialize(request, offer)

    # Finally, verify that the request was serialized as we expect
    assert data == b""
    assert b64decode(data) == b""""""
