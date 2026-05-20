import json
import logging
import re

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.core.config import settings

logger = logging.getLogger(__name__)


def analyze_risks(text: str) -> list[dict]:
    if not text.strip():
        return []

    if not settings.openai_api_key:
        logger.info("OPENAI_API_KEY missing. Using deterministic local risk analysis.")
        return _fallback_risk_analysis(text)

    llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0.1)
    prompt = ChatPromptTemplate.from_template(
        """
Identify risk signals in this tender:
- risky clauses
- hidden penalties
- unrealistic timelines
- legal risks
- financial risks

Return ONLY JSON:
[
  {{"risk_type":"...","severity":"low|medium|high|critical","description":"..."}}
]

Tender Text:
{text}
"""
    )
    chain = prompt | llm
    response = chain.invoke({"text": text[:22000]})
    raw = response.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.exception("Failed risk JSON parse")
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end != -1:
            return json.loads(raw[start : end + 1])
        raise ValueError("AI output parsing failed for risks")


def _fallback_risk_analysis(text: str) -> list[dict]:
    checks = [
        ("financial risk", r"(emd|security deposit|bank guarantee)", "medium"),
        ("legal risk", r"(indemnity|arbitration|jurisdiction)", "high"),
        ("hidden penalties", r"(penalt|liquidated damages|forfeit)", "high"),
        ("timeline risk", r"(within\s+\d+\s+days|completion\s+in\s+\d+\s+days)", "medium"),
        ("payment risk", r"(payment.*\d+\s+days|deferred payment|retention)", "medium"),
    ]
    risks: list[dict] = []
    for risk_type, pattern, severity in checks:
        if re.search(pattern, text, flags=re.IGNORECASE):
            risks.append(
                {
                    "risk_type": risk_type,
                    "severity": severity,
                    "description": f"Detected pattern '{pattern}' in tender text. Review this clause carefully.",
                }
            )
    if not risks:
        risks.append(
            {
                "risk_type": "general",
                "severity": "low",
                "description": "No obvious high-risk phrases detected in local analysis mode.",
            }
        )
    return risks
