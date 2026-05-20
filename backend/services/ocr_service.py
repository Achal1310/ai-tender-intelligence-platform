from backend.utils.pdf_utils import extract_text_from_pdf, extract_text_from_scanned_pdf


def run_ocr_pipeline(file_path: str) -> str:
    text = extract_text_from_pdf(file_path)
    if len(text.strip()) > 150:
        return text
    return extract_text_from_scanned_pdf(file_path)
