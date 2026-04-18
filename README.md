<div align="center">

# 🏢 Contoso Research System

### Multi-Agent Financial Research Intelligence Pipeline with FCA Compliance

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-GPT--4o-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![Cosmos DB](https://img.shields.io/badge/Cosmos_DB-Serverless-0078D4?logo=microsoftazure)](https://azure.microsoft.com/en-us/products/cosmos-db)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*A production-grade multi-agent system that orchestrates 5 specialist AI analysts concurrently, synthesises their findings into unified research reports, and validates every output against Financial Conduct Authority (FCA) compliance rules — all within a single API call.*

*Chapter 18 of "Prompt to Production" by Maneesh Kumar*

[Architecture](#architecture) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [Specialists](#specialist-agents) · [Compliance](#fca-compliance-gate) · [Deployment](#deployment)

</div>

---

## Why This Exists

Financial research teams need institutional-grade analysis that spans multiple domains — financial metrics, market dynamics, news sentiment, risk assessment, and ESG scoring — synthesised into a single coherent report that passes regulatory review. Traditional approaches either run these analyses sequentially (slow), skip compliance entirely (risky), or produce unstructured outputs that analysts must manually reconcile.

**Contoso Research System** solves this with a fan-out/gather architecture:

| Problem | Traditional Approach | This System |
|---------|---------------------|-------------|
| Multi-domain analysis | Sequential agent chain (~600s) | 5 concurrent specialists via `asyncio.gather` (~120s) |
| Synthesis quality | Manual reconciliation | Dedicated synthesis LLM with structured JSON output |
| Regulatory compliance | Post-hoc manual review | Automated FCA compliance gate with 6 rule checks |
| Partial failures | Pipeline abort | Graceful degradation — continues with available outputs |
| Report persistence | Single store | Dual-write: Cosmos DB (queries) + Blob Storage (archival) |
| Output format | Free-text | Structured JSON + Jinja2 Markdown report |

---

## Architecture

### High-Level Pipeline

```
                        ┌───────────────────┐
                        │   Client / API    │
                        │  POST /api/v1/    │
                        │     research      │
                        └────────┬──────────┘
                                 │
                  ┌──────────────▼───────────────┐
                  │   orchestrator/main.py        │
                  │   FastAPI App (lifespan)       │
                  │   ResearchPipeline singleton   │
                  └──────────────┬───────────────┘
                                 │
              ╔══════════════════╧══════════════════╗
              ║  PHASE 1: Fan-Out (asyncio.gather)  ║
              ║  5 specialists run CONCURRENTLY      ║
              ║  120-second timeout per specialist   ║
              ╚══════════════════╤══════════════════╝
                                 │
         ┌───────────┬───────────┼───────────┬───────────┐
         │           │           │           │           │
         ▼           ▼           ▼           ▼           ▼
   ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐
   │Financial ││ Market   ││  News    ││  Risk    ││  ESG     │
   │Analyst   ││Researcher││ Analyst  ││Assessor  ││ Analyst  │
   │conf=0.87 ││conf=0.83 ││conf=0.79 ││conf=0.85 ││conf=0.81 │
   └────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘
        │           │           │           │           │
        └───────────┴───────────┼───────────┴───────────┘
                                │
              ╔═════════════════╧════════════════╗
              ║  PHASE 2: Synthesis               ║
              ║  synthesiser/agent.py              ║
              ║  JSON structured output (GPT-4o)   ║
              ╚═════════════════╤════════════════╝
                                │
              ╔═════════════════╧════════════════╗
              ║  PHASE 3: Compliance Gate         ║
              ║  compliance_gate/agent.py          ║
              ║  6 FCA rules + 4 disclaimers       ║
              ║  temperature=0.1 for determinism   ║
              ╚═════════════════╤════════════════╝
                                │
              ╔═════════════════╧════════════════╗
              ║  PHASE 4: Dual-Write Persist      ║
              ║  → Cosmos DB (document store)      ║
              ║  → Azure Blob Storage (JSON)       ║
              ║  → In-memory cache (API lookup)    ║
              ╚═════════════════╤════════════════╝
                                │
                                ▼
                  ┌──────────────────────────────┐
                  │  FinalReport returned to API  │
                  └──────────────────────────────┘
```

### Data Flow Through the Pipeline

```
ResearchRequest
    ├── topic: str
    ├── company_name: str
    ├── date_range: str ("last 12 months")
    └── run_id: str (auto-generated UUID)
         │
         ▼
    5× SpecialistOutput (concurrent fan-out)
    ├── specialist_type: SpecialistType (enum)
    ├── analysis_text: str (LLM-generated)
    ├── confidence_score: float (0.0–1.0)
    ├── key_findings: List[str]
    ├── data_sources: List[str]
    └── processing_time_seconds: float
         │
         ▼
    SynthesisResult (structured JSON from LLM)
    ├── executive_summary: str (2-3 paragraphs)
    ├── detailed_report: str
    ├── key_findings: List[str] (top 5)
    ├── risk_factors: List[str] (top 3)
    ├── recommendations: List[str] (3-5 actionable)
    └── total_specialist_time: float
         │
         ▼
    ComplianceResult (FCA rule validation)
    ├── approved: bool
    ├── issues: List[str] (specific violations with quotes)
    ├── required_disclaimers: List[str] (4 mandatory)
    └── risk_rating: str ("low" | "medium" | "high")
         │
         ▼
    FinalReport → Cosmos DB + Blob Storage + API
```

### This Is NOT a RAG System

| Dimension | Generic RAG | Contoso Research System |
|-----------|-------------|------------------------|
| Data retrieval | Vector similarity search over chunks | No retrieval — structured mock data per specialist |
| Embeddings | Generates + stores in vector DB | None |
| Vector store | Pinecone / Chroma / FAISS | None |
| Agent count | 1 (retriever + generator) | 7 LLM calls (5 specialists + synthesiser + compliance) |
| Concurrency | Sequential retrieve→generate | Fan-out: 5 concurrent specialists |
| Compliance | None | FCA rules engine + LLM validation |
| Output format | Free-text answer | Structured JSON + formatted Markdown report |
| Domain | General Q&A | Financial research (equity analysis) |
| Persistence | Optional | Dual-write Cosmos DB + Blob Storage |
| Timeout handling | None | 120s per specialist with graceful degradation |

---

## Design Decisions

### Why Fan-Out/Gather Instead of Sequential Chain?

```
Sequential Chain (Traditional):
  Financial → Market → News → Risk → ESG → Synthesis → Compliance
  Total time: ~600 seconds (120s × 5 specialists)

Fan-Out/Gather (This System):
  Financial ─┐
  Market    ─┤
  News      ─┼→ Gather → Synthesis → Compliance
  Risk      ─┤
  ESG       ─┘
  Total time: ~120 seconds (all specialists concurrent)
```

**Decision**: `asyncio.gather` with per-specialist `asyncio.wait_for(timeout=120)` enables 5× throughput improvement while maintaining partial-failure tolerance.

### Why Separate LLM Clients per Phase?

The system creates **7 independent `AsyncAzureOpenAI` clients** — one per specialist (5), one for synthesis, one for compliance:

| Phase | Temperature | Max Tokens | Response Format | Purpose |
|-------|-------------|------------|-----------------|---------|
| Specialists (×5) | 0.3 | 1,500 | Text | Domain analysis |
| Synthesis (×1) | 0.3 | 2,000 | JSON object | Structured merging |
| Compliance (×1) | 0.1 | 1,000 | JSON object | Deterministic review |

**Decision**: Lower temperature (0.1) for compliance ensures more deterministic regulatory review. Separate clients prevent connection pool contention during concurrent fan-out.

### Why Hardcoded Confidence Scores?

Each specialist returns a static confidence score (Financial: 0.87, Market: 0.83, News: 0.79, Risk: 0.85, ESG: 0.81) rather than dynamically computing confidence from LLM response quality.

**Decision**: In a teaching/reference implementation, static scores demonstrate the confidence-scoring interface without adding LLM self-evaluation complexity. Production systems would replace these with calibrated confidence estimators.

### Why Dual-Write Persistence?

Reports are persisted to **both** Cosmos DB and Azure Blob Storage with independent error handling:

```python
# Cosmos DB write (structured queries)
try:
    await container.create_item(report_dict)
except Exception:
    logger.error("cosmos_write_failed")

# Blob Storage write (archival) — NOT blocked by Cosmos failure
try:
    await blob_client.upload_blob(json_bytes, overwrite=True)
except Exception:
    logger.error("blob_write_failed")
```

**Decision**: Cosmos DB enables structured queries (by company, date, compliance status). Blob Storage provides cheap archival with direct JSON access. Independent try/except ensures one failure doesn't block the other.

### Why Lazy Azure SDK Imports?

```python
# Azure SDKs imported inside function bodies, not at module level
async def store_report(report):
    from azure.cosmos.aio import CosmosClient  # Lazy import
    from azure.storage.blob.aio import BlobServiceClient  # Lazy import
```

**Decision**: When `LOCAL_MODE=true`, the system starts without Azure dependencies installed. Lazy imports prevent `ImportError` at module load time.

---

## Specialist Agents

### Agent Roster

| # | Specialist | File | Confidence | Data Sources |
|---|-----------|------|------------|--------------|
| 1 | Financial Analyst | `specialists/financial_analyst.py` | 0.87 | Company Financial Reports, Bloomberg, Refinitiv Eikon, SEC/Companies House Filings |
| 2 | Market Researcher | `specialists/market_researcher.py` | 0.83 | Gartner Market Research, IDC Reports, Primary Customer Surveys, Competitor Filings |
| 3 | News Analyst | `specialists/news_analyst.py` | 0.79 | Financial Times, Reuters, Bloomberg News, Company Press Releases |
| 4 | Risk Assessor | `specialists/risk_assessor.py` | 0.85 | Enterprise Risk Register, Regulatory Correspondence, Internal Audit Reports, Insurance Assessments |
| 5 | ESG Analyst | `specialists/esg_analyst.py` | 0.81 | MSCI ESG Ratings, Sustainalytics, CDP Climate Reports, Company Sustainability Report |

### Template Method Pattern

All specialists inherit from `BaseSpecialist` (abstract base class):

```
BaseSpecialist (ABC)
├── __init__()          → Creates AsyncAzureOpenAI client (max_retries=3)
├── _call_llm()         → Chat completion with token tracking
├── _extract_findings() → Parses bullet points from LLM response
└── analyse()           → ABSTRACT — domain-specific implementation

FinancialAnalyst(BaseSpecialist)
├── analyse()           → Financial metrics analysis with MOCK_FINANCIAL_DATA
├── SYSTEM_PROMPT       → Revenue trends, margins, valuation, balance sheet
└── confidence = 0.87

MarketResearcher(BaseSpecialist)
├── analyse()           → Market dynamics with MOCK_MARKET_DATA
├── SYSTEM_PROMPT       → TAM/SAM/SOM, competitive landscape, positioning
└── confidence = 0.83

NewsAnalyst(BaseSpecialist)
├── analyse()           → Sentiment analysis with MOCK_NEWS_DATA
├── SYSTEM_PROMPT       → Sentiment scoring, event impact, narrative trends
└── confidence = 0.79

RiskAssessor(BaseSpecialist)
├── analyse()           → Enterprise risk assessment with MOCK_RISK_DATA
├── SYSTEM_PROMPT       → Probability × impact matrix, 7 risk categories
└── confidence = 0.85

ESGAnalyst(BaseSpecialist)
├── analyse()           → E/S/G pillar scoring with MOCK_ESG_DATA
├── SYSTEM_PROMPT       → Scope 1/2 emissions, diversity, board independence
└── confidence = 0.81
```

### Mock Data Sets

Each specialist carries domain-specific structured data for offline development:

<details>
<summary><strong>Financial Analyst — MOCK_FINANCIAL_DATA</strong></summary>

```python
{
    "revenue": {"q1": 598, "q2": 612, "q3": 589, "q4": 601, "unit": "M GBP", "yoy_growth": "7.2%"},
    "gross_margin": "42.3%",
    "operating_margin": "18.7%",
    "ebitda_margin": "24.1%",
    "free_cash_flow": "£234M",
    "pe_ratio": 21.4,
    "ev_ebitda": 13.8,
    "debt_to_equity": 0.34,
    "roe": "19.2%",
    "roic": "14.8%",
}
```

</details>

<details>
<summary><strong>Market Researcher — MOCK_MARKET_DATA</strong></summary>

```python
{
    "market_share": "23.4%",
    "market_size_tam": "£8.2B",
    "market_growth_rate": "11.3% CAGR",
    "top_competitors": ["CompetitorA (18.2%)", "CompetitorB (15.7%)", "CompetitorC (12.1%)"],
    "customer_segments": {"enterprise": "45%", "mid_market": "35%", "sme": "20%"},
    "geographic_revenue": {"uk": "55%", "europe": "30%", "us": "12%", "apac": "3%"},
    "net_promoter_score": 42,
    "customer_retention": "87.3%",
}
```

</details>

<details>
<summary><strong>News Analyst — MOCK_NEWS_DATA</strong></summary>

```python
[
    {"date": "2024-11-15", "headline": "Company reports record Q3 revenue, beating analyst consensus by 4%",
     "sentiment": 0.8, "source": "Financial Times"},
    {"date": "2024-11-10", "headline": "CEO announces strategic AI investment of £150M over 3 years",
     "sentiment": 0.7, "source": "Reuters"},
    {"date": "2024-10-28", "headline": "Regulatory review initiated into data practices — company cooperating fully",
     "sentiment": -0.2, "source": "The Guardian"},
    {"date": "2024-10-15", "headline": "Partnership announced with leading cloud provider for infrastructure modernisation",
     "sentiment": 0.6, "source": "TechCrunch"},
    {"date": "2024-09-30", "headline": "CFO departure announced; succession plan detailed",
     "sentiment": -0.1, "source": "City A.M."},
]
```

</details>

<details>
<summary><strong>Risk Assessor — MOCK_RISK_DATA</strong></summary>

```python
{
    "regulatory_risk": {"probability": "Medium", "impact": "High", "status": "Active monitoring"},
    "cyber_risk": {"probability": "Medium", "impact": "High", "status": "ISO 27001 certified"},
    "key_person_risk": {"probability": "Medium", "impact": "Medium", "status": "Succession plans in place"},
    "market_concentration": {"probability": "Low", "impact": "Medium", "status": "Diversification strategy active"},
    "currency_exposure": {"probability": "High", "impact": "Medium", "status": "50% hedged via forwards"},
    "supply_chain": {"probability": "Low", "impact": "Low", "status": "Dual-sourcing implemented"},
    "data_privacy": {"probability": "Medium", "impact": "High", "status": "GDPR compliant, audit Q4 2024"},
}
```

</details>

<details>
<summary><strong>ESG Analyst — MOCK_ESG_DATA</strong></summary>

```python
{
    "environmental": {
        "scope1_emissions": "12,450 tCO2e", "scope2_emissions": "8,230 tCO2e",
        "renewable_energy": "67%", "water_reduction_yoy": "12%",
        "net_zero_target": "2040", "e_score": 71,
    },
    "social": {
        "gender_diversity_leadership": "38%", "employee_satisfaction": "74%",
        "training_hours_per_employee": 42, "living_wage_certified": True,
        "supply_chain_audits": "94% of tier-1 suppliers audited", "s_score": 68,
    },
    "governance": {
        "board_independence": "73%", "board_diversity": "42%",
        "ceo_pay_ratio": "47:1", "ethics_violations": 0,
        "audit_committee_expertise": "All members financially qualified", "g_score": 79,
    },
}
```

</details>

### System Prompts

<details>
<summary><strong>Financial Analyst System Prompt</strong></summary>

```
You are a senior equity research analyst specialising in quantitative financial analysis.
Analyse the provided company and financial data with rigorous attention to:
- Revenue growth trends and trajectory
- Gross margin and operating margin analysis
- Cash flow generation and quality
- Valuation multiples (P/E, EV/EBITDA, P/S)
- Balance sheet strength and debt metrics
- Return on equity (ROE) and return on invested capital (ROIC)

Structure your analysis with clear sections. Use specific numbers where available.
Conclude with 3-5 key financial findings as bullet points starting with '- '.
```

</details>

<details>
<summary><strong>Market Researcher System Prompt</strong></summary>

```
You are a senior market research analyst specialising in competitive intelligence.
Analyse market dynamics with focus on:
- Market size and growth rate (TAM, SAM, SOM)
- Competitive landscape and market share analysis
- Strategic positioning and differentiation
- Industry trends and disruption risks
- Geographic expansion opportunities
- Customer segment analysis

Use data-driven insights. Structure your response with clear sections.
End with 3-5 key market findings as bullet points starting with '- '.
```

</details>

<details>
<summary><strong>News Analyst System Prompt</strong></summary>

```
You are a financial news analyst specialising in sentiment analysis and event-driven research.
Analyse recent news and media coverage with focus on:
- Overall news sentiment (positive/negative/neutral) with score
- Key headline events and their business impact
- Management statements and strategic announcements
- Regulatory and legal developments
- Media narrative trends
- Social media sentiment indicators

Provide sentiment score from -1.0 (very negative) to 1.0 (very positive).
Structure your analysis clearly. End with 3-5 key news findings as bullet points starting with '- '.
```

</details>

<details>
<summary><strong>Risk Assessor System Prompt</strong></summary>

```
You are a chief risk officer conducting comprehensive enterprise risk assessment.
Assess risk across all dimensions:
- Regulatory and compliance risk (probability × impact matrix)
- Operational risk (technology, supply chain, key person)
- Financial risk (liquidity, credit, market, currency)
- Reputational risk (brand, ESG controversies)
- Strategic risk (disruption, M&A, geopolitical)
- Cyber and data security risk

For each major risk category, provide probability (Low/Medium/High), impact (Low/Medium/High),
and mitigation status. End with 3-5 key risk findings as bullet points starting with '- '.
```

</details>

<details>
<summary><strong>ESG Analyst System Prompt</strong></summary>

```
You are an ESG (Environmental, Social, Governance) analyst specialising in sustainable
investment research. Analyse ESG performance across all three pillars:

ENVIRONMENTAL:
- Carbon emissions (Scope 1, 2, 3) and net-zero commitments
- Energy efficiency and renewable energy usage
- Water usage, waste management, circular economy initiatives

SOCIAL:
- Employee diversity and inclusion metrics
- Pay equity and living wage commitments
- Supply chain labour standards

GOVERNANCE:
- Board composition (diversity, independence, skills matrix)
- Executive compensation alignment with long-term value
- Anti-corruption and ethics programmes

Provide individual E, S, G scores (0-100) and a composite ESG score.
End with 3-5 key ESG findings as bullet points starting with '- '.
```

</details>

<details>
<summary><strong>Synthesis System Prompt</strong></summary>

```
You are a senior investment analyst synthesising specialist research into a unified,
actionable research report for institutional investors.

You will receive analysis from 5 specialists: Financial, Market, News, Risk, and ESG analysts.
Your task is to:
1. Write a concise executive summary (2-3 paragraphs) that integrates all perspectives
2. Identify consensus findings across specialists
3. Highlight any contradictions or divergent views that require attention
4. Extract the top 5 key findings from across all analyses
5. Identify the top 3 risk factors
6. Provide 3-5 actionable recommendations with clear rationale

Write in professional, objective language appropriate for institutional investors.
Be specific — cite numbers and data points from the specialist reports.
```

</details>

<details>
<summary><strong>Compliance Gate System Prompt</strong></summary>

```
You are a compliance officer at a regulated financial services firm, reviewing research
reports against FCA (Financial Conduct Authority) rules.

Your role is to:
1. Check the report against each FCA rule provided
2. Identify any specific phrases or sections that violate compliance requirements
3. Assess the overall risk rating of the report
4. Determine whether the report can be approved as-is or requires amendments

Be thorough and specific. Cite specific text from the report when flagging issues.
Respond with JSON: {"approved": bool, "issues": [...], "risk_rating": "...", "review_notes": "..."}
```

</details>

---

## FCA Compliance Gate

### Regulatory Rules Engine

The compliance gate checks every synthesised report against 6 FCA rules before allowing persistence:

| Rule ID | Check | What the LLM Looks For |
|---------|-------|----------------------|
| FCA-001 | No guaranteed returns | Phrases like "guaranteed", "certain return", "risk-free", "will definitely" |
| FCA-002 | Past performance disclaimer | Historical performance discussed without "past performance is not indicative of future results" |
| FCA-003 | Clear, fair, not misleading | Cherry-picked statistics, omission of significant negative factors, one-sided presentation |
| FCA-004 | Risk warnings required | Investment recommendations without adequate risk disclosures |
| FCA-005 | No promotional language | Overly positive language, superlatives, or sales-oriented framing disguised as research |
| FCA-006 | Conflicts of interest | Missing disclosure of firm positions in discussed securities |

### Mandatory Disclaimers

Every approved report includes these 4 disclaimers:

> 1. "This research report is produced for informational purposes only and does not constitute investment advice."
> 2. "Past performance is not indicative of future results. The value of investments may fall as well as rise."
> 3. "This report is intended for professional investors and qualified counterparties only. It is not suitable for retail investors."
> 4. "Contoso Research Services Limited is authorised and regulated by the Financial Conduct Authority (FCA). FRN: 123456."

### Compliance Failure Handling

```
Report passes all 6 FCA rules?
├── YES → ComplianceResult(approved=True, risk_rating="low")
└── NO  → ComplianceResult(approved=False, issues=[...], risk_rating="high")
         Report still persisted with compliance status for audit trail

LLM call fails entirely?
└── Fail-safe: ComplianceResult(approved=False, risk_rating="high")
    No report is incorrectly marked as compliant
```

---

## Data Models

### Complete Pydantic Schema

```python
class SpecialistType(str, Enum):
    FINANCIAL_ANALYST = "financial_analyst"
    MARKET_RESEARCHER = "market_researcher"
    NEWS_ANALYST = "news_analyst"
    RISK_ASSESSOR = "risk_assessor"
    ESG_ANALYST = "esg_analyst"

class ResearchRequest(BaseModel):
    topic: str                                    # Research topic or company
    company_name: str                             # Company being researched
    date_range: str = "last 12 months"            # Time window for analysis
    requested_by: str = "system"                  # Requester identity
    run_id: str = Field(default_factory=uuid4)    # Unique pipeline run ID

class SpecialistOutput(BaseModel):
    specialist_type: SpecialistType               # Which specialist produced this
    analysis_text: str                            # Full LLM-generated analysis
    confidence_score: float                       # ge=0.0, le=1.0
    key_findings: List[str] = []                  # Extracted bullet points
    data_sources: List[str] = []                  # Attribution
    processing_time_seconds: float = 0.0          # Wall clock time

class SynthesisResult(BaseModel):
    executive_summary: str                        # 2-3 paragraph synthesis
    detailed_report: str                          # Full merged report
    key_findings: List[str] = []                  # Top 5 across specialists
    risk_factors: List[str] = []                  # Top 3 risks
    recommendations: List[str] = []               # 3-5 actionable items
    total_specialist_time: float = 0.0            # Sum of specialist times

class ComplianceResult(BaseModel):
    approved: bool                                # Pass/fail
    issues: List[str] = []                        # Specific violations
    required_disclaimers: List[str] = []          # 4 mandatory disclaimers
    risk_rating: str = "medium"                   # low/medium/high

class FinalReport(BaseModel):
    run_id: str                                   # Pipeline execution ID
    topic: str                                    # Original research topic
    company_name: str                             # Target company
    synthesis: SynthesisResult                    # Merged specialist output
    compliance: ComplianceResult                  # FCA validation result
    created_at: datetime = datetime.utcnow()      # Report timestamp
    total_pipeline_time: float = 0.0              # End-to-end duration
    status: str = "completed"                     # Pipeline status
```

---

## API Reference

### `GET /health`

Health check endpoint.

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "service": "contoso-research-system",
  "version": "1.0.0"
}
```

### `POST /api/v1/research`

Execute a full research pipeline. Runs 5 specialists concurrently, synthesises results, validates compliance, and persists the report.

```bash
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Azure AI Market Analysis",
    "company_name": "Microsoft",
    "date_range": "2024-Q4",
    "requested_by": "analyst@contoso.com"
  }'
