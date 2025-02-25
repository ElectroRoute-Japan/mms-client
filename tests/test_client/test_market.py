"""Tests the functionality in the mms_client.services.market module."""

from decimal import Decimal

import pytest
import responses
from pendulum import Date
from pendulum import DateTime
from pendulum import Timezone

from mms_client.client import MmsClient
from mms_client.types.award import AwardQuery
from mms_client.types.award import ContractSource
from mms_client.types.award import SubRequirement
from mms_client.types.bup import AbcBand
from mms_client.types.bup import BalancingUnitPrice
from mms_client.types.bup import BalancingUnitPriceBand
from mms_client.types.bup import BalancingUnitPriceQuery
from mms_client.types.bup import BalancingUnitPriceSubmit
from mms_client.types.bup import Pattern
from mms_client.types.bup import StartupCostBand
from mms_client.types.bup import Status
from mms_client.types.enums import AreaCode
from mms_client.types.enums import BooleanFlag
from mms_client.types.enums import CommandMonitorMethod
from mms_client.types.enums import ContractResult
from mms_client.types.enums import Direction
from mms_client.types.enums import ResourceType
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferQuery
from mms_client.types.offer import OfferStack
from mms_client.types.reserve import ReserveRequirementQuery
from mms_client.types.settlement import SettlementQuery
from mms_client.types.transport import RequestType
from mms_client.utils.errors import AudienceError
from mms_client.utils.web import ClientType
from tests.testutils import abc_band_verifier
from tests.testutils import award_result_verifier
from tests.testutils import award_verifier
from tests.testutils import bup_band_verifier
from tests.testutils import bup_verifier
from tests.testutils import offer_stack_verifier
from tests.testutils import pattern_data_verifier
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import register_mms_request
from tests.testutils import requirement_verifier
from tests.testutils import settlementfile_verifier
from tests.testutils import startup_cost_band_verifier
from tests.testutils import verify_award_response
from tests.testutils import verify_bup_submit
from tests.testutils import verify_offer_cancel
from tests.testutils import verify_offer_data
from tests.testutils import verify_reserve_requirement
from tests.testutils import verify_settlement_results


@responses.activate
def test_query_reserve_requirements_works(mock_certificate):
    """Test that the query_reserve_requirements method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test reserve requirement query
    request = ReserveRequirementQuery(
        market_type=MarketType.DAY_AHEAD,
        area=AreaCode.TOKYO,
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "j/QJWIqedO/PWDHdHSa9MHDyHvqx0UIkcFc1CAzWRku+8mXL0UFLtI01zP0xZsvD3SUjktFf5VauyM5u+Ypc9vAip9PF17Msv/0bREeTD"
            "bWEWGgcFic7Mue5783DaWFvcgwLopH2DkqGCNTEknrnF9y0YIj0FNezMbC7LCZ7CV4akjXzJtTAcV71OcsyyG1uFmgz3Z8oumxctkYYfu"
            "JJIQyyipkwo6FCHsKpNnFVEe6HDo2jGYcNmRLUxJ7iJmKvfb6mo0/zn7NywyHRJ5ci8UILvQaqJguvZfwEgwOfGuoO9zI9tgtThP8gmTF"
            "PKWkH0UtEo/cCkFTIfxftC8FkCPv3SfNB9wo/jQphgwlYIlVKM6on0XP0DfI5HVZFQXssgsX5UfYdurPJIvaTP86VpoWyV6FwCjtv6k5n"
            "07QkMpulyQDtBP5HhYcIBTKb8mcnCrZ584aO0AfGHutlfFwMN5RjyFzxwu4hwpdn+69nuPSo68gavWZjQ/b5nhb7piW8CrxwT0CAl+C6J"
            "syU4lcFveLAyMjKMKfk8Ji+Vhr0c35GFf8MS5OhFTNLnvWIBIZfsqMyttEDscOMa4VfDx00bZRAQlOdn0rk0txCkoctWKIeA+xKiBXVfm"
            "shtPDFZbjnfm/TzeaHYROrK1IiJjqxvn54N4QdluHspXvdCDEeMLs="
        ),
        read_request_file("query_reserve_requirements_request.xml"),
        read_file("query_reserve_requirements_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to query reserve requirements with the valid client type; this should succeed
    resp = client.query_reserve_requirements(request, 1, Date(2024, 4, 12))

    # Finally, verify the response
    assert len(resp) == 1
    verify_reserve_requirement(
        resp[0],
        AreaCode.TOKYO,
        [
            requirement_verifier(
                DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
                DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
                100,
                200,
                300,
                400,
                500,
                600,
                700,
                800,
            )
        ],
    )


def test_put_offer_invalid_client(mock_certificate):
    """Test that the put_offer method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.TSO, mock_certificate, test=True)

    # Next, create our test offer data
    request = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2019, 8, 30, 3, 24, 15),
        end=DateTime(2019, 9, 30, 3, 24, 15),
        direction=Direction.SELL,
    )

    # Now, attempt to put an offer with the invalid client type; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.put_offer(request, MarketType.DAY_AHEAD, 1)

    # Finvally, verify the details of the raised exception
    assert str(ex_info.value) == "MarketSubmit_OfferData: Invalid client type, 'TSO' provided. Only 'BSP' is supported."


