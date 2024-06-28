"""Contains a transport override supporting MTOMS attachments."""

import string
from base64 import b64encode
from email.encoders import encode_7or8bit
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from logging import getLogger
from random import SystemRandom
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from lxml import etree
from lxml.etree import _Element as Element
from pendulum import now
from requests import Response
from requests import Session
from zeep.cache import VersionedCacheBase
from zeep.transports import Transport
from zeep.wsdl.utils import etree_to_string

from mms_client.utils.plugin import Plugin

# Set the default logger for the MMS client
logger = getLogger(__name__)


# Define the namespaces used in the XML
XOP = "http://www.w3.org/2004/08/xop/include"
XMIME5 = "http://www.w3.org/2005/05/xmlmime"
FILETAG = "xop:Include:"
ID_LEN = 16


# Define a function to generate a randomized ID string
def get_id(length: int = ID_LEN) -> str:
    """Generate a randomized ID string.

    Arguments:
    length (int):   The length of the ID string to generate.

    Returns:    The randomized ID string.
    """
    return "".join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def now_b64():
    """Return a base64 encoded string of the current timestamp."""
    return b64encode(f"{now().timestamp()}".replace(".", "").encode("UTF-8")).decode("UTF-8")


def get_boundary() -> str:
    """Return a randomized MIME boundary string."""
    return f"MIMEBoundary_{now_b64()}".center(33, "=")


def get_content_id(domain: str) -> str:
    """Return a randomized MIME content ID string.

    Arguments:
    domain (str):   The domain of the content ID.

    Returns:    The randomized MIME content ID string.
    """
    return f"<{now_b64()}@{domain}>"


def overwrite_attachnode(node):
    """Overwrite the attachment node.

    Arguments:
    node (Element):    The XML node to be overwritten.

    Returns:    The attachment node.
    """
    cid = node.text[len(FILETAG) :]
    node.text = None
    etree.SubElement(node, f"{{{XOP}}}Include", nsmap={"xop": XOP}, href=f"cid:{cid}")
    return cid


def get_multipart(content_id: str) -> MIMEMultipart:
    """Create a MIME multipart object.

    Arguments:
    content_id (str):   The content ID to be used for the attachment.

    Returns:    The MIME multipart object.
    """
    part = MIMEMultipart(
        "related", charset="UTF-8", type="application/xop+xml", boundary=get_boundary(), start=content_id
    )
    part.set_param("start-info", "application/soap+xml")
    return part


def get_envelope_part(envelope: Element, content_id: str) -> MIMEApplication:
    """Create the MIME envelope part.

    Arguments:
    envelope (Element):    The XML envelope to be attached.
    content_id (str):      The content ID to be used for the attachment.

    Returns:    The MIME envelope part.
    """
    part = MIMEApplication(etree_to_string(envelope), "xop+xml", encode_7or8bit)
    part.set_param("charset", "utf-8")
    part.set_param("type", "text/xml")
    part.add_header("Content-ID", content_id)
    part.add_header("Content-Transfer-Encoding", "binary")
    return part


class Attachment:
    """Represents an attachment to be sent with a multipart request."""

    def __init__(self, name: str, data: bytes, domain: str):
        """Create a new attachment.

        Arguments:
        name (str):   The name of the attachment.
        data (bytes): The data to be attached.
        domain (str): The domain of the content ID.
        """
        self.name = name
        self.data = data
        self.cid = f"{get_id()}-{name}@{domain}"
        self.tag = FILETAG + self.cid


