"""Tests the functionality in the mms_client.security.certs module."""

import pytest
from mock import patch

from mms_client.security.certs import Certificate


@patch("mms_client.security.certs.load_key_and_certificates", return_value=(12, None, None))
def test_init_keytype_invalid(mock):
    """Test that the Certificate class raises a TypeError when the private key is not an RSAPrivateKey."""
    # Attempt to create a new CryptoWrapper with the fake certificate; this should fail
    with pytest.raises(TypeError) as ex_info:
        _ = Certificate(b"derp", "passphrase")

    # Verify the details of the raised exception
    assert str(ex_info.value) == "Private key of type (int) was not expected."


def test_init_works(mock_certificate):
    """Test that the Certificate class can be initialized."""
    assert len(mock_certificate.certificate) > 0
    assert not mock_certificate.passphrase


def test_to_adapter_works(mock_certificate, mocker):
    """Test that the to_adapter method works as expected."""
    # Create a certificate and convert it to an adapter
    mock = mocker.MagicMock()
    with patch("mms_client.security.certs.Pkcs12Adapter", mock):
        _ = mock_certificate.to_adapter()

    # Verify that the adapter was created with the correct parameters
    assert mock.call_args.kwargs["pkcs12_data"] == mock_certificate.certificate
    assert mock.call_args.kwargs["pkcs12_password"] == mock_certificate.passphrase