@responses.activate
def test_put_offer_works(mock_certificate):
    """Test that the put_offer method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test offer data
    request = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        direction=Direction.SELL,
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "z+shp4QJ9WmJG4tmB7FzYVu4TW8QclIF8n9Pp+VIu7Y/O/aySb0M6e4KGKuZrpy4eNiG1hPfM4nL6QXcgXoQFcsLMKyenYVyqW6kJOx9g"
            "uOiVWXlzbK/4d3pjaDR8RbEtEfJNGutAZ94G3rGnmfxg7EMLkOR3MpELZvbdZ0q+uYIeMaqD00jKHnUbF6qdTQO7grvLKaoJK6YODyqZB"
            "9ednzmMeGBuUP8zh1KF6k/p8x7LsM8FPbOvV7Bwuw9bPTxeAWcOnGiPycaBL/wW3iJfzIDX7k9xmd9f8UpgF6kxxAL4KxboF+gyiSezOb"
            "/DhUaTLiFZEw4jr993g2HsuNaV4E64jt6+XksUB8xNwsdtxfav7ItRoi/1/TWgAoHKK4bn9jBxk4hsEGJD3UwPzBxpyJD4flmfdwGZCp2"
            "/huDCItEh3Ej5GcVsUY5OjSglyogV3YwxZBVpWpMflxHRvtiYSGnCC+YCXedhu8nNm1vWwowGb8Pf31fagNT5PB+ghEu/DIe+PEr215FY"
            "2xMxYpmqzp5Vxcyg4aeC6A0XS2rT9XypZRrn+igIln23bCNYVAUpvk5a49CqRwPD+L4GEcGgmH16pCAwfSVvWvqxuzQ41iBsmw8qnXzlN"
            "JC1RFpRUagio2nL3LkRk2sF0iXeE9oi+70NGaDIJSIyPIV93Qg9RY="
        ),
        read_request_file("put_offer_request.xml"),
        read_file("put_offer_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to put an offer with the valid client type; this should succeed
    offer = client.put_offer(request, MarketType.DAY_AHEAD, 1, Date(2024, 3, 15))

    # Finally, verify the offer
    verify_offer_data(
        offer,
        [offer_stack_verifier(1, 100, 100, id="FAKE_ID")],
        "FAKE_RESO",
        DateTime(2024, 3, 15, 12, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 3, 15, 21, tzinfo=Timezone("Asia/Tokyo")),
        Direction.SELL,
        pattern=1,
        bsp_participant="F100",
        company_short_name="偽会社",
        operator="FAKE",
        area=AreaCode.CHUBU,
        resource_short_name="偽電力",
        system_code="FSYS0",
        submission_time=DateTime(2024, 3, 15, 11, 44, 15, tzinfo=Timezone("Asia/Tokyo")),
    )


def test_put_offers_invalid_client(mock_certificate):
    """Test that the put_offers method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.TSO, mock_certificate, test=True)

    # Next, create our test offer data
    request = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2019, 8, 30, 3, 24, 15),
        end=DateTime(2019, 9, 30, 3, 24, 15),
        direction=Direction.SELL,
    )

    # Now, attempt to put an offer with the invalid client type; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.put_offers([request], MarketType.DAY_AHEAD, 1)

    # Finvally, verify the details of the raised exception
    assert str(ex_info.value) == "MarketSubmit_OfferData: Invalid client type, 'TSO' provided. Only 'BSP' is supported."


