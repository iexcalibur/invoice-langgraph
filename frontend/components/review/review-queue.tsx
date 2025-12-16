"use client";

import { ReviewCard } from "./review-card";
import { EmptyState } from "@/components/common/empty-state";
import { useReviews } from "@/hooks/use-reviews";
import { Inbox } from "lucide-react";

export function ReviewQueue() {
  const { data: reviewsData, isLoading } = useReviews({ page: 1, page_size: 50 });

  if (isLoading) {
    return (
      <div className="text-white/60 text-center py-12">Loading reviews...</div>
    );
  }

  const reviews = reviewsData?.items || [];

  if (reviews.length === 0) {
    return (
      <EmptyState
        icon={Inbox}
        title="No Pending Reviews"
        description="All reviews have been completed. Great work!"
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {reviews.map((review) => (
        <ReviewCard key={review.checkpoint_id} review={review} />
      ))}
    </div>
  );
}

