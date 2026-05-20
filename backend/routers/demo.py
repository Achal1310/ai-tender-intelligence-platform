from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.middleware.auth_middleware import get_current_user
from backend.models import BOQItem, ExtractedClause, RiskAnalysis, Tender, User
from backend.services.demo_service import create_sample_tender_pdf

router = APIRouter(prefix="/demo", tags=["Demo"])


@router.post("/generate-sample-pdf")
def generate_sample_pdf(_: User = Depends(get_current_user)):
    path = create_sample_tender_pdf()
    return {"sample_pdf_path": path}


@router.get("/sample-output/{tender_id}")
def sample_output(tender_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    clauses = db.query(ExtractedClause).filter(ExtractedClause.tender_id == tender_id).all()
    boq = db.query(BOQItem).filter(BOQItem.tender_id == tender_id).all()
    risks = db.query(RiskAnalysis).filter(RiskAnalysis.tender_id == tender_id).all()
    return {
        "tender": {
            "id": tender.id if tender else tender_id,
            "title": tender.title if tender else "Unknown",
            "summary": tender.summary if tender else "Not available",
        },
        "clauses": [{"type": c.clause_type, "text": c.clause_text} for c in clauses],
        "boq": [
            {
                "item": b.item_name,
                "qty": b.quantity,
                "unit": b.unit,
                "rate": b.unit_rate,
                "total": b.total_cost,
            }
            for b in boq
        ],
        "risks": [{"type": r.risk_type, "severity": r.severity, "description": r.description} for r in risks],
    }
