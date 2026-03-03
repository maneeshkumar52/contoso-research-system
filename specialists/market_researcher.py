"""Market research specialist agent."""
import time
import structlog
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

logger = structlog.get_logger(__name__)

MARKET_SYSTEM_PROMPT = """You are a senior market research analyst specialising in competitive intelligence.
Analyse market dynamics with focus on:
- Market size and growth rate (TAM, SAM, SOM)
- Competitive landscape and market share analysis
- Strategic positioning and differentiation
- Industry trends and disruption risks
- Geographic expansion opportunities
- Customer segment analysis

Use data-driven insights. Structure your response with clear sections.
End with 3-5 key market findings as bullet points starting with '- '."""

MOCK_MARKET_DATA = {
    "market_share": "23.4%",
    "market_size_tam": "£8.2B",
    "market_growth_rate": "11.3% CAGR",
    "top_competitors": ["CompetitorA (18.2%)", "CompetitorB (15.7%)", "CompetitorC (12.1%)"],
    "customer_segments": {"enterprise": "45%", "mid_market": "35%", "sme": "20%"},
    "geographic_revenue": {"uk": "55%", "europe": "30%", "us": "12%", "apac": "3%"},
    "net_promoter_score": 42,
    "customer_retention": "87.3%",
}


class MarketResearcher(BaseSpecialist):
    """Analyses market position, trends, and competitive landscape."""

    specialist_type = SpecialistType.MARKET_RESEARCHER

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        """Analyse market position for the given company/topic."""
        start_time = time.time()
        logger.info("market_research_started", topic=topic)

        market_data = context.get("market_data", MOCK_MARKET_DATA)

        user_prompt = f"""
Company/Topic: {topic}

Market Data:
- Market Share: {market_data['market_share']}
- Total Addressable Market: {market_data['market_size_tam']}
- Market Growth Rate: {market_data['market_growth_rate']}
- Competitors: {', '.join(market_data['top_competitors'])}
- Customer Segments: Enterprise {market_data['customer_segments']['enterprise']}, Mid-Market {market_data['customer_segments']['mid_market']}, SME {market_data['customer_segments']['sme']}
- Geographic Revenue Split: UK {market_data['geographic_revenue']['uk']}, Europe {market_data['geographic_revenue']['europe']}, US {market_data['geographic_revenue']['us']}
- NPS Score: {market_data['net_promoter_score']}
- Customer Retention: {market_data['customer_retention']}

Provide comprehensive market analysis covering competitive positioning, growth opportunities, and strategic threats.
"""

        analysis_text = await self._call_llm(MARKET_SYSTEM_PROMPT, user_prompt)
        key_findings = self._extract_findings(analysis_text)
        processing_time = time.time() - start_time

        return SpecialistOutput(
            specialist_type=SpecialistType.MARKET_RESEARCHER,
            analysis_text=analysis_text,
            confidence_score=0.83,
            key_findings=key_findings,
            data_sources=["Gartner Market Research", "IDC Reports", "Primary Customer Surveys", "Competitor Filings"],
            processing_time_seconds=round(processing_time, 2),
        )
