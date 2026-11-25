
import pytest

from pathlib import Path
from PIL import Image

from cipher.main import hide_file, extract_file


def test_complete_file_recovery(tmp_path):

    # Create sample files
    source = tmp_path / "secret.txt"
    cover = tmp_path / "cover.png"

    hidden = tmp_path / "hidden.png"
    recovered = tmp_path / "recovered.txt"

    original_data = (
        b"CipherVeil complete integration test!"
    )

    source.write_bytes(original_data)

    Image.new(
        "RGB",
        (300, 300),
        color="white"
    ).save(cover)

    # Hide the file
    hide_file(
        source,
        cover,
        hidden,
        "StrongPassword123"
    )

    assert hidden.exists()

    # Extract the file
    extract_file(
        hidden,
        recovered,
        "StrongPassword123"
    )

    assert recovered.exists()

    # Verify exact binary equality
    assert recovered.read_bytes() == original_data


def test_wrong_password_does_not_create_file(tmp_path):

    source = tmp_path / "secret.txt"
    cover = tmp_path / "cover.png"

    hidden = tmp_path / "hidden.png"
    recovered = tmp_path / "recovered.txt"

    source.write_bytes(b"Confidential information")

    Image.new(
        "RGB",
        (300, 300),
        color="white"
    ).save(cover)

    hide_file(
        source,
        cover,
        hidden,
        "CorrectPassword"
    )

    with pytest.raises(ValueError, match="Incorrect password"):
        extract_file(
            hidden,
            recovered,
            "WrongPassword"
        )

    assert not recovered.exists()


def test_missing_source_file(tmp_path):

    cover = tmp_path / "cover.png"

    Image.new(
        "RGB",
        (100, 100),
        color="white"
    ).save(cover)

    with pytest.raises(FileNotFoundError):
        hide_file(
            tmp_path / "missing.txt",
            cover,
            tmp_path / "hidden.png",
            "Password123"
        )


def test_output_must_be_png(tmp_path):

    source = tmp_path / "secret.txt"
    cover = tmp_path / "cover.png"

    source.write_bytes(b"Secret data")

    Image.new(
        "RGB",
        (100, 100),
        color="white"
    ).save(cover)

    with pytest.raises(ValueError, match="PNG"):
        hide_file(
            source,
            cover,
            tmp_path / "hidden.jpg",
            "Password123"
        )
