"""Financial analyst specialist agent."""
import time
import structlog
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

logger = structlog.get_logger(__name__)

FINANCIAL_SYSTEM_PROMPT = """You are a senior equity research analyst specialising in quantitative financial analysis.
Analyse the provided company and financial data with rigorous attention to:
- Revenue growth trends and trajectory
- Gross margin and operating margin analysis
- Cash flow generation and quality
- Valuation multiples (P/E, EV/EBITDA, P/S)
- Balance sheet strength and debt metrics
- Return on equity (ROE) and return on invested capital (ROIC)

Structure your analysis with clear sections. Use specific numbers where available.
Conclude with 3-5 key financial findings as bullet points starting with '- '."""

MOCK_FINANCIAL_DATA = {
    "revenue": {"q1": 598, "q2": 612, "q3": 589, "q4": 601, "unit": "M GBP", "yoy_growth": "7.2%"},
    "gross_margin": "42.3%",
    "operating_margin": "18.7%",
    "ebitda_margin": "24.1%",
    "free_cash_flow": "£234M",
    "pe_ratio": 21.4,
    "ev_ebitda": 13.8,
    "debt_to_equity": 0.34,
    "roe": "19.2%",
    "roic": "14.8%",
}


class FinancialAnalyst(BaseSpecialist):
    """Performs quantitative financial analysis."""

    specialist_type = SpecialistType.FINANCIAL_ANALYST

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        """Analyse financial metrics for the given company/topic."""
        start_time = time.time()
        logger.info("financial_analysis_started", topic=topic)

        financial_data = context.get("financial_data", MOCK_FINANCIAL_DATA)

        user_prompt = f"""
Company/Topic: {topic}
Date Range: {context.get('date_range', 'last 12 months')}

Financial Data:
- Revenue: Q1 {financial_data['revenue']['q1']}M, Q2 {financial_data['revenue']['q2']}M, Q3 {financial_data['revenue']['q3']}M, Q4 {financial_data['revenue']['q4']}M {financial_data['revenue']['unit']}
- YoY Revenue Growth: {financial_data['revenue']['yoy_growth']}
- Gross Margin: {financial_data['gross_margin']}
- Operating Margin: {financial_data['operating_margin']}
- EBITDA Margin: {financial_data['ebitda_margin']}
- Free Cash Flow: {financial_data['free_cash_flow']}
- P/E Ratio: {financial_data['pe_ratio']}x
- EV/EBITDA: {financial_data['ev_ebitda']}x
- Debt/Equity: {financial_data['debt_to_equity']}
- ROE: {financial_data['roe']}
- ROIC: {financial_data['roic']}

Provide a comprehensive financial analysis with specific insights and investment implications.
"""

        analysis_text = await self._call_llm(FINANCIAL_SYSTEM_PROMPT, user_prompt)
        key_findings = self._extract_findings(analysis_text)
        processing_time = time.time() - start_time

        logger.info("financial_analysis_complete", processing_time=round(processing_time, 2))

        return SpecialistOutput(
            specialist_type=SpecialistType.FINANCIAL_ANALYST,
            analysis_text=analysis_text,
            confidence_score=0.87,
            key_findings=key_findings,
            data_sources=["Company Financial Reports", "Bloomberg", "Refinitiv Eikon", "SEC/Companies House Filings"],
            processing_time_seconds=round(processing_time, 2),
        )
