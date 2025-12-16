"""Review service - Business logic for human review operations."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import WorkflowStatus, StageID, HumanDecisionType
from app.db.models import Checkpoint, HumanReview, Workflow, AuditLog
from app.utils.logger import logger, get_workflow_logger


class ReviewService:
    """Service for human review operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def process_decision(
        self,
        checkpoint_id: str,
        decision: str,
        reviewer_id: str,
        notes: str = "",
    ) -> dict[str, Any]:
        """Process a human review decision."""
        
        # Get checkpoint
        query = select(Checkpoint).where(Checkpoint.checkpoint_id == checkpoint_id)
        result = await self.db.execute(query)
        checkpoint = result.scalar_one_or_none()
        
        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")
        
        if checkpoint.is_resolved:
            raise ValueError(f"Checkpoint already resolved: {checkpoint_id}")
        
        workflow = checkpoint.workflow
        wf_logger = get_workflow_logger(workflow.workflow_id)
        
        # Update checkpoint
        checkpoint.is_resolved = True
        checkpoint.resolved_at = datetime.utcnow()
        checkpoint.resolution = decision
        checkpoint.resolver_id = reviewer_id
        checkpoint.resolver_notes = notes
        
        # Update human review record
        review_query = select(HumanReview).where(HumanReview.checkpoint_id == checkpoint_id)
        review_result = await self.db.execute(review_query)
        review = review_result.scalar_one_or_none()
        if review:
            review.status = "REVIEWED"
        
        # Determine next action based on decision
        if decision == HumanDecisionType.ACCEPT:
            next_stage = StageID.RECONCILE
            workflow_status = WorkflowStatus.RUNNING
            wf_logger.workflow_resumed(checkpoint_id, decision)
        else:
            next_stage = StageID.COMPLETE
            workflow_status = WorkflowStatus.MANUAL_HANDOFF
            wf_logger.info(f"Workflow rejected, marking as {workflow_status}")
        
        # Update workflow
        workflow.status = workflow_status
        workflow.current_stage = next_stage
        workflow.state_data["human_decision"] = decision
        workflow.state_data["reviewer_id"] = reviewer_id
        workflow.state_data["reviewer_notes"] = notes
        
        # Create audit log
        audit_log = AuditLog(
            workflow_db_id=workflow.id,
            workflow_id=workflow.workflow_id,
            event_type="human_decision",
            stage_id=StageID.HITL_DECISION,
            message=f"Human decision: {decision}",
            details={
                "decision": decision,
                "reviewer_id": reviewer_id,
                "notes": notes,
                "next_stage": next_stage,
            },
            actor_type="human",
            actor_id=reviewer_id,
        )
        self.db.add(audit_log)
        await self.db.commit()
        
        # Resume workflow if accepted
        if decision == HumanDecisionType.ACCEPT:
            await self._resume_workflow(workflow, checkpoint)
        else:
            workflow.completed_at = datetime.utcnow()
            await self.db.commit()
        
        return {
            "resume_token": workflow.workflow_id,
            "next_stage": next_stage,
            "workflow_status": workflow_status,
        }
    
    async def _resume_workflow(self, workflow: Workflow, checkpoint: Checkpoint) -> None:
        """Resume workflow from checkpoint."""
        from app.graph.builder import get_workflow_graph
        
        wf_logger = get_workflow_logger(workflow.workflow_id)
        graph = get_workflow_graph()
        
        # Get state from checkpoint
        state = checkpoint.state_blob.copy()
        state["current_stage"] = StageID.RECONCILE
        state["status"] = WorkflowStatus.RUNNING
        
        config = {"configurable": {"thread_id": workflow.workflow_id}}
        
        try:
            final_state = await graph.ainvoke(state, config)
            
            workflow.status = final_state.get("status", WorkflowStatus.COMPLETED)
            workflow.current_stage = final_state.get("current_stage")
            workflow.state_data = final_state
            
            if workflow.status == WorkflowStatus.COMPLETED:
                workflow.completed_at = datetime.utcnow()
                wf_logger.workflow_complete(workflow.status)
            
            await self.db.commit()
            
        except Exception as e:
            wf_logger.error(f"Resume error: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(e)
            await self.db.commit()
            raise
