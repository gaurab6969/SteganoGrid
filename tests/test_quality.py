
import math
import pytest

from PIL import Image

from cipher.quality import calculate_mse, calculate_psnr


def test_identical_images(tmp_path):
    original = tmp_path / "original.png"
    modified = tmp_path / "modified.png"

    Image.new("RGB", (100, 100), (120, 150, 200)).save(original)
    Image.new("RGB", (100, 100), (120, 150, 200)).save(modified)

    assert calculate_mse(original, modified) == 0
    assert calculate_psnr(original, modified) == float("inf")


def test_different_images(tmp_path):
    original = tmp_path / "original.png"
    modified = tmp_path / "modified.png"

    Image.new("RGB", (100, 100), (100, 100, 100)).save(original)
    Image.new("RGB", (100, 100), (101, 101, 101)).save(modified)

    assert calculate_mse(original, modified) == 1
    assert calculate_psnr(original, modified) == pytest.approx(
        10 * math.log10(255 ** 2)
    )


def test_dimension_mismatch(tmp_path):
    original = tmp_path / "original.png"
    modified = tmp_path / "modified.png"

    Image.new("RGB", (100, 100)).save(original)
    Image.new("RGB", (200, 100)).save(modified)

    with pytest.raises(ValueError, match="dimensions"):
        calculate_mse(original, modified)
