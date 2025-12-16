/**
 * React Query hooks for human review operations
 */

import { useQuery } from "@tanstack/react-query";
import { getPendingReviews, getReview } from "@/lib/api";
import { ReviewListResponse, HumanReview } from "@/lib/types";

// ============================================
// Pending Reviews List
// ============================================

export function useReviews(params?: { page?: number; page_size?: number }) {
  return useQuery<ReviewListResponse>({
    queryKey: ["reviews", params],
    queryFn: () => getPendingReviews(params),
    staleTime: 5000, // 5 seconds
    refetchInterval: 10000, // Refetch every 10 seconds for live updates
  });
}

// ============================================
// Review Detail
// ============================================

export function useReview(checkpointId: string) {
  return useQuery<HumanReview>({
    queryKey: ["review", checkpointId],
    queryFn: () => getReview(checkpointId),
    enabled: !!checkpointId,
  });
}

