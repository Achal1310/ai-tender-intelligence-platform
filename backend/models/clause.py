from sqlalchemy import ForeignKey, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


class ExtractedClause(Base):
    __tablename__ = "extracted_clauses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), nullable=False, index=True)
    clause_type: Mapped[str] = mapped_column(String(120), nullable=False)
    clause_text: Mapped[str] = mapped_column(Text, nullable=False)

    tender = relationship("Tender", back_populates="clauses")
