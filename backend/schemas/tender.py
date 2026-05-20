from datetime import datetime

from pydantic import BaseModel


class TenderCreate(BaseModel):
    title: str


class ClauseOut(BaseModel):
    id: int
    clause_type: str
    clause_text: str

    class Config:
        from_attributes = True


class BOQItemOut(BaseModel):
    id: int
    item_name: str
    quantity: float
    unit: str
    unit_rate: float
    total_cost: float

    class Config:
        from_attributes = True


class RiskOut(BaseModel):
    id: int
    risk_type: str
    severity: str
    description: str

    class Config:
        from_attributes = True


class TenderOut(BaseModel):
    id: int
    title: str
    uploaded_by: int
    file_path: str
    upload_date: datetime
    summary: str

    class Config:
        from_attributes = True


class TenderDetail(TenderOut):
    extracted_text: str
    clauses: list[ClauseOut]
    boq_items: list[BOQItemOut]
    risks: list[RiskOut]
