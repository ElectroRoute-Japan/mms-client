"""Tests the functionality in the mms_client.services.market module."""

from datetime import date as Date

import pytest
import responses
from pendulum import DateTime
from pendulum import Timezone

from mms_client.client import MmsClient
from mms_client.types.enums import AreaCode
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferQuery
from mms_client.types.offer import OfferStack
from mms_client.types.transport import RequestType
from mms_client.utils.errors import AudienceError
from mms_client.utils.web import ClientType
from tests.testutils import offer_stack_verifier
from tests.testutils import register_mms_request
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
            "HsVd+Dqo/c/LYNpa8/yKNn0I6hZIz1DxKR0QLZFjWEUX4Kvj3WEqU700m6yJvZpg0LjcgDFfJsnMPwEZ8QkkenMRlYBa9Q1M2oeG7PMWS"
            "r82KoRP9howcq0Ad4a0UHaB8WwZKztyWf4P/cALqNydosrRy1m7j54wKyanQfMnnVLGMSpEFbvF6oem0q71MUhoT2jJ0xMDTTzs7W41qp"
            "bgDhcvFMKzRlFGZe/i3EMMWglACvTpQmp/5r5RjQ00DLZ+/VZnf2+NlE6sTetYWmcLyfWp737Z7e68Sk4Lb0+KgkAXziq7EA7nSAYDLgB"
            "DbQNSvNK8snlTsirY2V/HVrH5ETz+hduWyKRzYF91AHCgOOpBXyrEbeGvcsnNNujFxT36Re5mL7ngrTb087wfb1wHk8iHwawH0L7VVdMS"
            "8BJi+yofljmaAqZVGNQEfC5Q2hZsRhMRp5H4SJCHvbO8ZFdXD8lJGPqThmqr7hB5ttY+XqGKIsr0fv6V5OVEqrMWy64vQAMWSiC+jlhFy"
            "vTFw7h6hOQAcZXIQ/kdfqz6JvpjnzPjmDHVj3HGCKaw5afZJpUSDjiZjih+L+KBwJSiA02EBrvlCY/2lXKSo9xj5nU6bnso+rKt8Rwsqo"
            "qaNAR0x76pNcODGg3oxQQa+/kjxW0Wk/014sWhvkPC0vAUqYoTJCs="
        ),
        (
            """<?xml version='1.0' encoding='utf-8'?>\n<MarketData xmlns:xsi="http://www.w3.org/2001/XMLSchema" """
            """xsi:noNamespaceSchemaLocation="mi-market.xsd"><MarketSubmit Date="2024-03-15" ParticipantName="F100" """
            """UserName="FAKEUSER" MarketType="DAM" NumOfDays="1"><OfferData ResourceName="FAKE_RESO" """
            """StartTime="2024-03-15T12:00:00" EndTime="2024-03-15T21:00:00" Direction="1"><OfferStack """
            """StackNumber="1" MinimumQuantityInKw="100" OfferUnitPrice="100"/></OfferData></MarketSubmit>"""
            """</MarketData>"""
        ).encode("UTF-8"),
        (
            """<?xml version='1.0' encoding='utf-8'?>\n<MarketData xmlns:xsi="http://www.w3.org/2001/XMLSchema">"""
            """<ProcessingStatistics Received="1" Valid="1" Invalid="0" Successful="1" Unsuccessful="0" """
            """ProcessingTimeMs="187" TransactionId="derpderp" TimeStamp="Tue Mar 15 11:43:37 JST 2024" """
            """XmlTimeStamp="2024-03-15T11:43:37" /><Messages><Warning Code="Warning1" /><Warning Code="Warning2" />"""
            """<Information Code="Info1" /><Information Code="Info2" /></Messages><MarketSubmit Date="2024-03-15" """
            """ParticipantName="F100" UserName="FAKEUSER" MarketType="DAM" NumOfDays="1" Validation="PASSED" """
            """Success="true"><Messages><Warning Code="Warning1" /><Warning Code="Warning2" /><Information """
            """Code="Info1" /><Information Code="Info2" /></Messages><OfferData ResourceName="FAKE_RESO" """
            """StartTime="2024-03-15T12:00:00" EndTime="2024-03-15T21:00:00" Direction="1" DrPatternNumber="1" """
            """BspParticipantName="F100" CompanyShortName="偽会社" OperatorCode="FAKE" Area="04" """
            """ResourceShortName="偽電力" SystemCode="FSYS0" SubmissionTime="2024-03-15T11:44:15" Validation="PASSED" """
            """Success="true"><Messages><Warning Code="Warning1" /><Warning Code="Warning2" /><Information """
            """Code="Info1" /><Information Code="Info2" /></Messages><OfferStack StackNumber="1" """
            """MinimumQuantityInKw="100" OfferUnitPrice="100" OfferId="FAKE_ID"><Messages><Warning Code="Warning1" />"""
            """<Warning Code="Warning2" /><Information Code="Info1" /><Information Code="Info2" /></Messages>"""
            """</OfferStack></OfferData></MarketSubmit></MarketData>"""
        ).encode("UTF-8"),
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
            "SgqlN5rgyyA3JcbvilHB7Zbz+2HpmUQYmbG/7HDHDTAijg2ZOCB+uZo3D5ol7OPB5+o3PuxZkZ5GrUefeu88rh5efWSBHEItL5E+h0wR4"
            "/Sq9hPSrQ3JsMuzfNig9YCTcVVfFBLibb2FacwKe7hjXK13GqahJT9Fe45BCy2H8CSGU+alx4c2iGE7RdSTCRt0wOcArZ1TnrkN9jW1XL"
            "1YAP3XOZ0ItHxVyKIT5dk7ZuN9PQG5P6QrDFUDRTyQ52oP26PPHCTt65F61DMBkeOvxrhdnWDQlSvyFlCT9KPlTkjFtDxEqQYoAiSDGYC"
            "wHIHjCrRocd1V8LMy1LGLnuhLtvBSKw92kS3eV1FJ061W6SQoQ0LCaAAGxV+gGNTFpULY1MUp7Zekyn/Nb/JRXQAbsIDJiVUd0zg2Vy8S"
            "IAhx4ZiF/YlAF3psRL+Kn5HNgX5K/2ebeg1zDm3Jiurt+oR3P1V8XkVU+fOmxZ63AwXLjoFU8BHbqYZO9ATcuDkmE1PWlg39smxm8l/Uu"
            "KmMN7IxlzwN2Yg0sTq9Lwws6doHqnsiF3PCclHuUZKI48KFqz9jl9QxlLMUVDv6Bi5cIGCOUc34hcd/9ePILQSLCqczcplAn0AE8/19H/"
            "TZu1VSAXJznHH59JyaZRDADDgmglqjudtp0ryq/yZIZZO4Gi1vU8I="
        ),
        (
            """<?xml version='1.0' encoding='utf-8'?>\n<MarketData xmlns:xsi="http://www.w3.org/2001/XMLSchema" """
            """xsi:noNamespaceSchemaLocation="mi-market.xsd"><MarketQuery Date="2024-03-15" ParticipantName="F100" """
            """UserName="FAKEUSER" MarketType="DAM" NumOfDays="1"><OfferQuery MarketType="DAM" """
            """ResourceName="FAKE_RESO" Area="04"/></MarketQuery></MarketData>"""
        ).encode("UTF-8"),
        (
            """<?xml version='1.0' encoding='utf-8'?>\n<MarketData xmlns:xsi="http://www.w3.org/2001/XMLSchema">"""
            """<ProcessingStatistics Received="1" Valid="1" Invalid="0" Successful="1" Unsuccessful="0" """
            """ProcessingTimeMs="187" TransactionId="derpderp" TimeStamp="Tue Mar 15 11:43:37 JST 2024" """
            """XmlTimeStamp="2024-03-15T11:43:37" /><Messages><Warning Code="Warning1" /><Warning Code="Warning2" />"""
            """<Information Code="Info1" /><Information Code="Info2" /></Messages><MarketSubmit Date="2024-03-15" """
            """ParticipantName="F100" UserName="FAKEUSER" MarketType="DAM" NumOfDays="1" Validation="PASSED" """
            """Success="true"><Messages><Warning Code="Warning1" /><Warning Code="Warning2" /><Information """
            """Code="Info1" /><Information Code="Info2" /></Messages><OfferData ResourceName="FAKE_RESO" """
            """StartTime="2024-03-15T12:00:00" EndTime="2024-03-15T21:00:00" Direction="1" DrPatternNumber="1" """
            """BspParticipantName="F100" CompanyShortName="偽会社" OperatorCode="FAKE" Area="04" """
            """ResourceShortName="偽電力" SystemCode="FSYS0" SubmissionTime="2024-03-15T11:44:15" Validation="PASSED" """
            """Success="true"><Messages><Warning Code="Warning1" /><Warning Code="Warning2" /><Information """
            """Code="Info1" /><Information Code="Info2" /></Messages><OfferStack StackNumber="1" """
            """MinimumQuantityInKw="100" OfferUnitPrice="100" OfferId="FAKE_ID"><Messages><Warning Code="Warning1" />"""
            """<Warning Code="Warning2" /><Information Code="Info1" /><Information Code="Info2" /></Messages>"""
            """</OfferStack></OfferData></MarketSubmit></MarketData>"""
        ).encode("UTF-8"),
        warnings=True,
    )

    # Now, attempt to query offers with the valid client type; this should succeed
    offers = client.query_offers(request, MarketType.DAY_AHEAD, 1, Date(2024, 3, 15))

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
            "jKFHk8iwfL5wMjJ4a7Rz4pmQB8i0kprjlMG5+BxMXddOUk6geyKbiIu+5/BVgU7lfoepiYDQ5x2dN6XunKFV8F3jI13LECwxhPqnPL/eg"
            "kDInPbbMk4Oab9KvecrgdyLHx6Fu9sBoar/zTCjnRDxMxbKBw5VU0XG+QW0q/X+1ZlbYQnYl+kY+UgNm2DxcblKD3l9xZaPfMCpIvzcUh"
            "Z/E8henn+MHmUiojpxZ+OeXgdAYEbtsBRXOCy2LYdTczeFMDw3aFjCoZATU8cZHbuAcJd3xiKfbqOuaVQi5w3o90SiUgZJHG9BnvabSEi"
            "tp3a3QTnNnPSfH318jndI7ydArO051QsBlvT1HycwQ56T8NUhuHn306kZE70s4G0kQ2Lp24PuH4D1NXhK3lLukWu2Mc0JdtAnhnU63SFG"
            "eZCpjpb4Uv/pAW/4Q506iULy11ho09+xoiyr7yHumMIkedMo3+cIBvAwbYthCmzfQZFBd6rMzKEjfkjcJslu5MdRbVv16cPOsElqlcM5O"
            "NrzNFQgJzhffmOxk/hmI6DwVFRczXCOXaB9yFj19Xissy10uwhF0UiBp5AX/oMxemn62nDJcIer45DlLeZwKUUzsrrdeX/iDv9iuj/RrK"
            "EMNJNNv0t9VZ2v/y0+N9IXpxQeCnjwPnI0550KIU+K40Gcfa6w7f4="
        ),
        (
            """<?xml version='1.0' encoding='utf-8'?>\n<MarketData xmlns:xsi="http://www.w3.org/2001/XMLSchema" """
            """xsi:noNamespaceSchemaLocation="mi-market.xsd"><MarketCancel Date="2024-03-15" ParticipantName="F100" """
            """UserName="FAKEUSER" MarketType="DAM" NumOfDays="1"><OfferCancel ResourceName="FAKE_RESO" """
            """StartTime="2024-03-15T12:00:00" EndTime="2024-03-15T21:00:00" MarketType="DAM"/></MarketCancel>"""
            """</MarketData>"""
        ).encode("UTF-8"),
        (
            """<?xml version='1.0' encoding='utf-8'?>\n<MarketData xmlns:xsi="http://www.w3.org/2001/XMLSchema">"""
            """<ProcessingStatistics Received="1" Valid="1" Invalid="0" Successful="1" Unsuccessful="0" """
            """ProcessingTimeMs="187" TransactionId="derpderp" TimeStamp="Tue Mar 15 11:43:37 JST 2024" """
            """XmlTimeStamp="2024-03-15T11:43:37" /><Messages><Warning Code="Warning1" /><Warning Code="Warning2" />"""
            """<Information Code="Info1" /><Information Code="Info2" /></Messages><MarketCancel Date="2024-03-15" """
            """ParticipantName="F100" UserName="FAKEUSER" MarketType="DAM" NumOfDays="1" Validation="PASSED" """
            """Success="true"><Messages><Warning Code="Warning1" /><Warning Code="Warning2" /><Information """
            """Code="Info1" /><Information Code="Info2" /></Messages><OfferCancel ResourceName="FAKE_RESO" """
            """StartTime="2024-03-15T12:00:00" EndTime="2024-03-15T21:00:00" MarketType="DAM"/></MarketCancel>"""
            """</MarketData>"""
        ).encode("UTF-8"),
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
