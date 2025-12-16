# Invoice LangGraph Agent

**The Autonomous Invoice Agent. Intelligent processing with human control.**

Automate the messy 90% with AI, and handle the critical 10% with seamless Human-in-the-Loop checkpoints.

---

## 🚀 Quick Overview

A production-grade invoice processing system built with LangGraph that orchestrates a 12-stage pipeline with Human-in-the-Loop (HITL) support, MCP integration, and dynamic tool selection via Bigtool.

### Key Features

- **12-Stage Pipeline**: Automated invoice processing from intake to completion
- **Human-in-the-Loop**: Smart checkpoints for manual review when matching fails
- **Real-time Tracking**: Live workflow monitoring with SSE streaming logs
- **MCP Integration**: Route abilities to COMMON (internal) and ATLAS (external) servers
- **Bigtool Selection**: Dynamic tool selection from pools (OCR, Enrichment, ERP, DB, Email, Storage)
- **Modern UI**: Dark-themed, responsive Next.js interface

---

## 📋 Tech Stack

### Backend
- **LangGraph 0.2+** - Workflow orchestration
- **FastAPI 0.115+** - REST API
- **SQLite + SQLAlchemy 2.0** - Database
- **Pydantic 2.9+** - Validation
- **Loguru** - Structured logging

### Frontend
- **Next.js 14+** (App Router)
- **TypeScript 5+**
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **TanStack Query 5+** - Data fetching

---

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+ (includes npm)

### Setup

```bash
# Clone repository
git clone https://github.com/iexcalibur/invoice-langgraph.git
cd invoice-langgraph

# Setup both backend and frontend
make setup

# Or setup individually
make setup-backend
make setup-frontend
```

### Environment Variables (Optional)

For LLM fallback in Bigtool selection, create `backend/.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Note:** The system works without Claude API key using rule-based tool selection. The LLM fallback is only used when rule-based selection fails.

### Run Development Servers

```bash
# Run both backend and frontend together
make dev

# Or run separately:
# Terminal 1: Backend (port 8000)
make backend

# Terminal 2: Frontend (port 3000)
make frontend
```

**Access:**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health

### Database Setup

```bash
# Initialize database
make db-init

# Seed demo data
make seed

# Reset database
make db-reset
```

---

## 📁 Project Structure

```
invoice-langgraph/
├── backend/          # FastAPI + LangGraph backend
│   ├── app/         # Application code
│   │   ├── bigtool/ # Dynamic tool selection system
│   │   ├── db/      # Database models
│   │   ├── graph/   # LangGraph workflow definition
│   │   ├── mcp/     # MCP client integration
│   │   └── api/     # FastAPI routes
│   └── tests/       # Test suite
├── frontend/         # Next.js frontend
│   ├── app/         # App Router pages
│   ├── components/  # React components
│   └── lib/         # Utilities and API client
├── demo/            # Sample invoices and mock data
└── docs/             # Comprehensive documentation
```

---

## 🎬 Demo Scenarios

### Happy Path (Invoice Matches)
```bash
curl -X POST http://localhost:8000/api/v1/invoke \
  -H "Content-Type: application/json" \
  -d @demo/sample_invoices/invoice_matched.json
```

### HITL Path (Invoice Fails Matching)
```bash
curl -X POST http://localhost:8000/api/v1/invoke \
  -H "Content-Type: application/json" \
  -d @demo/sample_invoices/invoice_failed.json
```

See [`demo/README.md`](demo/README.md) for more scenarios and sample data.

---

## 📚 Documentation

For in-depth explanations, architecture details, API reference, and implementation guides, please refer to the comprehensive documentation in the [`docs/`](docs/) folder:

### Core Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - Complete system architecture, component details, data flow diagrams, and scalability considerations
  - High-level architecture overview
  - Component breakdown (Presentation, API, Orchestration, MCP, Bigtool, Data layers)
  - 12-stage pipeline explanation
  - Data flow scenarios (Happy Path & HITL Path)
  - Security and scalability notes

- **[API Reference](docs/API.md)** - Complete REST API documentation with request/response examples
  - All endpoints with detailed specifications
  - Request/response schemas
  - Status codes and error handling
  - Workflow status values
  - Rate limiting guidelines

- **[HITL Flow](docs/HITL_FLOW.md)** - Human-in-the-Loop workflow documentation
  - When HITL is triggered (matching thresholds)
  - Complete HITL flow diagram
  - Database schema for checkpoints and reviews
  - API contract for review operations
  - State persistence and resume logic
  - Configuration options

- **[Bigtool](docs/BIGTOOL.md)** - Dynamic tool selection system documentation
  - Tool pools (OCR, Enrichment, ERP, DB, Email, Storage)
  - Selection algorithms (rule-based and LLM fallback)
  - Usage examples and best practices
  - Configuration and logging

- **[Demo Script](docs/DEMO_SCRIPT.md)** - Step-by-step demo guide for presentations
  - 5-minute demo script
  - Happy path and HITL scenarios
  - Technical points to emphasize
  - Fallback plans and recording tips

### Quick Links

| Topic | Documentation |
|-------|--------------|
| System Design | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| API Endpoints | [`docs/API.md`](docs/API.md) |
| Human Review Flow | [`docs/HITL_FLOW.md`](docs/HITL_FLOW.md) |
| Tool Selection | [`docs/BIGTOOL.md`](docs/BIGTOOL.md) |
| Demo Guide | [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) |
| Sample Data | [`demo/README.md`](demo/README.md) |

---

## 🧪 Testing

```bash
# Run all tests
make test

# Backend tests only
make test-backend

# Linting
make lint
```

---

## 🔧 Available Commands

```bash
# Setup
make setup              # Setup both backend and frontend
make setup-backend      # Setup backend only
make setup-frontend     # Setup frontend only

# Development
make dev                # Run both servers concurrently
make backend            # Run backend only
make frontend           # Run frontend only

# Database
make db-init            # Initialize database tables
make db-reset           # Reset database (drop all tables)
make seed               # Seed demo data

# Testing & Quality
make test               # Run all tests
make test-backend       # Run backend tests only
make lint               # Run linters

# Cleanup
make clean              # Remove all generated files
make git-clean-pyc      # Remove Python cache files from git tracking
```

---

## 🎯 Workflow Stages

The system processes invoices through 12 stages:

1. **INTAKE** - Validate and persist invoice
2. **UNDERSTAND** - OCR and parse invoice
3. **PREPARE** - Normalize and enrich vendor
4. **RETRIEVE** - Fetch PO/GRN from ERP
5. **MATCH_TWO_WAY** - Compute match score
6. **CHECKPOINT_HITL** - Create checkpoint if match fails
7. **HITL_DECISION** - Process human decision
8. **RECONCILE** - Build accounting entries
9. **APPROVE** - Apply approval policy
10. **POSTING** - Post to ERP
11. **NOTIFY** - Send notifications
12. **COMPLETE** - Finalize workflow

For detailed stage descriptions and routing logic, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).


---

**Status**: ✅ Ready for Demo

For detailed implementation guides, architecture decisions, and API specifications, please refer to the [`docs/`](docs/) folder.
