"""Tests the functionality in the mms_client.services.market module."""

from datetime import date as Date
from decimal import Decimal

import pytest
import responses
from pendulum import DateTime
from pendulum import Timezone

from mms_client.client import MmsClient
from mms_client.types.award import AwardQuery
from mms_client.types.award import ContractSource
from mms_client.types.award import SubRequirement
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
from mms_client.types.transport import RequestType
from mms_client.utils.errors import AudienceError
from mms_client.utils.web import ClientType
from tests.testutils import award_result_verifier
from tests.testutils import award_verifier
from tests.testutils import offer_stack_verifier
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import register_mms_request
from tests.testutils import requirement_verifier
from tests.testutils import verify_award_response
from tests.testutils import verify_offer_cancel
from tests.testutils import verify_offer_data
from tests.testutils import verify_reserve_requirement


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
        RequestType.INFO,
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
    verify_reserve_requirement(
        resp,
        AreaCode.TOKYO,
        [
            requirement_verifier(
                DateTime(2024, 4, 12, 15, tzinfo=Timezone("UTC")),
                DateTime(2024, 4, 12, 18, tzinfo=Timezone("UTC")),
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
        DateTime(2024, 3, 15, 12, tzinfo=Timezone("UTC")),
        DateTime(2024, 3, 15, 21, tzinfo=Timezone("UTC")),
        Direction.SELL,
        pattern=1,
        bsp_participant="F100",
        company_short_name="偽会社",
        operator="FAKE",
        area=AreaCode.CHUBU,
        resource_short_name="偽電力",
        system_code="FSYS0",
        submission_time=DateTime(2024, 3, 15, 11, 44, 15, tzinfo=Timezone("UTC")),
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
        DateTime(2024, 3, 15, 12, tzinfo=Timezone("UTC")),
        DateTime(2024, 3, 15, 21, tzinfo=Timezone("UTC")),
        Direction.SELL,
        pattern=1,
        bsp_participant="F100",
        company_short_name="偽会社",
        operator="FAKE",
        area=AreaCode.CHUBU,
        resource_short_name="偽電力",
        system_code="FSYS0",
        submission_time=DateTime(2024, 3, 15, 11, 44, 15, tzinfo=Timezone("UTC")),
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
        DateTime(2024, 3, 15, 12, tzinfo=Timezone("UTC")),
        DateTime(2024, 3, 15, 21, tzinfo=Timezone("UTC")),
        Direction.SELL,
        pattern=1,
        bsp_participant="F100",
        company_short_name="偽会社",
        operator="FAKE",
        area=AreaCode.CHUBU,
        resource_short_name="偽電力",
        system_code="FSYS0",
        submission_time=DateTime(2024, 3, 15, 11, 44, 15, tzinfo=Timezone("UTC")),
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
        DateTime(2024, 3, 15, 12, tzinfo=Timezone("UTC")),
        DateTime(2024, 3, 15, 21, tzinfo=Timezone("UTC")),
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
            "BiEsp0K4TkHJv0NbYf82KOyn8bhkEQxX3QlOq5lLYQxzPOdonKDuy/E8huI6PgzX+Md5MckH2WRf14+eKpvJLtc8o9bDbcF+YkSxWr147"
            "jj7x28ScDJT4dMdOgMNzvCY2N66a9JD2TSZYEfgmFEy+Aez9KIXMHyiBva+wrQ13WLLyXambGZ3oZsOYK6U5qhgO842HPQu+LlCfory7w"
            "iTIOklUop5BxVnT9SDlwRuXv3hUEO3TqnjT8d2nvtuBeAcKMyHD4F83VOF8t0PRZz6haacOOqOBf5nzij5oA5JUdQaCPN2KLx0i0hqbe5"
            "L7q8+15D267UY2L5Pd2pfgNoT/8KUE4Rhgdzdsp7m7uQTWpt2xxNjvx/cdV27zRtIk6g57udT034QTtGct8s0+cX+2wMolh7hegPIoh4d"
            "oyUJFdSXdMtia3sRnD5HGREafaT3pFqH66NJp9/iu65stSIBSPMRdElCIlm/LBy3aA6fj1mhbUTWcPLOWvF4bDNbLEZuzPltnpZOhJo9I"
            "uhP3q+o2ZJceJmyyXO4ikuO6Rf/QSXLWl2DocvstfGfWjWmYWP9pgOhvxLWQw9XRksygEgXs0OmgeQW4NyB6NcpgVTdNX3Yj+qh9nUYVh"
            "/T43icqzkZTBcIPkpchMNe5Ms4l0r16WHhHdNKOYmfDGsP/KRk3js="
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
