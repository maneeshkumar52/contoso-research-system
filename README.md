# Contoso Research System

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

Multi-agent research intelligence platform with 5 specialist analysts (financial, market, news, risk, ESG), fan-out/gather orchestration, compliance gating, and synthesis — powered by Azure OpenAI, Cosmos DB, and Service Bus.

## Architecture

```
ResearchRequest
        │
        ▼
┌──────────────────────────────────────────┐
│  ResearchPipeline (orchestrator)         │
│                                          │
│  Fan-Out (5 specialists in parallel):    │
│       ├──► FinancialAnalyst             │
│       ├──► MarketResearcher             │
│       ├──► NewsAnalyst                  │
│       ├──► RiskAssessor                 │
│       └──► ESGAnalyst                   │
│       │                                  │
│  Gather ──► Timeout handling (120s)     │
│       │                                  │
│  Synthesiser ──► Unified report         │
│       │                                  │
│  ComplianceGate ──► Rules + prompts     │
│       │                                  │
│  ReportStore ──► Cosmos DB              │
└──────────────────────────────────────────┘
        │
        ▼
FinalReport (JSON + formatted template)
```

## Key Features

- **5 Specialist Agents** — Financial, market, news, risk, and ESG analysts run concurrently
- **Fan-Out/Gather Pattern** — `asyncio.gather` with 120-second timeout per specialist
- **Compliance Gate** — Rule-based + LLM validation with dedicated rules engine and prompts
- **Synthesiser** — Merges specialist outputs into a unified report with structured prompt engineering
- **Report Template** — `report_template.py` formats final output for executive consumption
- **Report Store** — Persists completed reports to Cosmos DB via `store_report()`
- **Service Bus Integration** — Async event-driven processing via Azure Service Bus

## Step-by-Step Flow

### Step 1: Research Request
User submits a `ResearchRequest` with topic, scope, and parameters via `POST /research`.

### Step 2: Fan-Out
`ResearchPipeline` launches all 5 specialists concurrently with `asyncio.gather`, each producing a `SpecialistOutput`.

### Step 3: Gather
Results collected with timeout handling. Failed specialists logged; pipeline continues with available outputs.

### Step 4: Synthesis
`synthesise()` combines all specialist outputs into a `SynthesisResult` using structured prompts.

### Step 5: Compliance Review
`review_compliance()` validates the synthesis against compliance rules and LLM-based checks.

### Step 6: Store & Respond
`store_report()` persists the `FinalReport` to Cosmos DB. Client receives the complete report.

## Repository Structure

```
contoso-research-system/
├── orchestrator/
│   ├── main.py              # FastAPI entry point
│   ├── pipeline.py           # ResearchPipeline — fan-out/gather
│   └── report_store.py       # Cosmos DB persistence
├── specialists/
│   ├── base_specialist.py    # BaseSpecialist ABC
│   ├── financial_analyst.py
│   ├── market_researcher.py
│   ├── news_analyst.py
│   ├── risk_assessor.py
│   └── esg_analyst.py
├── synthesiser/
│   ├── agent.py              # synthesise()
│   ├── prompts.py
│   └── report_template.py
├── compliance_gate/
│   ├── agent.py              # review_compliance()
│   ├── rules.py
│   └── prompts.py
├── shared/
│   ├── config.py, models.py, service_bus.py, logging_config.py
├── tests/
│   ├── test_specialists.py, test_compliance.py, test_pipeline_e2e.py
├── demo_e2e.py
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
git clone https://github.com/maneeshkumar52/contoso-research-system.git
cd contoso-research-system
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

```bash
pytest -q
python demo_e2e.py
```

## License

MIT
