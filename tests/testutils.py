"""Contains utility functions for testing the MMS client."""

from base64 import b64encode
from datetime import date as Date
from decimal import Decimal
from pathlib import Path
from re import compile as rcompile
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

from mms_client.types.award import Award
from mms_client.types.award import AwardQuery
from mms_client.types.award import AwardResponse
from mms_client.types.award import AwardResult
from mms_client.types.award import ContractResult
from mms_client.types.award import ContractSource
from mms_client.types.base import Message
from mms_client.types.base import Messages
from mms_client.types.enums import AreaCode
from mms_client.types.enums import BooleanFlag
from mms_client.types.enums import ResourceType
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
from mms_client.types.reserve import Requirement
from mms_client.types.reserve import ReserveRequirement
from mms_client.types.reserve import ReserveRequirementQuery
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


def read_request_file(file: str) -> str:
    """Read the contents of the given XML request file."""
    base = read_file(file).decode("UTF-8")
    base = base.replace("    ", "").replace("\t", "").replace("\r", "")
    base = base.replace("\n", "")
    return base


def verify_mms_request(
    request: MmsRequest,
    subsystem: RequestType,
    data_type: RequestDataType,
    signature: str,
    data: str,
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


def attachment_verifier(name: str, data: str, signature: str):
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


def verify_market_query(req: MarketQuery, date: Date, participant: str, user: str, days: int = 1):
    """Verify that the MarketQuery was created with the correct parameters."""
    verify_base_market_request(req, date, participant, user)
    assert req.days == days


def verify_market_submit(
    req: MarketSubmit, date: Date, participant: str, user: str, market_type: Optional[MarketType] = None, days: int = 1
):
    """Verify that the MarketSubmit was created with the correct parameters."""
    verify_base_market_request(req, date, participant, user)
    assert req.days == days
    assert req.market_type == market_type


def verify_market_cancel(
    req: MarketCancel, date: Date, participant: str, user: str, market_type: MarketType, days: int = 1
):
    """Verify that the MarketCancel was created with the correct parameters."""
    verify_base_market_request(req, date, participant, user)
    assert req.days == days
    assert req.market_type == market_type


def verify_base_market_request(req: BaseMarketRequest, date: Date, participant: str, user: str):
    """Verify that the BaseMarketRequest was created with the correct parameters."""
    assert req.date == date
    assert req.participant == participant
    assert req.user == user


def verify_registration_query(
    req: RegistrationQuery, action: QueryAction, query_type: QueryType, date: Optional[Date] = None
):
    """Verify that the RegistrationQuery was created with the correct parameters."""
    assert req.action == action
    assert req.query_type == query_type
    assert req.date == date


def verify_award_query(req: AwardQuery, market_type: MarketType, start: DateTime, end: DateTime, **kwargs):
    """Verify that the given AwardQuery has the expected parameters."""
    assert req.market_type == market_type
    assert req.start == start
    assert req.end == end
    for field, info in req.model_fields.items():
        if not (info.is_required() or field == "results"):
            if field in kwargs:
                assert getattr(req, field) == kwargs[field]
            else:
                assert getattr(req, field) is None


def verify_award_response(
    resp: AwardResponse,
    market_type: MarketType,
    start: DateTime,
    end: DateTime,
    result_verifiers: list = None,
    **kwargs,
):
    """Verify that the given AwardResponse has the expected parameters."""
    verify_award_query(resp, market_type, start, end, **kwargs)
    verify_list(resp.results, result_verifiers)


def award_result_verifier(start: DateTime, end: DateTime, direction: Direction, award_verifiers: list):
    """Return a function that verifies the award results response has the expected parameters."""

    def inner(resp: AwardResult):
        assert resp.start == start
        assert resp.end == end
        assert resp.direction == direction
        verify_list(resp.data, award_verifiers)

    return inner


def award_verifier(
    contract_id: str,
    jbms_id: str,
    area: AreaCode,
    resource: str,
    resource_name: str,
    system_code: str,
    resource_type: ResourceType,
    bsp_participant: str,
    company_name: str,
    operator: str,
    offer_price: Decimal,
    contract_price: Decimal,
    eval_coeff: Decimal,
    corrected_price: Decimal,
    result: ContractResult,
    source: ContractSource,
    gate_closed: BooleanFlag,
    **kwargs,
):
    """Return a function that verifies the award result has the expected parameters."""

    def inner(resp: Award):
        resp.contract_id == contract_id
        resp.jbms_id == jbms_id
        resp.area == area
        resp.resource == resource
        resp.resource_short_name == resource_name
        resp.system_code == system_code
        resp.resource_type == resource_type
        resp.bsp_participant == bsp_participant
        resp.company_short_name == company_name
        resp.operator == operator
        resp.offer_price == offer_price
        resp.contract_price == contract_price
        resp.performance_evaluation_coefficient == eval_coeff
        resp.corrected_unit_price == corrected_price
        resp.offer_award_level == result
        resp.contract_source == source
        resp.gate_closed == gate_closed
        for field, info in resp.model_fields.items():
            if not info.is_required():
                if field in kwargs:
                    assert getattr(resp, field) == kwargs[field]
                else:
                    assert getattr(resp, field) is None

    return inner


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


def verify_reserve_requirement_query(
    req: ReserveRequirementQuery, market_type: MarketType, area: Optional[AreaCode] = None
):
    """Verify that the ReserveRequirementQuery was created with the correct parameters."""
    assert req.area == area
    assert req.market_type == market_type


def verify_reserve_requirement(req: ReserveRequirement, area: AreaCode, requirement_verifiers: list):
    """Verify that the ReserveRequirement was created with the correct parameters."""
    assert req.area == area
    verify_list(req.requirements, requirement_verifiers)


def requirement_verifier(
    start: DateTime,
    end: DateTime,
    primary: Optional[int] = None,
    secondary_1: Optional[int] = None,
    secondary_2: Optional[int] = None,
    tertiary_1: Optional[int] = None,
    tertiary_2: Optional[int] = None,
    primary_secondary_1: Optional[int] = None,
    primary_secondary_2: Optional[int] = None,
    primary_tertiary_1: Optional[int] = None,
):
    """Verify that the given Requirement has the expected parameters."""

    def inner(req: Requirement):
        assert req.start == start
        assert req.end == end
        assert req.direction == Direction.SELL
        assert req.primary_qty_kw == primary
        assert req.secondary_1_qty_kw == secondary_1
        assert req.secondary_2_qty_kw == secondary_2
        assert req.tertiary_1_qty_kw == tertiary_1
        assert req.tertiary_2_qty_kw == tertiary_2
        assert req.primary_secondary_1_qty_kw == primary_secondary_1
        assert req.primary_secondary_2_qty_kw == primary_secondary_2
        assert req.primary_tertiary_1_qty_kw == primary_tertiary_1

    return inner


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
    data: str,
    response: bytes,
    status: int = 200,
    url: str = "https://www2.tdgc.jp/axis2/services/MiWebService",
    multipart: bool = False,
    encoded: bool = False,
    **kwargs,
):
    """Register a new MMS request and response with the responses library."""
    matches = (
        [MultipartPayloadMatcher(request_type, signature, data, encoded)]
        if multipart
        else [
            PayloadMatcher(request_type, signature, data),
            header_matcher({"Content-Type": "text/xml; charset=utf-8"}),
        ]
    )
    responses.add(
        responses.Response(
            method="POST",
            url=url,
            body=create_response(response, **kwargs) if status == 200 else b"",
            status=status,
            content_type="text/xml; charset=utf-8",
            auto_calculate_content_length=True,
            match=matches,
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


class MultipartPayloadMatcher:
    """A custom matcher for comparing XML payloads."""

    def __init__(self, request_type: RequestType, signature: str, data: str, encoded: bool):
        """Create a new XML payload matcher with the given expected XML payload."""
        self.request_type = request_type
        self.signature = signature
        self.encoded = encoded
        if self.encoded:
            b64 = b64encode(data.encode("UTF-8")).decode("UTF-8")
            self.data = "".join(b64[i : i + 76] + "\n" for i in range(0, len(b64), 76))
        else:
            self.data = b64encode(data.encode("UTF-8")).decode("UTF-8") if encoded else data
        self._regex = rcompile(
            r"(?s)--MIMEBoundary_(?P<boundary>[\w=]*).*Content-ID:\s<(?P<mtom>[\w=]*).*cid:(?P<cid>\w{16}.*)\"\/>.*"
        )

    def __call__(self, request: PreparedRequest) -> Tuple[bool, str]:
        """Return True if the request's body matches the expected XML payload."""
        # First, convert the request body to a string
        actual = request.body.decode("UTF-8")
        print(f"Actual: {actual}")

        # Next, match the request body against the expected pattern
        match = self._regex.match(actual)
        if not match:
            return False, "XML payload did not match expected pattern"

        # Now, verify the content-type header
        content_type = f'multipart/related; charset="UTF-8"; type="application/xop+xml"; start="<{match.group("mtom")}@fake.com>"; boundary="MIMEBoundary_{match.group("boundary")}"; start-info="application/soap+xml"'
        if request.headers["Content-Type"] != content_type:
            return (
                False,
                f"Content-Type header of {request.headers['Content-Type']} did not match expected value: {content_type}",
            )

        # Finally, compare the request body to the expected XML payload
        expected = (
            f"""--MIMEBoundary_{match.group('boundary')}\r\nMIME-Version: 1.0\r\nContent-Transfer-Encoding: 7bit\r\n"""
            """Content-Type: application/xop+xml; charset="utf-8"; type="text/xml"\r\nContent-ID: """
            f"""<{match.group('mtom')}@fake.com>\r\nContent-Transfer-Encoding: binary\n\n<?xml version='1.0' """
            f"""encoding='utf-8'?>\n<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">"""
            """<soap-env:Body><ns0:RequestAttInfo xmlns:ns0="urn:abb.com:project/mms/types"><requestType>"""
            f"""{self.request_type.value}</requestType><adminRole>false</adminRole><requestDataCompressed>false"""
            """</requestDataCompressed><requestDataType>XML</requestDataType><sendRequestDataOnSuccess>false"""
            """</sendRequestDataOnSuccess><sendResponseDataCompressed>false</sendResponseDataCompressed>"""
            f"""<requestSignature>{self.signature}</requestSignature><requestData><xop:Include xmlns:xop="http://"""
            f"""www.w3.org/2004/08/xop/include" href="cid:{match.group('cid')}"/></requestData></ns0:RequestAttInfo>"""
            f"""</soap-env:Body></soap-env:Envelope>\n--MIMEBoundary_{match.group('boundary')}\nContent-Transfer-"""
            f"""Encoding: {"base64" if self.encoded else "binary"}\nContent-ID: <{match.group('cid')}>\nContent-Type: """
            f"""application/octet-stream; charset="utf-8"\n\n{self.data}\n--MIMEBoundary_{match.group('boundary')}--\n"""
        )
        print(f"Expected: {expected}")
        try:
            assert actual == expected
        except AssertionError as e:
            print(e)
        return actual == expected, "XML payloads do not match"


class PayloadMatcher:
    """A custom matcher for comparing XML payloads."""

    def __init__(self, request_type: RequestType, signature: str, data: str):
        """Create a new XML payload matcher with the given expected XML payload."""
        self.expected = (
            """<?xml version='1.0' encoding='utf-8'?>\n<soap-env:Envelope """
            """xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"><soap-env:Body><ns0:RequestAttInfo """
            f"""xmlns:ns0="urn:abb.com:project/mms/types"><requestType>{request_type.value}</requestType><adminRole>"""
            """false</adminRole><requestDataCompressed>false</requestDataCompressed><requestDataType>XML"""
            """</requestDataType><sendRequestDataOnSuccess>false</sendRequestDataOnSuccess>"""
            f"""<sendResponseDataCompressed>false</sendResponseDataCompressed><requestSignature>{signature}"""
            f"""</requestSignature><requestData>{data}</requestData></ns0:RequestAttInfo></soap-env:Body>"""
            """</soap-env:Envelope>"""
        ).encode("utf-8")

    def __call__(self, request: PreparedRequest) -> Tuple[bool, str]:
        """Return True if the request's body matches the expected XML payload."""

        # First, parse the request body and the expected XML payload
        actual = request.body
        print(f"Actual: {actual}")
        print(f"Expected: {self.expected}")

        # Next, compare the two payloads and return the result
        return actual == self.expected, "XML payloads do not match"
