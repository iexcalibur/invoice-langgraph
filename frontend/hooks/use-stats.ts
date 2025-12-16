/**
 * React Query hook for dashboard statistics
 */

import { useQuery } from "@tanstack/react-query";
import { getWorkflowStats } from "@/lib/api";
import { StatsResponse } from "@/lib/types";

export function useStats() {
  return useQuery<StatsResponse>({
    queryKey: ["stats"],
    queryFn: getWorkflowStats,
    staleTime: 5000, // 5 seconds
    refetchInterval: 10000, // Refetch every 10 seconds
  });
}

