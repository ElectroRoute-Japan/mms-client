"""Contains objects for MMS settlement."""

from typing import List
from typing import Optional

from pydantic_core import PydanticUndefined
from pydantic_extra_types.pendulum_dt import Date
from pydantic_extra_types.pendulum_dt import DateTime
from pydantic_xml import attr
from pydantic_xml import element

from mms_client.types.base import Payload
from mms_client.types.fields import company_short_name
from mms_client.types.fields import participant


def file_name(alias: str, optional: bool = False):
    """Create a field for a file name.

    Arguments:
    alias (str):        The name of the alias to assign to the Pydanitc field. This value will be used to map the field
                        to the JSON/XML key.
    optional (bool):    If True, the field will be optional with a default of None. If False, the field will be
                        required, with no default.

    Returns:    A Pydantic Field object for the file name.
    """
    return attr(
        default=None if optional else PydanticUndefined,
        name=alias,
        min_length=18,
        max_length=60,
        pattern=r"^([A-Z0-9]{4}_){2}[A-Z0-9_-]{4,46}\.(pdf|zip|csv|xml)$",
    )


class SettlementFile(Payload):
    """Represents a settlement file."""

    # The name of the settlement file as it is recorded in the system
    name: str = file_name("Name")

    # The name of the participant (only valid if operating as a TSO)
    participant: Optional[str] = participant("ParticipantName", True)

    # The name of the company associated with the file (only valid if operating as a TSO)
    company: Optional[str] = company_short_name("CompanyShortName", True)

    # When the file was submitted (not sure why this can be None but it's in the spec)
    submission_time: Optional[DateTime] = attr(name="SubmissionTime", default=None)

    # The date when settlement occurred (not included if settlement is in the future)
    settlement_date: Optional[Date] = attr(name="SttlDate", default=None)

    # The size of the file in bytes, if it has been uploaded
    size: Optional[int] = attr(name="FileSize", default=None, ge=0, lt=1000000000)


class SettlementResults(Payload):
    """Contains a list of settlement files that can be requested separately later."""

    # The file results that were retrieved by the query
    files: List[SettlementFile] = element(tag="File", min_length=1)


class SettlementResultsFileListQuery(Payload):
    """Represents a request to query settlement results file list."""