```

**Response** (200 OK):

```json
{
  "run_id": "a1b2c3d4-...",
  "status": "completed",
  "report": {
    "run_id": "a1b2c3d4-...",
    "topic": "Azure AI Market Analysis",
    "company_name": "Microsoft",
    "synthesis": {
      "executive_summary": "...",
      "detailed_report": "...",
      "key_findings": ["Finding 1", "Finding 2", "..."],
      "risk_factors": ["Risk 1", "Risk 2", "Risk 3"],
      "recommendations": ["Recommendation 1", "..."],
      "total_specialist_time": 45.2
    },
    "compliance": {
      "approved": true,
      "issues": [],
      "required_disclaimers": ["Disclaimer 1", "..."],
      "risk_rating": "low"
    },
    "created_at": "2024-01-01T00:00:00",
    "total_pipeline_time": 52.3,
    "status": "completed"
  }
}
```

### `GET /api/v1/report/{run_id}`

Retrieve a previously generated report.

```bash
curl http://localhost:8000/api/v1/report/a1b2c3d4-...
```

**404**: `{"detail": "Report a1b2c3d4-... not found"}`

### `GET /api/v1/status/{run_id}`

Check pipeline execution status.

```bash
curl http://localhost:8000/api/v1/status/a1b2c3d4-...
```

```json
{"run_id": "a1b2c3d4-...", "status": "completed"}
```

---

## Quick Start

### Prerequisites

| Requirement | Version | Check |
|------------|---------|-------|
| Python | 3.11+ | `python --version` |
| Azure OpenAI | GPT-4o deployment | Azure Portal |
| pip | Latest | `pip --version` |

### Local Development (No Azure Infrastructure)

```bash
# Clone the repository
git clone https://github.com/maneeshkumar52/contoso-research-system.git
cd contoso-research-system

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials:
#   AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
#   AZURE_OPENAI_API_KEY=your-api-key
#   AZURE_OPENAI_DEPLOYMENT=gpt-4o
#   LOCAL_MODE=true

