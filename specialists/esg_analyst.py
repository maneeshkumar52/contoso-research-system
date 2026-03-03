"""ESG analysis specialist agent."""
import time
import structlog
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

logger = structlog.get_logger(__name__)

ESG_SYSTEM_PROMPT = """You are an ESG (Environmental, Social, Governance) analyst specialising in sustainable investment research.
Analyse ESG performance across all three pillars:

ENVIRONMENTAL:
- Carbon emissions (Scope 1, 2, 3) and net-zero commitments
- Energy efficiency and renewable energy usage
- Water usage, waste management, circular economy initiatives
- Biodiversity and land use impact

SOCIAL:
- Employee diversity and inclusion metrics
- Pay equity and living wage commitments
- Supply chain labour standards
- Community investment and social impact

GOVERNANCE:
- Board composition (diversity, independence, skills matrix)
- Executive compensation alignment with long-term value
- Anti-corruption and ethics programmes
- Shareholder rights and transparency

Provide individual E, S, G scores (0-100) and a composite ESG score.
End with 3-5 key ESG findings as bullet points starting with '- '."""

MOCK_ESG_DATA = {
    "environmental": {
        "scope1_emissions": "12,450 tCO2e",
        "scope2_emissions": "8,230 tCO2e",
        "renewable_energy": "67%",
        "water_reduction_yoy": "12%",
        "net_zero_target": "2040",
        "e_score": 71,
    },
    "social": {
        "gender_diversity_leadership": "38%",
        "employee_satisfaction": "74%",
        "training_hours_per_employee": 42,
        "living_wage_certified": True,
        "supply_chain_audits": "94% of tier-1 suppliers audited",
        "s_score": 68,
    },
    "governance": {
        "board_independence": "73%",
        "board_diversity": "42%",
        "ceo_pay_ratio": "47:1",
        "ethics_violations": 0,
        "audit_committee_expertise": "All members financially qualified",
        "g_score": 79,
    },
}


class ESGAnalyst(BaseSpecialist):
    """Analyses Environmental, Social, and Governance factors."""

    specialist_type = SpecialistType.ESG_ANALYST

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        """Perform ESG analysis for the given company/topic."""
        start_time = time.time()
        logger.info("esg_analysis_started", topic=topic)

        esg_data = context.get("esg_data", MOCK_ESG_DATA)
        e_score = esg_data["environmental"]["e_score"]
        s_score = esg_data["social"]["s_score"]
        g_score = esg_data["governance"]["g_score"]
        composite_score = round((e_score + s_score + g_score) / 3, 1)

        user_prompt = f"""
Company/Topic: {topic}

ESG Data:
ENVIRONMENTAL (Score: {e_score}/100):
- Scope 1 Emissions: {esg_data['environmental']['scope1_emissions']}
- Scope 2 Emissions: {esg_data['environmental']['scope2_emissions']}
- Renewable Energy Usage: {esg_data['environmental']['renewable_energy']}
- Water Reduction YoY: {esg_data['environmental']['water_reduction_yoy']}
- Net Zero Target: {esg_data['environmental']['net_zero_target']}

SOCIAL (Score: {s_score}/100):
- Gender Diversity in Leadership: {esg_data['social']['gender_diversity_leadership']}
- Employee Satisfaction: {esg_data['social']['employee_satisfaction']}
- Training Hours per Employee: {esg_data['social']['training_hours_per_employee']}
- Living Wage Certified: {esg_data['social']['living_wage_certified']}

GOVERNANCE (Score: {g_score}/100):
- Board Independence: {esg_data['governance']['board_independence']}
- Board Diversity: {esg_data['governance']['board_diversity']}
- CEO Pay Ratio: {esg_data['governance']['ceo_pay_ratio']}
- Ethics Violations: {esg_data['governance']['ethics_violations']}

Composite ESG Score: {composite_score}/100

Provide detailed ESG analysis with peer comparison context and improvement recommendations.
"""

        analysis_text = await self._call_llm(ESG_SYSTEM_PROMPT, user_prompt)
        key_findings = self._extract_findings(analysis_text)
        processing_time = time.time() - start_time

        return SpecialistOutput(
            specialist_type=SpecialistType.ESG_ANALYST,
            analysis_text=analysis_text,
            confidence_score=0.81,
            key_findings=key_findings,
            data_sources=["MSCI ESG Ratings", "Sustainalytics", "CDP Climate Reports", "Company Sustainability Report"],
            processing_time_seconds=round(processing_time, 2),
        )
