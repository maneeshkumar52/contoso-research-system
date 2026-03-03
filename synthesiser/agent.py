"""Synthesiser agent: combines all specialist outputs into a unified report."""
import json
import structlog
from openai import AsyncAzureOpenAI
from shared.config import get_settings
from shared.models import SpecialistOutput, SynthesisResult
from synthesiser.prompts import SYNTHESIS_SYSTEM_PROMPT

logger = structlog.get_logger(__name__)


async def synthesise(specialist_outputs: dict, topic: str, company_name: str) -> SynthesisResult:
    """
    Synthesise all specialist outputs into a unified research report.

    Args:
        specialist_outputs: Dict mapping specialist type to their output.
        topic: Research topic.
        company_name: Company being researched.

    Returns:
        SynthesisResult with executive summary, findings, and recommendations.
    """
    settings = get_settings()

    client = AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        max_retries=3,
    )

    total_specialist_time = sum(
        output.processing_time_seconds for output in specialist_outputs.values()
    )

    # Build combined context from all specialists
    specialist_context = ""
    for specialist_name, output in specialist_outputs.items():
        specialist_context += f"\n\n=== {specialist_name.upper().replace('_', ' ')} ===\n"
        specialist_context += f"Confidence: {output.confidence_score:.0%}\n"
        specialist_context += "Key Findings:\n" + "\n".join(f"- {f}" for f in output.key_findings) + "\n"
        specialist_context += f"\nDetailed Analysis:\n{output.analysis_text[:600]}..."

    user_prompt = f"""
Research Topic: {topic}
Company: {company_name}

SPECIALIST REPORTS:
{specialist_context}

Please synthesise all specialist inputs into a comprehensive, investment-grade research report.
Respond with a JSON object containing:
{{
  "executive_summary": "<2-3 paragraph synthesis>",
  "key_findings": ["<finding 1>", "<finding 2>", ...(5 total)],
  "risk_factors": ["<risk 1>", "<risk 2>", ...(3 total)],
  "recommendations": ["<recommendation 1>", ...(4 total)],
  "consensus_areas": "<brief note on where specialists agree>",
  "divergent_views": "<note on contradictions>"
}}
"""

    try:
        response = await client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000,
        )

        parsed = json.loads(response.choices[0].message.content)

        logger.info("synthesis_complete", findings_count=len(parsed.get("key_findings", [])))

        return SynthesisResult(
            executive_summary=parsed.get("executive_summary", ""),
            detailed_report=specialist_context,
            key_findings=parsed.get("key_findings", []),
            risk_factors=parsed.get("risk_factors", []),
            recommendations=parsed.get("recommendations", []),
            total_specialist_time=total_specialist_time,
        )

    except Exception as exc:
        logger.error("synthesis_failed", error=str(exc))
        all_findings = []
        for output in specialist_outputs.values():
            all_findings.extend(output.key_findings[:2])

        return SynthesisResult(
            executive_summary=f"Research analysis for {company_name} has been completed across 5 specialist domains. See detailed findings below.",
            detailed_report=specialist_context,
            key_findings=all_findings[:5],
            risk_factors=["Synthesis failed — review individual specialist reports for risk assessment"],
            recommendations=["Review individual specialist reports for recommendations"],
            total_specialist_time=total_specialist_time,
        )
