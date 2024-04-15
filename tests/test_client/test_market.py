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
from mms_client.types.transport import RequestType
from mms_client.utils.errors import AudienceError
from mms_client.utils.web import ClientType
from tests.testutils import award_result_verifier
from tests.testutils import award_verifier
from tests.testutils import offer_stack_verifier
from tests.testutils import read_file
from tests.testutils import read_request_file
from tests.testutils import register_mms_request
from tests.testutils import verify_award_response
from tests.testutils import verify_offer_cancel
from tests.testutils import verify_offer_data


def test_put_offer_invalid_client(mock_certificate):
    """Test that the put_offer method raises a ValueError when called by an invalid client type."""
    # First, create our test MMS client
    client = MmsClient("F100", "FAKEUSER", ClientType.TSO, mock_certificate, test=True)

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
    client = MmsClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)

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
        RequestType.INFO,
        (
            "uU52ZMls11Bw0mVTVVXgBoqfbLqtL4af3SZq0kbEIMLrVUYDuRtmgQ2hasCCg3wz2STJy64lfU4uw3j9ZYR+oLcE1WY9URhr5+udDEB4B"
            "n9lo+jWju+GH5+wV8SOEWYs325ymPheDqOhuVcUt5oVKAwd88RKxtnjzlV5boc+O1OEcaOlJt1M8qmpub8y2LAk1HKwb5Wo83UP0CMe+C"
            "QRKQ2fXBhsBiVDa0nHToRq5QpIWv6pnC9brGBO2R0KoZh0j6J6t6s6QqfCjUPShZbsiGDB9ju377l87YnwgkiFKRMzGlxzFo0Ayr6WHc0"
            "bN9/qZuqVkhLoKTs+0oK0kouJkiqsrfbdrqEN//zHpjCmD7IxmM1R8LXXSeljZXMntaABG7hPPUik7MkSN41V3pn6OkI1n7UdA+ZWmqjk"
            "/At+C2v4XtfPKaXtT7mMgu7UdNB4n64nJg1eR0BOw7clpkmWwaZzgTS5QXoW05gjnnkqKoorx0pGPcWUw8QC3jJWnnJ4H54iB5+MBlnJC"
            "thBeOefq16bmqQnTw6ETKxVRkbAkB3OqPpkw/zJXEoeVJK4abyuCNPHz8bzaZR8VloqLlFnYkSUUvWK0iqrg8ZzUtiuKMUS9t8cvRiOTn"
            "JiabuhKc863mxe2L+Baft7QCY4dHWjldY3uVwCrEXfWOCVyGQIpbQ="
        ),
        read_request_file("put_offer_request.xml"),
        read_file("put_offer_response.xml"),
        warnings=True,
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
    client = MmsClient("F100", "FAKEUSER", ClientType.TSO, mock_certificate, test=True)

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
    client = MmsClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)

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
        RequestType.INFO,
        (
            "uU52ZMls11Bw0mVTVVXgBoqfbLqtL4af3SZq0kbEIMLrVUYDuRtmgQ2hasCCg3wz2STJy64lfU4uw3j9ZYR+oLcE1WY9URhr5+udDEB4B"
            "n9lo+jWju+GH5+wV8SOEWYs325ymPheDqOhuVcUt5oVKAwd88RKxtnjzlV5boc+O1OEcaOlJt1M8qmpub8y2LAk1HKwb5Wo83UP0CMe+C"
            "QRKQ2fXBhsBiVDa0nHToRq5QpIWv6pnC9brGBO2R0KoZh0j6J6t6s6QqfCjUPShZbsiGDB9ju377l87YnwgkiFKRMzGlxzFo0Ayr6WHc0"
            "bN9/qZuqVkhLoKTs+0oK0kouJkiqsrfbdrqEN//zHpjCmD7IxmM1R8LXXSeljZXMntaABG7hPPUik7MkSN41V3pn6OkI1n7UdA+ZWmqjk"
            "/At+C2v4XtfPKaXtT7mMgu7UdNB4n64nJg1eR0BOw7clpkmWwaZzgTS5QXoW05gjnnkqKoorx0pGPcWUw8QC3jJWnnJ4H54iB5+MBlnJC"
            "thBeOefq16bmqQnTw6ETKxVRkbAkB3OqPpkw/zJXEoeVJK4abyuCNPHz8bzaZR8VloqLlFnYkSUUvWK0iqrg8ZzUtiuKMUS9t8cvRiOTn"
            "JiabuhKc863mxe2L+Baft7QCY4dHWjldY3uVwCrEXfWOCVyGQIpbQ="
        ),
        read_request_file("put_offer_request.xml"),
        read_file("put_offer_response.xml"),
        warnings=True,
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
    client = MmsClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test offer data
    request = OfferQuery(market_type=MarketType.DAY_AHEAD, area=AreaCode.CHUBU, resource="FAKE_RESO")

    # Register our test response with the responses library
    register_mms_request(
        RequestType.INFO,
        (
            "JfhNprmqF5WZn1vss/JlcPzq2YGOK2gN2AYdesom7WC6d5Ou3aDhM5pTdU2lu2ts2c5OEW0p8izVNMNsizxCeSb3pPvsLccWdprtZ5Gi163E9+S6VU16Y/i3whybqZr8/clSrcr40S1i1kYyH2IJSXvoTNWQxNQu/7Q4/gyYVL2Tz2nbI6yrxpQ3b1E4wCJJWRW+pg9p29UeLHg2REdtILlMPyBRquk8VXZ4H4SvzT5DGhyrWYiahoMz7kQQLbCURTKqBT/iTS4ZgyodN4bMGkkx/JPe4ExL6FcJJ0nT2iQnkI7XpZFyUwQfExF2Jz+J4xbJpRb0zRdgvDUvhgDgCqeSd3zgslwBT8ALoPz/0X89xzL1YErTfREGtFlJSL4FMQOioz7XZPDTKirxJ8M3KbxWQeNMJSqqyXE9ZhXvOK84Xk03zDnCPSKkvS1YI9UUxzkAK0F4zzJePdnA3QjMHg6rZVV2SC2KqKIIFQmiM0uqe61FUZmjnT7CuA2DVKZ8FMja5jZ71K/4+PUX+DLxyrEXDRAnKg7EfmJDSpFjL6mnEIVaIr8hJmyHzMivsfxjtaj5ymIPnR8DYfZOApvlIjm8ysRixlin/8CYzRZJWWcr/uY860Y9Mb9B7Kw+vTtIWBciABHOMvvj46ky4g2NzM4s2lGMy0j0pDxwyp+x7J0="
        ),
        read_request_file("query_offers_request.xml"),
        read_file("put_offer_response.xml"),
        warnings=True,
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
    client = MmsClient("F100", "FAKEUSER", ClientType.TSO, mock_certificate, test=True)

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
    client = MmsClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)

    # Next, create our test offer cancellation
    request = OfferCancel(
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        market_type=MarketType.DAY_AHEAD,
    )

    # Register our test response with the responses library
    register_mms_request(
        RequestType.INFO,
        (
            "tYViRBY8lgXK7ud/sYswT6UtC4QTFLYxToRgbhxqLL6uQYa2cD7pKJfgfj4iSFrf/jLfNvR+6f+FqXvalRcijdYEH29hdKJQ1lsZ5rLic"
            "iRiw6cq7a40hTVOG8NqTlhgak6i3A0Xa3wgPF8UTAjo4a5Orx70zZitkUITVrKY70Z2u+drMQM/BAs3R8/7kRKNPwzLpi9BNcrAMWqt0w"
            "23S5UoiC6EgXFCkt2VabGLUsmoXNabgR41e4n7A5a8C79ydmz3JVy6NHm34lOQWp9y8/QSNfA3I4lWWoLOLpNJXso4fD2CEHGPG2nonf5"
            "AjdC53EflgK/fwKQHZQo7GfhFIh1blSPnEY4Oiz9UJhpTvYHgwITM354X3VEousJ5is0EtD9hG3+8rM3LAQirCOyuJXEUfF5z30LXFwlQ"
            "dx5rFfYho3Z1fjhrbNLjg8cPnFwvfUa4+xueAxomN4O//E1VIceUW6ns9CGzR7VvqYaEGmX6gEcixXQ/lQ5kaeJtNhBHpFMDBbWZGiCON"
            "KOP1hGW9wI5QtWZeyHTJbcbXBbeuRXAIHPKYqEMADFWzKZyJeEspKGUTyCegRudLRwQgzDvq9XzRUsW4uH84CuUaPgsUK29Bjy8H7lYL/"
            "aAlcB/daZWmWd/5noHKMfokRgYQir1zHEgjBlrev9c4fk0ckRaNEw="
        ),
        read_request_file("delete_offer_request.xml"),
        read_file("delete_offer_response.xml"),
        warnings=True,
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
    client = MmsClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)

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
        RequestType.INFO,
        (
            "y/RTqaOCdC6ATv9L9Q2bVtZ9ovWERVbxMqn2gIwv90rvYpJ7ofgwjeEZ2MB9Yzvca+wixbUH1Um6rUhQ7IRVxnuSpHnLtyz+gMQC6E9KO1vsD7ILp6CoYVfTbzK5TkHCuLvlWbEHRe17/w8PgWr/bexkJ1+qguyNcF62/zfeSfzv7/ZbQXAuykcB0QyZ6Ha8aoO8GJKqV6UFHeH/0QFC1dWMkM+iv+LmK4+GsbjErL36bpNN1ePQ6I3a2F710l0TNZnwJ0FM/lwkdYyVzlD1G96rBe7GvROwdDOc/2InuWf+QEag8Hebnq+/s5VnKmD8u5W5UHL74B580wqLFtOmqf6vYYdvQq4MquBwVXEtrwqtUo4HSofAXJowDyKiIIx4UFZwcWYGDv//oYxGIWWMNc54p3lmmuqmnMsrpQqTIqvQJA+i2V4Sc8FyHlRO1ShEelC3nWuQceEmXyxnVii/256XlCLKQanG2w28jAqyU6rzoRoU1ZAihBKew3jx6lGHD4R6+JMoNiSEYeQKMgNkQ/YPrDnmSO8Txa/gklUqDnTySZWK9rcGZXo/sX2BA8SJQOng9roR+fsQXOldRuo5V+yTpF8mu6eVXcCBcelYixGsuvrkodJgdXZyuwHZ90bOMZlFTjSUqn0qJKMEwKJO/PdqkrUPVOXXLIGTkcFenfU="
        ),
        read_request_file("query_awards_request.xml"),
        read_file("query_awards_response.xml"),
        warnings=True,
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
