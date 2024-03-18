"""Module for containing pytest fixtures."""

from pathlib import Path

import pytest

from mms_client.security.certs import Certificate


@pytest.fixture(scope="function")
def mock_certificate():
    """Create a new Certificate with a fake certificate."""
    return Certificate(Path(__file__).parent / "test_files" / "fake.p12", "")
