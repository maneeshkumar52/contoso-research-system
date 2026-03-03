"""Tests for the compliance gate."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from shared.models import SynthesisResult


@pytest.mark.asyncio
async def test_compliance_approval():
    """Test that compliant reports are approved."""
    synthesis = SynthesisResult(
        executive_summary="This balanced research report presents analysis of Contoso Financial. Past performance may not predict future results. Investors should be aware that all investments carry risk.",
        detailed_report="Full analysis...",
        key_findings=["Revenue growth of 7.2% YoY", "Strong cash generation"],
        risk_factors=["Market competition", "Regulatory environment"],
        recommendations=["Consider portfolio allocation given risk profile"],
    )

    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"approved": true, "issues": [], "risk_rating": "low", "review_notes": "Report meets FCA standards"}'
    mock_response.usage.total_tokens = 150

    with patch("compliance_gate.agent.AsyncAzureOpenAI") as mock_openai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        from compliance_gate.agent import review_compliance
        result = await review_compliance(synthesis, "Contoso Financial")

        assert result.approved is True
        assert len(result.required_disclaimers) > 0


@pytest.mark.asyncio
async def test_compliance_rejection():
    """Test that non-compliant reports are rejected."""
    synthesis = SynthesisResult(
        executive_summary="Guaranteed returns of 20% with zero risk — best investment ever! Buy immediately!",
        detailed_report="Full analysis...",
        key_findings=["Guaranteed 20% return"],
        risk_factors=[],
        recommendations=["Buy immediately — can't lose"],
    )

    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"approved": false, "issues": ["Guaranteed returns language detected: \'Guaranteed returns of 20%\'", "Missing risk warnings", "Promotional language detected"], "risk_rating": "high", "review_notes": "Multiple critical FCA violations"}'
    mock_response.usage.total_tokens = 150

    with patch("compliance_gate.agent.AsyncAzureOpenAI") as mock_openai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        from compliance_gate.agent import review_compliance
        result = await review_compliance(synthesis, "Test Company")

        assert result.approved is False
        assert len(result.issues) > 0
        assert result.risk_rating == "high"
