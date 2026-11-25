
import os
import struct

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.exceptions import InvalidTag


# CipherVeil encryption format
MAGIC = b"CVLENC01"

# Cryptographic configuration
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1

# Header: Magic + Salt + Nonce + Ciphertext length
HEADER_FORMAT = ">8s16s12sI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# AES-GCM adds a 16-byte authentication tag
TAG_SIZE = 16


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit encryption key using Scrypt."""

    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty.")

    kdf = Scrypt(
        salt=salt,
        length=KEY_SIZE,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P
    )

    return kdf.derive(password.encode("utf-8"))


def encrypt_data(data: bytes, password: str) -> bytes:
    """Encrypt binary data using AES-256-GCM."""

    if not isinstance(data, bytes):
        raise TypeError("Data must be in bytes format.")

    if len(data) > (2**32 - 1 - TAG_SIZE):
        raise ValueError("Payload is too large.")

    # Generate cryptographically secure random values
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)

    # Derive encryption key
    key = derive_key(password, salt)

    # Prepare header before encryption
    encrypted_length = len(data) + TAG_SIZE

    header = struct.pack(
        HEADER_FORMAT,
        MAGIC,
        salt,
        nonce,
        encrypted_length
    )

    # AES-256-GCM authenticated encryption
    aes = AESGCM(key)

    ciphertext = aes.encrypt(
        nonce,
        data,
        header
    )

    # Header is also authenticated as additional data
    return header + ciphertext


def decrypt_data(payload: bytes, password: str) -> bytes:
    """Validate and decrypt an AES-256-GCM payload."""

    if len(payload) < HEADER_SIZE + TAG_SIZE:
        raise ValueError("Invalid or incomplete encrypted payload.")

    # Read header
    header = payload[:HEADER_SIZE]

    magic, salt, nonce, encrypted_length = struct.unpack(
        HEADER_FORMAT,
        header
    )

    if magic != MAGIC:
        raise ValueError("Invalid CipherVeil encryption format.")

    if encrypted_length < TAG_SIZE:
        raise ValueError("Invalid encrypted payload length.")

    ciphertext = payload[HEADER_SIZE:]

    if len(ciphertext) != encrypted_length:
        raise ValueError("Encrypted payload is incomplete or corrupted.")

    # Reconstruct the encryption key
    key = derive_key(password, salt)

    aes = AESGCM(key)

    # Decryption automatically verifies the authentication tag
    # and the authenticated header.
    return aes.decrypt(
        nonce,
        ciphertext,
        header
    )
