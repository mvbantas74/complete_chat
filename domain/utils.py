import base64
import io

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from PIL import Image

def reduce_image_size(file_input: UploadedFile) -> bytes:
    img = Image.open(file_input)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((1024, 1024))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=75)
    return buffer.getvalue()

def img_from_bytes_to_b64(img_bytes: bytes) -> str:
    return base64.b64encode(img_bytes).decode()

def img_from_b64_to_bytes(img_input: str) -> bytes:
    return base64.b64decode(img_input.encode())