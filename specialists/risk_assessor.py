"""Risk assessment specialist agent."""
import time
import structlog
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

logger = structlog.get_logger(__name__)

RISK_SYSTEM_PROMPT = """You are a chief risk officer conducting comprehensive enterprise risk assessment.
Assess risk across all dimensions:
- Regulatory and compliance risk (probability × impact matrix)
- Operational risk (technology, supply chain, key person)
- Financial risk (liquidity, credit, market, currency)
- Reputational risk (brand, ESG controversies)
- Strategic risk (disruption, M&A, geopolitical)
- Cyber and data security risk

For each major risk category, provide probability (Low/Medium/High), impact (Low/Medium/High), and mitigation status.
End with 3-5 key risk findings as bullet points starting with '- '."""

MOCK_RISK_DATA = {
    "regulatory_risk": {"probability": "Medium", "impact": "High", "status": "Active monitoring"},
    "cyber_risk": {"probability": "Medium", "impact": "High", "status": "ISO 27001 certified"},
    "key_person_risk": {"probability": "Medium", "impact": "Medium", "status": "Succession plans in place"},
    "market_concentration": {"probability": "Low", "impact": "Medium", "status": "Diversification strategy active"},
    "currency_exposure": {"probability": "High", "impact": "Medium", "status": "50% hedged via forwards"},
    "supply_chain": {"probability": "Low", "impact": "Low", "status": "Dual-sourcing implemented"},
    "data_privacy": {"probability": "Medium", "impact": "High", "status": "GDPR compliant, audit Q4 2024"},
}


class RiskAssessor(BaseSpecialist):
    """Assesses enterprise risk factors across all dimensions."""

    specialist_type = SpecialistType.RISK_ASSESSOR

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        """Perform comprehensive risk assessment for the given company/topic."""
        start_time = time.time()
        logger.info("risk_assessment_started", topic=topic)

        risk_data = context.get("risk_data", MOCK_RISK_DATA)

        risk_lines = "\n".join([
            f"- {risk_type.replace('_', ' ').title()}: Probability={data['probability']}, Impact={data['impact']}, Status={data['status']}"
            for risk_type, data in risk_data.items()
        ])

        user_prompt = f"""
Company/Topic: {topic}

Risk Registry:
{risk_lines}

Conduct a comprehensive risk assessment with probability-impact scoring, mitigation effectiveness analysis,
and emerging risk identification. Identify the top 3 risks requiring immediate board attention.
"""

        analysis_text = await self._call_llm(RISK_SYSTEM_PROMPT, user_prompt)
        key_findings = self._extract_findings(analysis_text)
        processing_time = time.time() - start_time

        return SpecialistOutput(
            specialist_type=SpecialistType.RISK_ASSESSOR,
            analysis_text=analysis_text,
            confidence_score=0.85,
            key_findings=key_findings,
            data_sources=["Enterprise Risk Register", "Regulatory Correspondence", "Internal Audit Reports", "Insurance Assessments"],
            processing_time_seconds=round(processing_time, 2),
        )
