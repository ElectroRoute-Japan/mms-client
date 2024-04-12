"""Contains utility functions for testing the MMS client."""

from base64 import b64encode
from datetime import date as Date
from decimal import Decimal
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import responses
from pendulum import DateTime
from requests import PreparedRequest
from responses.matchers import header_matcher

from mms_client.types.base import Message
from mms_client.types.base import Messages
from mms_client.types.enums import AreaCode
from mms_client.types.market import BaseMarketRequest
from mms_client.types.market import MarketCancel
from mms_client.types.market import MarketQuery
from mms_client.types.market import MarketSubmit
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction
from mms_client.types.offer import OfferCancel
from mms_client.types.offer import OfferData
from mms_client.types.offer import OfferQuery
from mms_client.types.offer import OfferStack
from mms_client.types.registration import QueryAction
from mms_client.types.registration import QueryType
from mms_client.types.registration import RegistrationQuery
from mms_client.types.resource import AfcMinimumOutput
from mms_client.types.resource import OutputBand
from mms_client.types.resource import ResourceData
from mms_client.types.resource import ResourceQuery
from mms_client.types.resource import ShutdownEvent
from mms_client.types.resource import ShutdownPattern
from mms_client.types.resource import StartupEvent
from mms_client.types.resource import StartupPattern
from mms_client.types.resource import Status
from mms_client.types.resource import SwitchOutput
from mms_client.types.transport import Attachment
from mms_client.types.transport import MmsRequest
from mms_client.types.transport import MmsResponse
from mms_client.types.transport import RequestDataType
from mms_client.types.transport import RequestType
from mms_client.types.transport import ResponseDataType


def read_file(file: str) -> bytes:
    """Read the contents of the given file."""
    with open(Path(__file__).parent / "test_files" / file, "rb") as f:
        return f.read()


def read_request_file(file: str, leave_one: bool = True) -> bytes:
    """Read the contents of the given XML request file."""
    base = read_file(file).decode("UTF-8")
    base = base.replace("    ", "").replace("\t", "").replace("\r", "")
    if leave_one:
        index = base.find("\n") + 1
        base = base[:index] + base[index:].replace("\n", "")
    else:
        base = base.replace("\n", "")
    return base.encode("UTF-8")


def verify_mms_request(
    request: MmsRequest,
    subsystem: RequestType,
    data_type: RequestDataType,
    signature: str,
    data: bytes,
    as_admin: bool = False,
    compressed: bool = False,
    send_request: bool = True,
    resp_compressed: bool = False,
    verifiers: List[Callable] = [],
):
    """Verify that the given MMS request was created with the correct parameters."""
    assert request.as_admin == as_admin
    assert request.compressed == compressed
    assert request.data_type == data_type
    assert request.payload == data
    assert request.respond_with_request == send_request
    assert request.response_compressed == resp_compressed
    assert request.signature == signature
    assert request.subsystem == subsystem
    verify_list(request.attachments, verifiers)


def verify_mms_response(
    response: MmsResponse,
    success: bool,
    data_type: ResponseDataType,
    payload: bytes,
    report_filename: Optional[str] = None,
    binary: bool = False,
    compressed: bool = False,
    warnings: bool = False,
    verifiers: List[Callable] = [],
):
    """Verify that the given MMS response was created with the correct parameters."""
    assert response.success == success
    assert response.data_type == data_type
    assert response.payload == payload
    assert response.report_filename == report_filename
    assert response.is_binary == binary
    assert response.compressed == compressed
    assert response.warnings == warnings
    verify_list(response.attachments, verifiers)


def attachment_verifier(name: str, data: bytes, signature: str):
    """Verify that the given attachment was created with the correct parameters."""

    def inner(att: Attachment):
        assert att.data == data
        assert att.name == name
        assert att.signature == signature

    return inner


def code_verifier(code: str):
    """Return a function that verifies a message has the expected code."""

    def inner(message: Message):
        assert message.code == code

    return inner


