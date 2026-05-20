from pathlib import Path

from reportlab.pdfgen import canvas

from backend.core.config import settings
from backend.utils.file_utils import ensure_directories


def create_sample_tender_pdf(filename: str = "sample_tender_demo.pdf") -> str:
    ensure_directories(settings.uploads_dir)
    full_path = Path(settings.uploads_dir) / filename
    c = canvas.Canvas(str(full_path))
    lines = [
        "Government Infrastructure Tender Notice",
        "EMD amount: INR 500000",
        "Completion timeline: 120 days from work order",
        "Eligibility criteria: 3 similar projects in last 5 years",
        "Penalties: 1% of contract value per week delay",
        "Payment terms: 30 days after invoice verification",
        "Technical requirements: IS standards compliant materials",
        "Submission deadline: 30 June 2026, 17:00 IST",
        "BOQ Item 1 | Cement Work | 120 | bags | 420 | 50400",
        "BOQ Item 2 | Steel Reinforcement | 2000 | kg | 78 | 156000",
    ]
    y = 800
    for line in lines:
        c.drawString(50, y, line)
        y -= 24
    c.save()
    return str(full_path)
