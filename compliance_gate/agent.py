"""Compliance gate agent: reviews synthesised reports against FCA rules."""
import json
import structlog
from openai import AsyncAzureOpenAI
from shared.config import get_settings
from shared.models import SynthesisResult, ComplianceResult
from compliance_gate.rules import FCA_RULES, REQUIRED_DISCLAIMERS
from compliance_gate.prompts import COMPLIANCE_SYSTEM_PROMPT

logger = structlog.get_logger(__name__)


async def review_compliance(synthesis: SynthesisResult, company_name: str) -> ComplianceResult:
    """
    Review a synthesised research report against FCA compliance rules.

    Args:
        synthesis: The synthesised research report to review.
        company_name: The company being researched.

    Returns:
        ComplianceResult indicating approval status, issues, and required disclaimers.
    """
    settings = get_settings()

    client = AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        max_retries=3,
    )

    rules_text = "\n".join([
        f"{rule.rule_id}: {rule.description}\nCheck: {rule.check_prompt}"
        for rule in FCA_RULES
    ])

    report_excerpt = f"""
Executive Summary:
{synthesis.executive_summary}

Key Findings:
{chr(10).join(f'- {f}' for f in synthesis.key_findings)}

Recommendations:
{chr(10).join(f'{i+1}. {r}' for i, r in enumerate(synthesis.recommendations))}

Risk Factors:
{chr(10).join(f'- {r}' for r in synthesis.risk_factors)}
"""

    user_prompt = f"""
Company Under Research: {company_name}

REPORT TO REVIEW:
{report_excerpt}

FCA COMPLIANCE RULES TO CHECK:
{rules_text}

Review this research report against all FCA rules. Be specific about any issues found.
"""

    try:
        response = await client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": COMPLIANCE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1000,
        )

        parsed = json.loads(response.choices[0].message.content)
        approved = parsed.get("approved", True)
        issues = parsed.get("issues", [])
        risk_rating = parsed.get("risk_rating", "medium")

        logger.info(
            "compliance_review_complete",
            approved=approved,
            issues_count=len(issues),
            risk_rating=risk_rating,
        )

        return ComplianceResult(
            approved=approved,
            issues=issues,
            required_disclaimers=REQUIRED_DISCLAIMERS,
            risk_rating=risk_rating,
        )

    except Exception as exc:
        logger.error("compliance_review_failed", error=str(exc))
        return ComplianceResult(
            approved=False,
            issues=[f"Compliance review could not be completed: {str(exc)}"],
            required_disclaimers=REQUIRED_DISCLAIMERS,
            risk_rating="high",
        )
