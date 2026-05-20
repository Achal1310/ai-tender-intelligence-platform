import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.ai.clause_extractor import extract_clauses
from backend.ai.risk_analyzer import analyze_risks
from backend.database.session import get_db
from backend.middleware.auth_middleware import get_current_user
from backend.models import BOQItem, ExtractedClause, RiskAnalysis, Tender, User
from backend.schemas import AnalyzeRequest, AnalyzeResponse
from backend.services.boq_service import boq_analytics, extract_boq_items

router = APIRouter(tags=["Analysis"])
logger = logging.getLogger(__name__)


@router.post("/analyze-tender", response_model=AnalyzeResponse)
def analyze_tender(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tender = db.query(Tender).filter(Tender.id == payload.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    logger.info("Starting analysis for tender_id=%s", payload.tender_id)
    clause_result = extract_clauses(tender.extracted_text)
    tender.summary = clause_result.get("summary", "No summary")

    db.query(ExtractedClause).filter(ExtractedClause.tender_id == tender.id).delete()
    for clause in clause_result.get("clauses", []):
        db.add(
            ExtractedClause(
                tender_id=tender.id,
                clause_type=clause.get("clause_type", "unknown"),
                clause_text=clause.get("clause_text", ""),
            )
        )

    db.query(BOQItem).filter(BOQItem.tender_id == tender.id).delete()
    boq_items = extract_boq_items(tender.file_path)
    for item in boq_items:
        db.add(BOQItem(tender_id=tender.id, **item))

    db.query(RiskAnalysis).filter(RiskAnalysis.tender_id == tender.id).delete()
    risks = analyze_risks(tender.extracted_text)
    for risk in risks:
        db.add(
            RiskAnalysis(
                tender_id=tender.id,
                risk_type=risk.get("risk_type", "general"),
                severity=risk.get("severity", "medium"),
                description=risk.get("description", ""),
            )
        )

    # Keep derived BOQ metrics available in summary for quick dashboard display.
    metrics = boq_analytics(boq_items)
    tender.summary = (
        f"{tender.summary}\nEstimated Cost: {metrics['estimated_project_cost']}"
        f"\nTotal Quantity: {metrics['material_totals']}"
    )

    db.commit()
    db.refresh(tender)
    logger.info("Completed analysis for tender_id=%s", payload.tender_id)
    return AnalyzeResponse(
        tender_id=tender.id,
        summary=tender.summary,
        clauses_count=len(tender.clauses),
        boq_count=len(tender.boq_items),
        risks_count=len(tender.risks),
    )


@router.get("/clauses/{tender_id}")
def get_clauses(tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ExtractedClause).filter(ExtractedClause.tender_id == tender_id).all()


@router.get("/boq/{tender_id}")
def get_boq(tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(BOQItem).filter(BOQItem.tender_id == tender_id).all()


@router.get("/risk-analysis/{tender_id}")
def get_risks(tender_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(RiskAnalysis).filter(RiskAnalysis.tender_id == tender_id).all()
