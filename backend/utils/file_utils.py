import os
import uuid
from pathlib import Path

from fastapi import UploadFile


ALLOWED_TYPES = {"application/pdf"}


def validate_pdf(uploaded_file: UploadFile) -> None:
    if uploaded_file.content_type not in ALLOWED_TYPES:
        raise ValueError("Only PDF files are allowed")


def generate_unique_filename(original_name: str) -> str:
    ext = Path(original_name).suffix.lower() or ".pdf"
    return f"{uuid.uuid4().hex}{ext}"


def ensure_directories(*dirs: str) -> None:
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
