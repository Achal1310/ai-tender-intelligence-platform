import os
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from backend.core.config import settings
from backend.models import Tender
from backend.utils.file_utils import ensure_directories


def generate_pdf_report(tender: Tender) -> str:
    ensure_directories(settings.reports_dir)
    filename = f"tender_report_{tender.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
    path = os.path.join(settings.reports_dir, filename)

    c = canvas.Canvas(path, pagesize=A4)
    y = 800
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, f"Tender Report: {tender.title}")
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Uploaded: {tender.upload_date}")
    y -= 20
    c.drawString(40, y, "Summary:")
    y -= 15
    for line in (tender.summary or "No summary available").split("\n")[:35]:
        c.drawString(40, y, line[:100])
        y -= 13
        if y < 80:
            c.showPage()
            y = 800
    c.save()
    return path


def generate_excel_report(tender: Tender) -> str:
    ensure_directories(settings.reports_dir)
    filename = f"tender_report_{tender.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.xlsx"
    path = os.path.join(settings.reports_dir, filename)

    clauses_df = pd.DataFrame(
        [{"type": c.clause_type, "text": c.clause_text} for c in tender.clauses]
    )
    boq_df = pd.DataFrame(
        [
            {
                "item_name": b.item_name,
                "quantity": b.quantity,
                "unit": b.unit,
                "unit_rate": b.unit_rate,
                "total_cost": b.total_cost,
            }
            for b in tender.boq_items
        ]
    )
    risks_df = pd.DataFrame(
        [{"risk_type": r.risk_type, "severity": r.severity, "description": r.description} for r in tender.risks]
    )

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame([{"title": tender.title, "summary": tender.summary}]).to_excel(
            writer, sheet_name="summary", index=False
        )
        clauses_df.to_excel(writer, sheet_name="clauses", index=False)
        boq_df.to_excel(writer, sheet_name="boq", index=False)
        risks_df.to_excel(writer, sheet_name="risks", index=False)
    return path
