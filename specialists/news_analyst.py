"""News analysis specialist agent."""
import time
import structlog
from shared.models import SpecialistOutput, SpecialistType
from specialists.base_specialist import BaseSpecialist

logger = structlog.get_logger(__name__)

NEWS_SYSTEM_PROMPT = """You are a financial news analyst specialising in sentiment analysis and event-driven research.
Analyse recent news and media coverage with focus on:
- Overall news sentiment (positive/negative/neutral) with score
- Key headline events and their business impact
- Management statements and strategic announcements
- Regulatory and legal developments
- Media narrative trends
- Social media sentiment indicators

Provide sentiment score from -1.0 (very negative) to 1.0 (very positive).
Structure your analysis clearly. End with 3-5 key news findings as bullet points starting with '- '."""

MOCK_NEWS_DATA = [
    {"date": "2024-11-15", "headline": "Company reports record Q3 revenue, beating analyst consensus by 4%", "sentiment": 0.8, "source": "Financial Times"},
    {"date": "2024-11-10", "headline": "CEO announces strategic AI investment of £150M over 3 years", "sentiment": 0.7, "source": "Reuters"},
    {"date": "2024-10-28", "headline": "Regulatory review initiated into data practices — company cooperating fully", "sentiment": -0.2, "source": "The Guardian"},
    {"date": "2024-10-15", "headline": "Partnership announced with leading cloud provider for infrastructure modernisation", "sentiment": 0.6, "source": "TechCrunch"},
    {"date": "2024-09-30", "headline": "CFO departure announced; succession plan detailed", "sentiment": -0.1, "source": "City A.M."},
]


class NewsAnalyst(BaseSpecialist):
    """Analyses news sentiment and key recent developments."""

    specialist_type = SpecialistType.NEWS_ANALYST

    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        """Analyse recent news coverage for the given company/topic."""
        start_time = time.time()
        logger.info("news_analysis_started", topic=topic)

        news_items = context.get("news_data", MOCK_NEWS_DATA)

        news_text = "\n".join([
            f"- [{item['date']}] {item['headline']} (Sentiment: {item['sentiment']}, Source: {item['source']})"
            for item in news_items
        ])

        avg_sentiment = sum(item["sentiment"] for item in news_items) / len(news_items)

        user_prompt = f"""
Company/Topic: {topic}
Average News Sentiment: {round(avg_sentiment, 2)}

Recent News Coverage:
{news_text}

Analyse the news narrative, key themes, and implications for investors and stakeholders.
"""

        analysis_text = await self._call_llm(NEWS_SYSTEM_PROMPT, user_prompt)
        key_findings = self._extract_findings(analysis_text)
        processing_time = time.time() - start_time

        return SpecialistOutput(
            specialist_type=SpecialistType.NEWS_ANALYST,
            analysis_text=analysis_text,
            confidence_score=0.79,
            key_findings=key_findings,
            data_sources=["Financial Times", "Reuters", "Bloomberg News", "Company Press Releases"],
            processing_time_seconds=round(processing_time, 2),
        )