def messages_verifier(errors: list, warnings: list, infos: list):
    """Return a function that verifies that a message has the expected errors, warnings, and information."""

    def inner(messages: Messages):
        verify_list(messages.errors, errors)
        verify_list(messages.warnings, warnings)
        verify_list(messages.information, infos)

    return inner


def verify_messages(messages: Dict[str, Messages], verifiers: dict):
    """Verify that the messages are as we expect."""
    assert len(messages) == len(verifiers)
    print(messages)
    for key, verifier in verifiers.items():
        verifier(messages[key])


def verify_market_query(
    req: MarketQuery, date: Date, participant: str, user: str, market_type: Optional[MarketType] = None, days: int = 1
):
    """Verify that the MarketQuery was created with the correct parameters."""
    verify_base_market_request(req, date, participant, user, market_type)
    assert req.days == days


def verify_market_submit(
    req: MarketSubmit, date: Date, participant: str, user: str, market_type: Optional[MarketType] = None, days: int = 1
):
    """Verify that the MarketSubmit was created with the correct parameters."""
    verify_base_market_request(req, date, participant, user, market_type)
    assert req.days == days


def verify_market_cancel(
    req: MarketCancel, date: Date, participant: str, user: str, market_type: Optional[MarketType] = None, days: int = 1
):
    """Verify that the MarketCancel was created with the correct parameters."""
    verify_base_market_request(req, date, participant, user, market_type)
    assert req.days == days


def verify_base_market_request(
    req: BaseMarketRequest, date: Date, participant: str, user: str, market_type: Optional[MarketType] = None
):
    """Verify that the BaseMarketRequest was created with the correct parameters."""
    assert req.date == date
    assert req.participant == participant
    assert req.user == user
    assert req.market_type == market_type


def verify_registration_query(
    req: RegistrationQuery, action: QueryAction, query_type: QueryType, date: Optional[Date] = None
):
    """Verify that the RegistrationQuery was created with the correct parameters."""
    assert req.action == action
    assert req.query_type == query_type
    assert req.date == date


def verify_offer_data(
    request: OfferData,
    stack_verifiers: list,
    resource: str,
    start: DateTime,
    end: DateTime,
    direction: Direction,
    pattern: Optional[int] = None,
    bsp_participant: Optional[str] = None,
    company_short_name: Optional[str] = None,
    operator: Optional[str] = None,
    area: Optional[AreaCode] = None,
    resource_short_name: Optional[str] = None,
    system_code: Optional[str] = None,
    submission_time: Optional[DateTime] = None,
):
    """Verify that the given offer data request has the expected parameters."""
    assert request.resource == resource
    assert request.start == start
    assert request.end == end
    assert request.direction == direction
    verify_list(request.stack, stack_verifiers)
    verify_offer_data_optional(
        request,
        pattern_number=pattern,
        bsp_participant=bsp_participant,
        company_short_name=company_short_name,
        operator=operator,
        area=area,
        resource_short_name=resource_short_name,
        system_code=system_code,
        submission_time=submission_time,
    )


def verify_offer_data_optional(request: OfferData, **kwargs):
    """Verify that the given offer data request has the expected parameters."""
    for field, info in request.model_fields.items():
        if not info.is_required():
            if field in kwargs:
                assert getattr(request, field) == kwargs[field]
            else:
                assert getattr(request, field) is None


def offer_stack_verifier(
    number: int,
    price: float,
    quantity: float,
    primary: Optional[float] = None,
    seconday_1: Optional[float] = None,
    secondary_2: Optional[float] = None,
    tertiary_1: Optional[float] = None,
    tertiary_2: Optional[float] = None,
    id: Optional[str] = None,
):
    """Verify that the given offer stack has the expected parameters."""

    def inner(stack: OfferStack):
        assert stack.number == number
        assert stack.unit_price == price
        assert stack.minimum_quantity_kw == quantity
        assert stack.primary_qty_kw == primary
        assert stack.secondary_1_qty_kw == seconday_1
        assert stack.secondary_2_qty_kw == secondary_2
        assert stack.tertiary_1_qty_kw == tertiary_1
        assert stack.tertiary_2_qty_kw == tertiary_2
        assert stack.id == id

    return inner


