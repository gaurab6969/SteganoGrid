
import pytest

from PIL import Image
from cryptography.exceptions import InvalidTag

from cipher.crypto import encrypt_data, decrypt_data
from cipher.steganography import embed_data, extract_data


def test_tampered_stego_image_fails_authentication(tmp_path):
    cover = tmp_path / "cover.png"
    hidden = tmp_path / "hidden.png"
    tampered = tmp_path / "tampered.png"

    Image.new("RGB", (300, 300), (120, 150, 200)).save(cover)

    original_data = b"Confidential CipherVeil security test"
    encrypted = encrypt_data(original_data, "StrongPassword123")

    embed_data(str(cover), encrypted, str(hidden))

    # Modify one embedded ciphertext bit.
    image = Image.open(hidden).convert("RGB")
    pixels = bytearray(image.tobytes())

    # 12 bytes: steganography header.
    # 40 bytes: encryption header.
    ciphertext_start = (12 + 40) * 8

    pixels[ciphertext_start] ^= 1

    modified = Image.frombytes(
        "RGB",
        image.size,
        bytes(pixels)
    )
    modified.save(tampered, format="PNG")

    extracted = extract_data(str(tampered))

    with pytest.raises(InvalidTag):
        decrypt_data(extracted, "StrongPassword123")


def test_modified_steganography_header_is_rejected(tmp_path):
    cover = tmp_path / "cover.png"
    hidden = tmp_path / "hidden.png"
    tampered = tmp_path / "tampered.png"

    Image.new("RGB", (300, 300), (120, 150, 200)).save(cover)

    encrypted = encrypt_data(b"Security test", "Password123")

    embed_data(str(cover), encrypted, str(hidden))

    image = Image.open(hidden).convert("RGB")
    pixels = bytearray(image.tobytes())

    # Change the first bit of the steganography magic header.
    pixels[0] ^= 1

    modified = Image.frombytes(
        "RGB",
        image.size,
        bytes(pixels)
    )
    modified.save(tampered, format="PNG")

    with pytest.raises(ValueError, match="No valid CipherVeil"):
        extract_data(str(tampered))
