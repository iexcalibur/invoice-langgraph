# Architecture Documentation

## Invoice LangGraph Agent - System Architecture

### Overview

The Invoice LangGraph Agent is a production-grade invoice processing system built using LangGraph for workflow orchestration. It implements a 12-stage pipeline with Human-in-the-Loop (HITL) capabilities, MCP (Model Context Protocol) integration, and dynamic tool selection via Bigtool.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                         Next.js 14 (App Router)                             ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    ││
│  │  │  Dashboard   │  │   Invoke     │  │  Workflows   │  │Human Review  │    ││
│  │  │    Page      │  │    Page      │  │    Pages     │  │    Pages     │    ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ HTTP/SSE
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 API LAYER                                        │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                            FastAPI 0.115+                                   ││
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    ││
│  │  │POST /invoke│  │GET /status │  │GET /reviews│  │POST /review/decision│   ││
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘    ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            ORCHESTRATION LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                          LangGraph 0.2+ Engine                              ││
│  │                                                                             ││
│  │   INTAKE → UNDERSTAND → PREPARE → RETRIEVE → MATCH ──┬──→ RECONCILE        ││
│  │                                                       │        ↓            ││
│  │                                              [FAILED] │     APPROVE         ││
│  │                                                       ↓        ↓            ││
│  │                                              CHECKPOINT → HITL → POSTING    ││
│  │                                                                    ↓        ││
│  │                                                               NOTIFY        ││
│  │                                                                    ↓        ││
│  │                                                               COMPLETE      ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
┌────────────────────┐    ┌──────────────────────────┐    ┌────────────────────┐
│   BIGTOOL LAYER    │    │       MCP LAYER          │    │    DATA LAYER      │
│  ┌──────────────┐  │    │  ┌────────────────────┐  │    │  ┌──────────────┐  │
│  │ Tool Pools   │  │    │  │  COMMON Server     │  │    │  │   SQLite     │  │
│  │ - OCR        │  │    │  │  (Internal Ops)    │  │    │  │   demo.db    │  │
│  │ - Enrichment │  │    │  └────────────────────┘  │    │  └──────────────┘  │
│  │ - ERP        │  │    │  ┌────────────────────┐  │    │                    │
│  │ - Email      │  │    │  │  ATLAS Server      │  │    │                    │
│  │ - Storage    │  │    │  │  (External APIs)   │  │    │                    │
│  └──────────────┘  │    │  └────────────────────┘  │    │                    │
└────────────────────┘    └──────────────────────────┘    └────────────────────┘
```

---

## Component Details

### 1. Presentation Layer (Frontend)

**Technology:** Next.js 14 with App Router

**Key Features:**
- Server-side rendering for initial page load
- Client-side navigation for SPA experience
- Real-time updates via TanStack Query
- SSE (Server-Sent Events) for live log streaming

**Pages:**
| Route | Purpose |
|-------|---------|
| `/` | Dashboard with stats and recent activity |
| `/invoke` | Invoice submission form |
| `/workflows` | List all workflows |
| `/workflows/[id]` | Workflow detail with live logs |
| `/review` | Human review queue |
| `/review/[checkpointId]` | Review decision interface |

---

### 2. API Layer (Backend)

**Technology:** FastAPI 0.115+

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/invoke` | Start invoice processing |
| POST | `/api/v1/invoke/sync` | Start and wait for completion |
| GET | `/api/v1/workflows` | List all workflows |
| GET | `/api/v1/workflows/{id}` | Get workflow details |
| GET | `/api/v1/workflows/{id}/state` | Get full workflow state |
| GET | `/api/v1/human-review/pending` | List pending reviews |
| GET | `/api/v1/human-review/{checkpointId}` | Get review details |
| POST | `/api/v1/human-review/decision` | Submit review decision |
| GET | `/api/v1/logs/{workflowId}` | Get workflow logs |
| GET | `/api/v1/logs/{workflowId}/stream` | Stream logs via SSE |

---

### 3. Orchestration Layer (LangGraph)

**Technology:** LangGraph 0.2+

**State Management:**
- `InvoiceState` TypedDict maintains all workflow variables
- State persists across nodes via LangGraph's native mechanism
- Checkpoints saved to SQLite for HITL resume

**12-Stage Pipeline:**

| Stage | Mode | Server | Description |
|-------|------|--------|-------------|
| INTAKE | Deterministic | COMMON | Validate and persist invoice |
| UNDERSTAND | Deterministic | ATLAS | OCR and parse invoice |
| PREPARE | Deterministic | COMMON+ATLAS | Normalize and enrich vendor |
| RETRIEVE | Deterministic | ATLAS | Fetch PO/GRN from ERP |
| MATCH_TWO_WAY | Deterministic | COMMON | Compute match score |
| CHECKPOINT_HITL | Deterministic | COMMON | Create checkpoint if match fails |
| HITL_DECISION | Non-Deterministic | ATLAS | Process human decision |
| RECONCILE | Deterministic | COMMON | Build accounting entries |
| APPROVE | Deterministic | COMMON | Apply approval policy |
| POSTING | Deterministic | ATLAS | Post to ERP |
| NOTIFY | Deterministic | ATLAS | Send notifications |
| COMPLETE | Deterministic | COMMON | Finalize workflow |

