"""Tests the functionality in the mms_client.security.crypto module."""

from mms_client.security.crypto import CryptoWrapper

# Signature for a piece of fake data to use for testing
SIGNATURE = b"wY7zAeuvn/gea4Otx0OtBN205B4L8XuMCaSFeWZW7mr1lAeWSo9SVOCMy7TMnGYOYpNIWwJ9RI8H0C6asYammU6VvB4GCuDvMPj+XzQm1pOPqTFpAnorCzfrZPLgvc9AwrN2hgy06clGSeD3ArBKcO1be3rV87WEEaAuG4hjcn9XDxcsRL3Fw5fSbq3q9WRl+z0Vc2d7wRyIZ8AJ9GxbA97OCKQ9ioXykHquP829RqTibDNhZglHyQSkRh9v8eoXvsYxO/h0brif1hMjmknh8uSO4hMUBJ0lma0Ni6nWyeytq7tmJelzWaOQYqXcqAxbMRsSAgOStd1L9/lna3OIJgpkAfdEKOpLEHrRsSKzkwP1sWjKZVExX0de/GtBqIspQlI0bXz8zZ9FPStGwfElTPJtizN8SuLbvIoP91X0x6/FnQLXBULn7vemtzdu2S4Mf05Wt5ixOrGGPEx9OlnkJprSQdjzgrsZ6/mr+5DjxIewlF0lSZk1x4tAR7PiSDY+7zXUOBI+dDRVG9t4/xpxjK4JgqNJy2nQhsZYto2tYp2sAQub0we7qpPdu8Y+qz0ZyjtCXiOCEinjv35H7A1RLdg6Rp8XGScE1l6tvLbRZd6eNFFoLjdgjcB7YtaS4PoTsckGDfAMRZTtRAeE9Zmvd0xrW9Ag9+yKutMTN0DYpGU="


def test_sign(mock_certificate):
    """Test that the CryptoWrapper class signs data as we expect."""
    # First, create a new CryptoWrapper with a fake certificate
    wrapper = CryptoWrapper(mock_certificate)

    # Next, create a signature from some fake data
    signature = wrapper.sign(b"FAKE_DATA")

    # Finally, verify that the signature is as we expect
    assert signature == SIGNATURE


def test_verify_mismatches(mock_certificate):
    """Test that the CryptoWrapper class verifies data as we expect."""
    # Create a new CryptoWrapper with a fake certificate
    wrapper = CryptoWrapper(mock_certificate)

    # Verify that the signature is as we expect
    assert not wrapper.verify(b"FAKE_DATA1", SIGNATURE)


def test_verify_matches(mock_certificate):
    """Test that the CryptoWrapper class verifies data as we expect."""
    # Create a new CryptoWrapper with a fake certificate
    wrapper = CryptoWrapper(mock_certificate)

    # Verify that the signature is as we expect
    assert wrapper.verify(b"FAKE_DATA", SIGNATURE)
