"""Tests the functionality in the mms_client.types.base module."""

from typing import Optional

from pendulum import DateTime
from pendulum import Timezone
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr

from mms_client.types.base import BaseResponse
from mms_client.types.base import Envelope
from mms_client.types.base import MultiResponse
from mms_client.types.base import ProcessingStatistics
from mms_client.types.base import Response
from mms_client.types.base import ResponseData
from mms_client.types.base import SchemaType


def test_response_base_validate_defaults_works():
    """Test that the ResponseBase class can be converted from an XML payload as expected."""

    # First, create our test XML payload
    raw = b"""<BaseResponse xmlns:xsi="http://www.w3.org/2001/XMLSchema"><ProcessingStatistics TimeStamp=""/></BaseResponse>"""

    # Next, attempt to validate it against our ResponseBase model
    data = BaseResponse[Envelope].from_xml(raw)

    # Finally, verify the data was created as expected
    verify_base_response(data)


def test_response_base_validate_full_works():
    """Test that the ResponseBase class can be converted from an XML payload as expected."""

    # First, create our test XML payload
    raw = b"""<BaseResponse xmlns:xsi="http://www.w3.org/2001/XMLSchema"><ProcessingStatistics Received="1" Valid="2" Invalid="3" Successful="4" Unsuccessful="5" ProcessingTimeMs="6" TransactionID="derpderp" TimeStamp="Mon Aug 30 03:25:41 JST 2019" XmlTimeStamp="2019-08-30T03:25:41Z"/></BaseResponse>"""

    # Next, attempt to validate it against our ResponseBase model
    data = BaseResponse[Envelope].from_xml(raw)

    # Finally, verify the data was created as expected
    verify_base_response(
        data,
        valid=2,
        invalid=3,
        received=1,
        successful=4,
        unsuccessful=5,
        time_ms=6,
        timestamp="Mon Aug 30 03:25:41 JST 2019",
        timestamp_xml=DateTime(2019, 8, 30, 3, 25, 41, tzinfo=Timezone("UTC")),
        id="derpderp",
    )


def test_response_data_works():
    """Test that the data property of the Response class works as expected."""
    # Create a new response data object
    resp = Response[Envelope, FakeModel](statistics=ProcessingStatistics())
    resp.payload = ResponseData[FakeModel](FakeModel(), None)

    # Verify that the data property returns the correct value
    assert resp.payload.data.name == "test"


def test_response_multi_data_works():
    """Test that the data property of the MultiResponse class works as expected."""
    # Create a new response data object
    resp = MultiResponse[Envelope, FakeModel](statistics=ProcessingStatistics())
    resp.payload = [
        ResponseData[FakeModel](FakeModel(name="test1"), None),
        ResponseData[FakeModel](FakeModel(name="test2"), None),
    ]

    # Verify that the data property returns the correct value
    assert resp.payload[0].data.name == "test1"
    assert resp.payload[1].data.name == "test2"


class FakeModel(BaseXmlModel):
    """Test model to use for testing the Response classes."""

    # The name of the test model
    name: str = attr(default="test")


def verify_base_response(
    resp: BaseResponse[Envelope],
    valid: Optional[int] = None,
    invalid: Optional[int] = None,
    received: Optional[int] = None,
    successful: Optional[int] = None,
    unsuccessful: Optional[bool] = None,
    time_ms: Optional[int] = None,
    timestamp: str = "",
    timestamp_xml: Optional[DateTime] = None,
    id: Optional[str] = None,
):
    """Verify that the given BaseResponse was created with the correct parameters."""
    assert not resp.messages
    assert not resp.envelope
    assert not resp.envelope_validation
    verify_statistics(
        resp.statistics,
        valid=valid,
        invalid=invalid,
        received=received,
        successful=successful,
        unsuccessful=unsuccessful,
        time_ms=time_ms,
        timestamp=timestamp,
        timestamp_xml=timestamp_xml,
        transaction_id=id,
    )


def verify_statistics(stats: ProcessingStatistics, **kwargs):
    """Verify that the given ProcessingStatistics was created with the correct parameters."""
    for key, value in kwargs.items():
        assert getattr(stats, key) == value
