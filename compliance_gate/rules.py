"""FCA compliance rules for financial research reports."""
from dataclasses import dataclass
from typing import List


@dataclass
class FCARule:
    """A single FCA compliance rule."""
    rule_id: str
    description: str
    check_prompt: str


FCA_RULES: List[FCARule] = [
    FCARule(
        rule_id="FCA-001",
        description="No guaranteed returns language",
        check_prompt="Does this report contain any language that guarantees investment returns or implies zero risk? Look for phrases like 'guaranteed', 'certain return', 'risk-free', 'will definitely'.",
    ),
    FCARule(
        rule_id="FCA-002",
        description="Past performance disclaimer required",
        check_prompt="Does the report discuss historical performance without including a past performance disclaimer? The report should note that past performance is not indicative of future results.",
    ),
    FCARule(
        rule_id="FCA-003",
        description="Clear, fair, and not misleading",
        check_prompt="Is any information presented in this report potentially misleading, one-sided, or not balanced? Check for cherry-picked statistics or omission of significant negative factors.",
    ),
    FCARule(
        rule_id="FCA-004",
        description="Risk warnings for investment recommendations",
        check_prompt="Does the report make investment recommendations without adequate risk warnings? All recommendations should be accompanied by appropriate risk disclosures.",
    ),
    FCARule(
        rule_id="FCA-005",
        description="No promotional language as research",
        check_prompt="Does this report use promotional or marketing language that could be mistaken for objective research? Look for overly positive language, superlatives, or sales-oriented framing.",
    ),
    FCARule(
        rule_id="FCA-006",
        description="Conflicts of interest disclosure",
        check_prompt="Does the report disclose any potential conflicts of interest, such as the firm holding positions in the securities discussed?",
    ),
]

REQUIRED_DISCLAIMERS = [
    "This research report is produced for informational purposes only and does not constitute investment advice.",
    "Past performance is not indicative of future results. The value of investments may fall as well as rise.",
    "This report is intended for professional investors and qualified counterparties only. It is not suitable for retail investors.",
    "Contoso Research Services Limited is authorised and regulated by the Financial Conduct Authority (FCA). FRN: 123456.",
]
