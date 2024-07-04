"""Tests the functionality in the mms_client.types.registration module."""

from pendulum import Date

from mms_client.types.registration import QueryAction
from mms_client.types.registration import QueryType
from mms_client.types.registration import RegistrationApproval
from mms_client.types.registration import RegistrationQuery
from mms_client.types.registration import RegistrationSubmit
from tests.testutils import verify_registration_query


def test_registration_approval():
    """Test that the RegistrationApproval class initializes and converts to XML as expected."""
    # First, we create a new registration approval request
    request = RegistrationApproval()

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the conversion succeeded
    assert data == b"<RegistrationApproval/>"


def test_registration_query_defaults():
    """Test that the RegistrationQuery class initializes and converts to XML as expected."""
    # First, create a new registration query request
    request = RegistrationQuery()

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<RegistrationQuery Action="NORMAL" DateType="TRADE"/>"""
    verify_registration_query(request, QueryAction.NORMAL, QueryType.TRADE)


def test_registration_query_full():
    """Test that the RegistrationQuery class initializes and converts to XML as expected."""
    # First, create a new registration query request
    request = RegistrationQuery(
        action=QueryAction.LATEST,
        query_type=QueryType.TRADE,
        date=Date(2019, 8, 30),
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<RegistrationQuery Action="LATEST" DateType="TRADE" Date="2019-08-30"/>"""
    verify_registration_query(request, QueryAction.LATEST, QueryType.TRADE, Date(2019, 8, 30))


def test_registration_submit():
    """Test that the RegistrationSubmit class initializes and converts to XML as expected."""
    # First, create a new registration submit request
    request = RegistrationSubmit()

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the conversion succeeded
    assert data == b"<RegistrationSubmit/>"