# Run the server
uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
```

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

```bash
# Test with a research request
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI Market Analysis", "company_name": "Microsoft"}'
```

### Offline Validation (No Azure OpenAI Needed)

```bash
# Run the demo script to validate models, rules, and local service bus
python demo_e2e.py
```

```
=== Contoso Research System - E2E Demo ===
✓ ResearchRequest model validated
✓ FCA rules loaded (6 rules)
✓ ServiceBusHelper local mode working
✓ SpecialistOutput model validated
=== All validations passed ===
```

### Docker

```bash
cd infra
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

---

## Project Structure

```
contoso-research-system/
├── orchestrator/                    # Pipeline coordination
│   ├── main.py                     # FastAPI app, endpoints, lifespan
│   ├── pipeline.py                 # ResearchPipeline fan-out/gather
│   └── report_store.py            # Cosmos DB + Blob Storage persistence
├── specialists/                    # 5 domain-specific AI analysts
│   ├── base_specialist.py         # ABC with LLM helpers + token tracking
│   ├── financial_analyst.py       # Revenue, margins, valuation analysis
│   ├── market_researcher.py       # TAM/SAM, competitive intelligence
│   ├── news_analyst.py            # Sentiment scoring, event analysis
│   ├── risk_assessor.py           # 7-category risk assessment matrix
│   └── esg_analyst.py             # E/S/G pillar scoring (0-100)
├── synthesiser/                    # Report synthesis
│   ├── agent.py                   # Merges 5 specialist outputs via LLM
│   ├── prompts.py                 # SYNTHESIS_SYSTEM_PROMPT
│   └── report_template.py        # Jinja2 Markdown report formatter
├── compliance_gate/                # FCA regulatory validation
│   ├── agent.py                   # review_compliance() with 6 FCA rules
│   ├── prompts.py                 # COMPLIANCE_SYSTEM_PROMPT
│   └── rules.py                   # FCA_RULES + REQUIRED_DISCLAIMERS
├── shared/                         # Cross-cutting concerns
│   ├── config.py                  # Settings via pydantic-settings
│   ├── models.py                  # All Pydantic domain models
│   ├── service_bus.py             # ServiceBusHelper (Azure + local mode)
│   └── logging_config.py         # structlog JSON configuration
├── tests/                          # Test suite
│   ├── test_specialists.py        # 3 specialist unit tests
│   ├── test_compliance.py         # Approval + rejection scenarios
│   └── test_pipeline_e2e.py       # Full pipeline integration test
├── infra/                          # Deployment
│   ├── Dockerfile                 # python:3.11-slim container
│   ├── docker-compose.yml         # Single-service local compose
│   └── azure-deploy.bicep         # OpenAI + Cosmos + Service Bus
├── .env.example                    # Environment variable template
├── demo_e2e.py                    # Offline validation script
├── requirements.txt               # 15 dependencies with pinned versions
└── pyproject.toml                 # pytest + ruff configuration
```

