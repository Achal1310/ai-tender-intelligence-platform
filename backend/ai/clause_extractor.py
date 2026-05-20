import json
import logging
import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.core.config import settings

logger = logging.getLogger(__name__)

CLAUSE_TYPES = [
    "EMD amount",
    "completion timeline",
    "eligibility criteria",
    "penalties",
    "payment terms",
    "technical requirements",
    "submission deadline",
]


def extract_clauses(text: str) -> dict:
    if not text.strip():
        raise ValueError("No extracted text available for clause extraction")

    if not settings.openai_api_key:
        logger.info("OPENAI_API_KEY missing. Using deterministic local clause extraction.")
        return _fallback_clause_extraction(text)

    llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0)
    prompt = ChatPromptTemplate.from_template(
        """
You are a tender analysis expert.
Extract the following clause categories from the tender text:
{clause_types}

Return ONLY valid JSON with this schema:
{{
  "summary": "short summary",
  "clauses": [
    {{"clause_type":"EMD amount","clause_text":"..."}}
  ]
}}

If a clause is missing, include it with clause_text as "Not Found".
Tender Text:
{text}
"""
    )
    chain = prompt | llm
    response = chain.invoke({"clause_types": ", ".join(CLAUSE_TYPES), "text": text[:25000]})
    raw = response.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.exception("Failed clause JSON parse")
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start : end + 1])
        raise ValueError("AI output parsing failed for clauses")


def _fallback_clause_extraction(text: str) -> dict:
    short = " ".join(text.split())[:900]
    patterns = {
        "EMD amount": r"(EMD[^.\n:]*[:\-]?\s*[A-Z]{0,3}\s?[\d,]+(?:\.\d+)?)",
        "completion timeline": r"(completion[^.\n:]*[:\-]?\s*[\d]+\s*(days|months|weeks))",
        "eligibility criteria": r"(eligibility[^.\n]{0,200})",
        "penalties": r"(penalt(?:y|ies)[^.\n]{0,220})",
        "payment terms": r"(payment[^.\n]{0,220})",
        "technical requirements": r"(technical[^.\n]{0,240})",
        "submission deadline": r"(submission deadline[^.\n]{0,220})",
    }
    clauses = []
    for clause_type in CLAUSE_TYPES:
        match = re.search(patterns[clause_type], text, flags=re.IGNORECASE)
        clauses.append(
            {
                "clause_type": clause_type,
                "clause_text": match.group(1).strip() if match else "Not Found",
            }
        )
    return {
        "summary": f"Demo summary generated from local parser. Preview: {short}",
        "clauses": clauses,
    }
