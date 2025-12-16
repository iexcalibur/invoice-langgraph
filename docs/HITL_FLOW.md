# Human-in-the-Loop (HITL) Flow Documentation

## Overview

The Human-in-the-Loop (HITL) flow enables human intervention when automated invoice matching fails. This ensures that invoices requiring judgment are reviewed by humans before being processed further.

---

## When HITL is Triggered

HITL is triggered when the two-way matching score falls below the configured threshold:

```
match_score < match_threshold (default: 0.90)
```

### Matching Logic

```python
# Two-way match score calculation
if po_total == 0:
    score = 0.0
else:
    diff_pct = abs(invoice_amount - po_total) / po_total * 100
    
    if diff_pct <= tolerance_pct:  # default: 5%
        score = 1.0 - (diff_pct / tolerance_pct) * 0.1
    else:
        score = max(0.0, 1.0 - (diff_pct / 100))
```

### Example Scenarios

| Invoice Amount | PO Total | Diff % | Score | Result |
|---------------|----------|--------|-------|--------|
| $10,000 | $10,000 | 0% | 1.00 | MATCHED |
| $10,000 | $10,500 | 5% | 0.90 | MATCHED |
| $10,000 | $11,000 | 10% | 0.89 | FAILED → HITL |
| $10,000 | $8,000 | 25% | 0.75 | FAILED → HITL |
| $10,000 | $0 | N/A | 0.00 | FAILED → HITL |

---

## HITL Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MATCH_TWO_WAY Stage                                │
│                                                                             │
│  Invoice Amount: $15,000                                                    │
│  PO Total: $12,000                                                         │
│  Match Score: 0.75                                                         │
│  Threshold: 0.90                                                           │
│                                                                             │
│  Result: FAILED (score < threshold)                                        │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CHECKPOINT_HITL Stage                                │
│                                                                             │
│  1. Generate checkpoint_id: "cp_wf_INV-001_xyz789"                         │
│  2. Save full workflow state to checkpoint table                           │
│  3. Create human review queue entry                                        │
│  4. Generate review URL: http://localhost:3000/review/cp_wf_INV-001_xyz789 │
│  5. Set workflow status: PAUSED                                            │
│  6. Pause workflow execution                                               │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Human Review Interface                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Invoice: INV-2024-001                                              │   │
│  │  Vendor: Acme Corporation                                           │   │
│  │  Amount: $15,000.00 USD                                             │   │
│  │                                                                     │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│   │
│  │  Match Details                                                      │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│   │
│  │  Score: 0.75 (Threshold: 0.90)                                      │   │
│  │  PO Total: $12,000.00                                               │   │
│  │  Difference: $3,000.00 (25%)                                        │   │
│  │                                                                     │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│   │
│  │  Matched Purchase Orders                                            │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│   │
│  │  PO-2024-001 | $12,000.00 | APPROVED                                │   │
│  │                                                                     │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│   │
│  │  Reviewer Notes:                                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ Additional $3,000 for rush delivery charges confirmed      │   │   │
│  │  │ by vendor via email on 2024-01-14.                         │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌──────────────┐          ┌──────────────┐                        │   │
│  │  │   ACCEPT     │          │   REJECT     │                        │   │
│  │  └──────────────┘          └──────────────┘                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│         ACCEPT Decision          │   │         REJECT Decision          │
│                                  │   │                                  │
│  1. Update checkpoint:           │   │  1. Update checkpoint:           │
│     is_resolved = true           │   │     is_resolved = true           │
│     resolution = "ACCEPT"        │   │     resolution = "REJECT"        │
│                                  │   │                                  │
│  2. Update workflow:             │   │  2. Update workflow:             │
│     status = RUNNING             │   │     status = MANUAL_HANDOFF      │
│                                  │   │                                  │
│  3. Resume at RECONCILE stage    │   │  3. Skip to COMPLETE stage       │
└─────────────────┬────────────────┘   └─────────────────┬────────────────┘
                  │                                       │
                  ▼                                       ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│  Continue Normal Flow:           │   │  Workflow Ends:                  │