### Module Responsibility Table

| Module | Files | Responsibility | Key Pattern |
|--------|-------|---------------|-------------|
| `orchestrator` | 3 | API endpoints, pipeline coordination, report persistence | Singleton pipeline via lifespan |
| `specialists` | 6 | Domain-specific LLM analysis with mock data | Template Method (ABC) |
| `synthesiser` | 3 | Merge specialist outputs into unified report | Structured JSON output |
| `compliance_gate` | 3 | FCA regulatory validation with 6 rules | Fail-safe (default reject) |
| `shared` | 4 | Configuration, models, messaging, logging | LRU-cached settings singleton |
| `tests` | 3 | Unit + integration tests with AsyncMock | pytest-asyncio auto mode |
| `infra` | 3 | Docker container + Azure Bicep deployment | Single-service compose |

---

## Configuration Reference

### Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | — | ✅ | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | — | ✅ | Azure OpenAI API key |
| `AZURE_OPENAI_API_VERSION` | `2024-02-01` | — | OpenAI API version |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o` | — | Model deployment name |
| `LOCAL_MODE` | `true` | — | Run without Service Bus (in-process queues) |
| `LOG_LEVEL` | `INFO` | — | Logging level |
| `SERVICE_BUS_CONNECTION_STRING` | `""` | When `LOCAL_MODE=false` | Azure Service Bus connection |
| `SERVICE_BUS_NAMESPACE` | `""` | When `LOCAL_MODE=false` | Service Bus namespace FQDN |
| `COSMOS_ENDPOINT` | `https://your-cosmos...` | For persistence | Cosmos DB endpoint |
| `COSMOS_KEY` | — | For persistence | Cosmos DB access key |
| `COSMOS_DATABASE` | `contoso-research` | — | Database name |
| `COSMOS_REPORTS_CONTAINER` | `research-reports` | — | Container name |
| `STORAGE_ACCOUNT_NAME` | — | For persistence | Blob Storage account |
| `STORAGE_ACCOUNT_KEY` | — | For persistence | Blob Storage key |
| `STORAGE_CONTAINER_NAME` | `research-reports` | — | Blob container name |

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.111.0 | Web framework, API endpoints |
| `uvicorn` | 0.30.0 | ASGI server |
| `openai` | 1.40.0 | Azure OpenAI SDK (AsyncAzureOpenAI) |
| `azure-servicebus` | 7.12.0 | Azure Service Bus pub/sub |
| `azure-cosmos` | 4.7.0 | Cosmos DB document storage |
| `azure-storage-blob` | 12.20.0 | Azure Blob Storage |
| `azure-identity` | 1.16.0 | Azure credential management |
| `pydantic` | 2.7.0 | Data models, validation |
| `pydantic-settings` | 2.3.0 | Configuration from env vars |
| `structlog` | 24.2.0 | Structured JSON logging |
| `python-dotenv` | 1.0.1 | `.env` file loading |
| `jinja2` | 3.1.4 | Report template rendering |
| `httpx` | 0.27.0 | HTTP client (testing) |
| `pytest` | 8.2.0 | Test framework |
| `pytest-asyncio` | 0.23.0 | Async test support |

