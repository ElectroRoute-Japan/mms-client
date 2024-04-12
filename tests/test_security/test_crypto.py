"""Tests the functionality in the mms_client.security.crypto module."""

import pytest
from mock import patch

from mms_client.security.crypto import CryptoWrapper


@patch("mms_client.security.crypto.load_key_and_certificates", return_value=(12, None, None))
def test_init_keytype_invalid(mock, mock_certificate):
    """Test that the CryptoWrapper class raises a TypeError when the private key is not an RSAPrivateKey."""
    # Attempt to create a new CryptoWrapper with the fake certificate; this should fail
    with pytest.raises(TypeError) as ex_info:
        _ = CryptoWrapper(mock_certificate)

    # Verify the details of the raised exception
    assert str(ex_info.value) == "Private key of type (int) was not expected."


def test_sign(mock_certificate):
    """Test that the CryptoWrapper class signs data as we expect."""
    # First, create a new CryptoWrapper with a fake certificate
    wrapper = CryptoWrapper(mock_certificate)

    # Next, create a signature from some fake data
    signature = wrapper.sign(b"FAKE_DATA")

    # Finally, verify that the signature is as we expect
    assert signature == (
        b"Q3iv2Nq6BqpNexc1flEcXHualIctgpFNv97XAVq+pSAsO+i36drPeDvjcvcbDZkwZwJPKaXCQVUTai3q8ufjd9Dq6e+4ipL1zIoHPXI/Tc2j"
        b"g8fCWFAiNHT66YG+sm7vZ4ZIp8iCu0sWpSLRogPpdh77xYMJ5/s3BWqhku1npKSwtLGArnaH+FryGJRrd/TM9OaZ9E3aI3dBRh+/jfhrwf/2"
        b"2f0UKav0Xae+FIZMufopom73lBCCI93Ka37lQswwMKJxHaXtGe9qhEpAsD3xr5fiSov9CC7cuf6BtOyh8/IZqGdHShdeRa+hRbDyyM2lowRn"
        b"+Lkjxd5BjbKpA2N3hTWl/Uu0jTNpNm0IG9cBVJ2EERf0N2XuOdXuFRNz+649cB889x8qiNvBhWq3f4FX5g6AERAScfDAK1zjzQK9vvCU4n3s"
        b"GkW1L726f87sUWB8qRcqkf+T1oYYB97GymVbI9Z7E1TFNSp2uCatjUznDNzBB2cv9Ho82axH7VYUVRjnAViFSMc4GeozUw+E1jJm6iGGNuNS"
        b"A4T8r1l/r3X1gjVKU9EGZtIaF1K6xaULVbStR0IHIioYMesqeN1o+WO4hw7oSgxQBhNjqdFONtm7AuDyGiHS5dq0mUKxYGvdPgGKnykjwF/V"
        b"Jl95I7f9Mlq4kd+m2LdSPhoOzCN3e2SkNvQ="
    )
