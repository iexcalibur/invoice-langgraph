"""Workflow service - Business logic for workflow operations."""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings, WorkflowStatus, StageID
from app.db.models import Invoice, Workflow, AuditLog
from app.schemas.invoice import InvoicePayload, InvokeResponse
from app.utils.helpers import generate_workflow_id, utc_now_iso
from app.utils.logger import logger, get_workflow_logger


class WorkflowService:
    """Service for workflow operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
    
    async def start_workflow(self, payload: InvoicePayload) -> InvokeResponse:
        """Start a new invoice processing workflow."""
        workflow_id = generate_workflow_id(payload.invoice_id)
        wf_logger = get_workflow_logger(workflow_id)
        
        # Create invoice record
        invoice = Invoice(
            invoice_id=payload.invoice_id,
            vendor_name=payload.vendor_name,
            vendor_tax_id=payload.vendor_tax_id,
            invoice_date=payload.invoice_date,
            due_date=payload.due_date,
            amount=payload.amount,
            currency=payload.currency,
            line_items=[item.model_dump() for item in payload.line_items],
            attachments=payload.attachments,
            raw_payload=payload.model_dump(),
        )
        self.db.add(invoice)
        await self.db.flush()
        
        # Create workflow record
        workflow = Workflow(
            workflow_id=workflow_id,
            invoice_db_id=invoice.id,
            invoice_id=payload.invoice_id,
            status=WorkflowStatus.RUNNING,
            current_stage=StageID.INTAKE,
            started_at=datetime.utcnow(),
            state_data={"raw_payload": payload.model_dump()},
        )
        self.db.add(workflow)
        await self.db.flush()
        
        # Create audit log
        audit_log = AuditLog(
            workflow_db_id=workflow.id,
            workflow_id=workflow_id,
            event_type="workflow_started",
            stage_id=StageID.INTAKE,
            message=f"Workflow started for invoice {payload.invoice_id}",
            details={"invoice_id": payload.invoice_id, "amount": payload.amount},
        )
        self.db.add(audit_log)
        await self.db.commit()
        
        wf_logger.info(f"Workflow created: {workflow_id}")
        
        # Start async graph execution (in background)
        # For demo, we'll execute synchronously
        try:
            await self._execute_workflow(workflow)
        except Exception as e:
            wf_logger.error(f"Workflow execution error: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(e)
            await self.db.commit()
        
        return InvokeResponse(
            success=True,
            workflow_id=workflow_id,
            invoice_id=payload.invoice_id,
            status=workflow.status,
            current_stage=workflow.current_stage,
            message="Workflow started",
            timestamp=utc_now_iso(),
        )
    
    async def start_workflow_sync(self, payload: InvoicePayload) -> dict[str, Any]:
        """Start workflow and wait for completion."""
        result = await self.start_workflow(payload)
        
        # Get final state
        workflow = await self.db.get(Workflow, result.workflow_id)
        if workflow:
            return workflow.to_detailed_dict()
        
        return result.model_dump()
    
    async def _execute_workflow(self, workflow: Workflow) -> None:
        """Execute workflow stages using LangGraph."""
        from app.graph.builder import get_workflow_graph
        
        wf_logger = get_workflow_logger(workflow.workflow_id)
        graph = get_workflow_graph()
        
        initial_state = {
            "workflow_id": workflow.workflow_id,
            "invoice_id": workflow.invoice_id,
            "status": WorkflowStatus.RUNNING,
            "current_stage": StageID.INTAKE,
            "raw_payload": workflow.state_data.get("raw_payload", {}),
        }
        
        config = {"configurable": {"thread_id": workflow.workflow_id}}
        
        try:
            # Run the graph
            final_state = await graph.ainvoke(initial_state, config)
            
            # Update workflow with final state
            workflow.status = final_state.get("status", WorkflowStatus.COMPLETED)
            workflow.current_stage = final_state.get("current_stage")
            workflow.state_data = final_state
            workflow.match_score = final_state.get("match_score")
            workflow.match_result = final_state.get("match_result")
            
            if workflow.status == WorkflowStatus.COMPLETED:
                workflow.completed_at = datetime.utcnow()
                wf_logger.workflow_complete(workflow.status)
            
            await self.db.commit()
            
        except Exception as e:
            wf_logger.error(f"Graph execution error: {e}")
            raise
