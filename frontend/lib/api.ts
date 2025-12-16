/**
 * API client functions for Invoice LangGraph Agent
 */

import {
  InvoicePayload,
  InvokeResponse,
  Workflow,
  WorkflowDetail,
  WorkflowListResponse,
  HumanReview,
  ReviewListResponse,
  ReviewDecision,
  StatsResponse,
  LogEntry,
} from "./types";
import { API_PREFIX } from "./constants";

// ============================================
// Helper Functions
// ============================================

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }
  return response.json();
}

// ============================================
// Invoice API
// ============================================

export async function invokeWorkflow(payload: InvoicePayload): Promise<InvokeResponse> {
  const response = await fetch(`${API_PREFIX}/invoke`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<InvokeResponse>(response);
}

export async function validateInvoice(payload: InvoicePayload): Promise<{ valid: boolean; errors?: string[] }> {
  const response = await fetch(`${API_PREFIX}/invoke/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<{ valid: boolean; errors?: string[] }>(response);
}

// ============================================
// Workflow API
// ============================================

export async function getWorkflows(params?: {
  page?: number;
  page_size?: number;
  status?: string;
}): Promise<WorkflowListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", params.page.toString());
  if (params?.page_size) searchParams.set("page_size", params.page_size.toString());
  if (params?.status) searchParams.set("status", params.status);

  const url = `${API_PREFIX}/workflows${searchParams.toString() ? `?${searchParams}` : ""}`;
  const response = await fetch(url);
  return handleResponse<WorkflowListResponse>(response);
}

export async function getWorkflow(workflowId: string): Promise<WorkflowDetail> {
  const response = await fetch(`${API_PREFIX}/workflows/${workflowId}`);
  return handleResponse<WorkflowDetail>(response);
}

export async function getWorkflowStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_PREFIX}/workflows/stats`);
  return handleResponse<StatsResponse>(response);
}

// ============================================
// Human Review API
// ============================================

export async function getPendingReviews(params?: {
  page?: number;
  page_size?: number;
}): Promise<ReviewListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", params.page.toString());
  if (params?.page_size) searchParams.set("page_size", params.page_size.toString());

  const url = `${API_PREFIX}/human-review/pending${searchParams.toString() ? `?${searchParams}` : ""}`;
  const response = await fetch(url);
  return handleResponse<ReviewListResponse>(response);
}

export async function getReview(checkpointId: string): Promise<HumanReview> {
  const response = await fetch(`${API_PREFIX}/human-review/${checkpointId}`);
  return handleResponse<HumanReview>(response);
}

export async function submitDecision(decision: ReviewDecision): Promise<{
  resume_token: string;
  next_stage: string;
  workflow_status: string;
}> {
  const response = await fetch(`${API_PREFIX}/human-review/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(decision),
  });
  return handleResponse(response);
}

// ============================================
// Logs API
// ============================================

export async function getWorkflowLogs(workflowId: string): Promise<LogEntry[]> {
  const response = await fetch(`${API_PREFIX}/workflows/${workflowId}/logs`);
  return handleResponse<LogEntry[]>(response);
}

// ============================================
// Health Check
// ============================================

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_PREFIX.replace("/api/v1", "")}/health`);
  return handleResponse<{ status: string }>(response);
}

