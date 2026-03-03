"""Pydantic models for all agents in the research system."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class SpecialistType(str, Enum):
    FINANCIAL_ANALYST = "financial_analyst"
    MARKET_RESEARCHER = "market_researcher"
    NEWS_ANALYST = "news_analyst"
    RISK_ASSESSOR = "risk_assessor"
    ESG_ANALYST = "esg_analyst"


class ResearchRequest(BaseModel):
    topic: str = Field(..., description="Research topic or company name")
    company_name: str = Field(..., description="Company being researched")
    date_range: str = Field(default="last 12 months")
    requested_by: str = Field(default="system")
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class SpecialistOutput(BaseModel):
    specialist_type: SpecialistType
    analysis_text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    key_findings: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    processing_time_seconds: float = 0.0


class SynthesisResult(BaseModel):
    executive_summary: str
    detailed_report: str
    key_findings: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    total_specialist_time: float = 0.0


class ComplianceResult(BaseModel):
    approved: bool
    issues: List[str] = Field(default_factory=list)
    required_disclaimers: List[str] = Field(default_factory=list)
    risk_rating: str = Field(default="medium")


class FinalReport(BaseModel):
    run_id: str
    topic: str
    company_name: str
    synthesis: SynthesisResult
    compliance: ComplianceResult
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_pipeline_time: float = 0.0
    status: str = "completed"
