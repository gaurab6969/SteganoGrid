
import math
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image
from cryptography.exceptions import InvalidTag

from cipher.crypto import encrypt_data, decrypt_data
from cipher.steganography import embed_data, extract_data


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SteganoGrid | Secure File Hiding",
    page_icon="🔐",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 25px;
        border-radius: 14px;
        background: linear-gradient(135deg, #101d35, #162b45);
        border: 1px solid #294568;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: #58a6ff;
        margin-bottom: 5px;
    }

    .hero p {
        color: #c9d1d9;
        margin-bottom: 0;
    }

    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>🔐 SteganoGrid</h1>
    <p>Secure Image Steganography & Encrypted Data Hiding System</p>
</div>
""", unsafe_allow_html=True)

st.write(
    "Encrypt confidential files and conceal them inside images "
    "using AES-256-GCM and LSB steganography."
)

st.divider()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_image_capacity(image_bytes):
    """Calculate the maximum payload capacity in bytes."""

    from io import BytesIO

    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    total_channels = image.width * image.height * 3

    return total_channels // 8


def safe_filename(filename):
    """Prevent directory traversal in download filenames."""

    return Path(filename).name or "recovered_file.bin"


# --------------------------------------------------
# TABS
# --------------------------------------------------

hide_tab, extract_tab, about_tab = st.tabs([
    "🔒 Hide File",
    "🔓 Extract File",
    "ℹ️ About"
])


# ==================================================
# HIDE FILE TAB
# ==================================================

with hide_tab:

    st.header("Hide and Encrypt a File")

    st.write(
        "Select a secret file, choose a cover image, "
        "and protect your data with a password."
    )

    col1, col2 = st.columns(2)

    with col1:

        secret_file = st.file_uploader(
            "Upload Secret File",
            help="Supports TXT, PDF, DOCX, ZIP and other file formats.",
            key="secret_file"
        )

        if secret_file:
            st.success(f"Selected: {secret_file.name}")
            st.caption(f"File size: {len(secret_file.getvalue()):,} bytes")

    with col2:

        cover_image = st.file_uploader(
            "Upload Cover Image",
            type=["png", "jpg", "jpeg", "bmp", "webp"],
            help="Any cover image format (JPG, PNG, WEBP, BMP) can be used.",
            key="cover_image"
        )

        if cover_image:
            cover_bytes = cover_image.getvalue()

            st.image(
                cover_bytes,
                caption="Cover Image",
                use_container_width=True
            )

            capacity = get_image_capacity(cover_bytes)

            st.caption(
                f"Approximate maximum payload capacity: "
                f"{capacity:,} bytes"
            )
            st.info("💡 You can upload photos in JPG, JPEG, PNG, etc. The hidden output is saved as PNG so the data is preserved losslessly.")

    st.divider()

    password = st.text_input(
        "Encryption Password",
        type="password",
        key="hide_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="confirm_password"
    )

    if secret_file and cover_image:

        encrypted_size = len(secret_file.getvalue()) + 56
        required_size = encrypted_size + 12
        capacity = get_image_capacity(cover_image.getvalue())

        st.write("### Capacity Check")

        col1, col2 = st.columns(2)

        col1.metric(
            "Required image capacity",
            f"{required_size:,} bytes"
        )

        col2.metric(
            "Available image capacity",
            f"{capacity:,} bytes"
        )

        if required_size > capacity:
            st.error(
                "The selected image does not have enough capacity. "
                "Choose a larger image or a smaller secret file."
            )
        else:
            st.success("The selected image has sufficient capacity.")

    if st.button("🔐 Encrypt and Hide File", key="hide_button"):

        if not secret_file or not cover_image:
            st.error("Please upload both a secret file and a cover image.")

        elif not password:
            st.error("Please enter an encryption password.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        else:

            try:
                cover_bytes = cover_image.getvalue()
                secret_bytes = secret_file.getvalue()

                capacity = get_image_capacity(cover_bytes)
                required_size = len(secret_bytes) + 56 + 12

                if required_size > capacity:
                    st.error(
                        "Insufficient image capacity. "
                        "Select a larger cover image."
                    )

                else:

                    with st.spinner(
                        "Encrypting and embedding your file..."
                    ):

                        with tempfile.TemporaryDirectory() as temp_dir:

                            temp_dir = Path(temp_dir)

                            cover_path = temp_dir / "cover_image"
                            output_path = temp_dir / "hidden_image.png"

                            cover_path.write_bytes(cover_bytes)

                            # Step 1: Encrypt the secret file
                            encrypted_payload = encrypt_data(
                                secret_bytes,
                                password
                            )

                            # Step 2: Embed encrypted data into image
                            embed_data(
                                str(cover_path),
                                encrypted_payload,
                                str(output_path)
                            )

                            # Step 3: Read generated PNG
                            stego_bytes = output_path.read_bytes()

                    st.success(
                        "File encrypted and hidden successfully!"
                    )

                    st.image(
                        stego_bytes,
                        caption="Generated CipherVeil Image",
                        use_container_width=True
                    )

                    st.download_button(
                        label="⬇️ Download Hidden PNG",
                        data=stego_bytes,
                        file_name="cipherveil_hidden.png",
                        mime="image/png",
                        key="download_hidden"
                    )

                    st.info(
                        "Keep your password safe. You will need the same "
                        "password to recover the original file."
                    )

            except (ValueError, OSError) as error:

                st.error(f"Operation failed: {error}")

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )


# ==================================================
# EXTRACT FILE TAB
# ==================================================

with extract_tab:

    st.header("Extract and Decrypt a File")

    st.write(
        "Upload a CipherVeil PNG image and enter the password "
        "used during encryption."
    )

    stego_image = st.file_uploader(
        "Upload Steganographic Image",
        type=["png", "bmp", "webp", "jpg", "jpeg"],
        key="stego_image",
        help="Upload the image containing hidden data (lossless PNG format is recommended)."
    )

    if stego_image:

        stego_bytes = stego_image.getvalue()

        st.image(
            stego_bytes,
            caption="Uploaded Steganographic Image",
            use_container_width=True
        )

    decrypt_password = st.text_input(
        "Decryption Password",
        type="password",
        key="decrypt_password"
    )

    recovered_filename = st.text_input(
        "Recovered File Name",
        value="recovered_file.bin",
        help="Enter the desired output filename, including its extension."
    )

    if st.button("🔓 Extract and Decrypt File", key="extract_button"):

        if not stego_image:
            st.error("Please upload a CipherVeil PNG image.")

        elif not decrypt_password:
            st.error("Please enter the decryption password.")

        elif not recovered_filename.strip():
            st.error("Please enter a recovered filename.")

        else:

            try:

                with st.spinner(
                    "Extracting and decrypting your file..."
                ):

                    with tempfile.TemporaryDirectory() as temp_dir:

                        temp_dir = Path(temp_dir)

                        image_path = temp_dir / "hidden_image.png"

                        image_path.write_bytes(stego_bytes)

                        # Step 1: Extract encrypted payload
                        encrypted_payload = extract_data(
                            str(image_path)
                        )

                        # Step 2: Decrypt extracted payload
                        original_data = decrypt_data(
                            encrypted_payload,
                            decrypt_password
                        )

                filename = safe_filename(recovered_filename.strip())

                st.success("File successfully recovered!")

                st.metric(
                    "Recovered file size",
                    f"{len(original_data):,} bytes"
                )

                st.download_button(
                    label="⬇️ Download Recovered File",
                    data=original_data,
                    file_name=filename,
                    mime="application/octet-stream",
                    key="download_recovered"
                )

            except InvalidTag:

                st.error(
                    "Decryption failed. Incorrect password or "
                    "encrypted data has been modified."
                )

            except (ValueError, OSError) as error:

                if stego_image and stego_image.name.lower().endswith((".jpg", ".jpeg")):
                    st.error(
                        f"Extraction failed: {error}\n\n"
                        "⚠️ **Notice on JPG/JPEG:** JPEG uses lossy compression (DCT/quantization) "
                        "which alters pixel values and corrupts hidden LSB data. "
                        "CipherVeil stego images must be kept in lossless formats like PNG."
                    )
                else:
                    st.error(f"Extraction failed: {error}")

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )


# ==================================================
# ABOUT TAB
# ==================================================

with about_tab:

    st.header("About CipherVeil")

    st.write("""
    CipherVeil is a Python-based cybersecurity application that
    combines encryption and image steganography to protect confidential
    information.
    """)

    st.subheader("Security Technologies")

    st.markdown("""
    - **AES-256-GCM:** Authenticated encryption.
    - **Scrypt:** Password-based key derivation.
    - **LSB Steganography:** Conceals encrypted data inside image pixels.
    - **Pillow:** Image processing.
    - **Streamlit:** Web-based graphical interface.
    """)

    st.subheader("How It Works")

    st.markdown("""
    1. Select a file and a cover image.
    2. Encrypt the file using AES-256-GCM.
    3. Embed the encrypted payload into the image using LSB.
    4. Download the generated PNG.
    5. Upload the PNG later to extract and decrypt the file.
    """)

    st.warning(
        "Use PNG for the final steganographic image. "
        "JPEG compression can destroy hidden LSB data. "
        "Steganography does not guarantee that the presence of "
        "hidden information cannot be detected."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SteganoGrid | Secure Image Steganography & Encrypted Data Hiding"
)