---

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specialist tests only
pytest tests/test_specialists.py -v

# Compliance tests only
pytest tests/test_compliance.py -v

# Full pipeline integration test
pytest tests/test_pipeline_e2e.py -v
```

### Test Coverage

| Test File | Tests | What's Validated |
|-----------|-------|-----------------|
| `test_specialists.py` | 3 | Financial/ESG/Risk analyst output shape, confidence bounds, findings extraction |
| `test_compliance.py` | 2 | FCA approval (compliant report) + rejection (guaranteed returns language) |
| `test_pipeline_e2e.py` | 1 | End-to-end: 5 specialists → synthesis → compliance → store (all mocked) |

All tests use `unittest.mock.AsyncMock` to mock Azure OpenAI calls. No live API calls during testing.

### Offline Validation

```bash
python demo_e2e.py
```

Validates Pydantic models, FCA rules loading, local ServiceBusHelper, and SpecialistOutput construction without any Azure dependencies.

---

## Error Handling Strategy

| Component | Error Type | Behaviour |
|-----------|-----------|-----------|
| Specialist agent | `asyncio.TimeoutError` (120s) | Log, return `None`, pipeline continues with remaining specialists |
| Specialist agent | General `Exception` | Log, return `None`, pipeline continues |
| All 5 specialists fail | — | `ValueError` raised — pipeline aborts |
| Synthesis LLM call | `Exception` | Returns fallback `SynthesisResult` with aggregated specialist findings |
| Compliance LLM call | `Exception` | Returns `ComplianceResult(approved=False, risk_rating="high")` — fail-safe |
| Cosmos DB write | `Exception` | Logged, does not block Blob write or API response |
| Blob Storage write | `Exception` | Logged, does not block API response |
| Service Bus publish | `Exception` | Raised to caller |
| Service Bus handler | Message processing error | Message dead-lettered |

---

## Deployment

### Docker

```bash
# Build and run
cd infra
docker-compose up --build

