"""Research System FastAPI entry point."""
from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import structlog

from shared.logging_config import configure_logging
from shared.models import ResearchRequest, FinalReport
from orchestrator.pipeline import ResearchPipeline

configure_logging()
logger = structlog.get_logger(__name__)

pipeline: ResearchPipeline = None
_report_store: Dict[str, dict] = {}  # In-memory store for demo; use Cosmos in production


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    pipeline = ResearchPipeline()
    logger.info("research_system_starting")
    yield
    logger.info("research_system_stopping")


app = FastAPI(
    title="Contoso Research System",
    description="Multi-agent financial research system with fan-out/gather architecture",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "contoso-research-system", "version": "1.0.0"}


@app.post("/api/v1/research")
async def start_research(request: ResearchRequest) -> dict:
    """Start a research pipeline run. Returns immediately with run_id."""
    try:
        # Run synchronously for simplicity — in production use background task
        report = await pipeline.run(request)
        report_dict = report.model_dump()
        report_dict["created_at"] = report.created_at.isoformat()
        _report_store[request.run_id] = report_dict
        return {"run_id": request.run_id, "status": "completed", "report": report_dict}
    except Exception as exc:
        logger.error("research_endpoint_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/report/{run_id}")
async def get_report(run_id: str) -> dict:
    """Retrieve a completed research report."""
    if run_id not in _report_store:
        raise HTTPException(status_code=404, detail=f"Report {run_id} not found")
    return _report_store[run_id]


@app.get("/api/v1/status/{run_id}")
async def get_status(run_id: str) -> dict:
    """Get pipeline status for a run."""
    if run_id in _report_store:
        return {"run_id": run_id, "status": "completed"}
    return {"run_id": run_id, "status": "not_found"}
