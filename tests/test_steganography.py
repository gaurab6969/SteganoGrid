
from PIL import Image

import pytest

from cipher.steganography import (
    embed_data,
    extract_data
)


def test_hide_and_extract(tmp_path):

    cover = tmp_path / "cover.png"
    output = tmp_path / "hidden.png"

    # Create a test cover image
    Image.new(
        "RGB",
        (100, 100),
        color="white"
    ).save(cover)

    secret = b"CipherVeil Cybersecurity Project"

    # Hide data
    embed_data(
        str(cover),
        secret,
        str(output)
    )

    # Extract data
    recovered = extract_data(str(output))

    assert recovered == secret


def test_invalid_image(tmp_path):

    image = tmp_path / "normal.png"

    Image.new(
        "RGB",
        (100, 100),
        color="blue"
    ).save(image)

    with pytest.raises(ValueError):
        extract_data(str(image))


def test_capacity_error(tmp_path):

    cover = tmp_path / "small.png"
    output = tmp_path / "hidden.png"

    Image.new(
        "RGB",
        (2, 2),
        color="white"
    ).save(cover)

    secret = b"This message is too large."

    with pytest.raises(ValueError):
        embed_data(
            str(cover),
            secret,
            str(output)
        )
