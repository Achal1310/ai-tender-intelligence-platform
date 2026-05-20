import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.middleware.auth_middleware import get_current_user
from backend.models import Tender, User
from backend.services.report_service import generate_excel_report, generate_pdf_report

router = APIRouter(tags=["Export"])


@router.get("/export/pdf/{tender_id}")
def export_pdf(tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    path = generate_pdf_report(tender)
    return FileResponse(path, media_type="application/pdf", filename=os.path.basename(path))


@router.get("/export/excel/{tender_id}")
def export_excel(tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    path = generate_excel_report(tender)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(path),
    )
