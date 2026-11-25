
import pytest
from PIL import Image

from cipher.steganalysis import analyze_lsb


def test_all_zero_lsb(tmp_path):
    image_path = tmp_path / "zeros.png"

    Image.new("RGB", (10, 10), (100, 100, 100)).save(image_path)

    result = analyze_lsb(image_path)

    assert result["zero_count"] == 300
    assert result["one_count"] == 0
    assert result["entropy"] == 0


def test_all_one_lsb(tmp_path):
    image_path = tmp_path / "ones.png"

    Image.new("RGB", (10, 10), (101, 101, 101)).save(image_path)

    result = analyze_lsb(image_path)

    assert result["zero_count"] == 0
    assert result["one_count"] == 300
    assert result["entropy"] == 0


def test_balanced_lsb(tmp_path):
    image_path = tmp_path / "balanced.png"

    image = Image.new("RGB", (10, 10))
    pixels = []

    for i in range(100):
        value = 100 if i % 2 == 0 else 101
        pixels.append((value, value, value))

    image.putdata(pixels)
    image.save(image_path)

    result = analyze_lsb(image_path)

    assert result["zero_count"] == 150
    assert result["one_count"] == 150
    assert result["chi_square"] == 0
    assert result["entropy"] == pytest.approx(1.0)
