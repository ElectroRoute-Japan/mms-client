"""Tests the functionality in the mms_client.types.base module."""

from typing import Optional

from pendulum import DateTime
from pendulum import Timezone
from pydantic import BaseModel
from pydantic import Field

from mms_client.types.base import BaseResponse
from mms_client.types.base import MultiResponse
from mms_client.types.base import ProcessingStatistics
from mms_client.types.base import RequestPayload
from mms_client.types.base import Response
from mms_client.types.base import ResponseData


def test_response_base_validate_defaults_works():
    """Test that the ResponseBase class can be converted from a dictionary as expected."""

    # First, create our test dictionary
    raw = {"ProcessingStatistics": {}}

    # Next, attempt to validate it against our ResponseBase model
    data = BaseResponse[RequestPayload].model_validate(raw)

    # Finally, verify the data was created as expected
    verify_base_response(data)


def test_response_base_validate_full_works():
    """Test that the ResponseBase class can be converted from a dictionary as expected."""

    # First, create our test dictionary
    raw = {
        "ProcessingStatistics": {
            "Received": 1,
            "Valid": 2,
            "Invalid": 3,
            "Successful": 4,
            "Unsuccessful": 5,
            "ProcessingTimeMs": 6,
            "TransactionID": "derpderp",
            "TimeStamp": "Mon Aug 30 03:25:41 JST 2019",
            "XmlTimeStamp": "2019-08-30T03:25:41Z",
        },
    }

    # Next, attempt to validate it against our ResponseBase model
    data = BaseResponse[RequestPayload].model_validate(raw)

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
    resp = Response[RequestPayload, FakeModel](ProcessingStatistics=ProcessingStatistics())
    resp.payload_data = ResponseData[FakeModel](FakeModel(), None)

    # Verify that the data property returns the correct value
    assert resp.data.name == "test"


def test_response_multi_data_works():
    """Test that the data property of the MultiResponse class works as expected."""
    # Create a new response data object
    resp = MultiResponse[RequestPayload, FakeModel](ProcessingStatistics=ProcessingStatistics())
    resp.payload_data = [
        ResponseData[FakeModel](FakeModel(name="test1"), None),
        ResponseData[FakeModel](FakeModel(name="test2"), None),
    ]

    # Verify that the data property returns the correct value
    assert resp.data[0].name == "test1"
    assert resp.data[1].name == "test2"


class FakeModel(BaseModel):
    """Test model to use for testing the Response classes."""

    # The name of the test model
    name: str = Field(default="test")


def verify_base_response(
    resp: BaseResponse[RequestPayload],
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
    assert not resp.payload
    assert not resp.payload_validation
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
