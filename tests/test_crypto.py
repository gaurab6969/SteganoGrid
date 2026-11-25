
import pytest

from cryptography.exceptions import InvalidTag

from cipher.crypto import (
    encrypt_data,
    decrypt_data,
    HEADER_SIZE
)


def test_encryption_decryption():

    original = b"CipherVeil Cybersecurity Project"

    encrypted = encrypt_data(
        original,
        "StrongPassword123"
    )

    decrypted = decrypt_data(
        encrypted,
        "StrongPassword123"
    )

    assert decrypted == original


def test_random_salt_and_nonce():

    message = b"Confidential information"

    first = encrypt_data(message, "Password123")
    second = encrypt_data(message, "Password123")

    # Both encryptions should produce different payloads
    assert first != second


def test_wrong_password():

    encrypted = encrypt_data(
        b"Secret message",
        "CorrectPassword"
    )

    with pytest.raises(InvalidTag):
        decrypt_data(encrypted, "WrongPassword")


def test_tampered_ciphertext():

    encrypted = bytearray(
        encrypt_data(
            b"Important data",
            "Password123"
        )
    )

    encrypted[-1] ^= 1

    with pytest.raises(InvalidTag):
        decrypt_data(bytes(encrypted), "Password123")


def test_tampered_header():

    encrypted = bytearray(
        encrypt_data(
            b"Important data",
            "Password123"
        )
    )

    encrypted[8] ^= 1

    with pytest.raises(InvalidTag):
        decrypt_data(bytes(encrypted), "Password123")


def test_empty_payload():

    encrypted = encrypt_data(b"", "Password123")

    assert decrypt_data(encrypted, "Password123") == b""


def test_truncated_payload():

    encrypted = encrypt_data(
        b"Secret information",
        "Password123"
    )

    with pytest.raises(ValueError):
        decrypt_data(encrypted[:-1], "Password123")


def test_empty_password():

    with pytest.raises(ValueError):
        encrypt_data(b"Secret", "")
