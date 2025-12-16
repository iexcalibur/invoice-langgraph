# Bigtool Documentation

## Overview

Bigtool is the dynamic tool selection system that chooses the appropriate tool from a pool based on capability requirements and context. It enables the workflow to adapt to different environments (dev/prod) and optimize for specific use cases.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BigtoolPicker                                     │
│                                                                             │
│   ┌─────────────┐     ┌─────────────────────┐     ┌───────────────────┐   │
│   │   Request   │ ──▶ │  Selection Engine   │ ──▶ │  Selected Tool    │   │
│   │             │     │                     │     │                   │   │
│   │ capability  │     │ 1. Rule-based       │     │  e.g., "google_   │   │
│   │ context     │     │ 2. Context-aware    │     │       vision"     │   │
│   │             │     │ 3. LLM fallback     │     │                   │   │
│   └─────────────┘     └─────────────────────┘     └───────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                         Tool Pools                                   │ │
│   │                                                                     │ │
│   │  ┌─────────┐  ┌─────────────┐  ┌───────────────┐  ┌─────────┐     │ │
│   │  │   OCR   │  │ Enrichment  │  │ ERP Connector │  │  Email  │     │ │
│   │  │         │  │             │  │               │  │         │     │ │
│   │  │ google_ │  │ clearbit    │  │ sap_sandbox   │  │ sendgrid│     │ │
│   │  │ vision  │  │ pdl         │  │ netsuite      │  │ ses     │     │ │
│   │  │ tesser- │  │ vendor_db   │  │ mock_erp      │  │ smart-  │     │ │
│   │  │ act     │  │             │  │               │  │ lead    │     │ │
│   │  │ aws_    │  │             │  │               │  │         │     │ │
│   │  │ textract│  │             │  │               │  │         │     │ │
│   │  └─────────┘  └─────────────┘  └───────────────┘  └─────────┘     │ │
│   │                                                                     │ │
│   │  ┌─────────┐  ┌─────────┐                                          │ │
│   │  │   DB    │  │ Storage │                                          │ │
│   │  │         │  │         │                                          │ │
│   │  │ postgres│  │ s3      │                                          │ │
│   │  │ sqlite  │  │ gcs     │                                          │ │
│   │  │ dynamodb│  │ local_fs│                                          │ │
│   │  └─────────┘  └─────────┘                                          │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tool Pools

### OCR Pool

| Tool | Use Case | Accuracy | Cost |
|------|----------|----------|------|
| `google_vision` | High-accuracy document OCR | 99%+ | $$$ |
| `tesseract` | Open-source, local processing | 90-95% | Free |
| `aws_textract` | AWS-native, form extraction | 98%+ | $$ |

**Selection Logic:**
```python
if document_type in ["invoice", "receipt", "contract"]:
    return "google_vision"  # High accuracy needed
else:
    return "tesseract"  # Cost-effective for simple docs
```

### Enrichment Pool

| Tool | Use Case | Coverage | Cost |
|------|----------|----------|------|
| `clearbit` | Company enrichment | Global B2B | $$$ |
| `people_data_labs` | Individual/company data | US-focused | $$ |
| `vendor_db` | Internal vendor database | Custom | Free |

**Selection Logic:**
```python
if vendor_name:  # Known company
    return "clearbit"
else:  # Individual or unknown
    return "people_data_labs"
```

### ERP Connector Pool

| Tool | Use Case | Integration |
|------|----------|-------------|
| `sap_sandbox` | SAP ERP integration | SAP S/4HANA |
| `netsuite` | NetSuite ERP | Oracle NetSuite |
| `mock_erp` | Demo/testing | Mock data |

**Selection Logic:**
```python
if environment == "production":
    return configured_erp_connector
else:
    return "mock_erp"  # Always use mock for demo
```

### Database Pool

| Tool | Use Case | Performance |
|------|----------|-------------|
| `postgres` | Production database | High |
| `sqlite` | Development/demo | Medium |
| `dynamodb` | Serverless/scalable | Very High |

**Selection Logic:**
```python
if environment == "production":
    return "postgres"
else:
    return "sqlite"  # Simple for demo
```

### Email Pool

| Tool | Use Case | Volume |
|------|----------|--------|
| `sendgrid` | Transactional email | Medium |
| `ses` | High-volume email | Very High |
| `smartlead` | Outreach campaigns | Medium |

**Selection Logic:**
```python
if volume == "high":
    return "ses"  # Cost-effective at scale
else:
    return "sendgrid"  # Easy setup
```

### Storage Pool

| Tool | Use Case | Durability |
|------|----------|------------|
| `s3` | AWS cloud storage | 99.999999999% |
| `gcs` | GCP cloud storage | 99.999999999% |
| `local_fs` | Local development | N/A |

**Selection Logic:**
```python
if file_size > 100_MB:
    return "s3" or "gcs"
else:
    return "local_fs"  # Quick for small files
```

---

## Usage

### Basic Usage

```python
from app.bigtool import get_bigtool_picker

# Get picker instance
bigtool = get_bigtool_picker()

# Select OCR tool
ocr_tool = bigtool.select("ocr", {"document_type": "invoice"})
# Returns: "google_vision"

# Select enrichment tool
enrichment_tool = bigtool.select("enrichment", {"vendor_name": "Acme Corp"})
# Returns: "clearbit"

# Select with no context
db_tool = bigtool.select("db")
# Returns: "sqlite" (default)
```

### In Workflow Nodes