│                                  │   │                                  │
│  RECONCILE                       │   │  COMPLETE                        │
│      ↓                           │   │                                  │
│  APPROVE                         │   │  status: MANUAL_HANDOFF          │
│      ↓                           │   │                                  │
│  POSTING                         │   │  Final payload indicates         │
│      ↓                           │   │  manual handling required        │
│  NOTIFY                          │   │                                  │
│      ↓                           │   │                                  │
│  COMPLETE (status: COMPLETED)    │   │                                  │
└──────────────────────────────────┘   └──────────────────────────────────┘
```

---

## Database Schema for HITL

### Checkpoint Table

```sql
CREATE TABLE checkpoints (
    id INTEGER PRIMARY KEY,
    checkpoint_id VARCHAR(100) UNIQUE NOT NULL,
    workflow_db_id INTEGER REFERENCES workflows(id),
    workflow_id VARCHAR(100) NOT NULL,
    stage_id VARCHAR(50) NOT NULL,
    state_blob JSON NOT NULL,          -- Full workflow state
    paused_reason TEXT NOT NULL,
    review_url VARCHAR(500),
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolution VARCHAR(50),            -- ACCEPT or REJECT
    resolver_id VARCHAR(100),
    resolver_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Human Review Table

```sql
CREATE TABLE human_reviews (
    id INTEGER PRIMARY KEY,
    checkpoint_db_id INTEGER REFERENCES checkpoints(id),
    checkpoint_id VARCHAR(100) NOT NULL,
    invoice_id VARCHAR(100) NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    amount FLOAT NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    match_score FLOAT,
    reason_for_hold TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',  -- PENDING, REVIEWED, EXPIRED
    priority INTEGER DEFAULT 0,
    review_url VARCHAR(500),
    assigned_to VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

---

## API Contract

### List Pending Reviews

```
GET /api/v1/human-review/pending
```

Response:
```json
{
  "items": [
    {
      "checkpoint_id": "cp_wf_INV-001_xyz789",
      "invoice_id": "INV-2024-001",
      "vendor_name": "Acme Corporation",
      "amount": 15000.00,
      "match_score": 0.75,
      "reason_for_hold": "Two-way match failed. Score: 0.75 (threshold: 0.90)",
      "status": "PENDING",
      "review_url": "http://localhost:3000/review/cp_wf_INV-001_xyz789",
      "created_at": "2024-01-15T10:30:02Z"
    }
  ]
}
```

### Submit Decision

```
POST /api/v1/human-review/decision
```

Request:
```json
{
  "checkpoint_id": "cp_wf_INV-001_xyz789",
  "decision": "ACCEPT",
  "notes": "Approved after vendor confirmation",
  "reviewer_id": "john_doe"
}
```

Response:
```json
{
  "success": true,
  "checkpoint_id": "cp_wf_INV-001_xyz789",
  "decision": "ACCEPT",
  "resume_token": "wf_INV-2024-001_abc12345",
  "next_stage": "RECONCILE",
  "workflow_status": "RUNNING"
}
```

---

## State Persistence

### What's Saved in Checkpoint

The checkpoint `state_blob` contains the complete workflow state:

```json
{
  "workflow_id": "wf_INV-2024-001_abc12345",
  "invoice_id": "INV-2024-001",
  "status": "PAUSED",
  "current_stage": "CHECKPOINT_HITL",
  
  "raw_payload": {
    "invoice_id": "INV-2024-001",
    "vendor_name": "Acme Corporation",
    "amount": 15000.00
  },
  
  "parsed_invoice": {
    "invoice_text": "...",
    "parsed_line_items": [...]
  },
  
  "vendor_profile": {
    "normalized_name": "ACME CORPORATION",
    "enrichment_meta": {...}
  },
  
  "matched_pos": [
    {"po_id": "PO-2024-001", "amount": 12000.00}
  ],
  
  "match_score": 0.75,
  "match_result": "FAILED",
  "match_evidence": {
    "invoice_amount": 15000.00,
    "po_total": 12000.00,
    "difference_pct": 25.0
  }
}
```

### Resuming from Checkpoint

When a decision is submitted:

1. Load `state_blob` from checkpoint
2. Add human decision fields to state
3. Resume LangGraph execution from appropriate stage:
   - ACCEPT → Start at RECONCILE
   - REJECT → Start at COMPLETE

```python
# Resume logic
state = checkpoint.state_blob.copy()
state["human_decision"] = decision
state["reviewer_id"] = reviewer_id
state["reviewer_notes"] = notes

if decision == "ACCEPT":
    state["current_stage"] = "RECONCILE"
    state["status"] = "RUNNING"
else:
    state["current_stage"] = "COMPLETE"
    state["status"] = "MANUAL_HANDOFF"

# Resume graph execution
await graph.ainvoke(state, config)
```

---

## Audit Trail

All HITL actions are logged to the `audit_logs` table:

```json
{
  "event_type": "human_decision",
  "stage_id": "HITL_DECISION",
  "message": "Human decision: ACCEPT",
  "details": {
    "decision": "ACCEPT",
    "reviewer_id": "john_doe",
    "notes": "Approved after vendor confirmation",
    "checkpoint_id": "cp_wf_INV-001_xyz789",
    "next_stage": "RECONCILE"
  },
  "actor_type": "human",
  "actor_id": "john_doe",
  "created_at": "2024-01-15T11:00:00Z"
}
```

---

## Configuration

### Environment Variables

```env
# Matching thresholds
MATCH_THRESHOLD=0.90
TWO_WAY_TOLERANCE_PCT=5

# Queue settings
HUMAN_REVIEW_QUEUE=human_review_queue

# Frontend URL for review links
FRONTEND_URL=http://localhost:3000
```

### Customizing Thresholds

Adjust in `workflow.json`:

```json
{
  "config": {
    "match_threshold": 0.90,
    "two_way_tolerance_pct": 5
  }
}
```

Or via environment variables:
```bash
export MATCH_THRESHOLD=0.85
export TWO_WAY_TOLERANCE_PCT=10
```