def verify_offer_query(
    req: OfferQuery, market_type: MarketType, area: Optional[AreaCode] = None, resource: Optional[str] = None
):
    """Verify that the OfferQuery was created with the correct parameters."""
    assert req.market_type == market_type
    assert req.area == area
    assert req.resource == resource


def verify_offer_cancel(req: OfferCancel, resource: str, start: DateTime, end: DateTime, market_type: MarketType):
    """Verify that the OfferCancel was created with the correct parameters."""
    assert req.resource == resource
    assert req.start == start
    assert req.end == end
    assert req.market_type == market_type


def verify_resource_data(
    req: ResourceData,
    output_band_verifiers: list = None,
    switch_verifiers: list = None,
    afc_minimum_verifiers: list = None,
    startup_verifiers: list = None,
    shutdown_verifiers: list = None,
    **kwargs,
):
    """Verify that the given resource data request has the expected parameters."""
    # Verify the list sub-types
    print(req)
    verify_list(req.output_bands, output_band_verifiers)
    verify_list(req.switch_outputs, switch_verifiers)
    verify_list(req.afc_minimum_outputs, afc_minimum_verifiers)
    verify_list(req.startup_patterns, startup_verifiers)
    verify_list(req.shutdown_patterns, shutdown_verifiers)

    # Verify the remaining fields
    for field in req.model_fields.keys():
        if field not in [
            "output_bands",
            "switch_outputs",
            "afc_minimum_outputs",
            "startup_patterns",
            "shutdown_patterns",
        ]:
            if field in kwargs:
                assert getattr(req, field) == kwargs[field]
            else:
                assert getattr(req, field) is None


def verify_resource_query(
    req: ResourceQuery, participant: Optional[str] = None, name: Optional[str] = None, status: Optional[Status] = None
):
    """Verify that the ResourceQuery was created with the correct parameters."""
    assert req.participant == participant
    assert req.name == name
    assert req.status == status


def output_band_verifier(
    output: int,
    gf_bandwidth: int,
    lfc_bandwidth: int,
    lfc_variation_speed: int,
    edc_change_rate: int,
    edc_lfc_change_rate: int,
):
    """Verify that the given output band has the expected parameters."""

    def inner(band: OutputBand):
        assert band.output_kW == output
        assert band.gf_bandwidth_kW == gf_bandwidth
        assert band.lfc_bandwidth_kW == lfc_bandwidth
        assert band.lfc_variation_speed_kW_min == lfc_variation_speed
        assert band.edc_change_rate_kW_min == edc_change_rate
        assert band.edc_lfc_change_rate_kW_min == edc_lfc_change_rate

    return inner


def switch_output_verifier(output: int, switch_time: int):
    """Verify that the given switch output has the expected parameters."""

    def inner(switch: SwitchOutput):
        assert switch.output_kW == output
        assert switch.switch_time_min == switch_time

    return inner


def afc_minimum_output_verifier(output: int, operation_time: Decimal, variation_speed: int):
    """Verify that the given AFC minimum output has the expected parameters."""

    def inner(afc: AfcMinimumOutput):
        assert afc.output_kW == output
        assert afc.operation_time_hr == operation_time
        assert afc.variation_speed_kW_min == variation_speed

    return inner


def pattern_verifier(name: str, events: list):
    """Verify that a StartupPattern has the expected parameters."""

    def inner(pattern: Union[StartupPattern, ShutdownPattern]):
        assert pattern.pattern_name == name
        assert len(pattern.events) == len(events)
        for event, verifier in zip(pattern.events, events):
            verifier(event)

    return inner


