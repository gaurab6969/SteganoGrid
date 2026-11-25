
import math
from PIL import Image


def analyze_lsb(image_path):
    """
    Analyze the least significant bit distribution
    of RGB image channels.
    """

    image = Image.open(image_path).convert("RGB")
    pixels = image.tobytes()

    total_bits = len(pixels)

    zero_count = 0
    one_count = 0

    for value in pixels:
        if value & 1:
            one_count += 1
        else:
            zero_count += 1

    zero_ratio = zero_count / total_bits
    one_ratio = one_count / total_bits

    expected = total_bits / 2

    chi_square = (
        ((zero_count - expected) ** 2 / expected)
        + ((one_count - expected) ** 2 / expected)
    )

    if zero_ratio == 0 or one_ratio == 0:
        entropy = 0.0
    else:
        entropy = -(
            zero_ratio * math.log2(zero_ratio)
            + one_ratio * math.log2(one_ratio)
        )

    return {
        "total_bits": total_bits,
        "zero_count": zero_count,
        "one_count": one_count,
        "zero_ratio": zero_ratio,
        "one_ratio": one_ratio,
        "chi_square": chi_square,
        "entropy": entropy
    }
