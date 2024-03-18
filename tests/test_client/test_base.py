"""Tests the functionality of the mms_client.services.base module."""

from datetime import date as Date

import pytest
import responses
from pendulum import DateTime

from mms_client.services.base import BaseClient
from mms_client.services.base import EndpointConfiguration
from mms_client.services.base import ServiceConfiguration
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferStack
from mms_client.types.transport import RequestType
from mms_client.types.transport import ResponseDataType
from mms_client.utils.errors import MMSClientError
from mms_client.utils.errors import MMSValidationError
from mms_client.utils.serialization import SchemaType
from mms_client.utils.serialization import Serializer
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface
from tests.testutils import code_verifier
from tests.testutils import messages_verifier
from tests.testutils import register_mms_request
from tests.testutils import verify_messages


@responses.activate
@pytest.mark.parametrize(
    "data_type,compressed,message",
    [
        (ResponseDataType.JSON, False, "Invalid MMS response data type: JSON. Only XML is supported."),
        (ResponseDataType.XML, True, "Invalid MMS response. Compressed responses are not supported."),
    ],
)
def test_non_xml_received_error(mock_certificate, data_type: ResponseDataType, compressed: bool, message: str):
    """Test that an exception is raised if a non-XML response is received."""
    # First, create our base client and endpoint configuration
    client = BaseClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)
    config = EndpointConfiguration(
        "Test",
        ClientType.BSP,
        ServiceConfiguration(Interface.MI, Serializer(SchemaType.MARKET, "MarketData")),
        RequestType.INFO,
        None,
        None,
    )

    # Next, register our test response with the responses library
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
        data_type=data_type,
        compressed=compressed,
    )

    # Now, create our request envelope and payload
    envelope = MarketSubmit(
        date=Date(2024, 3, 15), participant="F100", user="FAKEUSER", market_type=MarketType.DAY_AHEAD, days=1
    )
    payload = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        direction=Direction.SELL,
    )

    # Finally, attempt to submit the request; this should fail
    with pytest.raises(MMSClientError) as exc_info:
        _ = client.request_one(envelope, payload, config)

    # Verify the details of the raised exception
    assert exc_info.value.method == "Test"
    assert exc_info.value.message == message
    assert f"Test: {message}" in str(exc_info.value)


