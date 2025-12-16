# Demo Video Script

## Invoice LangGraph Agent - Demo Guide

**Total Duration:** 5 minutes
- Introduction: 1 minute
- Demo: 4 minutes

---

## Part 1: Self Introduction (1 minute)

### Script

> "Hello, I'm [Your Name], an ML Engineer with 5 years of experience in building production AI systems. I've worked on fraud detection systems processing millions of transactions, RAG-based customer support, and document intelligence pipelines.
>
> Today, I'll demonstrate my implementation of the Invoice Processing LangGraph Agent - a workflow system that handles invoice processing with human-in-the-loop capabilities."

### Key Points to Mention

- Your background in AI/ML
- Experience with production systems
- Brief mention of the project scope

---

## Part 2: Architecture Overview (30 seconds)

### Script

> "Let me quickly walk you through the architecture. This system has:
>
> - A **Next.js frontend** for the user interface
> - A **FastAPI backend** handling API requests
> - **LangGraph** orchestrating the 12-stage workflow
> - **MCP integration** routing abilities to COMMON and ATLAS servers
> - **Bigtool** for dynamic tool selection
>
> The workflow processes invoices through stages like OCR, vendor enrichment, PO matching, and can pause for human review when needed."

### Show

- Architecture diagram (keep it brief)
- List of 12 stages

---

## Part 3: Starting the Application (30 seconds)

### Commands to Run

```bash
# Terminal 1: Start backend
cd backend
make backend
# or: uvicorn app.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
pnpm dev
```

### Script

> "I'll start the backend server on port 8000 and the frontend on port 3000. The backend initializes the database and loads the workflow configuration."

### Show

- Terminal output showing startup logs
- "Application started successfully" message

---

## Part 4: Demo Scenario 1 - Happy Path (1.5 minutes)

### Scenario: Invoice that matches PO

### Steps

1. **Open Dashboard**
   > "Here's the dashboard showing workflow statistics and recent activity."

2. **Navigate to Invoice Submission**
   > "Let me submit an invoice. I'll use a test invoice from Acme Corporation for $12,000."

3. **Submit Invoice**
   ```json
   {
     "invoice_id": "INV-2024-001",
     "vendor_name": "Acme Corporation",
     "amount": 12000.00,
     "currency": "USD",
     "line_items": [
       {"desc": "Consulting Services", "qty": 8, "unit_price": 1500, "total": 12000}
     ]
   }
   ```

4. **Watch Workflow Progress**
   > "The workflow starts immediately. Watch the stages execute:
   > - INTAKE: Validating and persisting the invoice
   > - UNDERSTAND: Running OCR (using Google Vision selected by Bigtool)
   > - PREPARE: Enriching vendor data via Clearbit
   > - RETRIEVE: Fetching POs from the mock ERP
   > - MATCH: Computing two-way match score..."

5. **Show Match Success**
   > "The match score is 0.95 - above our 0.90 threshold. The workflow continues without human review."

6. **Show Completion**
   > "Workflow completes with status COMPLETED. Let me show you the final payload and audit log."

### Key Points to Highlight

- Bigtool selections in logs
- MCP calls to COMMON and ATLAS servers
- Match score calculation
- Workflow completion

---

## Part 5: Demo Scenario 2 - HITL Path (1.5 minutes)

### Scenario: Invoice that fails PO matching

### Steps

1. **Submit Mismatched Invoice**
   > "Now let's submit an invoice that won't match. This invoice is for $20,000 but the PO is only $12,000."

   ```json
   {
     "invoice_id": "INV-2024-002",
     "vendor_name": "Acme Corporation",
     "amount": 20000.00,
     "currency": "USD"
   }
   ```

2. **Watch Workflow Pause**
   > "Watch the workflow progress... and here at MATCH_TWO_WAY, the score is 0.60 - below threshold. The workflow pauses and creates a checkpoint."

3. **Show Human Review Queue**
   > "The invoice appears in the Human Review queue. You can see:
   > - Invoice details
   > - Match score: 0.60
   > - Reason: Two-way match failed
   > - Review URL"

4. **Open Review Detail**
   > "Let me click into the review. Here we see:
   > - The invoice vs PO comparison
   > - The $8,000 difference (40%)
   > - Matched purchase orders
   > - Space for reviewer notes"

5. **Submit Accept Decision**
   > "I'll approve this invoice, adding a note that the vendor confirmed additional charges."

   ```json
   {
     "decision": "ACCEPT",
     "notes": "Vendor confirmed rush delivery charges via email",
     "reviewer_id": "demo_reviewer"
   }
   ```

6. **Watch Workflow Resume**
   > "After accepting, the workflow resumes from RECONCILE:
   > - RECONCILE: Building accounting entries
   > - APPROVE: Auto-approved (under threshold)
   > - POSTING: Posted to ERP
   > - NOTIFY: Sent notifications
   > - COMPLETE: Done!"

7. **Show Final Result**
   > "The workflow completes with status COMPLETED. The audit log shows the human decision was captured."

### Key Points to Highlight

- Checkpoint creation
- Review queue UI
- Human decision flow
- Workflow resume from checkpoint
- Full audit trail

---

## Part 6: Wrap-Up (30 seconds)

### Script

> "To summarize, this implementation demonstrates:
>
> 1. **LangGraph orchestration** with 12 stages and conditional routing
> 2. **State persistence** across nodes with checkpoint/resume
> 3. **Human-in-the-Loop** when automated matching fails
> 4. **MCP integration** routing to COMMON and ATLAS servers
> 5. **Bigtool selection** dynamically choosing tools from pools
> 6. **Full audit logging** of all decisions and tool selections
>
> Thank you for watching. The code is available on GitHub with full documentation."

---

## Technical Points to Emphasize

### During the Demo

1. **Bigtool Selections**
   - "Notice in the logs: Bigtool selected Google Vision for OCR because this is an invoice document."
   - "For enrichment, Bigtool chose Clearbit since we have a vendor name."

2. **MCP Routing**
   - "This OCR call goes to ATLAS server - that's our external integration layer."
   - "The validation is handled by COMMON server - internal operations."

3. **State Management**
   - "All state persists across stages. The checkpoint saves the complete workflow state."

4. **Checkpoint/Resume**
   - "The workflow pauses at the checkpoint. All state is saved to the database."
   - "When we accept, LangGraph resumes from exactly where we left off."

---

## Fallback Plans

### If Something Fails

1. **Backend won't start**
   - Show the code structure instead
   - Walk through the LangGraph builder

2. **Frontend issues**
   - Use Postman/curl to demonstrate API
   - Show API docs at `/docs`

3. **Workflow errors**
   - Explain error handling
   - Show retry logic

---

## Screen Recording Tips

1. **Resolution:** 1920x1080
2. **Zoom in** on important elements
3. **Speak clearly** and at moderate pace
4. **Pause** after key actions
5. **Test recording** before final take
6. **Check audio** levels

---

## Checklist Before Recording

- [ ] Backend starts cleanly
- [ ] Frontend loads without errors
- [ ] Database is reset (clean state)
- [ ] Sample invoices ready
- [ ] Postman/API docs as backup
- [ ] Screen recording software ready
- [ ] Microphone tested
- [ ] Notes visible (but not on screen)
