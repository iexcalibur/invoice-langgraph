# API Documentation

## Invoice LangGraph Agent - REST API

Base URL: `http://localhost:8000/api/v1`

---

## Authentication

Currently, no authentication is required (demo mode). For production, implement JWT or API key authentication.

---

## Endpoints

### 1. Invoke Workflow

#### POST `/invoke`

Start a new invoice processing workflow.

**Request Body:**
```json
{
  "invoice_id": "INV-2024-001",
  "vendor_name": "Acme Corporation",
  "vendor_tax_id": "GSTIN123456",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "amount": 15000.00,
  "currency": "USD",
  "line_items": [
    {
      "desc": "Consulting Services",
      "qty": 10,
      "unit_price": 1500.00,
      "total": 15000.00
    }
  ],
  "attachments": ["invoice_scan.pdf"]
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "workflow_id": "wf_INV-2024-001_abc12345",
  "invoice_id": "INV-2024-001",
  "status": "RUNNING",
  "current_stage": "INTAKE",
  "message": "Workflow started",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Error Response (422 Validation Error):**
```json
{
  "success": false,
  "error": {
    "type": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "loc": ["body", "amount"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

#### POST `/invoke/sync`

Start workflow and wait for completion (synchronous).

**Request:** Same as `/invoke`

**Response (200 OK):**
```json
{
  "success": true,
  "workflow_id": "wf_INV-2024-001_abc12345",
  "status": "COMPLETED",
  "current_stage": "COMPLETE",
  "result": {
    "workflow_id": "wf_INV-2024-001_abc12345",
    "invoice_id": "INV-2024-001",
    "status": "COMPLETED",
    "match_score": 0.95,
    "match_result": "MATCHED",
    "final_payload": { ... }
  },
  "timestamp": "2024-01-15T10:30:05Z"
}
```

---

### 2. Workflows

#### GET `/workflows`

List all workflows with pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | - | Filter by status (PENDING, RUNNING, PAUSED, COMPLETED, FAILED) |
| `limit` | int | 20 | Items per page (1-100) |
| `offset` | int | 0 | Pagination offset |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "workflow_id": "wf_INV-2024-001_abc12345",
      "invoice_id": "INV-2024-001",
      "status": "COMPLETED",
      "current_stage": "COMPLETE",
      "match_score": 0.95,
      "match_result": "MATCHED",
      "error_message": null,
      "retry_count": 0,
      "started_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:30:05Z",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:05Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

#### GET `/workflows/stats`

Get workflow statistics.

**Response (200 OK):**
```json
{
  "total": 100,
  "by_status": {
    "pending": 5,
    "running": 2,
    "paused": 3,
    "completed": 85,
    "failed": 3,
    "manual_handoff": 2
  },
  "pending_review": 3
}
```

---

#### GET `/workflows/{workflow_id}`

Get detailed workflow information.

**Response (200 OK):**
```json
{
  "id": 1,
  "workflow_id": "wf_INV-2024-001_abc12345",
  "invoice_id": "INV-2024-001",
  "status": "PAUSED",
  "current_stage": "CHECKPOINT_HITL",
  "match_score": 0.75,
  "match_result": "FAILED",
  "error_message": null,
  "retry_count": 0,
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:02Z",
  "invoice": {
    "invoice_id": "INV-2024-001",
    "vendor_name": "Acme Corporation",
    "amount": 15000.00,
    "currency": "USD"
  },
  "checkpoints": [
    {
      "checkpoint_id": "cp_wf_INV-2024-001_xyz789",
      "stage_id": "CHECKPOINT_HITL",
      "paused_reason": "Two-way match failed. Score: 0.75 (threshold: 0.90)",
      "review_url": "http://localhost:3000/review/cp_wf_INV-2024-001_xyz789",
      "is_resolved": false,
      "created_at": "2024-01-15T10:30:02Z"
    }
  ]
}
```

---

#### GET `/workflows/{workflow_id}/state`

Get full workflow state data.

**Response (200 OK):**
```json
{
  "workflow_id": "wf_INV-2024-001_abc12345",
  "status": "PAUSED",
  "current_stage": "CHECKPOINT_HITL",
  "state_data": {
    "raw_payload": { ... },
    "parsed_invoice": { ... },
    "vendor_profile": { ... },
    "matched_pos": [ ... ],
    "match_score": 0.75,
    "match_result": "FAILED",
    "checkpoint_id": "cp_wf_INV-2024-001_xyz789"
  }
}
```

---

#### DELETE `/workflows/{workflow_id}`

Delete a workflow and all associated data.

**Response (204 No Content)**

---

### 3. Human Review

#### GET `/human-review/pending`

List all pending human reviews.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Items per page (1-100) |
| `offset` | int | 0 | Pagination offset |

**Response (200 OK):**
```json
{
  "items": [
    {
      "checkpoint_id": "cp_wf_INV-2024-001_xyz789",
      "invoice_id": "INV-2024-001",
      "vendor_name": "Acme Corporation",
      "amount": 15000.00,
      "currency": "USD",
      "match_score": 0.75,
      "reason_for_hold": "Two-way match failed. Score: 0.75 (threshold: 0.90)",
      "status": "PENDING",
      "priority": 0,
      "review_url": "http://localhost:3000/review/cp_wf_INV-2024-001_xyz789",
      "assigned_to": null,
      "created_at": "2024-01-15T10:30:02Z",
      "expires_at": null
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

#### GET `/human-review/stats`

Get human review statistics.

**Response (200 OK):**
```json
{
  "total": 10,
  "by_status": {
    "pending": 3,
    "reviewed": 6,
    "expired": 1
  },
  "pending": 3
}
```

---

#### GET `/human-review/{checkpoint_id}`

Get detailed review information.

**Response (200 OK):**
```json
{
  "checkpoint_id": "cp_wf_INV-2024-001_xyz789",
  "invoice_id": "INV-2024-001",
  "vendor_name": "Acme Corporation",
  "amount": 15000.00,
  "currency": "USD",
  "match_score": 0.75,
  "reason_for_hold": "Two-way match failed. Score: 0.75 (threshold: 0.90)",
  "status": "PENDING",
  "priority": 0,
  "review_url": "http://localhost:3000/review/cp_wf_INV-2024-001_xyz789",
  "assigned_to": null,
  "created_at": "2024-01-15T10:30:02Z",
  "expires_at": null,
  "checkpoint_data": {
    "raw_payload": { ... },
    "parsed_invoice": { ... },
    "matched_pos": [ ... ]
  },
  "workflow_status": "PAUSED",
  "invoice_data": {
    "invoice_text": "...",
    "parsed_line_items": [ ... ]
  },
  "matched_pos": [
    {
      "po_id": "PO-2024-001",
      "vendor": "ACME CORPORATION",
      "amount": 12000.00,
      "status": "APPROVED"
    }
  ],
  "match_evidence": {
    "invoice_amount": 15000.00,
    "po_total": 12000.00,
    "difference_pct": 25.0
  }
}
```

---

#### POST `/human-review/decision`

Submit a review decision.

**Request Body:**
```json
{
  "checkpoint_id": "cp_wf_INV-2024-001_xyz789",
  "decision": "ACCEPT",
  "notes": "Approved after vendor confirmation of additional charges",
  "reviewer_id": "user_john_doe"
}
```

**Decision Values:**
- `ACCEPT` - Approve and continue workflow to RECONCILE
- `REJECT` - Reject and mark as MANUAL_HANDOFF

**Response (200 OK):**
```json
{
  "success": true,
  "checkpoint_id": "cp_wf_INV-2024-001_xyz789",
  "decision": "ACCEPT",
  "resume_token": "wf_INV-2024-001_abc12345",
  "next_stage": "RECONCILE",
  "workflow_status": "RUNNING"
}
```

---

### 4. Logs

#### GET `/logs/{workflow_id}`

Get all logs for a workflow.

**Response (200 OK):**
```json
{
  "workflow_id": "wf_INV-2024-001_abc12345",
  "status": "COMPLETED",
  "stages": [
    {
      "stage_id": "INTAKE",
      "status": "completed",
      "started_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:30:00.5Z",
      "duration_ms": 500,
      "entries": [
        {
          "timestamp": "2024-01-15T10:30:00Z",
          "level": "INFO",
          "stage_id": "INTAKE",
          "event_type": "stage_start",
          "message": "Stage [INTAKE] started",
          "details": null
        }
      ],
      "outputs": {}
    }
  ],
  "bigtool_selections": [
    {
      "capability": "storage",
      "selected": "local_fs",
      "available": ["s3", "gcs", "local_fs"],
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "mcp_calls": [
    {
      "ability": "validate_schema",
      "server": "COMMON",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### GET `/logs/{workflow_id}/stream`

Stream real-time logs via Server-Sent Events (SSE).

**Response (200 OK, text/event-stream):**
```
data: {"id": 1, "event_type": "stage_start", "stage_id": "INTAKE", "message": "Stage started", "timestamp": "2024-01-15T10:30:00Z"}

data: {"id": 2, "event_type": "mcp_call", "stage_id": "INTAKE", "message": "MCP [COMMON] → validate_schema", "timestamp": "2024-01-15T10:30:00Z"}

data: {"event": "workflow_complete", "status": "COMPLETED"}
```

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 202 | Accepted (async processing started) |
| 204 | No Content (successful deletion) |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Workflow Status Values

| Status | Description |
|--------|-------------|
| `PENDING` | Workflow created, not yet started |
| `RUNNING` | Workflow actively processing |
| `PAUSED` | Waiting for human review |
| `COMPLETED` | Successfully finished |
| `FAILED` | Error occurred during processing |
| `MANUAL_HANDOFF` | Rejected by human reviewer |

---

## Rate Limits

Demo mode: No rate limits

Production recommendation:
- 100 requests/minute per IP for general endpoints
- 10 requests/minute for `/invoke` endpoint
