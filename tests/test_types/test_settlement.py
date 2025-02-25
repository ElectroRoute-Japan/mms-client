"""Tests the functionality of the mms_client.types.settlement module."""

from pendulum import Date
from pendulum import DateTime
from pendulum import Timezone

from mms_client.types.settlement import SettlementFile
from mms_client.types.settlement import SettlementQuery
from mms_client.types.settlement import SettlementResults
from tests.testutils import settlementfile_verifier
from tests.testutils import verify_settlement_results


def test_settlement_results_defaults():
    """Test that the SettlementResults class initializes and converts to XML as we expect."""
    # First, create a new settlement results request
    request = SettlementResults(
        files=[
            SettlementFile(
                name="A000_B111_FAKE-FILE.xml",
            )
        ]
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<SettlementResults><File Name="A000_B111_FAKE-FILE.xml"/></SettlementResults>"""
    verify_settlement_results(request, [settlementfile_verifier("A000_B111_FAKE-FILE.xml")])


def test_settlement_results_full():
    """Test that the SettlementResults class initializes and converts to XML as we expect."""
    # First, create a new settlement results request
    request = SettlementResults(
        files=[
            SettlementFile(
                name="A000_B111_FAKE-FILE.xml",
                participant="F100",
                company="偽会社",
                submission_time=DateTime(2024, 4, 10, 22, 34, 44),
                settlement_date=Date(2024, 4, 11),
                size=123456,
            )
        ]
    )

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == (
        """<SettlementResults><File Name="A000_B111_FAKE-FILE.xml" ParticipantName="F100" CompanyShortName="偽会社" """
        """SubmissionTime="2024-04-10T22:34:44" SttlDate="2024-04-11" FileSize="123456"/></SettlementResults>"""
    ).encode("UTF-8")
    verify_settlement_results(
        request,
        [
            settlementfile_verifier(
                "A000_B111_FAKE-FILE.xml",
                participant="F100",
                company="偽会社",
                submission_time=DateTime(2024, 4, 10, 22, 34, 44, tzinfo=Timezone("Asia/Tokyo")),
                settlement_date=Date(2024, 4, 11),
                size=123456,
            )
        ],
    )


def test_settlement_query_defaults():
    """Test that the SettlementQuery class initializes and converts to XML as we expect."""
    # First, create a new settlement query request
    request = SettlementQuery()

    # Next, convert the request to XML
    data = request.to_xml(skip_empty=True, encoding="utf-8")

    # Finally, verify that the request was created with the correct parameters
    assert data == b"""<SettlementResultsFileListQuery/>"""