# The API is available at http://localhost:8000
# LOCAL_MODE=true is set by default in docker-compose.yml
```

**Dockerfile** (python:3.11-slim):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Azure Bicep Deployment

The `infra/azure-deploy.bicep` template provisions:

| Resource | Azure Service | SKU | Purpose |
|----------|--------------|-----|---------|
| Azure OpenAI | `Microsoft.CognitiveServices/accounts` | S0 | GPT-4o for all 7 LLM calls |
| Cosmos DB | `Microsoft.DocumentDB/databaseAccounts` | Serverless | Structured report storage |
| Service Bus | `Microsoft.ServiceBus/namespaces` | Standard | Async message queue (production) |

```bash
# Deploy Azure infrastructure
az deployment group create \
  --resource-group contoso-research-rg \
  --template-file infra/azure-deploy.bicep \
  --parameters environmentName=prod
```

**Outputs**: `openaiEndpoint`, `cosmosEndpoint`

### Azure Production Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Azure Resource Group                   │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Azure OpenAI │  │  Cosmos DB   │  │ Service Bus  │  │
│  │   (S0)       │  │ (Serverless) │  │ (Standard)   │  │
│  │   GPT-4o     │  │  Reports DB  │  │  Async Queue │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┼──────────────────┘          │
│                           │                              │
│                  ┌────────▼────────┐                     │
│                  │ Container App   │                     │
│                  │ (FastAPI)       │                     │
│                  │ Port 8000       │                     │
│                  └─────────────────┘                     │
│                                                          │
│  ┌──────────────┐                                        │
│  │ Blob Storage │  ← Report JSON archival                │
│  │ (Standard)   │                                        │
│  └──────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

---

## Design Patterns Summary

| # | Pattern | Where | Purpose |
|---|---------|-------|---------|
| 1 | Fan-Out / Gather | `pipeline.py` | 5 concurrent specialists via `asyncio.gather` |
| 2 | Template Method | `base_specialist.py` | ABC skeleton with domain-specific `analyse()` |
| 3 | Strategy | `specialists/*` | Each specialist is a swappable analysis strategy |
| 4 | Pipeline | `pipeline.py → run()` | Sequential phases: fan-out → synthesis → compliance → store |
| 5 | Compliance Gate | `compliance_gate/agent.py` | Post-synthesis regulatory validation |
| 6 | Dual-Write | `report_store.py` | Independent Cosmos DB + Blob writes |
| 7 | Feature Flag | `config.py` → `LOCAL_MODE` | Toggle Azure dependencies for local development |
| 8 | Singleton (LRU) | `config.py` → `get_settings()` | Single Settings instance |
| 9 | Graceful Degradation | `pipeline.py` | Partial specialist failure tolerance |
| 10 | Fail-Safe Default | `compliance_gate/agent.py` | Default reject on compliance failure |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `openai.AuthenticationError` | Invalid Azure OpenAI credentials | Verify `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` in `.env` |
| `openai.NotFoundError` | Wrong deployment name | Check `AZURE_OPENAI_DEPLOYMENT` matches your Azure deployment |
| All specialists timeout | Azure OpenAI rate limiting | Check deployment TPM limits; reduce concurrent requests |
| `ValueError: All specialists failed` | No specialist returned results | Check network connectivity and Azure OpenAI status |
| `ImportError: azure.cosmos` | Missing Azure SDKs | `pip install -r requirements.txt`; or set `LOCAL_MODE=true` |
| Cosmos DB write fails silently | Invalid credentials | Check `COSMOS_ENDPOINT` and `COSMOS_KEY`; Blob write continues |
| Empty `key_findings` in output | LLM response format mismatch | Verify prompt instructs "bullet points starting with '- '" |
| Service Bus not connecting | `LOCAL_MODE=false` but no connection string | Set `LOCAL_MODE=true` for development, or configure Service Bus |
| Docker build fails | Missing `requirements.txt` context | Build from repo root: `docker build -f infra/Dockerfile .` |
| Tests fail with `AsyncMock` | Python < 3.8 | Use Python 3.11+ as specified |

---

## Production Checklist

- [ ] Replace mock data with real data source integrations (Bloomberg API, market data feeds)
- [ ] Add API authentication (OAuth 2.0 / API key middleware)
- [ ] Restrict CORS origins from `["*"]` to specific domains
- [ ] Add rate limiting per client
- [ ] Add non-root `USER` directive in Dockerfile
- [ ] Add Docker health check
- [ ] Replace hardcoded confidence scores with dynamic calibration
- [ ] Add input sanitisation beyond Pydantic type checking
- [ ] Configure Managed Identity instead of connection strings
- [ ] Add Application Insights for telemetry and distributed tracing
- [ ] Set up Cosmos DB backup and restore policies
- [ ] Add circuit breaker for Azure OpenAI calls
- [ ] Configure auto-scaling for Container App instances

---

## License

This project is part of **"Prompt to Production"** by Maneesh Kumar (Chapter 18).

---

<div align="center">

**[⬆ Back to Top](#-contoso-research-system)**

</div>