```python
async def understand_node(state: InvoiceState) -> dict:
    bigtool = get_bigtool_picker()
    logger = get_workflow_logger(state["workflow_id"])
    
    # Select OCR provider based on document type
    ocr_tool = bigtool.select("ocr", {
        "document_type": "invoice",
        "attachments": state.get("raw_payload", {}).get("attachments", [])
    })
    
    # Log the selection
    logger.bigtool_selection(
        capability="ocr",
        selected_tool=ocr_tool,
        available_tools=["google_vision", "tesseract", "aws_textract"]
    )
    
    # Use the selected tool via MCP
    result = mcp.call("ocr_extract", {
        "attachments": attachments,
        "provider": ocr_tool
    })
    
    return {"ocr_provider_used": ocr_tool, ...}
```

---

## Selection Engine

### Rule-Based Selection (Primary)

```python
def _rule_based_select(
    self,
    capability: str,
    available: list[str],
    context: dict[str, Any],
) -> str:
    """
    Rule-based tool selection.
    
    Each capability has specific rules based on context.
    """
    
    # OCR: Based on document type
    if capability == "ocr":
        doc_type = context.get("document_type", "")
        if doc_type in ["invoice", "receipt", "contract"]:
            return "google_vision"
        return "tesseract"
    
    # Enrichment: Based on entity type
    elif capability == "enrichment":
        if context.get("vendor_name"):
            return "clearbit"
        return "people_data_labs"
    
    # ERP: Always mock for demo
    elif capability == "erp_connector":
        return "mock_erp"
    
    # DB: SQLite for demo
    elif capability == "db":
        return "sqlite"
    
    # Email: SendGrid by default
    elif capability == "email":
        volume = context.get("volume", "low")
        if volume == "high":
            return "ses"
        return "sendgrid"
    
    # Storage: Local for small files
    elif capability == "storage":
        size = context.get("size", "small")
        if size == "large":
            return "s3"
        return "local_fs"
    
    # Default: First available
    return available[0]
```

### LLM Fallback (Optional)

For complex decisions where rules aren't sufficient:

```python
async def _llm_select(
    self,
    capability: str,
    available: list[str],
    context: dict[str, Any],
) -> str:
    """
    Use LLM for complex tool selection decisions.
    """
    prompt = f"""
    Select the best tool for the following scenario:
    
    Capability: {capability}
    Available tools: {available}
    Context: {json.dumps(context, indent=2)}
    
    Consider:
    - Accuracy requirements
    - Cost constraints
    - Performance needs
    - Data sensitivity
    
    Return only the tool name.
    """
    
    response = await llm.ainvoke(prompt)
    selected = response.content.strip()
    
    if selected in available:
        return selected
    return available[0]  # Fallback
```

---

## Selection Logging

All tool selections are logged for audit and debugging:

```python
{
    "capability": "ocr",
    "selected": "google_vision",
    "available": ["google_vision", "tesseract", "aws_textract"],
    "context_keys": ["document_type", "attachments"],
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Accessing Selection Log

```python
bigtool = get_bigtool_picker()

# Make selections
bigtool.select("ocr", {"document_type": "invoice"})
bigtool.select("enrichment", {"vendor_name": "Acme"})

# Get selection history
log = bigtool.get_selection_log()
print(log)
# [
#   {"capability": "ocr", "selected": "google_vision", ...},
#   {"capability": "enrichment", "selected": "clearbit", ...}
# ]

# Clear log
bigtool.clear_selection_log()
```

---

## Configuration

### Defining Tool Pools

In `workflow.json`:

```json
{
  "tools_hint": {
    "bigtool_picker": "Use BigtoolPicker.select(capability, context)",
    "example_pools": {
      "ocr": ["google_vision", "tesseract", "aws_textract"],
      "enrichment": ["clearbit", "people_data_labs", "vendor_db"],
      "erp_connector": ["sap_sandbox", "netsuite", "mock_erp"],
      "db": ["postgres", "sqlite", "dynamodb"],
      "email": ["sendgrid", "smartlead", "ses"],
      "storage": ["s3", "gcs", "local_fs"]
    }
  }
}
```

### Default Selections

In `config.py`:

```python
DEFAULT_TOOL_SELECTIONS = {
    "ocr": "google_vision",
    "enrichment": "clearbit",
    "erp_connector": "mock_erp",
    "db": "sqlite",
    "email": "sendgrid",
    "storage": "local_fs",
}
```

---

## Stage-to-Tool Mapping

| Stage | Capability | Pool Hint |
|-------|------------|-----------|
| INTAKE | storage | s3, gcs, local_fs |
| UNDERSTAND | ocr | google_vision, tesseract, aws_textract |
| PREPARE | enrichment | clearbit, people_data_labs, vendor_db |
| RETRIEVE | erp_connector | sap_sandbox, netsuite, mock_erp |
| CHECKPOINT | db | postgres, sqlite, dynamodb |
| POSTING | erp_connector | sap_sandbox, netsuite, mock_erp |
| NOTIFY | email | sendgrid, smartlead, ses |
| COMPLETE | db | postgres, sqlite, dynamodb |

---

## Best Practices

1. **Always log selections** - Helps with debugging and audit
2. **Provide rich context** - Better context = better selection
3. **Define clear rules** - Rule-based is faster than LLM
4. **Test with mock tools** - Use `mock_*` tools in development
5. **Monitor tool performance** - Track accuracy and latency per tool
