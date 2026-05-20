import os
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.database.session import get_db
from backend.middleware.auth_middleware import get_current_user
from backend.models import Tender, User
from backend.schemas import TenderDetail, TenderOut
from backend.services.ocr_service import run_ocr_pipeline
from backend.utils.file_utils import ensure_directories, generate_unique_filename, validate_pdf

router = APIRouter(tags=["Tenders"])
logger = logging.getLogger(__name__)


@router.post("/upload-tender", response_model=TenderOut)
async def upload_tender(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        validate_pdf(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    ensure_directories(settings.uploads_dir)
    unique_name = generate_unique_filename(file.filename)
    file_path = os.path.join(settings.uploads_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    extracted_text = run_ocr_pipeline(file_path)
    logger.info("Uploaded tender '%s' by user=%s path=%s", title, current_user.id, file_path)
    tender = Tender(
        title=title,
        uploaded_by=current_user.id,
        file_path=file_path,
        extracted_text=extracted_text,
        summary="Pending analysis",
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)
    return tender


@router.get("/tenders", response_model=list[TenderOut])
def list_tenders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Tender).order_by(Tender.upload_date.desc()).all()


@router.get("/tender/{tender_id}", response_model=TenderDetail)
def tender_detail(tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender
