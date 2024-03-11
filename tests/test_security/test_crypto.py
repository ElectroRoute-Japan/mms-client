"""Tests the functionality in the mms_client.security.crypto module."""

from pathlib import Path

import pytest
from mock import patch

from mms_client.security.certs import Certificate
from mms_client.security.crypto import CryptoWrapper


@patch("mms_client.security.crypto.load_key_and_certificates", return_value=(12, None, None))
def test_init_keytype_invalid(mock):
    """Test that the CryptoWrapper class raises a TypeError when the private key is not an RSAPrivateKey."""
    # First, create a new Certificate with a fake certificate
    cert = Certificate(Path(__file__).parent / "fake.p12", "")

    # Next, attempt to create a new CryptoWrapper with the fake certificate; this should fail
    with pytest.raises(TypeError) as ex_info:
        _ = CryptoWrapper(cert)

    # Finally, verify the details of the raised exception
    assert str(ex_info.value) == "Private key of type (int) was not expected."


def test_sign():
    """Test that the CryptoWrapper class signs data as we expect."""
    # First, create a new CryptoWrapper with a fake certificate
    wrapper = CryptoWrapper(Certificate(Path(__file__).parent / "fake.p12", ""))

    # Next, create a signature from some fake data
    signature = wrapper.sign(b"FAKE_DATA")

    # Finally, verify that the signature is as we expect
    assert signature == (
        b"Nn36Zbx4onfPggD2uvwNQiWzA93yoBsXtHvJLm7MeRCxfBDh1pFgEBZ0D5V5v6IefPCF4/cLJqh+wzli+JodMKHGseBwk3lREg6opO/8z6m3"
        b"DXIHqqkJ5aUlpsq2/DzLllAC6tq0DZDAXSUlUv6MP/3Fv3wqIawxqUkoSj4mZw+Zaq3ay6zjQzY9r5XW/7xSpeiHgFwdGur5iccp7/M/w3mh"
        b"dIT8hhRUsDGT5ctC8pBhCF5TIXEiQ0JZsAvkMLHj+/K1L4VQTc5R7AjOdoWqfHen+8UvRlrYj3zZ1DsONJVMqBkQw8RfMog9P2d0w6dRwYg1"
        b"gtffcO/3wA9/hoZbeY2dRyr87NXOTRVw3BEdW1HZ9stVKBgnz05ZJlQnjOcQ/wvh03Iu8zwpZxKgUyD3ejxXtCSiuBEjpHCA0ZMGmWplRgTE"
        b"hJgmTGoV4aXk8nddq14kKoEgi33d26pGrT9oCmNXrD3TBE4Em0bfQ0Lew8npBH6mdVC6dorq66maaKMOAkXdYCmCD8falSFrCT1NLjCKgVB0"
        b"/c/IcXzTUuyD8f5ikk+7j4we0PreUTYJa79i9hICn5MJtZcbo9oFmxkOZwj1UBTO627Stz2U5wNJrrFUfqAW6hZKG++3c+VP6V5QirZsXWBj"
        b"hAFK/MR1zYLzloffDa3eycTiVouBbhLgBv0="
    )