def event_verifier(name, charge_time: str, output: int):
    """Verify that a StartupEvent or ShutdownEvent has the expected parameters."""

    def inner(event: Union[StartupEvent, ShutdownEvent]):
        assert event.name == name
        assert event.change_time == charge_time
        assert event.output_kw == output

    return inner


def verify_list(items: list = None, verifiers: list = None):
    """Verify that the given list of items was created with the correct parameters."""
    print(items)
    if items is None or verifiers is None:
        assert items is None and verifiers is None
        return
    assert len(items) == len(verifiers)
    for item, verifier in zip(items, verifiers):
        verifier(item)


def register_mms_request(
    request_type: RequestType,
    signature: str,
    data: bytes,
    response: bytes,
    status: int = 200,
    url: str = "https://www2.tdgc.jp/axis2/services/MiWebService",
    **kwargs,
):
    """Register a new MMS request and response with the responses library."""
    responses.add(
        responses.Response(
            method="POST",
            url=url,
            body=create_response(response, **kwargs) if status == 200 else b"",
            status=status,
            content_type="text/xml; charset=utf-8",
            auto_calculate_content_length=True,
            match=[
                PayloadMatcher(request_type, signature, data),
                header_matcher({"Content-Type": "text/xml; charset=utf-8"}),
            ],
        )
    )


def create_response(
    data: bytes,
    data_type: ResponseDataType = ResponseDataType.XML,
    success: bool = True,
    warnings: bool = False,
    compressed: bool = False,
) -> bytes:
    """Create a new MMS response with the given data."""

    def to_bool(value: bool) -> str:
        return "true" if value else "false"

    return (
        """<?xml version='1.0' encoding='utf-8'?>\n<soap-env:Envelope """
        """xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"><soap-env:Body><ns0:ResponseAttInfo """
        f"""xmlns:ns0="urn:abb.com:project/mms/types"><success>{to_bool(success)}</success><warnings>"""
        f"""{to_bool(warnings)}</warnings><responseBinary>false</responseBinary><responseCompressed>"""
        f"""{to_bool(compressed)}</responseCompressed><responseDataType>{data_type.value}</responseDataType>"""
        f"""<responseData>{b64encode(data).decode("UTF-8")}</responseData></ns0:ResponseAttInfo></soap-env:Body>"""
        """</soap-env:Envelope>"""
    ).encode("UTF-8")


class PayloadMatcher:
    """A custom matcher for comparing XML payloads."""

    def __init__(self, request_type: RequestType, signature: str, data: bytes):
        """Create a new XML payload matcher with the given expected XML payload."""
        self.expected = (
            """<?xml version='1.0' encoding='utf-8'?>\n<soap-env:Envelope """
            """xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"><soap-env:Body><ns0:RequestAttInfo """
            f"""xmlns:ns0="urn:abb.com:project/mms/types"><requestType>{request_type.value}</requestType><adminRole>"""
            """false</adminRole><requestDataCompressed>false</requestDataCompressed><requestDataType>XML"""
            """</requestDataType><sendRequestDataOnSuccess>false</sendRequestDataOnSuccess>"""
            f"""<sendResponseDataCompressed>false</sendResponseDataCompressed><requestSignature>{signature}"""
            f"""</requestSignature><requestData>{b64encode(data).decode("UTF-8")}</requestData></ns0:RequestAttInfo>"""
            """</soap-env:Body></soap-env:Envelope>"""
        ).encode("utf-8")

    def __call__(self, request: PreparedRequest) -> Tuple[bool, str]:
        """Return True if the request's body matches the expected XML payload."""

        # First, parse the request body and the expected XML payload
        actual = request.body
        print(f"Actual: {actual}")
        print(f"Expected: {self.expected}")

        # Next, compare the two payloads and return the result
        return actual == self.expected, "XML payloads do not match"