@responses.activate
def test_put_offers_works(mock_certificate):
    """Test that the put_offer method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test offer data
    request = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        direction=Direction.SELL,
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "z+shp4QJ9WmJG4tmB7FzYVu4TW8QclIF8n9Pp+VIu7Y/O/aySb0M6e4KGKuZrpy4eNiG1hPfM4nL6QXcgXoQFcsLMKyenYVyqW6kJOx9g"
            "uOiVWXlzbK/4d3pjaDR8RbEtEfJNGutAZ94G3rGnmfxg7EMLkOR3MpELZvbdZ0q+uYIeMaqD00jKHnUbF6qdTQO7grvLKaoJK6YODyqZB"
            "9ednzmMeGBuUP8zh1KF6k/p8x7LsM8FPbOvV7Bwuw9bPTxeAWcOnGiPycaBL/wW3iJfzIDX7k9xmd9f8UpgF6kxxAL4KxboF+gyiSezOb"
            "/DhUaTLiFZEw4jr993g2HsuNaV4E64jt6+XksUB8xNwsdtxfav7ItRoi/1/TWgAoHKK4bn9jBxk4hsEGJD3UwPzBxpyJD4flmfdwGZCp2"
            "/huDCItEh3Ej5GcVsUY5OjSglyogV3YwxZBVpWpMflxHRvtiYSGnCC+YCXedhu8nNm1vWwowGb8Pf31fagNT5PB+ghEu/DIe+PEr215FY"
            "2xMxYpmqzp5Vxcyg4aeC6A0XS2rT9XypZRrn+igIln23bCNYVAUpvk5a49CqRwPD+L4GEcGgmH16pCAwfSVvWvqxuzQ41iBsmw8qnXzlN"
            "JC1RFpRUagio2nL3LkRk2sF0iXeE9oi+70NGaDIJSIyPIV93Qg9RY="
        ),
        read_request_file("put_offer_request.xml"),
        read_file("put_offer_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to put an offer with the valid client type; this should succeed
    offers = client.put_offers([request], MarketType.DAY_AHEAD, 1, Date(2024, 3, 15))

    # Finally, verify the offer
    assert len(offers) == 1
    verify_offer_data(
        offers[0],
        [offer_stack_verifier(1, 100, 100, id="FAKE_ID")],
        "FAKE_RESO",
        DateTime(2024, 3, 15, 12, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 3, 15, 21, tzinfo=Timezone("Asia/Tokyo")),
        Direction.SELL,
        pattern=1,
        bsp_participant="F100",
        company_short_name="偽会社",
        operator="FAKE",
        area=AreaCode.CHUBU,
        resource_short_name="偽電力",
        system_code="FSYS0",
        submission_time=DateTime(2024, 3, 15, 11, 44, 15, tzinfo=Timezone("Asia/Tokyo")),
    )


@responses.activate
def test_query_offers_works(mock_certificate):
    """Test that the query_offers method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test offer data
    request = OfferQuery(market_type=MarketType.DAY_AHEAD, area=AreaCode.CHUBU, resource="FAKE_RESO")

    # Register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "eBki+iSH6OaDGQSRkB6unDPyDxqMnpmZravPSYLztpaYqc1L8Zxx4ZcPFVbM2BJZ3CbKCw4urcRDsCA+4p5Lnx0BwCtCWCknFfrPyJfkg"
            "/VHixX2GJygyCzfY39Ysm3Lor8a5m5VjVukhiYG8roTE55wqivEzYX6mBDxSWSKx697c0Kmfy6lsIZaALxdLWMEnZwSgf4i/nSWdqaqFc"
            "/6oAmpHYkdp2woeXs4UTgG0BxPsoaDwhHH1HTqSzJqFexgilmOLMKo/9wg/zyEOiwOdp+chaaI4DEYhi7q+d6coFQiN0+pWh4+KA6PeHk"
            "QsaAVTurw60MVtw3CQ4EL5Od3lDutndkdVdwsW8/fbY0xsH1/uusqoZjhZine4oRTdOudP2y8pPhE65N//XP9Tgti7DU8I7CaQ9418FgZ"
            "/9u9N7Ut3W/CgwWVTuiTG3JJN8UvrO3833ANl0QlhY78az9rEa58MfpZ0mmaxNIH8Y55XqX2BDytsN6YUNlZHYFw0fe2qt+jRursDlbcb"
            "AvNn+AGUTEwAdLxzUiHbuEvX/i4Rc7R9mGm3F0XFA6OXb8EOrXCyPuerfpqbVEAW7WRSsEOB4tzq53VnJPbdsNHPD/5z2JdOkHwB2Ztfn"
            "qvAZ8yXx0B5FFyS6oiTZbD/tjdU1bGLPgc782d9zqFr4B1Gn7UDro="
        ),
        read_request_file("query_offers_request.xml"),
        read_file("put_offer_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to query offers with the valid client type; this should succeed
    offers = client.query_offers(request, 1, Date(2024, 3, 15))

    # Finally, verify the offer
    assert len(offers) == 1
    verify_offer_data(
        offers[0],
        [offer_stack_verifier(1, 100, 100, id="FAKE_ID")],
        "FAKE_RESO",
        DateTime(2024, 3, 15, 12, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 3, 15, 21, tzinfo=Timezone("Asia/Tokyo")),
        Direction.SELL,
        pattern=1,
        bsp_participant="F100",
        company_short_name="偽会社",
        operator="FAKE",
        area=AreaCode.CHUBU,
        resource_short_name="偽電力",
        system_code="FSYS0",
        submission_time=DateTime(2024, 3, 15, 11, 44, 15, tzinfo=Timezone("Asia/Tokyo")),
    )


def test_cancel_offer_invalid_client(mock_certificate):
    """Test that the cancel_offer method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.TSO, mock_certificate, test=True)

    # Next, create our test offer cancellation
    request = OfferCancel(
        resource="FAKE_RESO",
        start=DateTime(2019, 8, 30, 3, 24, 15),
        end=DateTime(2019, 9, 30, 3, 24, 15),
        market_type=MarketType.DAY_AHEAD,
    )

    # Now, attempt to cancel an offer with the invalid client type; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.cancel_offer(request, MarketType.DAY_AHEAD, 1)

    # Finvally, verify the details of the raised exception
    assert (
        str(ex_info.value) == "MarketCancel_OfferCancel: Invalid client type, 'TSO' provided. Only 'BSP' is supported."
    )


@responses.activate
def test_cancel_offer_works(mock_certificate):
    """Test that the cancel_offer method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test offer cancellation
    request = OfferCancel(
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        market_type=MarketType.DAY_AHEAD,
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "y1QlSIDeZjY21o00JTxT1HDJYbrNZExq1ZeM/O5dx3hDW9LA3dL9fAKEy/Pfkj2MzmP+f2/hwp7lSBkHhvrD9j/3D0jeTkv4sRVe7WQO6"
            "WybDwcN7uMDta2KHUkxO+i85KIUuEX4zKMm8JDwMjyXsiKZQ7zercRpjmqm9oWnli8rQkfh1E0KPirayKErSccmZJWkrIiVkWpzsJGOl2"
            "+HSo8E5A6jhZz5D1rrRlru2q6QIM47SEWjTsJ720/CUBZUZsneTMz8r1wAqk9nTeO7cbAYXWt5EWbt85DXy9G5UbJnkdlUXUSMCIOuo3z"
            "nfmZI4kxMXYWIBMnUDqlflgxt0wD60CaBjxGNhrfV2EmC8QQLjwldS69bIIqF0BD8jOQEkL7GSKrk8WUmqc1Re2crypSGpmjYuprMPsER"
            "JCw1LnO65dodkqIZpKrILS99U5Nqm4Jwn53u2hhZWKZtDc3xRxXSx0TasOlL/A+NElXYehra3p6miFTtcx1FSGMxB7AaWrAnHGLci46/k"
            "lEiWzFeFbjbY7RvaAKM8CS4+3WUZQqpqpp6Md/IWqAXyPN/1QC9O/UqrDsYWIhssK+1Bvljt9e7jJoxiW5fUtMvstZ8D90S4EJLxB6EJb"
            "+KDHLyURXevuW+koCGvollsZI58iG9G2UGNu4bb8iQaBNo+x89iqk="
        ),
        read_request_file("delete_offer_request.xml"),
        read_file("delete_offer_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to cancel an offer with the valid client type; this should succeed
    resp = client.cancel_offer(request, MarketType.DAY_AHEAD, 1, Date(2024, 3, 15))

    # Finally, verify the response
    verify_offer_cancel(
        resp,
        "FAKE_RESO",
        DateTime(2024, 3, 15, 12, tzinfo=Timezone("Asia/Tokyo")),
        DateTime(2024, 3, 15, 21, tzinfo=Timezone("Asia/Tokyo")),
        MarketType.DAY_AHEAD,
    )


@responses.activate
def test_query_awards_works(mock_certificate):
    """Test that the query_awards method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test award query
    request = AwardQuery(
        market_type=MarketType.DAY_AHEAD,
        area=AreaCode.TOKYO,
        linked_area=AreaCode.TOHOKU,
        resource="FAKE_RESO",
        start=DateTime(2024, 4, 12, 15, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 18, tzinfo=Timezone("Asia/Tokyo")),
        gate_closed=BooleanFlag.YES,
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "8JZ4ecLOMVtm30sjaxVsk6WL/A08yhDsidfgX4tYenxZeLyN0TDC8RTQVUNBlOc6zXP4eE6rYXu4SJ2OBTMdbVud8CrC0Yy9uD+R40gZ+H"
            "SfLf5bDPjdHXMrFbXBhA8pY5J5HFs3zhMZNuhGyUtvTqPbs6q6nWkuXdPqyftO/MX4ZjCqq3R3ZFpldM5lS5dLYRFX/CEQ9mnxISM9cQUb"
            "qeVawQZNo+PsFOylG91jGNlw4ZL7CDEC+BFqJk7BL8l5b3cCvTwGknFg4IM55MzYQgtfnisn73cN69a1LJbabAOr2NFuj98n8PaLhpxled"
            "wyVM3gN4oCFlA8SnzviMY/iPAzN81pxHg69aUJAJbLyqwmUqPb7/E/qiC6dY9ty/8eFdvoN+APFYAnY8sWQyQUENFBas8Osij9i50J2n/x"
            "3muQ8zzcmWIXW+mmp0KnxzyO/HKPqxoadfqAPQgzhh/4KyGZxa6jhYYV6rfs7BwiJH47pSQ+AXPasOJOdwMK4K9a8yQoEQloaxr/dLcwPW"
            "FccsShXFtMSZxCRVl2tJA0KtK7B1n6LXf3YkmqHS0tfUb7dh2dpXbQCfSGRaZgzAd5DZrYh5XTX99Up38m+qeESsxMmHzBnA5UED6n77yP"
            "7ufN4j5P2mCOwrVf0mxJJUa/b2gtJT5xKTRN30kzfrYrSFc="
        ),
        read_request_file("query_awards_request.xml"),
        read_file("query_awards_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to query awards with the valid client type; this should succeed
    awards = client.query_awards(request, 1, Date(2024, 4, 12))

    # Finally, verify the response
    verify_award_response(
        awards,
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
                        start_up_unit_price=Decimal("99.99"),
                        ramp_down_unit_price=Decimal("99.99"),
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


def test_get_settlement_results_invalid_client(mock_certificate):
    """Test that the get_settlement_results method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.MO, mock_certificate, test=True)

    # Next, create our test settlement results query
    request = SettlementQuery(
        date=Date(2024, 4, 12),
        participant="F100",
        user="FAKEUSER",
    )

    # Now, attempt to get settlement results with the invalid client type; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.get_settlement_results(request, 1)

    # Finvally, verify the details of the raised exception
    assert (
        str(ex_info.value)
        == "MarketQuery_SettlementResultsFileListQuery: Invalid client type, 'MO' provided. Only 'BSP' or 'TSO' are supported."
    )


@responses.activate
def test_get_settlement_results_works(mock_certificate):
    """Test that the get_settlement_results method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "jZmNScnlYiBOYwp94/5/dYGRcy6wW9Wq3EP/CQRWQ8GjHCY5b+6drlGKX2upAEEjnDIiRUbbzR9rFglTkb9G9jCxkL5bRQI3Hxu7EoBr+i"
            "6A3CbnoahoIDYa2rO/F2RWFRYxYkgm1p7OUPDcJmSLGHD1vgbPyETr/nbLqHLs+YNtkm+YwLZzhyolQez4AIqOd8S/TjP012nMTg0wm3zp"
            "0T1BylcO94mY4/zmTKC9Xs11rm+Hw0qztiu5h6LnMqh6cOeE84maFKg29kp6c/IRFFrkVWGhACCipQUdFvK5pLHzP5RsQxGhRJMWHVtO6m"
            "nu891I1VEtkzn+3GxEpCE3nawv+sNXS88LHSrcy06k+7QEaFZfzqqjftoa0B50iY/FpjEDvaQTZ0lMn6sipZJELa/AZhU3phayO7WZ5Cut"
            "+I0VLQ1dKqxBLamxmAtBnjyZp7bzsnYJqshGtKSlaGj4yMfsnjEwlxanTzn2elxiB3bFOIMlD8MLbbYlLqaFdKHrEEUybkh9W8Mdu5sN/z"
            "0zPlNHF6Zb9uC+IvrIaypoA2JsE012wzNsJ06/z/K5YT4zH26+edrIHNB40bHLpYa53yaHdRpZHxhMEDfUlnc3cjkVxVAVZlIruPPya8lb"
            "SM+UAx2byBLwvoqFNvuvY42Z2eKeK7Sb/bbS/kqHjqNWqHg="
        ),
        read_request_file("get_settlement_results_request.xml"),
        read_file("get_settlement_results_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to get settlement results with the valid client type; this should succeed
    resp = client.get_settlement_results(SettlementQuery(), 1, Date(2024, 4, 12))

    # Finally, verify the response
    verify_settlement_results(
        resp,
        [
            settlementfile_verifier(
                "A000_B111_FAKE-FILE.xml",
                participant="F100",
                company="偽会社",
                submission_time=DateTime(2024, 4, 10, 22, 34, 44, tzinfo=Timezone("Asia/Tokyo")),
                settlement_date=Date(2024, 4, 11),
                size=123456,
            )
        ],
    )


def test_put_bups_invalid_client(mock_certificate):
    """Test that the put_bups method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.MO, mock_certificate, test=True)

    # Next, create our test settlement results query
    request = BalancingUnitPriceSubmit(
        resource_code="FAKE_RESO",
        start=DateTime(2024, 4, 12, 9),
        end=DateTime(2024, 4, 12, 12),
        patterns=[
            Pattern(number=1, status=Status.ACTIVE),
        ],
    )

    # Now, attempt to get settlement results with the invalid client type; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.put_bups([request], Date(2024, 4, 12))

    # Finvally, verify the details of the raised exception
    assert str(ex_info.value) == "MarketSubmit_BupSubmit: Invalid client type, 'MO' provided. Only 'BSP' is supported."


