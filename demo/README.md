# Demo Data

This folder contains sample data for demonstrating the Invoice LangGraph Agent.

## 📁 Structure

```
demo/
├── sample_invoices/        # Invoice payloads for testing
│   ├── invoice_matched.json    # Happy path - passes 2-way matching
│   ├── invoice_failed.json     # HITL path - fails matching, needs review
│   └── invoice_edge_cases.json # Various edge case scenarios
│
├── mock_data/              # Mock ERP/backend data
│   ├── purchase_orders.json    # Sample POs for matching
│   ├── grns.json               # Goods Received Notes
│   ├── vendors.json            # Vendor profiles with enrichment data
│   └── historical_invoices.json # Past invoice history
│
└── screenshots/            # Demo video screenshots (add during recording)
    └── .gitkeep
```

## 🎬 Demo Scenarios

### Scenario 1: Happy Path (Invoice Matches)

Use `invoice_matched.json`:
- Invoice: INV-2024-001 from Acme Corporation
- Amount: $15,000.00
- Matches PO-2024-001 exactly
- **Flow**: INTAKE → UNDERSTAND → PREPARE → RETRIEVE → MATCH (PASS) → RECONCILE → APPROVE → POSTING → NOTIFY → COMPLETE

```bash
curl -X POST http://localhost:8000/api/v1/invoke \
  -H "Content-Type: application/json" \
  -d @demo/sample_invoices/invoice_matched.json
```

### Scenario 2: HITL Path (Invoice Fails Matching)

Use `invoice_failed.json`:
- Invoice: INV-2024-002 from Unknown Vendor LLC
- Amount: $75,000.00
- No matching PO, high amount, unknown vendor
- **Flow**: INTAKE → UNDERSTAND → PREPARE → RETRIEVE → MATCH (FAIL) → CHECKPOINT_HITL (PAUSE)
- Requires human review to ACCEPT or REJECT

```bash
# Start workflow (will pause at checkpoint)
curl -X POST http://localhost:8000/api/v1/invoke \
  -H "Content-Type: application/json" \
  -d @demo/sample_invoices/invoice_failed.json

# Check pending reviews
curl http://localhost:8000/api/v1/human-review/pending

# Accept the invoice
curl -X POST http://localhost:8000/api/v1/human-review/decision \
  -H "Content-Type: application/json" \
  -d '{
    "checkpoint_id": "<checkpoint_id>",
    "decision": "ACCEPT",
    "reviewer_id": "reviewer_001",
    "notes": "Approved after verification"
  }'
```

### Scenario 3: Edge Cases

Use test cases from `invoice_edge_cases.json`:

| Test Case | Description | Expected Behavior |
|-----------|-------------|-------------------|
| Missing Tax ID | Vendor has no tax ID | Flags missing_info, continues |
| Within Tolerance | 3.3% difference from PO | Passes matching (5% tolerance) |
| Outside Tolerance | 33% difference | Fails, triggers HITL |
| High Risk Vendor | New vendor, $100K invoice | High risk score, escalated approval |
| Foreign Currency | EUR invoice | Currency conversion before match |

## 📊 Mock Data Details

### Purchase Orders (5 POs)

| PO ID | Vendor | Amount | Status |
|-------|--------|--------|--------|
| PO-2024-001 | Acme Corporation | $15,000 | APPROVED |
| PO-2024-002 | Global Parts Ltd | $32,500 | APPROVED |
| PO-2024-003 | Euro Supplies GmbH | €8,500 | APPROVED |
| PO-2024-004 | TechSupply Inc | $5,000 | APPROVED |
| PO-2024-005 | Premium Services Co | $25,000 | PENDING |

### Vendors (5 vendors)

| Vendor | Tax ID | Status | Risk |
|--------|--------|--------|------|
| Acme Corporation | 12-3456789 | ACTIVE | LOW |
| Global Parts Ltd | 98-7654321 | ACTIVE | LOW |
| Euro Supplies GmbH | DE123456789 | ACTIVE | LOW |
| TechSupply Inc | (missing) | ACTIVE | MEDIUM |
| Unknown Vendor LLC | (missing) | PENDING | HIGH |

### GRNs (4 receipts)

All linked to corresponding POs with receipt details and inspection status.

### Historical Invoices (10 invoices)

Past invoices from the last quarter showing payment patterns and averages.

## 🔧 Using in Tests

```python
import json

# Load sample invoice
with open("demo/sample_invoices/invoice_matched.json") as f:
    invoice = json.load(f)

# Load mock POs
with open("demo/mock_data/purchase_orders.json") as f:
    pos = json.load(f)["purchase_orders"]
```

## 📸 Screenshots

Add screenshots during demo video recording:
- `dashboard.png` - Main dashboard with workflow overview
- `workflow-detail.png` - Workflow detail page with stage progress
- `human-review.png` - Human review queue and decision UI
- `logs-viewer.png` - Real-time execution logs

