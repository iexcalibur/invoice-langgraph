/**
 * TypeScript type definitions for Invoice LangGraph Agent Frontend
 */

// ============================================
// Invoice Types
// ============================================

export interface LineItem {
  desc: string;
  qty: number;
  unit_price: number;
  total: number;
}

export interface InvoicePayload {
  invoice_id: string;
  vendor_name: string;
  vendor_tax_id?: string;
  invoice_date: string;
  due_date: string;
  amount: number;
  currency: string;
  line_items: LineItem[];
  attachments?: string[];
}

// ============================================
// Workflow Types
// ============================================

export type WorkflowStatus = 
  | "PENDING" 
  | "RUNNING" 
  | "PAUSED" 
  | "COMPLETED" 
  | "FAILED" 
  | "MANUAL_HANDOFF";

export type StageID =
  | "INTAKE"
  | "UNDERSTAND"
  | "PREPARE"
  | "RETRIEVE"
  | "MATCH_TWO_WAY"
  | "CHECKPOINT_HITL"
  | "HITL_DECISION"
  | "RECONCILE"
  | "APPROVE"
  | "POSTING"
  | "NOTIFY"
  | "COMPLETE";

export type MatchResult = "MATCHED" | "FAILED";
export type HumanDecision = "ACCEPT" | "REJECT";
export type ApprovalStatus = "AUTO_APPROVED" | "ESCALATED" | "APPROVED" | "REJECTED";

export interface Workflow {
  id: number;
  workflow_id: string;
  invoice_id: string;
  status: WorkflowStatus;
  current_stage: StageID | null;
  match_score: number | null;
  match_result: MatchResult | null;
  error_message: string | null;
  retry_count: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkflowDetail extends Workflow {
  state_data: Record<string, any>;
  invoice?: InvoicePayload;
}

export interface StageLog {
  stage_id: StageID;
  status: "pending" | "running" | "completed" | "failed";
  started_at: string | null;
  completed_at: string | null;
  output?: Record<string, any>;
  error?: string;
}

export interface LogEntry {
  id: number;
  workflow_id: string;
  event_type: string;
  stage_id: StageID | null;
  message: string;
  details: Record<string, any> | null;
  actor_type: string;
  actor_id: string | null;
  created_at: string;
}

// ============================================
// Human Review Types
// ============================================

export interface Checkpoint {
  id: number;
  checkpoint_id: string;
  workflow_id: string;
  stage_id: StageID;
  paused_reason: string;
  review_url: string | null;
  is_resolved: boolean;
  resolved_at: string | null;
  resolution: HumanDecision | null;
  resolver_id: string | null;
  resolver_notes: string | null;
  created_at: string;
}

export interface HumanReview {
  checkpoint_id: string;
  invoice_id: string;
  vendor_name: string;
  amount: number;
  currency: string;
  match_score: number | null;
  reason_for_hold: string;
  status: "PENDING" | "REVIEWED";
  priority: number;
  review_url: string | null;
  assigned_to: string | null;
  created_at: string;
  expires_at: string | null;
}

export interface ReviewDecision {
  checkpoint_id: string;
  decision: HumanDecision;
  reviewer_id: string;
  notes?: string;
}

// ============================================
// API Response Types
// ============================================

export interface InvokeResponse {
  success: boolean;
  workflow_id: string;
  invoice_id: string;
  status: WorkflowStatus;
  current_stage: StageID | null;
  message: string;
  timestamp: string;
}

export interface WorkflowListResponse {
  items: Workflow[];
  total: number;
  page: number;
  page_size: number;
}

export interface ReviewListResponse {
  items: HumanReview[];
  total: number;
  page: number;
  page_size: number;
}

export interface StatsResponse {
  total_workflows: number;
  running: number;
  completed: number;
  paused: number;
  failed: number;
  pending_reviews: number;
}

// ============================================
// Component Props Types
// ============================================

export interface StageProgressProps {
  currentStage: StageID | null;
  status: WorkflowStatus;
  stages: StageID[];
}

export interface WorkflowCardProps {
  workflow: Workflow;
  onClick?: () => void;
}

export interface ReviewCardProps {
  review: HumanReview;
  onClick?: () => void;
}