@responses.activate
def test_put_bups_works(mock_certificate):
    """Test that the put_bups method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test BUP requests
    request = BalancingUnitPriceSubmit(
        resource_code="FAKE_RESO",
        start=DateTime(2024, 4, 12, 9),
        end=DateTime(2024, 4, 12, 12),
        patterns=[
            Pattern(
                number=1,
                status=Status.ACTIVE,
                remarks="Some patterned remarks",
                balancing_unit_profile=BalancingUnitPrice(
                    v4_unit_price=Decimal("100.00"),
                    bands=[
                        BalancingUnitPriceBand(
                            number=1,
                            from_capacity=9000,
                            v1_unit_price=Decimal("200.00"),
                            v2_unit_price=Decimal("300.00"),
                        )
                    ],
                ),
                abc=[
                    AbcBand(
                        number=1,
                        from_capacity=9001,
                        a=Decimal("400.1"),
                        b=Decimal("400.2"),
                        c=Decimal("400.3"),
                    )
                ],
                startup_costs=[
                    StartupCostBand(
                        number=1,
                        stop_time_hours=42,
                        v3_unit_price=500,
                        remarks="Some comment on startup",
                    )
                ],
            ),
        ],
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "rsYtJGiffeeNRRSm1tHBtetM5DM91h6itsw6ADnKy03HUQ3xqsOo8wIhzTqt32m3iGibRbUv6MgkR82zJv+HQ1sShc0HYuy5SJYVHCQuQb"
            "Ru1W7N/meYPMCnD2uleqDJAojm71f29lUiwddXAguoRz1Y2THo1Lrjp1xRHfdnX/c2Tz17nVg54VQy4+BJ61wYkP1K/RnHDrWZbdzdil3H"
            "w+nU9JD/QE3pmTBjLW5p8JBl89472NAo+tDYFkIFe/bq7VgOidW6jnIShh1Fh+l3AsP8zXEhugBNqZCnyef/J30MeOPB4/NHIYP8veaf5u"
            "j/Ku6oDmK7XOVGJrrjHcrZb5vjIkCUyQB/UX/9fO96gBDj4prziZOfNzGy0b5OLevhLEdpi2Qgbjqcjd1Y+1eaWHWrASXEDF7/PrqM+jlI"
            "AU+RTUTleItfR7V1nFPgOPpKiWIrEM0PsPZF7EC9soJJVOiwd8jfmS5D1TCQBHURRq459mn6iYUDgUz3nbc85eKYN4cpEOf2E9yG+U9g//"
            "oGFBjwAxphsCWQ4nP7Rw8scUHL4WZ4O8+wp97NhjTC+tAxMraJi+FLr3NNGVZCyQoqCiDwo3ybBA/KqzlmPAmWiqRI9vUAosS3RstIYQMY"
            "TjTHAA+nsRYOlUWKtoPdnO08x0BZSs3/NG+di8c0gIiKWM8="
        ),
        read_request_file("put_bup_request.xml"),
        read_file("put_bup_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to put BUPs with the valid client type; this should succeed
    resp = client.put_bups([request], Date(2024, 4, 12))

    # Finally, verify the response
    assert len(resp) == 1
    verify_bup_submit(
        resp[0],
        resource_code="FAKE_RESO",
        start=DateTime(2024, 4, 12, 9, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 12, tzinfo=Timezone("Asia/Tokyo")),
        participant_name="F100",
        company="偽会社",
        area=AreaCode.TOKYO,
        resource_name="偽電力",
        system_code="FSYS0",
        pattern_verifiers=[
            pattern_data_verifier(
                1,
                Status.ACTIVE,
                "Some patterned remarks",
                bup_verifier(Decimal("100.00"), [bup_band_verifier(1, 9000, Decimal("200.00"), Decimal("300.00"))]),
                [abc_band_verifier(1, 9001, Decimal("400.1"), Decimal("400.2"), Decimal("400.3"))],
                [startup_cost_band_verifier(1, 42, 500, "Some comment on startup")],
            )
        ],
    )


def test_put_bup_invalid_client(mock_certificate):
    """Test that the put_bup method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.MO, mock_certificate, test=True)

    # Next, create our test settlement results query
    request = BalancingUnitPriceSubmit(
        resource_code="FAKE_RESO",
        start=DateTime(2024, 4, 12, 9),
        end=DateTime(2024, 4, 12, 12),
        patterns=[
            Pattern(number=1, status=Status.ACTIVE),
        ],
    )

    # Now, attempt to get settlement results with the invalid client type; this should fail
    with pytest.raises(AudienceError) as ex_info:
        _ = client.put_bup(request, Date(2024, 4, 12))

    # Finvally, verify the details of the raised exception
    assert str(ex_info.value) == "MarketSubmit_BupSubmit: Invalid client type, 'MO' provided. Only 'BSP' is supported."


