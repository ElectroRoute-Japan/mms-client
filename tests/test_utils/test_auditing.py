"""Tests the functionality of the mms_client.utils.auditing module."""

from base64 import b64encode
from logging import getLogger

import responses

from mms_client.security.certs import Certificate
from mms_client.types.transport import MmsRequest
from mms_client.types.transport import RequestDataType
from mms_client.types.transport import RequestType
from mms_client.types.transport import ResponseDataType
from mms_client.utils.auditing import AuditPlugin
from mms_client.utils.web import ClientType
from mms_client.utils.web import Interface
from mms_client.utils.web import ZWrapper
from tests.testutils import register_mms_request
from tests.testutils import verify_mms_response


class FakeAuditPlugin(AuditPlugin):
    """Test AuditPlugin that we'll use to verify the functionality of the AuditPlugin class."""

    def __init__(self):
        """Initialize the TestAuditPlugin class."""
        self.name = None
        self.request = None
        self.response = None

    def audit_request(self, name: str, mms_request: bytes) -> None:
        """Audit an MMS request."""
        self.request = mms_request
        self.name = name

    def audit_response(self, name: str, mms_response: bytes) -> None:
        """Audit an MMS response."""
        self.response = mms_response
        self.name = name


@responses.activate
def test_auditer_works(mock_certificate: Certificate):
    """Test that the submit method of the ZWrapper class handles server errors as expected."""
    # First, register our test responses with the responses library
    register_mms_request(RequestType.INFO, "test", "derp", b"derp")

    # Next, create our Zeep client
    auditor = FakeAuditPlugin()
    z = ZWrapper("fake.com", ClientType.BSP, Interface.MI, mock_certificate.to_adapter(), plugins=[auditor])

    # Now, attempt to submit a request and retrieve the response
    resp = z.submit(
        MmsRequest(
            requestType=RequestType.INFO,
            requestDataType=RequestDataType.XML,
            requestSignature="test",
            requestData="derp",
            sendRequestDataOnSuccess=False,
        )
    )

    # Finally, verify that the response is as expected and that the data was audited properly
    verify_mms_response(resp, True, ResponseDataType.XML, b"derp")
    data = b64encode(b"derp").decode("UTF-8")
    assert auditor.request == (
        """<?xml version='1.0' encoding='UTF-8'?>\n<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/"""
        """soap/envelope/"><soap-env:Body><ns0:RequestAttInfo xmlns:ns0="urn:abb.com:project/mms/types">"""
        """<requestType>mp.info</requestType><adminRole>false</adminRole><requestDataCompressed>false"""
        """</requestDataCompressed><requestDataType>XML</requestDataType><sendRequestDataOnSuccess>false"""
        """</sendRequestDataOnSuccess><sendResponseDataCompressed>false</sendResponseDataCompressed>"""
        f"""<requestSignature>test</requestSignature><requestData>derp</requestData></ns0:RequestAttInfo>"""
        """</soap-env:Body></soap-env:Envelope>"""
    ).encode("UTF-8")
    assert auditor.response == (
        """<?xml version='1.0' encoding='UTF-8'?>\n<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/"""
        """soap/envelope/"><soap-env:Body><ns0:ResponseAttInfo xmlns:ns0="urn:abb.com:project/mms/types"><success>"""
        """true</success><warnings>false</warnings><responseBinary>false</responseBinary><responseCompressed>false"""
        f"""</responseCompressed><responseDataType>XML</responseDataType><responseData>{data}</responseData>"""
        """</ns0:ResponseAttInfo></soap-env:Body></soap-env:Envelope>"""
    ).encode("UTF-8")
    assert auditor.name == "submitAttachment"