**Conditional Routing:**
```
MATCH_TWO_WAY
    │
    ├── match_score >= 0.90 → RECONCILE (skip HITL)
    │
    └── match_score < 0.90 → CHECKPOINT_HITL → HITL_DECISION
                                                    │
                                                    ├── ACCEPT → RECONCILE
                                                    │
                                                    └── REJECT → COMPLETE (MANUAL_HANDOFF)
```

---

### 4. MCP Layer

**Purpose:** Route abilities to appropriate servers

**COMMON Server (Internal Operations):**
- `validate_schema` - Validate invoice payload
- `parse_line_items` - Parse invoice line items
- `normalize_vendor` - Normalize vendor name
- `compute_flags` - Compute validation flags
- `compute_match_score` - Two-way matching
- `save_checkpoint` - Persist checkpoint
- `build_accounting_entries` - Create journal entries
- `apply_approval_policy` - Approval logic
- `output_final_payload` - Finalize output

**ATLAS Server (External Integrations):**
- `ocr_extract` - OCR via Google Vision/Tesseract/Textract
- `enrich_vendor` - Vendor enrichment via Clearbit/PDL
- `fetch_po` - Fetch POs from ERP
- `fetch_grn` - Fetch GRNs from ERP
- `fetch_history` - Historical invoices
- `post_to_erp` - Post journal entries
- `schedule_payment` - Schedule payment
- `notify_vendor` - Email vendor
- `notify_finance_team` - Email finance team

---

### 5. Bigtool Layer

**Purpose:** Dynamic tool selection from pools

**Tool Pools:**

| Capability | Available Tools | Selection Logic |
|------------|-----------------|-----------------|
| OCR | google_vision, tesseract, aws_textract | Document type based |
| Enrichment | clearbit, people_data_labs, vendor_db | Entity type based |
| ERP Connector | sap_sandbox, netsuite, mock_erp | Environment based |
| DB | postgres, sqlite, dynamodb | Environment based |
| Email | sendgrid, smartlead, ses | Volume based |
| Storage | s3, gcs, local_fs | Size based |

**Selection Algorithm:**
1. Rule-based selection (primary)
2. Context-aware adjustments
3. LLM fallback (optional, for complex decisions)

---

### 6. Data Layer

**Technology:** SQLite + SQLAlchemy 2.0

**Models:**

| Model | Purpose |
|-------|---------|
| `Invoice` | Raw invoice data |
| `Workflow` | Workflow execution state |
| `Checkpoint` | HITL checkpoint data |
| `HumanReview` | Review queue entries |
| `AuditLog` | Audit trail |

**Relationships:**
```
Invoice (1) ──── (N) Workflow
Workflow (1) ──── (N) Checkpoint
Workflow (1) ──── (N) AuditLog
Checkpoint (1) ──── (1) HumanReview
```

---

## Data Flow

### Happy Path (Match Succeeds)

```
Invoice JSON
    │
    ▼
┌─────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐   ┌─────────┐
│ INTAKE  │ → │UNDERSTAND│ → │ PREPARE │ → │ RETRIEVE │ → │  MATCH  │
└─────────┘   └──────────┘   └─────────┘   └──────────┘   └────┬────┘
                                                               │
                                              match_score ≥ 0.90
                                                               │
                                                               ▼
┌──────────┐   ┌────────┐   ┌─────────┐   ┌─────────┐   ┌───────────┐
│ COMPLETE │ ← │ NOTIFY │ ← │ POSTING │ ← │ APPROVE │ ← │ RECONCILE │
└──────────┘   └────────┘   └─────────┘   └─────────┘   └───────────┘
    │
    ▼
Final Payload (status: COMPLETED)
```

### HITL Path (Match Fails)

```
Invoice JSON
    │
    ▼
INTAKE → UNDERSTAND → PREPARE → RETRIEVE → MATCH
                                              │
                                 match_score < 0.90
                                              │
                                              ▼
                                     ┌──────────────┐
                                     │  CHECKPOINT  │
                                     │   (Pause)    │
                                     └──────┬───────┘
                                            │
                         Save to DB, create review_url
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ HITL_DECISION │
                                    │ (Await Human) │
                                    └───────┬───────┘
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               │                                                         │
          ACCEPT                                                    REJECT
               │                                                         │
               ▼                                                         ▼
RECONCILE → APPROVE → POSTING → NOTIFY → COMPLETE              COMPLETE
                                            │                  (MANUAL_HANDOFF)
                                            ▼
                               Final Payload (COMPLETED)
```

---

## Security Considerations

1. **Input Validation:** Pydantic schemas validate all inputs
2. **CORS:** Configured for frontend origin only
3. **Error Handling:** Global exception handlers prevent info leakage
4. **Audit Logging:** All operations logged for compliance

---

## Scalability

**Current Design (Demo):**
- Single-process FastAPI
- SQLite database
- Synchronous workflow execution

**Production Recommendations:**
- Deploy with Uvicorn workers + Gunicorn
- Use PostgreSQL for persistence
- Add Redis for caching and task queues
- Implement async workflow execution with Celery/RQ
- Add Kubernetes for horizontal scaling