@responses.activate
def test_put_bup_works(mock_certificate):
    """Test that the put_bup method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test BUP requests
    request = BalancingUnitPriceSubmit(
        resource_code="FAKE_RESO",
        start=DateTime(2024, 4, 12, 9),
        end=DateTime(2024, 4, 12, 12),
        patterns=[
            Pattern(
                number=1,
                status=Status.ACTIVE,
                remarks="Some patterned remarks",
                balancing_unit_profile=BalancingUnitPrice(
                    v4_unit_price=Decimal("100.00"),
                    bands=[
                        BalancingUnitPriceBand(
                            number=1,
                            from_capacity=9000,
                            v1_unit_price=Decimal("200.00"),
                            v2_unit_price=Decimal("300.00"),
                        )
                    ],
                ),
                abc=[
                    AbcBand(
                        number=1,
                        from_capacity=9001,
                        a=Decimal("400.1"),
                        b=Decimal("400.2"),
                        c=Decimal("400.3"),
                    )
                ],
                startup_costs=[
                    StartupCostBand(
                        number=1,
                        stop_time_hours=42,
                        v3_unit_price=Decimal("500.00"),
                        remarks="Some comment on startup",
                    )
                ],
            ),
        ],
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "rsYtJGiffeeNRRSm1tHBtetM5DM91h6itsw6ADnKy03HUQ3xqsOo8wIhzTqt32m3iGibRbUv6MgkR82zJv+HQ1sShc0HYuy5SJYVHCQuQb"
            "Ru1W7N/meYPMCnD2uleqDJAojm71f29lUiwddXAguoRz1Y2THo1Lrjp1xRHfdnX/c2Tz17nVg54VQy4+BJ61wYkP1K/RnHDrWZbdzdil3H"
            "w+nU9JD/QE3pmTBjLW5p8JBl89472NAo+tDYFkIFe/bq7VgOidW6jnIShh1Fh+l3AsP8zXEhugBNqZCnyef/J30MeOPB4/NHIYP8veaf5u"
            "j/Ku6oDmK7XOVGJrrjHcrZb5vjIkCUyQB/UX/9fO96gBDj4prziZOfNzGy0b5OLevhLEdpi2Qgbjqcjd1Y+1eaWHWrASXEDF7/PrqM+jlI"
            "AU+RTUTleItfR7V1nFPgOPpKiWIrEM0PsPZF7EC9soJJVOiwd8jfmS5D1TCQBHURRq459mn6iYUDgUz3nbc85eKYN4cpEOf2E9yG+U9g//"
            "oGFBjwAxphsCWQ4nP7Rw8scUHL4WZ4O8+wp97NhjTC+tAxMraJi+FLr3NNGVZCyQoqCiDwo3ybBA/KqzlmPAmWiqRI9vUAosS3RstIYQMY"
            "TjTHAA+nsRYOlUWKtoPdnO08x0BZSs3/NG+di8c0gIiKWM8="
        ),
        read_request_file("put_bup_request.xml"),
        read_file("put_bup_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to put BUPs with the valid client type; this should succeed
    resp = client.put_bup(request, Date(2024, 4, 12))

    # Finally, verify the response
    verify_bup_submit(
        resp,
        resource_code="FAKE_RESO",
        start=DateTime(2024, 4, 12, 9, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 12, tzinfo=Timezone("Asia/Tokyo")),
        participant_name="F100",
        company="偽会社",
        area=AreaCode.TOKYO,
        resource_name="偽電力",
        system_code="FSYS0",
        pattern_verifiers=[
            pattern_data_verifier(
                1,
                Status.ACTIVE,
                "Some patterned remarks",
                bup_verifier(Decimal("100.00"), [bup_band_verifier(1, 9000, Decimal("200.00"), Decimal("300.00"))]),
                [abc_band_verifier(1, 9001, Decimal("400.1"), Decimal("400.2"), Decimal("400.3"))],
                [startup_cost_band_verifier(1, 42, 500, "Some comment on startup")],
            )
        ],
    )


@responses.activate
def test_query_bups_works(mock_certificate):
    """Test that the query_bups method works as expected."""
    # First, create our test MMS client
    client = MmsClient("fake.com", "F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test bup query
    request = BalancingUnitPriceQuery(
        resource_code="FAKE_RESO",
        start=DateTime(2024, 4, 12, 15),
        end=DateTime(2024, 4, 12, 18),
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.MARKET,
        (
            "LhwxZ4I1mJfd8ew0gERS5TP0ZPFxlzyN+RpLhe17AK/itZzDigPCMJRiUfpsNxv/kKx4EqNcN5jOpIzcWp1ZHWmAOaD31dbx2irlfiHQ4P"
            "6o5xlCmQciRKycgEEgkFyXuHJon7hRVyACXh9Mq5kLzAxsLgvmWahQ7isF0knCBlhhUnmZtzZldWEw+huSUJnJ7rmYKEu9a0Vw36JJnSCf"
            "C4Q0x0Am0uyvk7EMKBzwLiTz6h4GjA+nOAHYhKflu1vUECOxYhr6Mw48uyZsjZXJUBJqIfI3hnSfjEBV/VPMq6wuwZQu9T49uLIPIvq85i"
            "Qv4xKnBjp5s/j0TdQZnt/Uznl5pICnDCtR17ImmlNbkyrnE407RMxa4UjCxOATyLZLPCNhj0kZFZpH9p130JVie8esh6U6+/UnH9yUWgOm"
            "3k3byxom/al8A5XUK32tcKSBeaOeaOmg+Isqv1BAxcpkWXcrv4Kb3LSmq3QC7jxWAf4uIKMMgbAM24CRm9j7CS7XM44RZ49t7id3uk2BVn"
            "9TCJJigk/esR4AWU6RVcccEv9DFOBmdbX0LX7bWxxvnhAm9af1/gKiojx31rgKk63/rtTSFidjdC6I2ahXRbxvdWyEY+J2c7IvA1QE0M8C"
            "zg2epv3ajT+jfJsepU01rJpb5nN9ck+x5d3Q0QvDDKOlmTw="
        ),
        read_request_file("query_bups_request.xml"),
        read_file("put_bup_response.xml"),
        warnings=True,
        multipart=True,
    )

    # Now, attempt to get BUPs with the valid client type; this should succeed
    resp = client.query_bups(request, Date(2024, 4, 12))

    # Finally, verify the response
    assert len(resp) == 1
    verify_bup_submit(
        resp[0],
        resource_code="FAKE_RESO",
        start=DateTime(2024, 4, 12, 9, tzinfo=Timezone("Asia/Tokyo")),
        end=DateTime(2024, 4, 12, 12, tzinfo=Timezone("Asia/Tokyo")),
        participant_name="F100",
        company="偽会社",
        area=AreaCode.TOKYO,
        resource_name="偽電力",
        system_code="FSYS0",
        pattern_verifiers=[
            pattern_data_verifier(
                1,
                Status.ACTIVE,
                "Some patterned remarks",
                bup_verifier(Decimal("100.00"), [bup_band_verifier(1, 9000, Decimal("200.00"), Decimal("300.00"))]),
                [abc_band_verifier(1, 9001, Decimal("400.1"), Decimal("400.2"), Decimal("400.3"))],
                [startup_cost_band_verifier(1, 42, 500, "Some comment on startup")],
            )
        ],
    )
