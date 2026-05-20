from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    tender_id: int


class AnalyzeResponse(BaseModel):
    tender_id: int
    summary: str
    clauses_count: int
    boq_count: int
    risks_count: int
