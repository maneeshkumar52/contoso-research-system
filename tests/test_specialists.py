"""Tests for specialist agents."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from shared.models import SpecialistType, ResearchRequest


@pytest.mark.asyncio
async def test_financial_analyst():
    """Test financial analyst produces valid output."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = """
Revenue has grown 7.2% YoY demonstrating solid top-line momentum.

Key analysis points:
- Strong gross margin of 42.3% indicates pricing power
- Free cash flow of £234M provides financial flexibility for M&A
- ROIC of 14.8% exceeds cost of capital, indicating value creation
- P/E of 21.4x represents moderate premium vs sector average of 18x
"""
    mock_response.usage.total_tokens = 200

    with patch("openai.AsyncAzureOpenAI") as mock_openai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        from specialists.financial_analyst import FinancialAnalyst
        analyst = FinancialAnalyst()
        analyst.client = mock_client

        result = await analyst.analyse("Contoso Financial", {"date_range": "last 12 months"})

        assert result.specialist_type == SpecialistType.FINANCIAL_ANALYST
        assert len(result.analysis_text) > 50
        assert 0.0 <= result.confidence_score <= 1.0
        assert len(result.key_findings) > 0
        assert result.processing_time_seconds >= 0


@pytest.mark.asyncio
async def test_esg_analyst():
    """Test ESG analyst produces valid output with composite score."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = """
Overall ESG score of 72.7/100 positions the company in the top quartile.

Key ESG findings:
- Environmental score of 71 reflects solid progress on decarbonisation
- Social score of 68 shows room for improvement in diversity metrics
- Governance score of 79 demonstrates best-in-class board practices
- Net zero target of 2040 is ambitious but achievable
"""
    mock_response.usage.total_tokens = 180

    with patch("openai.AsyncAzureOpenAI") as mock_openai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        from specialists.esg_analyst import ESGAnalyst
        analyst = ESGAnalyst()
        analyst.client = mock_client

        result = await analyst.analyse("Contoso Financial", {})

        assert result.specialist_type == SpecialistType.ESG_ANALYST
        assert result.confidence_score > 0
        assert len(result.data_sources) > 0


@pytest.mark.asyncio
async def test_risk_assessor():
    """Test risk assessor produces valid output."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = """
Enterprise risk profile is moderate with several key areas requiring attention.

Key risk findings:
- Cyber risk remains the highest priority with probability Medium and High impact
- Currency exposure on 45% of revenue is partially mitigated through forwards
- Regulatory risk elevated due to ongoing data practices review
"""
    mock_response.usage.total_tokens = 190

    with patch("openai.AsyncAzureOpenAI") as mock_openai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        from specialists.risk_assessor import RiskAssessor
        analyst = RiskAssessor()
        analyst.client = mock_client

        result = await analyst.analyse("Contoso Financial", {})

        assert result.specialist_type == SpecialistType.RISK_ASSESSOR
        assert len(result.key_findings) > 0
