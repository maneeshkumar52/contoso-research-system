"""End-to-end pipeline tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from shared.models import ResearchRequest


@pytest.mark.asyncio
async def test_pipeline_local_mode():
    """Test full pipeline runs in LOCAL_MODE without Service Bus."""
    request = ResearchRequest(
        topic="Contoso Financial Q4 2024 Analysis",
        company_name="Contoso Financial plc",
        date_range="last 12 months",
    )

    specialist_response = MagicMock()
    specialist_response.choices[0].message.content = "Strong performance observed.\n- Revenue grew 7% YoY\n- Margins improved"
    specialist_response.usage.total_tokens = 200

    synthesis_response = MagicMock()
    synthesis_response.choices[0].message.content = '{"executive_summary": "Contoso Financial demonstrates strong fundamentals.", "key_findings": ["Revenue growth of 7.2%", "Strong margins", "Good ESG score", "Low debt", "Positive news sentiment"], "risk_factors": ["Regulatory risk", "Cyber risk", "Currency exposure"], "recommendations": ["Maintain overweight position", "Monitor regulatory developments"], "consensus_areas": "All specialists agree on financial health", "divergent_views": "None significant"}'
    synthesis_response.usage.total_tokens = 300

    compliance_response = MagicMock()
    compliance_response.choices[0].message.content = '{"approved": true, "issues": [], "risk_rating": "low", "review_notes": "Meets FCA standards"}'
    compliance_response.usage.total_tokens = 100

    responses = [specialist_response] * 5 + [synthesis_response, compliance_response]

    with patch("specialists.base_specialist.AsyncAzureOpenAI") as mock_specialist_oai, \
         patch("synthesiser.agent.AsyncAzureOpenAI") as mock_synth_oai, \
         patch("compliance_gate.agent.AsyncAzureOpenAI") as mock_compliance_oai, \
         patch("orchestrator.report_store.store_report", new_callable=AsyncMock) as mock_store:

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=responses + [specialist_response] * 10)
        mock_specialist_oai.return_value = mock_client
        mock_synth_oai.return_value = mock_client
        mock_compliance_oai.return_value = mock_client
        mock_store.return_value = request.run_id

        from orchestrator.pipeline import ResearchPipeline
        pipeline = ResearchPipeline()
        report = await pipeline.run(request)

        assert report is not None
        assert report.run_id == request.run_id
        assert report.company_name == "Contoso Financial plc"
        assert report.synthesis is not None
        assert report.compliance is not None
        assert report.total_pipeline_time >= 0
