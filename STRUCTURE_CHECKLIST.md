## Invoice LangGraph - Structure & Config Checklist

This file helps you quickly verify that the repo matches the intended scaffolding from the spec.

### Root

- [x] `README.md` – Project overview + setup
- [x] `Makefile` – Dev, setup, db, test, lint, demo, docker targets
- [x] `.gitignore` – Python, Node, env, demo artifacts, docker override
- [x] `docker-compose.yml` – Backend (8000) + Frontend (3000) services
- [x] `backend/`
- [x] `frontend/`
- [x] `demo/`
- [x] `docs/`
- [x] `scripts/`

### Backend

- [x] `backend/pyproject.toml` – uv project config (Python 3.11, deps, ruff, pytest)
- [x] `backend/requirements.txt` – Mirrors `pyproject` runtime + dev deps
- [x] `backend/workflow.json` – Workflow config (12-stage pipeline)
- [x] `backend/app/main.py` – FastAPI entrypoint
- [x] `backend/app/config.py` – Settings + workflow config loading
- [x] `backend/app/api/` – `router.py`, `invoke.py`, `workflows.py`, `human_review.py`, `logs.py`
- [x] `backend/app/graph/` – `state.py`, `builder.py`, `routing.py`, `nodes/` (12 stages)
- [x] `backend/app/bigtool/` – `base.py`, `picker.py`, `registry.py`, `tools/` subpackages
- [x] `backend/app/mcp/` – `router.py`, `base.py`, `common_server.py`, `atlas_server.py`
- [x] `backend/app/db/` – `database.py`, `models.py`, `checkpoint_store.py`
- [x] `backend/app/schemas/` – `invoice.py`, `workflow.py`, `human_review.py`, `logs.py`
- [x] `backend/app/services/` – `workflow_service.py`, `review_service.py`, `log_service.py`
- [x] `backend/app/utils/` – `logger.py`, `exceptions.py`, `helpers.py`
- [x] `backend/tests/` – `test_api/`, `test_graph/`, `test_bigtool/`, `test_mcp/`

> Note: Example env files (like `backend/.env.example`) may not be present if your environment blocks writing `.env*` files; you can safely create them manually from the spec if needed.

### Frontend

- [x] `frontend/package.json` – Next 14, React 18, shadcn/ui, TanStack Query, tooling
- [x] `frontend/tailwind.config.ts` – App Router paths + stage color tokens
- [x] `frontend/components.json` – shadcn/ui config with aliases
- [x] `frontend/app/` – `layout.tsx`, `page.tsx`, `globals.css`, `error.tsx`, `loading.tsx`
- [x] `frontend/app/invoke/` – `page.tsx`, `loading.tsx`
- [x] `frontend/app/workflows/` – list + `[id]/` detail + loading states
- [x] `frontend/app/review/` – queue + `[checkpointId]/` detail + loading states
- [x] `frontend/components/ui/` – shadcn primitives (button, card, table, dialog, etc.)
- [x] `frontend/components/layout/` – `sidebar.tsx`, `header.tsx`, `nav-item.tsx`, `providers.tsx`
- [x] `frontend/components/dashboard/` – stats, recent workflows, pending reviews, system health
- [x] `frontend/components/invoice/` – form, line items editor, upload, preview
- [x] `frontend/components/workflow/` – table, cards, detail, stage progress, logs viewer
- [x] `frontend/components/review/` – queue, detail, comparison, decision dialog, notes
- [x] `frontend/components/common/` – page header, empty/error state, JSON viewer, timestamp, copy
- [x] `frontend/lib/` – `api.ts`, `api-client.ts`, `types.ts`, `constants.ts`, `utils.ts`, `sse.ts`
- [x] `frontend/hooks/` – `use-invoke`, `use-workflows`, `use-workflow-logs`, `use-reviews`, `use-decision`, `use-stats`
- [x] `frontend/styles/themes.css` – theme variables (optional)

### Demo & Docs

- [x] `demo/sample_invoices/` – `invoice_matched.json`, `invoice_failed.json`, `invoice_edge_cases.json`
- [x] `demo/mock_data/` – `purchase_orders.json`, `grns.json`, `vendors.json`, `historical_invoices.json`
- [x] `demo/screenshots/` – `dashboard.png`, `workflow-detail.png`, `human-review.png`, `logs-viewer.png`
- [x] `docs/ARCHITECTURE.md`
- [x] `docs/API.md`
- [x] `docs/HITL_FLOW.md`
- [x] `docs/BIGTOOL.md`
- [x] `docs/DEMO_SCRIPT.md`

### Scripts

- [x] `scripts/init_db.py` – Initialize database tables
- [x] `scripts/seed_data.py` – Seed demo data
- [x] `scripts/run_demo.py` – End-to-end demo scenario

If any box you expect to be `[x]` is missing, compare against the original scaffold spec and create/copy the missing file or directory. 

