
import argparse
import getpass
import sys

from pathlib import Path

from cryptography.exceptions import InvalidTag

from cipher.crypto import encrypt_data, decrypt_data
from cipher.steganography import embed_data, extract_data


def hide_file(source, carrier, output, password):
    """Encrypt a file and hide it inside an image (saved as lossless PNG)."""

    source = Path(source)
    carrier = Path(carrier)
    output = Path(output)

    if not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}")

    if not carrier.is_file():
        raise FileNotFoundError(f"Cover image not found: {carrier}")

    if output.suffix.lower() != ".png":
        raise ValueError(
            "Output image must have a .png (PNG) extension. "
            "Lossy formats like JPEG alter pixel values and destroy LSB steganographic data."
        )

    if output.resolve() in (source.resolve(), carrier.resolve()):
        raise ValueError("Output must be different from input files.")

    # Read original file as binary data
    original_data = source.read_bytes()

    print("[*] Encrypting source file...")

    # Encrypt using AES-256-GCM
    encrypted_payload = encrypt_data(
        original_data,
        password
    )

    print("[*] Embedding encrypted data into image...")

    # Embed encrypted bytes using LSB
    output.parent.mkdir(parents=True, exist_ok=True)

    embed_data(
        str(carrier),
        encrypted_payload,
        str(output)
    )

    print("\n[+] CipherVeil operation successful!")
    print(f"[+] Original file: {source.name}")
    print(f"[+] Output image: {output}")
    print(f"[+] Original size: {len(original_data)} bytes")
    print(f"[+] Encrypted payload: {len(encrypted_payload)} bytes")


def extract_file(image, output, password):
    """Extract encrypted data and recover the original file."""

    image = Path(image)
    output = Path(output)

    if not image.is_file():
        raise FileNotFoundError(f"Stego image not found: {image}")

    if output.resolve() == image.resolve():
        raise ValueError("Output file must differ from the image.")

    print("[*] Extracting hidden data...")

    # Extract encrypted payload
    encrypted_payload = extract_data(str(image))

    print("[*] Decrypting payload...")

    try:
        # Decrypt and authenticate
        original_data = decrypt_data(
            encrypted_payload,
            password
        )

    except InvalidTag:
        raise ValueError(
            "Incorrect password or encrypted data has been modified."
        ) from None

    # Save recovered file only after successful authentication
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_bytes(original_data)

    print("\n[+] File successfully recovered!")
    print(f"[+] Recovered file: {output}")
    print(f"[+] Recovered size: {len(original_data)} bytes")


def main():
    parser = argparse.ArgumentParser(
        prog="CipherVeil",
        description="Secure Image Steganography and Encryption Tool"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # HIDE COMMAND
    hide_parser = subparsers.add_parser(
        "hide",
        help="Encrypt a file and hide it inside an image"
    )

    hide_parser.add_argument(
        "source",
        help="File to hide"
    )

    hide_parser.add_argument(
        "carrier",
        help="Cover image (JPG, JPEG, PNG, BMP, WEBP, etc.)"
    )

    hide_parser.add_argument(
        "output",
        help="Output PNG image path (must end with .png)"
    )

    # EXTRACT COMMAND
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract and decrypt hidden data"
    )

    extract_parser.add_argument(
        "image",
        help="Stego image"
    )

    extract_parser.add_argument(
        "output",
        help="Recovered file path"
    )

    args = parser.parse_args()

    try:

        if args.command == "hide":

            password = getpass.getpass(
                "Enter encryption password: "
            )

            if not password:
                raise ValueError("Password cannot be empty.")

            confirmation = getpass.getpass(
                "Confirm encryption password: "
            )

            if password != confirmation:
                raise ValueError("Passwords do not match.")

            hide_file(
                args.source,
                args.carrier,
                args.output,
                password
            )

        elif args.command == "extract":

            password = getpass.getpass(
                "Enter decryption password: "
            )

            if not password:
                raise ValueError("Password cannot be empty.")

            extract_file(
                args.image,
                args.output,
                password
            )

    except (ValueError, OSError) as error:
        print(f"\n[!] Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
