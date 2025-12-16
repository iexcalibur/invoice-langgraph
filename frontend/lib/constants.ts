/**
 * Constants for Invoice LangGraph Agent Frontend
 */

import { StageID } from "./types";

// ============================================
// Stage Configuration
// ============================================

export const STAGES: StageID[] = [
  "INTAKE",
  "UNDERSTAND",
  "PREPARE",
  "RETRIEVE",
  "MATCH_TWO_WAY",
  "CHECKPOINT_HITL",
  "HITL_DECISION",
  "RECONCILE",
  "APPROVE",
  "POSTING",
  "NOTIFY",
  "COMPLETE",
];

export const STAGE_LABELS: Record<StageID, string> = {
  INTAKE: "Intake",
  UNDERSTAND: "Understand",
  PREPARE: "Prepare",
  RETRIEVE: "Retrieve",
  MATCH_TWO_WAY: "Match Two-Way",
  CHECKPOINT_HITL: "Checkpoint HITL",
  HITL_DECISION: "HITL Decision",
  RECONCILE: "Reconcile",
  APPROVE: "Approve",
  POSTING: "Posting",
  NOTIFY: "Notify",
  COMPLETE: "Complete",
};

export const STAGE_COLORS: Record<StageID, string> = {
  INTAKE: "bg-blue-500",
  UNDERSTAND: "bg-purple-500",
  PREPARE: "bg-indigo-500",
  RETRIEVE: "bg-cyan-500",
  MATCH_TWO_WAY: "bg-yellow-500",
  CHECKPOINT_HITL: "bg-orange-500",
  HITL_DECISION: "bg-pink-500",
  RECONCILE: "bg-green-500",
  APPROVE: "bg-emerald-500",
  POSTING: "bg-teal-500",
  NOTIFY: "bg-sky-500",
  COMPLETE: "bg-gray-500",
};

// ============================================
// Status Configuration
// ============================================

export const STATUS_COLORS: Record<string, string> = {
  PENDING: "text-yellow-400",
  RUNNING: "text-blue-400",
  PAUSED: "text-orange-400",
  COMPLETED: "text-green-400",
  FAILED: "text-red-400",
  MANUAL_HANDOFF: "text-purple-400",
};

export const STATUS_BADGE_COLORS: Record<string, string> = {
  PENDING: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  RUNNING: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  PAUSED: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  COMPLETED: "bg-green-500/20 text-green-400 border-green-500/30",
  FAILED: "bg-red-500/20 text-red-400 border-red-500/30",
  MANUAL_HANDOFF: "bg-purple-500/20 text-purple-400 border-purple-500/30",
};

// ============================================
// API Configuration
// ============================================

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const API_VERSION = "v1";
export const API_PREFIX = `${API_BASE_URL}/api/${API_VERSION}`;

// ============================================
// Routes
// ============================================

export const ROUTES = {
  HOME: "/",
  INVOKE: "/invoke",
  WORKFLOWS: "/workflows",
  WORKFLOW_DETAIL: (id: string) => `/workflows/${id}`,
  REVIEW: "/review",
  REVIEW_DETAIL: (checkpointId: string) => `/review/${checkpointId}`,
} as const;

// ============================================
// Pagination
// ============================================

export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

// ============================================
// Date Formatting
// ============================================

export const DATE_FORMAT = "MMM dd, yyyy";
export const DATETIME_FORMAT = "MMM dd, yyyy HH:mm:ss";
export const TIME_FORMAT = "HH:mm:ss";