class MultipartTransport(Transport):
    """A transport that supports MTOMS attachments."""

    def __init__(
        self,
        domain: str,
        cache: Optional[VersionedCacheBase] = None,
        timeout: int = 300,
        operation_timeout: Optional[int] = None,
        session: Optional[Session] = None,
        plugins: Optional[List[Plugin]] = None,
    ):
        """Create a new MTOMS transport.

        Arguments:
        domain (str):                           The domain of the content ID to use.
        cache (VersionedCacheBase, optional):   The cache to be used for the transport.
        timeout (int):                          The timeout for the transport.
        operation_timeout (int, optional):      The operation timeout for the transport.
        session (Session, optional):            The session to be used for the transport.
        plugins (List[Plugin], optional):       The plugins to be used for the transport.
        """
        # Save the domain for later use
        self._domain = domain

        # Setup a dictionary to store the attachments and operations after they're registered
        self._attachments: Dict[str, Attachment] = {}
        self._operations: Dict[str, str] = {}

        # Save our list of plugins
        self._plugins = plugins or []

        # Call the parent constructor
        super().__init__(
            cache=cache,
            timeout=timeout,
            operation_timeout=operation_timeout,
            session=session,
        )

    def register_attachment(self, operation: str, name: str, data: bytes) -> str:
        """Register an attachment.

        Registered attachments will be sent with the request as MTOMS attachments. The content ID of the attachment
        will be returned so that it can be used in the request.

        Arguments:
        operation (str):    The name of the operation.
        name (str):         The name of the attachment.
        data (bytes):       The data to be attached.

        Returns:    The content ID of the attachment, which should be used in place of the attachment data.
        """
        attachment = Attachment(name, data, self._domain)
        self._attachments[attachment.cid] = attachment
        self._operations[attachment.cid] = operation
        return attachment.tag

    def post_xml(self, address: str, envelope: Element, headers: dict) -> Response:
        """Post the XML envelope and attachments.

        Arguments:
        address (str):      The address to post the data to.
        envelope (Element): The XML envelope to be attached.
        headers (dict):     The headers to be used for the request.

        Returns:    The response from the server.
        """
        # First, search for values that start with our FILETAG
        filetags = envelope.xpath(f"//*[starts-with(text(), '{FILETAG}')]")

        # Next, if there are any attached files, we will set the attachments. Otherwise, just the envelope
        if filetags:
            message, operation = self.create_mtom_request(filetags, envelope, headers)
        else:
            message, operation = etree_to_string(envelope), address

        # Iterate over all the plugins and call their egress methods
        for plugin in self._plugins:
            message, headers = plugin.egress(message, headers, operation)

        # Now, post the request and get the response
        resp = self.post(address, message, headers)

        # Iterate over all the plugins and call their ingress methods
        for plugin in self._plugins:
            resp._content, resp.headers = plugin.ingress(resp.content, resp.headers, operation)

        # Finally, return the response
        return resp

    def create_mtom_request(self, filetags, envelope: Element, headers: dict) -> Tuple[bytes, str]:
        """Set MTOM attachments and return the right envelope.

        Arguments:
        filetags (list):    The list of XML paths to the attachments.
        envelope (Element): The XML envelope to be attached.
        headers (dict):     The headers to be used for the request.

        Returns:    The XML envelope with the attachments.
        """
        # First, get an identifier for the request and then use it to create a new multipart request
        content_id = get_content_id(self._domain)
        mtom_part = get_multipart(content_id)

        # Next, let's set the XOP:Include nodes for each attachment
        files = [overwrite_attachnode(f) for f in filetags]

        # Now, create the request envelope and attach it to the multipart request
        env_part = get_envelope_part(envelope, content_id)
        mtom_part.attach(env_part)

        # Attach each file to the multipart request
        for cid in files:
            operation = self._operations.pop(cid)
            mtom_part.attach(self.create_attachment(cid))

        # Finally, create the final multipart request string
        bound = f"--{mtom_part.get_boundary()}"
        marray = mtom_part.as_string().split(bound)
        mtombody = bound + bound.join(marray[1:])

        # Set the content length and add the MTOM headers to the request
        mtom_part.add_header("Content-Length", str(len(mtombody)))
        headers.update(dict(mtom_part.items()))

        # Decode the XML and return the request
        message = mtom_part.as_string().split("\n\n", 1)[1]
        message = message.replace("\n", "\r\n", 5)
        return message.encode("UTF-8"), operation

    def create_attachment(self, cid):
        """Create an attachment for the multipart request.

        Arguments:
        cid (str):   The content ID of the attachment.

        Returns:    The attachment.
        """
        # First, get the attachment from the cache
        attach = self._attachments.pop(cid)

        # Next, create the attachment
        part = MIMEBase("application", "octet-stream")
        part["Content-Transfer-Encoding"] = "binary"
        part["Content-ID"] = f"<{attach.cid}>"
        part.set_payload(attach.data, charset="utf-8")
        del part["mime-version"]

        # Finally, return the attachment
        return part
