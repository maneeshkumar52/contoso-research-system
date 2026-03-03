# Contoso Research System

**Chapter 18 of "Prompt to Production" by Maneesh Kumar**

A production-grade multi-agent financial research system demonstrating the fan-out/gather pattern for parallel specialist agent orchestration.

---

## Architecture

```
                        ┌─────────────────────────────────────────────┐
                        │           ResearchRequest (topic, company)   │
                        └────────────────────┬────────────────────────┘
                                             │
                                             ▼
                        ┌─────────────────────────────────────────────┐
                        │              Orchestrator / Pipeline         │
                        │         (orchestrator/pipeline.py)           │
                        └──────────────────┬──────────────────────────┘
                                           │ Fan-out (asyncio.gather)
               ┌──────────┬───────────────┼───────────────┬──────────┐
               ▼          ▼               ▼               ▼          ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
        │Financial │ │  Market  │ │  News    │ │  Risk    │ │   ESG    │
        │ Analyst  │ │Researcher│ │ Analyst  │ │Assessor  │ │ Analyst  │
        └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
             └────────────┴────────────┴─────────────┴────────────┘
                                        │ Gather (SpecialistOutput x5)
                                        ▼
                        ┌─────────────────────────────────────────────┐
                        │              Synthesiser Agent               │
                        │       (synthesiser/agent.py)                 │
                        │  Produces: executive summary, findings,      │
                        │           recommendations                    │
                        └────────────────────┬────────────────────────┘
                                             │
                                             ▼
                        ┌─────────────────────────────────────────────┐
                        │            Compliance Gate Agent             │
                        │        (compliance_gate/agent.py)            │
                        │  FCA rules check → approved / issues         │
                        └────────────────────┬────────────────────────┘
                                             │
                                             ▼
                        ┌─────────────────────────────────────────────┐
                        │              Report Store                    │
                        │   Cosmos DB + Azure Blob Storage             │
                        └─────────────────────────────────────────────┘
```

---

## Agent Descriptions

### Specialist Agents (run in parallel)

| Agent | Module | Purpose |
|-------|--------|---------|
| Financial Analyst | `specialists/financial_analyst.py` | Revenue, margins, valuation multiples, cash flow, ROE/ROIC |
| Market Researcher | `specialists/market_researcher.py` | TAM/SAM, competitive landscape, NPS, geographic revenue split |
| News Analyst | `specialists/news_analyst.py` | Sentiment scoring, headline events, regulatory developments |
| Risk Assessor | `specialists/risk_assessor.py` | Risk registry (probability x impact), cyber, regulatory, FX, operational |
| ESG Analyst | `specialists/esg_analyst.py` | E/S/G scores, carbon emissions, board governance, diversity metrics |

### Synthesiser Agent
Receives all 5 specialist outputs and produces a unified JSON report with executive summary, key findings, risk factors, and strategic recommendations.

### Compliance Gate Agent
Reviews the synthesised report against 6 FCA rules (FCA-001 through FCA-006) and determines approval status, risk rating, and required disclaimers.

---

## LOCAL_MODE

When `LOCAL_MODE=true` (default), the system:
- Runs entirely in-process without requiring Azure Service Bus
- Uses mock financial/market/ESG data for specialist context
- Still calls Azure OpenAI for LLM inference
- Storage calls (Cosmos DB, Blob) are attempted but silently caught on failure

This allows full local development with only an Azure OpenAI endpoint required.

---

## Prerequisites

For full production deployment you need:

- **Azure OpenAI** — GPT-4o deployment
- **Azure Service Bus** — Standard tier namespace (optional with LOCAL_MODE)
- **Azure Cosmos DB** — Serverless account, database: `contoso-research`, container: `research-reports`
- **Azure Blob Storage** — Container: `research-reports`
- Python 3.11+

---

## Setup

### 1. Clone and install dependencies

