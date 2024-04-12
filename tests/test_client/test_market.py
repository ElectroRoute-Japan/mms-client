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
            "uU52ZMls11Bw0mVTVVXgBoqfbLqtL4af3SZq0kbEIMLrVUYDuRtmgQ2hasCCg3wz2STJy64lfU4uw3j9ZYR+oLcE1WY9URhr5+udDEB4B"
            "n9lo+jWju+GH5+wV8SOEWYs325ymPheDqOhuVcUt5oVKAwd88RKxtnjzlV5boc+O1OEcaOlJt1M8qmpub8y2LAk1HKwb5Wo83UP0CMe+C"
            "QRKQ2fXBhsBiVDa0nHToRq5QpIWv6pnC9brGBO2R0KoZh0j6J6t6s6QqfCjUPShZbsiGDB9ju377l87YnwgkiFKRMzGlxzFo0Ayr6WHc0"
            "bN9/qZuqVkhLoKTs+0oK0kouJkiqsrfbdrqEN//zHpjCmD7IxmM1R8LXXSeljZXMntaABG7hPPUik7MkSN41V3pn6OkI1n7UdA+ZWmqjk"
            "/At+C2v4XtfPKaXtT7mMgu7UdNB4n64nJg1eR0BOw7clpkmWwaZzgTS5QXoW05gjnnkqKoorx0pGPcWUw8QC3jJWnnJ4H54iB5+MBlnJC"
            "thBeOefq16bmqQnTw6ETKxVRkbAkB3OqPpkw/zJXEoeVJK4abyuCNPHz8bzaZR8VloqLlFnYkSUUvWK0iqrg8ZzUtiuKMUS9t8cvRiOTn"
            "JiabuhKc863mxe2L+Baft7QCY4dHWjldY3uVwCrEXfWOCVyGQIpbQ="
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
            "HXD+EdcN+NJi6vlVZ3OirpncAxvwoy3YxMABLPpEKnHGv2+NB51TBujizFeKoxROy6nQEKtuGQYRKiPSnpuSJKF2PhaVBAteEz5w/C1We"
            "HriBDOTnl6j0zBJbi896T7gLTwp3Zj94GTwhVh1Hnc0ZIGb+W0cpcZo6XDu4844zBtnRbjkE5UDbOp1Sm0mDVZ0BiwAC7DR+NFkpUrMNQ"
            "qHor9HHMiXIT1blLP0TkioIo2l//1pEqd8NibHvjAYM5dZuDmz6ucxQivMrNgInlgXivINCzj3zkbfy66PqLUX1WJmEIlejOskC7qxuP6"
            "JSywtV4kWUBqKBXHSHjB0Ie6JS3hoqVFOvC9lZhDiU3Geb054wZqk50+CldWeGzIsub5a9vgZZK/+6MbNVh8N5k2vZSyXS3GWhxHW/WCK"
            "NkT6UZ4PHsaGI6eSyj2jqpGKJlZ8N9h/DDm9saBBLnqcdWQOubGDvrhloph/WIkqcYJJx6uzCOsIeZDI/Q0dSIMjtF4wpo3D6nD1rGvr+"
            "E/Sxw7AyD2vAK6K999N3b4U/sdnfJncFldeOXJMRTxDeSRBHnSmkrQteKIJ91K53nQuhC3XaAGYaKgbSMeLV/WzWO85DoUSvWJrljhMWi"
            "Uxn0ZMj46wrnJqU9KxZpNzvqHyrIoCnry+xJMSTJn2HtiqxywieOQ="
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
            "tYViRBY8lgXK7ud/sYswT6UtC4QTFLYxToRgbhxqLL6uQYa2cD7pKJfgfj4iSFrf/jLfNvR+6f+FqXvalRcijdYEH29hdKJQ1lsZ5rLic"
            "iRiw6cq7a40hTVOG8NqTlhgak6i3A0Xa3wgPF8UTAjo4a5Orx70zZitkUITVrKY70Z2u+drMQM/BAs3R8/7kRKNPwzLpi9BNcrAMWqt0w"
            "23S5UoiC6EgXFCkt2VabGLUsmoXNabgR41e4n7A5a8C79ydmz3JVy6NHm34lOQWp9y8/QSNfA3I4lWWoLOLpNJXso4fD2CEHGPG2nonf5"
            "AjdC53EflgK/fwKQHZQo7GfhFIh1blSPnEY4Oiz9UJhpTvYHgwITM354X3VEousJ5is0EtD9hG3+8rM3LAQirCOyuJXEUfF5z30LXFwlQ"
            "dx5rFfYho3Z1fjhrbNLjg8cPnFwvfUa4+xueAxomN4O//E1VIceUW6ns9CGzR7VvqYaEGmX6gEcixXQ/lQ5kaeJtNhBHpFMDBbWZGiCON"
            "KOP1hGW9wI5QtWZeyHTJbcbXBbeuRXAIHPKYqEMADFWzKZyJeEspKGUTyCegRudLRwQgzDvq9XzRUsW4uH84CuUaPgsUK29Bjy8H7lYL/"
            "aAlcB/daZWmWd/5noHKMfokRgYQir1zHEgjBlrev9c4fk0ckRaNEw="
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
