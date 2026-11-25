
from PIL import Image
import struct


# CipherVeil payload identification
MAGIC = b"CVLSTG01"

# 8 bytes for magic + 4 bytes for payload length
HEADER_SIZE = 12


def bytes_to_bits(data):
    """Convert bytes into individual binary bits."""

    for byte in data:
        for shift in range(7, -1, -1):
            yield (byte >> shift) & 1


def bits_to_bytes(bits):
    """Convert binary bits back into bytes."""

    result = bytearray()

    for i in range(0, len(bits), 8):
        value = 0

        for bit in bits[i:i + 8]:
            value = (value << 1) | bit

        result.append(value)

    return bytes(result)


def embed_data(image_path, payload, output_path):
    """
    Embed binary data into an RGB image
    using Least Significant Bit steganography.
    """

    with Image.open(image_path) as img:
        image = img.convert("RGB")
        pixels = bytearray(image.tobytes())
        image_size = image.size

    # Construct payload header
    header = MAGIC + struct.pack(">I", len(payload))

    complete_payload = header + payload

    required_bits = len(complete_payload) * 8

    if required_bits > len(pixels):
        raise ValueError(
            "Image does not have enough capacity!"
        )

    # Embed payload into pixel LSBs
    for index, bit in enumerate(
        bytes_to_bits(complete_payload)
    ):

        pixels[index] = (
            pixels[index] & 0xFE
        ) | bit

    # Reconstruct image
    result = Image.frombytes(
        "RGB",
        image_size,
        bytes(pixels)
    )

    # Always save as lossless PNG
    result.save(output_path, format="PNG")

    print("[+] Data successfully embedded!")


def extract_data(image_path):
    """
    Extract hidden binary data from an RGB image.
    """

    with Image.open(image_path) as img:
        image = img.convert("RGB")
        pixels = image.tobytes()

    capacity = len(pixels) // 8

    if capacity < HEADER_SIZE:
        raise ValueError("Image is too small.")

    # Extract fixed-size header first
    header_bits = [
        pixels[i] & 1
        for i in range(HEADER_SIZE * 8)
    ]

    header = bits_to_bytes(header_bits)

    magic = header[:8]

    if magic != MAGIC:
        raise ValueError(
            "No valid CipherVeil data found."
        )

    payload_length = struct.unpack(
        ">I", header[8:12]
    )[0]

    if payload_length > capacity - HEADER_SIZE:
        raise ValueError(
            "Invalid payload length or corrupted image."
        )

    total_size = HEADER_SIZE + payload_length

    # Extract complete payload
    extracted_bits = [
        pixels[i] & 1
        for i in range(total_size * 8)
    ]

    complete_data = bits_to_bytes(extracted_bits)

    return complete_data[HEADER_SIZE:]
