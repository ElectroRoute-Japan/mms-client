[![Unit Tests Status](https://github.com/ElectroRoute-Japan/mms-client/actions/workflows/check.yml/badge.svg)](https://github.com/ElectroRoute-Japan/mms-client/actions)

# Overview
This repository contains a Python client that is capable of communication with the Market Management System (MMS), which handles requests related to Flex or Virtual Power Plant (VPP) trading. The underlying library relies on SOAP communication, which is a pain to work with at the best of times. This particular SOAP API adds its own special layer of obnoxiousness, however. As such, it was deemed useful to have a client which would obfuscate most, if not all of this away from the user.

# Communication
The underlying API sends and receives XML documents. Each of these request or responses, which we will hereafter refer to as *outer* requests and responses, contains metadata about the request/response as well as three fields which are extremely important to successful communication with the API:
- Attachments data, included as a list of elements with the binary data in a base-64 encoded format
- Payload data, encoded in a base-64 encoded format
- Payload signature, which is the SHA256 hash of the payload XML data, then signed with an RSA key, in a base-64 encoded format

After the data has been converted and added to the outer request object, it is sent to the appropriate server endpoint via a Zeep client. The client certificate is also injected into the request using a PCKS12 adaptor.

## Domain
The domain to use when signing the content ID to MTOM attachments is specified when creating the client. This is not verified by the server, but it is used to generate the content ID for the MTOM attachments. As such, it is important to ensure that the domain is correct.

# Serialization
This library relies on Pydantic 2 and the pydantic-xml library for serialization/deserialization. As such, any type in this library can be converted to not only XML, but to JSON as well. This is extremely useful if you're trying to build a pass-through API service or something similar.

## Client Types
Clients cannot call any and all endpoints in this API, willy-nilly. Some endpoints are restricted to particular clients. At the moment, there are three clients: Balance Service Providers (BSPs), Market Operators (MOs), and Transmission Service Operators (TSOs). Most likely you're operating as a BSP or MO, in which case you'll have access to most or all endpoints. However, it makes little sense for a TSO to be able to submit bids on their own power, so they are restricted to a read-only role in most cases.

Note that MOs and BSPs access the MMS service using the same endpoints, but have distinct permissions. As such, both client types are supported explicitly here.

Should you request an endpoint which you are not authorized for, you will receive an `mms_client.utils.errors.AudienceError`.

## Interface Type
The MMS has two separate endpoints, depending on whether you want to access market information (MI), or other market information (OMI). Really informative, I know. Fortunately, we have designed this API in such a way that the distinction around which interface is which is unnecessary for you to know. However, note that separate Zeep clients will be maintained for each interface. These will be created as needed, which endpoints requiring the associated interface are first called. These are both setup to cache schemas to improve performance, as well. The memory required for these clients is still light, but you may want to reduce that further based on your application.

# Object Hierarchy
The object hierarchy contained in this project is not trivial, and perhaps that reflects a bit of overengineering on our part. However, we chose the paradigm we did to reduce the number of types which had to be exposed to the user. The diagram below indicates how this hierarchy works:

![MMS Client Object Hierarchy](https://github.com/ElectroRoute-Japan/mms-client/raw/main/docs/mmsclient_hierarchy.drawio.png)

Note that there are some types here that are shared between the request and response: mainly, anything inheriting from `mms_client.types.base.Envelop` or `mms_client.types.base.Payload`. For users of the client, only the Payload types need ever be used. Everything else has been obfuscated away, so it is unecessary for the user to have access to these. However, we will explain our reasoning here to provide additional context.

## Requests
The primary request DTO is the `mms_client.types.transport.MmsRequest` object. The majority of the fields here are metadata specifying how the client should communicate with the MMS server. However, `requestData`, `requestSignature` and `attachmentData` do bear considering as these represent the actual request, a signature used to verify that the request was received, and any attachments to the request, respectively. As mentioned before, `requestData` and `attachementData` can each represent more complex objects, which should be serialized and then encoded as base-64 strings.

## Responses
The primary response DTO is the `mms_client.types.transport.MmsResponse` object. Similar to the request DTO, this object includes a number of fields containing metadata describing how the response should be interpretted. Currently, only uncompressed XML is supported and any other response type will result in an `mms_client.utils.errors.MmsClientError`. Again, the `requestData` and `attachmentData` fields contain the payload data, encoded as base-64 strings.

### BaseResponse
This object represents the top-level XML element contained within the `MmsResponse`. It contains all other response data. Note that the structure of this object will not mimic the structure of the XML response, as that structure is incompatible with the philosophy of this library. However, all the information has been preserved. This type contains a number of validation elements as well as the envelope.

### Response & MultiResponse
These objects contain the actual payload data and inherit from `BaseResponse`. These are what will actually be returned from the deserialization process. They also contain validation data for the top-level paylaod item(s). The difference between `Response` and `MultiResponse` is that the former contains a single item and the latter contains a list.

## Envelopes
Not to be confused with the SOAP envelope, this envelope contains the method parameters used to send requests to the MMS server. For example, if you wanted to send a market-related request, this would take on the form of a `MarketQuery`, `MarketSubmit` or `MarketCancel` object. This is combined with the payload during the serialization process to produce the final XML payload before injecting it into the `MmsRequest`. During the deserialization process, this is extracted from the XML paylod on the `MmsResponse` object. Each of these should inherit from `mms_client.types.base.Envelope`.

## Payloads
This is the actual data that is sent to and returned from client methods and represent the actual "data", as contained on the MMS server. As such, these represent the first-class objects within this library. During the serialization process, this data is inserted into the envelope before being serialized to XML. During the deserialization process, these objects are extracted from the envelope XML and converted to the object therein. Each of these should inherit from `mms_client.types.base.Payload`. Note, however, that not everything that inherits from this class will represent a top-level object.

## Validation
There are a number of validation objects returned with the response, each with its own purpose. Any case resulting in a validation failure will cause an `mms_client.utils.errors.MMSValidationError` to be raised.

### ProcessingStatistics
This object describes the number of items in the request that were received, the number of valid items, the number of invalid items, the number of items successfully and unsuccessfully returned, respectively. This object also features some information on the latency and receipt time of the request. Given how the MMS determines the values of these fields, this client will check that there are no invalid files and raise an exception otherwise.

### ResponseCommon
This object can be found on the envelope and top-level payload object(s) within the response. It contains a success flag and a value describing whether or not validation passed. If `success` is True, then `validation` should be either "PASSED" or "NOT_DONE". Any other status indicates a failure and will result in an exception.

### Messages
Each Payload object will have a collection of messages. These are organized into three categories: information, warnings and errors. Information and warnings will be logged, but will not cause validation failures. Errors will, however, result in an exception being raised.

# Authentication
The authentication scheme used by the MMS has been forced down to this client, but we have tried to make it nicer for our users to ingest. Essentially, to authenticate requests with the MMS server, three pieces of information are required.

## Certificate
The MMS should have made a certificate available to you when you signed up to access the system. This certificate should be a PCKS#12 file and should have a passphrase associated with it. We have created a convenience class to handle this objects, called `mms_client.security.certs.Certificate`. There are a number of ways the certificate can be created, as demonstrated below:

```python

from pathlib import Path
from mms_client.security.certs import Certificate

# Create a cert from a path to a certificate
cert = Certificate("/path/to/my/cert.p12", "my_passphrase")

# Create a cert using a Path object
cert = Certificate(Path("/path/to/my") / "cert.p12", "my_passphrase")

# Create a cert using the raw certificate data
with open("/path/to/my/cert.p12", "rb") as f:
    cert = Certificate(f.read(), "my_passphrase")
```

This object can then be used to generate signatures for requests, and also to create a `Pkcs12Adapter`, which is mounted to the HTTP sessions used to send those same requests. As such, this one object represents the single source of authentication for the entire package.

## Participant Name
This is a 4-digit alphanumerical code that can be used to identify the market participant to which a user belongs, and on behalf of whom a request is being made. This value must be provided when an MMS client is created, and it must match the value encoded in the certificate and also the participant to whom the certificate is registered on the MMS server.

## User Name
This is a 1-12 digit alphanumerical code that can be used to identify the user making the request. This value must be provided when an MMS client is created, and it must match the value encoded in the certificate and also the user to whom the certificate is registered on the MMS server.

# Examples
This section includes some examples of creating a client and requesting data.

## Basic Example
Create the base client and then add an offer.

```python
from pendulum import DateTime

from mms_client.client import MmsClient
from mms_client.security.certs import Certificate
from mms_client.types.market import MarketType
from mms_client.types.offer import Direction, OfferData, OfferStack
from mms_client.utils.web import ClientType

# Create a certificate
cert = Certificate("/path/to/my/cert.p12", "fake_passphrase")

# Create a new MMS client
client = MmsClient(domain="mydomain.com", participant="F100", user="FAKEUSER", client_type=ClientType.BSP, cert)

# Create our request offer
request_offer = OfferData(
    stack=[
        OfferStack(
            number=1,
            unit_price=100,
            minimum_quantity_kw=100,
        ),
    ],
    resource="FAKE_RESO",
    start=DateTime(2024, 3, 15, 12),
    end=DateTime(2024, 3, 15, 21),
    direction=Direction.SELL,
)

# Submit our offer to the client, returning the completed offer
response_offer = client.put_offer(
    request=request_offer,
    market_type=MarketType.DAY_AHEAD,
    days=1,
)

# Print out the response offer
print(response_offer)
```

There's a lot of code here but it's not terribly difficult to understand. All this does is pull in the authentication data, create the client, create the payload, submit it to the server and retrieve the response.

## Connecting to a Test Server
If you want to test your MMS connection, you can try using the test server:

```python
client = MmsClient(domain="mydomain.com", participant="F100", user="FAKEUSER", client_type=ClientType.BSP, cert, test=True)
```

## Connecting as a Market Admin
If you're connecting as a market operator (MO), you can connect in admin mode:

```python
client = MmsClient(domain="mydomain.com", participant="F100", user="FAKEUSER", client_type=ClientType.BSP, cert, is_admin=True)
```

## Auditing XML Requests & Responses
A common requirement for this sort of library is recording or saving the raw XML requests and responses for audit/logging purposes. This library supports this workflow through the `mms_client.utils.plugin.Plugin` object. This object intercepts the XML request at the Zeep client level right before it is sent to the MMS and, similarly, intercepts the XML response immediately after it is received from the MMS. Before passing these objects on, without modifying them, it records the XML data as a byte string and passes it to two methods: `audit_request` and `audit_response`. These can be overridden by any object that inherits from this class, allowing the user to direct this data to whatever store they prefer to use for auditing or logging.

```python
class TestAuditPlugin(Plugin):

    def __init__(self):
        self.request = None
        self.response = None

    def audit_request(self, mms_request: bytes) -> None:
        self.request = mms_request

    def audit_response(self, mms_response: bytes) -> None:
        self.response = mms_response

client = MmsClient(domain="mydomain.com", participant="F100", user="FAKEUSER", client_type=ClientType.BSP, cert, plugins=[TestAuditPlugin()])
```

This same input allows for the user to create their own plugins and add them to the Zeep client, allowing for a certain amount of extensibility.

# Completeness
This client is not complete. Currently, it supports the following endpoints:
- MarketQuery_ReserveRequirementQuery
- MarketSubmit_OfferData
- MarketQuery_OfferQuery
- MarketCancel_OfferCancel
- MarketQuery_AwardResultsQuery
- RegistrationSubmit_Resource
- RegistrationQuery_Resource
- ReportCreateRequest
- ReportListRequest
- ReportDownloadRequestTrnID
- BSP_ResourceList

We can add support for additional endpoints as time goes on, and independent contribution is, of course, welcome. However, support for attachments is currently limited because none of the endpoints we support currently require them. We have implemented attachment support up to the client level, but we haven't developed an architecture for submitting them through an endpoint yet.

# Installation
We have a package on PyPI so installation is as easy as doing:

```
pip install mms-client
```

or

```
poetry add mms-client
```