```bash
cd contoso-research-system
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials at minimum:
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_API_KEY=your-key
# AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

### 3. Run the API server

```bash
uvicorn orchestrator.main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy", "service": "contoso-research-system", "version": "1.0.0"}
```

### Start a Research Pipeline

```bash
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Contoso Financial Q4 2024 Analysis",
    "company_name": "Contoso Financial plc",
    "date_range": "last 12 months",
    "requested_by": "portfolio-manager-01"
  }'
```

### Sample Response Structure

```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "report": {
    "run_id": "550e8400-e29b-41d4-a716-446655440000",
    "topic": "Contoso Financial Q4 2024 Analysis",
    "company_name": "Contoso Financial plc",
    "synthesis": {
      "executive_summary": "Contoso Financial plc demonstrates strong financial performance...",
      "key_findings": [
        "Revenue grew 7.2% YoY to £2.4B, beating consensus by 120bps",
        "Gross margins expanded 80bps to 42.3%, driven by product mix shift",
        "ESG composite score of 72.7 places company in sector top quartile",
        "Cyber risk and ongoing regulatory review represent key near-term risks",
        "News sentiment broadly positive (avg 0.36) with AI investment well-received"
      ],
      "risk_factors": [
        "Ongoing FCA data practices review with uncertain timeline and outcome",
        "Currency exposure on 45% of international revenue — 50% hedging leaves meaningful gap",
        "CFO transition introduces operational continuity risk in FY2025"
      ],
      "recommendations": [
        "Maintain overweight position given strong cash generation and expanding margins",
        "Monitor Q1 2025 regulatory correspondence for resolution of data practices review",
        "Engage management on currency hedging strategy at next investor day",
        "Revisit ESG social score trajectory — gender diversity in leadership below sector median"
      ],
      "total_specialist_time": 18.4
    },
    "compliance": {
      "approved": true,
      "issues": [],
      "required_disclaimers": [
        "This research report is produced for informational purposes only...",
        "Past performance is not indicative of future results..."
      ],
      "risk_rating": "low"
    },
    "created_at": "2024-11-28T14:32:10.123456",
    "total_pipeline_time": 22.7,
    "status": "completed"
  }
}
```

### Retrieve a Report by Run ID

```bash
curl http://localhost:8000/api/v1/report/550e8400-e29b-41d4-a716-446655440000
```

### Check Pipeline Status

```bash
curl http://localhost:8000/api/v1/status/550e8400-e29b-41d4-a716-446655440000
```

---

## Running with Docker Compose

```bash
# Build and start
docker compose -f infra/docker-compose.yml up --build

# The API will be available at http://localhost:8000
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use mocked OpenAI responses and do not require live Azure credentials.

---

## Azure Deployment

```bash
# Deploy infrastructure
az deployment group create \
  --resource-group rg-research \
  --template-file infra/azure-deploy.bicep \
  --parameters environmentName=prod

# Build and push container
az acr build --registry yourregistry --image contoso-research:latest .

# Deploy to Azure Container Apps or AKS
```

---

## Project Structure

```
contoso-research-system/
├── shared/                  # Shared config, models, logging, service bus
├── specialists/             # Five parallel analyst agents
├── synthesiser/             # Report synthesis agent
├── compliance_gate/         # FCA compliance review agent
├── orchestrator/            # FastAPI app, pipeline, report storage
├── tests/                   # Unit and E2E tests
├── infra/                   # Docker, docker-compose, Bicep IaC
├── .env.example
├── requirements.txt
└── pyproject.toml
```

---

## Book Reference

This system is the complete implementation for **Chapter 18: Production Multi-Agent Systems** of:

> **"Prompt to Production: Engineering Agentic AI Systems"**
> by Maneesh Kumar
>
> The chapter covers:
> - Fan-out/gather pattern for parallel specialist agents
> - Structured output validation with Pydantic
> - Compliance gates in agentic pipelines
> - Azure Service Bus for reliable agent communication
> - Production observability with structured logging

---

*Contoso Research Services Limited is a fictional company used for demonstration purposes.*
