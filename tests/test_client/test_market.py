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
            "eVnILLetkUevnDGEKTUYwuxgQzOAlH6g8keMr/sP84QXHq7geOaB54Mkdp0Gw3ShYXwhZnzkWQMQK1EuSJEGuauNh3MnJ5VJWI6tCnPIv"
            "5E7cfjH/1OP3Ez0JbjucHUFqqFJrgbJ8dxJxnUuhDX7359oodlmUrFAIXhyzh7XfEjrHLQzhRQsNZV/aa+OgIj0UplHf9Mah62pENa48f"
            "+ZN9+15v/S7Ob2V4ZOFY5oeB2tyuwjydJkdcDL2hkewblkc4wLJwopk4bGfVWBI3m42kH32YdokPCyRx/PoDQNmCH/QDwJ8gKFMiMULHy"
            "/hsvmxcogN3bx7xMeaxun+ROyBYpXX2VCQX2P/x8zSn/uoSRXRZyqbbSd1hYnHp2sN47niteGndHMZv1tqKw/rOIccL2598nkUj8PNqw7"
            "FCpqi9eeHaOkuHOLYLLmexICeE9zhtvz2RWbNLlLaUsMhzcjOYqos2JBUJLOn7uIf+1cZOZVr/9QG62n42pJifZcAjFCraq5k1dlpLCZr"
            "SB7bgP0uterkeTbau1TfVQ+H+iFC7rL9/N7zUHg21KxlQme8p+BQIDGXSEswMucj+TaY3H1VuZAL8bmz+xv0d4L47CbvYf8A1kwOc+2Ed"
            "BvIBTy9QCj+/x92xbopX8knV3/rqUlBJjQR1ZcGIAOn+Yf2DG6iQw="
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
            "eVnILLetkUevnDGEKTUYwuxgQzOAlH6g8keMr/sP84QXHq7geOaB54Mkdp0Gw3ShYXwhZnzkWQMQK1EuSJEGuauNh3MnJ5VJWI6tCnPIv"
            "5E7cfjH/1OP3Ez0JbjucHUFqqFJrgbJ8dxJxnUuhDX7359oodlmUrFAIXhyzh7XfEjrHLQzhRQsNZV/aa+OgIj0UplHf9Mah62pENa48f"
            "+ZN9+15v/S7Ob2V4ZOFY5oeB2tyuwjydJkdcDL2hkewblkc4wLJwopk4bGfVWBI3m42kH32YdokPCyRx/PoDQNmCH/QDwJ8gKFMiMULHy"
            "/hsvmxcogN3bx7xMeaxun+ROyBYpXX2VCQX2P/x8zSn/uoSRXRZyqbbSd1hYnHp2sN47niteGndHMZv1tqKw/rOIccL2598nkUj8PNqw7"
            "FCpqi9eeHaOkuHOLYLLmexICeE9zhtvz2RWbNLlLaUsMhzcjOYqos2JBUJLOn7uIf+1cZOZVr/9QG62n42pJifZcAjFCraq5k1dlpLCZr"
            "SB7bgP0uterkeTbau1TfVQ+H+iFC7rL9/N7zUHg21KxlQme8p+BQIDGXSEswMucj+TaY3H1VuZAL8bmz+xv0d4L47CbvYf8A1kwOc+2Ed"
            "BvIBTy9QCj+/x92xbopX8knV3/rqUlBJjQR1ZcGIAOn+Yf2DG6iQw="
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
            "MbWcUSlJ6fJq8SDusw3kLBMPrTxO2ip2rrUbtIhv7XiCjzav6JGCtdqOtli0Y9JufEqYs1jhA0vPWCDand8jACzK8/fVMNlVard1roUtm"
            "TujJ0Nlf2mtAVmCkAAxA43cCXIwqd67aH/GxSGGfP4lwES2CU5MsbSKDi3x1Yrko7NVgC3z26LZlyeUbFOG7A8KcZQyxNQKY3sQ3/PW8o"
            "QHuZEvz9jDS09pGZRpuWifqPs1sPMzdruVIkhJCUbtEpmVaTZgUjQbmLaKMLK8dHLGvfJh335mlEWOqkOlcdvk4tDOAO3Krzdhk5VI46U"
            "VXMIF2hWPWx1IgMkPXRb4J7SqRa0t2PbDBhIc5DLzv3ecWQC6A0Jn0t4059b17bHa77bB2/RDPCJfsjwyg/xa+4Ftf1R5QQQukQzR8bQs"
            "DIhPX33F7dFcW8mMt0MItFn76AsDWgsGIMpFO+wjdXx1ISHsI4lttJqx58DwXdbx/N8qtBgSrZAUzxEOhqzqOJRMHhFQWZIMHMTXm4v98"
            "cWKmeeO+1mup8+H0j4Mlv25+BYA9S8WE8iD/8JTizKiplPZr7eTPcazfWR4oXY1lxAHZqaCNZlz6yHR/qZ/nu8qwPhsaa7ZMCGd89ZnIT"
            "lkMz/xgMQNv8FjikpqDN9S5vWu9UfAJNug1xjAOo5gjb3a1oMEtiE="
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
            "mPUqEy9Ee8UiJmviQW0EelZEkccyE7NiNxb1f73Ifsi+e4430y2XJT9vmMBt7gW+zBoCGVDvhf0qm/DTFbaWgsOWk7ZD0vFhNrJvEaGpy"
            "SasFJe5aSngJ6dfAaCTajpMdmAcxUHh/t6dC4cla6DrCmrX0UfsPMqXzq56fn/Gz9rawfkHNfZHzaxo0lW/g+UQHVXPohIvs2qyg/wBGl"
            "QcQ3qrVZEcuO2d0LCVhk5ouxmKUkThMXLH3mKFG16RRuhHFWqqSdrGY3sR5LwFiCCzplrloksIqqFLz2JnM4pohUeHwdYKFcRC2LzK/Cv"
            "T6g4fMgwBrtI0liW10lDQzeBGmFKJKv21ya1l8t/opG0PKEUunajx3IfyvQcvTpUDAbaCKTaI/DzyHvyCgFpsO64tYxBOXXA3FzvDKGhx"
            "eYBzySxYz9xYELzZTjzCo3jmP+h9sTWkgHva3fxgdVXgGJ9RT3F4euqrxdXL6aQX07GtyQmp8h5J3TFe44gILYS5iDDI64L63gt1FmKPq"
            "waaqA1mGVOivW3vkZO9IVCMoL4PzfcN54td6R/2hESZK/f1csVzxk9F4gWaupemym3YaeSQGoIZRVcjbmWXidTRsMc+ZWsxI7oP6sl3m9"
            "rU17ZiGkJLcUpjBs3NV6nOU3LAgIjqvBW/10KEjikQU3idWXT4Rps="
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
            "0/vQHWWqpCEZl/OttLYjq18Y59aRDJ7kodDIYn1uxHoUGXAv0OwbI3rJblCYFbf8D9rDkatEXxhG5IUrgXqeA/Cx6NoL/zFI8JBcR/iFF"
            "gp9wGEUMxvDZjEs+ue8wGuw/TMwECOGLNi5VRRwyUo0NXGZSWH0Nt+XdLVs/I73EzMu6/uHYELBFlGJFhNWGENRQ+eWFXMcFsabTAdcxy"
            "KrywH3vS3fWznbNfIMX6rGLjNKJsHjTR2uUCxbNIZ3tFgCtT0d4lNSjcb1blhv6rZGFV2srvs/O790d7+VIH6oWH3MEz1MfXRiw6j/okQ"
            "ZeneGJN5Bw4Nu3QOJlGjrbE+1tUH6AM1r29CvbKzZ2TiQTrE6GU9wlks/pgIW1sRui5GiQA5EW6Uv8m6TXBOF2tNw++VJVrDorORZkpc4"
            "ObbZO2E75IsMv1k27FDiYMTBuqRITx2zVid1MIUc0A1BUaXv4CV9XnJdf+MZG9+mxcmGCJeNX9emQIg3EY/M4n8T5L8WVkPl2taHxq13c"
            "h0AYv8xci+n45yFs2KeTtWA/VkjVfDSUbzJ94C/tvx/8jY/OJuSG12703UXbdTlXQdtmObJDgBGgtxs9co3or9/YTjZMGEePxep9k3ETQ"
            "rRHHOEteceDK/7Y099zrriix102+aMz1H+zZIOfvi/jcufrRMh270="
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
