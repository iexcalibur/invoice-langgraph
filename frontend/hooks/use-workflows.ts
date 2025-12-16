/**
 * React Query hooks for workflow operations
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getWorkflows, getWorkflow, getWorkflowStats } from "@/lib/api";
import { WorkflowListResponse, WorkflowDetail, StatsResponse } from "@/lib/types";

// ============================================
// Workflow List
// ============================================

export function useWorkflows(params?: { page?: number; page_size?: number; status?: string }) {
  return useQuery<WorkflowListResponse>({
    queryKey: ["workflows", params],
    queryFn: () => getWorkflows(params),
    staleTime: 10000, // 10 seconds
  });
}

// ============================================
// Workflow Detail
// ============================================

export function useWorkflow(workflowId: string) {
  return useQuery<WorkflowDetail>({
    queryKey: ["workflow", workflowId],
    queryFn: () => getWorkflow(workflowId),
    enabled: !!workflowId,
    refetchInterval: 2000, // Refetch every 2 seconds for live updates
  });
}

// ============================================
// Workflow Stats
// ============================================

export function useStats() {
  return useQuery<StatsResponse>({
    queryKey: ["stats"],
    queryFn: getWorkflowStats,
    staleTime: 5000, // 5 seconds
    refetchInterval: 10000, // Refetch every 10 seconds
  });
}

// ============================================
// Invalidate Queries Helper
// ============================================

export function useInvalidateWorkflows() {
  const queryClient = useQueryClient();
  
  return {
    invalidateAll: () => {
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
    },
    invalidateWorkflow: (workflowId: string) => {
      queryClient.invalidateQueries({ queryKey: ["workflow", workflowId] });
    },
  };
}