@responses.activate
def test_request_one_response_invalid(mock_certificate):
    """Test that an exception is raised if the response is invalid."""
    # First, create our base client and endpoint configuration
    client = BaseClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)
    config = EndpointConfiguration(
        "Test",
        ClientType.BSP,
        ServiceConfiguration(Interface.MI, Serializer(SchemaType.MARKET, "MarketData")),
        RequestType.INFO,
        None,
        None,
    )

    # Next, register our test response with the responses library
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
            """XmlTimeStamp="2024-03-15T11:43:37" /><Messages><Error Code="Error1" /><Warning Code="Warning1" />"""
            """<Warning Code="Warning2" /><Information Code="Info1" /><Information Code="Info2" /></Messages>"""
            """<MarketSubmit Date="2024-03-15" ParticipantName="F100" UserName="FAKEUSER" MarketType="DAM" """
            """NumOfDays="1" Validation="FAILED" Success="false"><Messages><Error Code="Error1" /><Warning """
            """Code="Warning1" /><Warning Code="Warning2" /><Information Code="Info1" /><Information Code="Info2" />"""
            """</Messages><OfferData ResourceName="FAKE_RESO" StartTime="2024-03-15T12:00:00" """
            """EndTime="2024-03-15T21:00:00" Direction="1" DrPatternNumber="1" BspParticipantName="F100" """
            """CompanyShortName="偽会社" OperatorCode="FAKE" Area="04" ResourceShortName="偽電力" SystemCode="FSYS0" """
            """SubmissionTime="2024-03-15T11:44:15" Validation="PASSED" Success="true"><Messages><Warning """
            """Code="Warning1" /><Warning Code="Warning2" /><Information Code="Info1" /><Information Code="Info2" />"""
            """</Messages><OfferStack StackNumber="1" MinimumQuantityInKw="100" OfferUnitPrice="100" """
            """OfferId="FAKE_ID"><Messages><Warning Code="Warning1" /><Warning Code="Warning2" /><Information """
            """Code="Info1" /><Information Code="Info2" /></Messages></OfferStack></OfferData></MarketSubmit>"""
            """</MarketData>"""
        ).encode("UTF-8"),
        success=False,
    )

    # Now, create our request envelope and payload
    envelope = MarketSubmit(
        date=Date(2024, 3, 15), participant="F100", user="FAKEUSER", market_type=MarketType.DAY_AHEAD, days=1
    )
    payload = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        direction=Direction.SELL,
    )

    # Finally, attempt to submit the request; this should fail
    with pytest.raises(MMSValidationError) as exc_info:
        _ = client.request_one(envelope, payload, config)

    # Verify the details of the raised exception
    assert exc_info.value.method == "Test"
    verify_messages(
        exc_info.value.messages,
        {
            "MarketData": messages_verifier(
                [code_verifier("Error1")],
                [code_verifier("Warning2"), code_verifier("Warning1")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                [code_verifier("Error1")],
                [code_verifier("Warning2"), code_verifier("Warning1")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData": messages_verifier(
                [],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData.OfferStack[0]": messages_verifier(
                [],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
        },
    )


@responses.activate
def test_request_many_response_invalid(mock_certificate):
    """Test that an exception is raised if the response is invalid."""
    # First, create our base client and endpoint configuration
    client = BaseClient("F100", "FAKEUSER", ClientType.BSP, mock_certificate)
    config = EndpointConfiguration(
        "Test",
        ClientType.BSP,
        ServiceConfiguration(Interface.MI, Serializer(SchemaType.MARKET, "MarketData")),
        RequestType.INFO,
        None,
        None,
    )

    # Next, register our test response with the responses library
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
            """XmlTimeStamp="2024-03-15T11:43:37" /><Messages><Error Code="Error1" /><Warning Code="Warning1" />"""
            """<Warning Code="Warning2" /><Information Code="Info1" /><Information Code="Info2" /></Messages>"""
            """<MarketSubmit Date="2024-03-15" ParticipantName="F100" UserName="FAKEUSER" MarketType="DAM" """
            """NumOfDays="1" Validation="FAILED" Success="false"><Messages><Error Code="Error1" /><Warning """
            """Code="Warning1" /><Warning Code="Warning2" /><Information Code="Info1" /><Information Code="Info2" />"""
            """</Messages><OfferData ResourceName="FAKE_RESO" StartTime="2024-03-15T12:00:00" """
            """EndTime="2024-03-15T21:00:00" Direction="1" DrPatternNumber="1" BspParticipantName="F100" """
            """CompanyShortName="偽会社" OperatorCode="FAKE" Area="04" ResourceShortName="偽電力" SystemCode="FSYS0" """
            """SubmissionTime="2024-03-15T11:44:15" Validation="PASSED" Success="true"><Messages><Warning """
            """Code="Warning1" /><Warning Code="Warning2" /><Information Code="Info1" /><Information Code="Info2" />"""
            """</Messages><OfferStack StackNumber="1" MinimumQuantityInKw="100" OfferUnitPrice="100" """
            """OfferId="FAKE_ID"><Messages><Warning Code="Warning1" /><Warning Code="Warning2" /><Information """
            """Code="Info1" /><Information Code="Info2" /></Messages></OfferStack></OfferData></MarketSubmit>"""
            """</MarketData>"""
        ).encode("UTF-8"),
        success=False,
    )

    # Now, create our request envelope and payload
    envelope = MarketSubmit(
        date=Date(2024, 3, 15), participant="F100", user="FAKEUSER", market_type=MarketType.DAY_AHEAD, days=1
    )
    payload = OfferData(
        stack=[OfferStack(number=1, unit_price=100, minimum_quantity_kw=100)],
        resource="FAKE_RESO",
        start=DateTime(2024, 3, 15, 12),
        end=DateTime(2024, 3, 15, 21),
        direction=Direction.SELL,
    )

    # Finally, attempt to submit the request; this should fail
    with pytest.raises(MMSValidationError) as exc_info:
        _ = client.request_many(envelope, payload, config)

    # Verify the details of the raised exception
    assert exc_info.value.method == "Test"
    verify_messages(
        exc_info.value.messages,
        {
            "MarketData": messages_verifier(
                [code_verifier("Error1")],
                [code_verifier("Warning2"), code_verifier("Warning1")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit": messages_verifier(
                [code_verifier("Error1")],
                [code_verifier("Warning2"), code_verifier("Warning1")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData[0]": messages_verifier(
                [],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
            "MarketData.MarketSubmit.OfferData[0].OfferStack[0]": messages_verifier(
                [],
                [code_verifier("Warning1"), code_verifier("Warning2")],
                [code_verifier("Info1"), code_verifier("Info2")],
            ),
        },
    )
