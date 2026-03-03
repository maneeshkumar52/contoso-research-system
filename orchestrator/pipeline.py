"""Fan-out/gather orchestration pipeline."""
import asyncio
import time
import structlog
from shared.config import get_settings
from shared.models import (
    ResearchRequest, SpecialistOutput, SpecialistType, FinalReport, SynthesisResult,
)
from specialists.financial_analyst import FinancialAnalyst
from specialists.market_researcher import MarketResearcher
from specialists.news_analyst import NewsAnalyst
from specialists.risk_assessor import RiskAssessor
from specialists.esg_analyst import ESGAnalyst
from synthesiser.agent import synthesise
from compliance_gate.agent import review_compliance
from orchestrator.report_store import store_report

logger = structlog.get_logger(__name__)

SPECIALIST_TIMEOUT_SECONDS = 120.0


class ResearchPipeline:
    """
    Orchestrates the full research pipeline:
    1. Fan-out: run all 5 specialists concurrently
    2. Gather: collect results with timeout handling
    3. Synthesise: combine into unified report
    4. Gate: compliance review
    5. Store: persist the final report
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.specialists = {
            SpecialistType.FINANCIAL_ANALYST: FinancialAnalyst(),
            SpecialistType.MARKET_RESEARCHER: MarketResearcher(),
            SpecialistType.NEWS_ANALYST: NewsAnalyst(),
            SpecialistType.RISK_ASSESSOR: RiskAssessor(),
            SpecialistType.ESG_ANALYST: ESGAnalyst(),
        }

    async def _run_specialist(
        self,
        specialist_type: SpecialistType,
        specialist,
        request: ResearchRequest,
    ) -> tuple:
        """Run a single specialist with timeout handling."""
        try:
            output = await asyncio.wait_for(
                specialist.analyse(
                    topic=request.topic,
                    context={"date_range": request.date_range, "company_name": request.company_name},
                ),
                timeout=SPECIALIST_TIMEOUT_SECONDS,
            )
            return specialist_type, output
        except asyncio.TimeoutError:
            logger.error("specialist_timeout", specialist=specialist_type.value)
            return specialist_type, None
        except Exception as exc:
            logger.error("specialist_failed", specialist=specialist_type.value, error=str(exc))
            return specialist_type, None

    async def run(self, request: ResearchRequest) -> FinalReport:
        """
        Execute the full research pipeline.

        Args:
            request: The research request with topic and company details.

        Returns:
            FinalReport with synthesis and compliance review.
        """
        pipeline_start = time.time()
        logger.info("research_pipeline_started", run_id=request.run_id, topic=request.topic)

        # Phase 1: Fan-out — run all specialists concurrently
        logger.info("phase1_fan_out_started", num_specialists=len(self.specialists))
        tasks = [
            self._run_specialist(spec_type, specialist, request)
            for spec_type, specialist in self.specialists.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Gather results — handle partial failures
        specialist_outputs = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error("specialist_gather_error", error=str(result))
                continue
            specialist_type, output = result
            if output is not None:
                specialist_outputs[specialist_type.value] = output

        logger.info("phase1_complete", specialists_succeeded=len(specialist_outputs))

        if not specialist_outputs:
            raise ValueError("All specialist agents failed — cannot produce research report")

        # Phase 2: Synthesise
        logger.info("phase2_synthesis_started")
        synthesis = await synthesise(
            specialist_outputs=specialist_outputs,
            topic=request.topic,
            company_name=request.company_name,
        )
        logger.info("phase2_synthesis_complete")

        # Phase 3: Compliance gate
        logger.info("phase3_compliance_started")
        compliance = await review_compliance(synthesis=synthesis, company_name=request.company_name)
        logger.info("phase3_compliance_complete", approved=compliance.approved)

        total_pipeline_time = time.time() - pipeline_start

        report = FinalReport(
            run_id=request.run_id,
            topic=request.topic,
            company_name=request.company_name,
            synthesis=synthesis,
            compliance=compliance,
            total_pipeline_time=round(total_pipeline_time, 2),
        )

        # Phase 4: Store
        logger.info("phase4_store_started")
        await store_report(report)

        logger.info(
            "research_pipeline_complete",
            run_id=request.run_id,
            total_time=round(total_pipeline_time, 2),
            approved=compliance.approved,
        )

        return report
