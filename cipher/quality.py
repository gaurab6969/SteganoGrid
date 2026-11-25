
import math

from PIL import Image, ImageChops, ImageStat


def calculate_mse(original_path, modified_path):
    """
    Calculate Mean Squared Error between two RGB images.
    Lower MSE indicates greater similarity.
    """

    original = Image.open(original_path).convert("RGB")
    modified = Image.open(modified_path).convert("RGB")

    if original.size != modified.size:
        raise ValueError("Both images must have the same dimensions.")

    difference = ImageChops.difference(original, modified)
    statistics = ImageStat.Stat(difference)

    mse = sum(value ** 2 for value in statistics.rms) / 3

    return mse


def calculate_psnr(original_path, modified_path):
    """
    Calculate Peak Signal-to-Noise Ratio in decibels.
    Higher PSNR indicates greater similarity.
    """

    mse = calculate_mse(original_path, modified_path)

    if mse == 0:
        return float("inf")

    psnr = 10 * math.log10((255 ** 2) / mse)

    return psnr
