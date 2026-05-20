import fitz
import pdfplumber
import pytesseract
from PIL import Image


def extract_text_from_pdf(file_path: str) -> str:
    chunks: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                chunks.append(page_text)
    if chunks:
        return "\n".join(chunks)

    # Fallback to PyMuPDF text parsing if pdfplumber finds nothing.
    doc = fitz.open(file_path)
    text = "\n".join(page.get_text("text") for page in doc)
    doc.close()
    return text


def extract_text_from_scanned_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    pages: list[str] = []
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append(pytesseract.image_to_string(img))
    doc.close()
    return "\n".join(pages)
