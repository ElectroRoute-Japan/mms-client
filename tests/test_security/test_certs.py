"""Tests the functionality in the mms_client.security.certs module."""

import pytest
from mock import patch
from pyfakefs.fake_filesystem_unittest import Patcher

from mms_client.security.certs import Certificate


def test_init_works():
    """Test that the Certificate class can be initialized."""
    # Create our certificate using a fake cert file and passphrase
    cert = Certificate(b"derp", "passphrase")

    # Verify that the certificate was created with the correct parameters
    assert cert.certificate == b"derp"
    assert cert.passphrase == "passphrase"


def test_to_adapter_works(mocker, dir_mocker):
    """Test that the to_adapter method works as expected."""
    # First, create a fake certificate file
    dir_mocker.create_file("cert.p12", contents=b"derp")

    # Next, create a certificate and convert it to an adapter
    mock = mocker.MagicMock()
    with patch("mms_client.security.certs.Pkcs12Adapter", mock):
        cert = Certificate("cert.p12", "passphrase")
        _ = cert.to_adapter()

    # Finally, verify that the adapter was created with the correct parameters
    assert cert.certificate == b"derp"
    assert cert.passphrase == "passphrase"
    assert mock.call_args.kwargs["pkcs12_data"] == b"derp"
    assert mock.call_args.kwargs["pkcs12_password"] == "passphrase"


@pytest.fixture(scope="function")
def dir_mocker():
    """Create a fake file-system we can use for testing."""
    with Patcher() as patcher:
        yield patcher.fs
