from sqlalchemy.orm import Session

from backend.ai.clause_extractor import extract_clauses
from backend.ai.risk_analyzer import analyze_risks
from backend.database.session import SessionLocal
from backend.models import BOQItem, ExtractedClause, RiskAnalysis, Tender
from backend.services.boq_service import extract_boq_items


def generate_for_latest_tender() -> None:
    db: Session = SessionLocal()
    try:
        tender = db.query(Tender).order_by(Tender.id.desc()).first()
        if not tender:
            print("No tenders found.")
            return

        db.query(ExtractedClause).filter(ExtractedClause.tender_id == tender.id).delete()
        db.query(BOQItem).filter(BOQItem.tender_id == tender.id).delete()
        db.query(RiskAnalysis).filter(RiskAnalysis.tender_id == tender.id).delete()

        clause_result = extract_clauses(tender.extracted_text)
        tender.summary = clause_result.get("summary", "No summary")
        for clause in clause_result.get("clauses", []):
            db.add(
                ExtractedClause(
                    tender_id=tender.id,
                    clause_type=clause.get("clause_type", "unknown"),
                    clause_text=clause.get("clause_text", ""),
                )
            )

        for item in extract_boq_items(tender.file_path):
            db.add(BOQItem(tender_id=tender.id, **item))

        for risk in analyze_risks(tender.extracted_text):
            db.add(
                RiskAnalysis(
                    tender_id=tender.id,
                    risk_type=risk.get("risk_type", "general"),
                    severity=risk.get("severity", "medium"),
                    description=risk.get("description", ""),
                )
            )
        db.commit()
        print(f"Generated demo outputs for tender_id={tender.id}")
    finally:
        db.close()


if __name__ == "__main__":
    generate_for_latest_tender()
