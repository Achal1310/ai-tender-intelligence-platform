from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


class Tender(Base):
    __tablename__ = "tenders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)

    uploader = relationship("User", back_populates="tenders")
    clauses = relationship("ExtractedClause", back_populates="tender", cascade="all, delete-orphan")
    boq_items = relationship("BOQItem", back_populates="tender", cascade="all, delete-orphan")
    risks = relationship("RiskAnalysis", back_populates="tender", cascade="all, delete-orphan")
