"""Tests the functionality in the cert module."""

from pathlib import Path

import pytest
from mock import patch
from pyfakefs.fake_filesystem_unittest import Patcher

from mms_client.utils.certs import Certificate


def test_from_directory_not_found():
    """Test what happens when the certificate files can't be found.

    Tests that, when the from_directory method is called, if the certificate files cannot be found then an exception
    will be raised.
    """
    with pytest.raises(RuntimeError) as e_info:
        _ = Certificate.from_directory(name_pref="derp")

    assert e_info.type is RuntimeError
    assert "Expected to find file with extension '.crt.pem' in directory" in str(e_info.value.args[0])


def test_from_directory_found(dir_mocker):
    """Test that the certificate is loaded when it is found.

    Tests that, when the from_directory method is called, if the certificate files can both be found, then no exception
    will be raised.
    """
    # First, create our fake certificate files
    dir_mocker.create_file("TSO_CERT.crt.pem")
    dir_mocker.create_file("TSO_CERT.key.pem")

    # Next, attempt to create a certificate from the default directory
    cert = Certificate.from_directory()

    # Finally, verify that the cert files exist and have been mapped
    assert cert.cert_file == str(Path("TSO_CERT.crt.pem").resolve())
    assert cert.key_file == str(Path("TSO_CERT.key.pem").resolve())


@pytest.fixture(scope="function")
def dir_mocker():
    """Create a fake file-system we can use for testing."""
    with Patcher() as patcher:
        with patch("mms_client.utils.certs.BASE_DIR", Path("").resolve()):
            yield patcher.fs
