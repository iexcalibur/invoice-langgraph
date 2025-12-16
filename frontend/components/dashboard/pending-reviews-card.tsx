"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useReviews } from "@/hooks/use-reviews";
import { AlertCircle, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";

export function PendingReviewsCard() {
  const router = useRouter();
  const { data: reviewsData, isLoading } = useReviews({ page: 1, page_size: 5 });

  const pendingCount = reviewsData?.total || 0;
  const highPriorityCount = reviewsData?.items.filter((r) => r.priority > 7).length || 0;

  return (
    <Card
      className="glass p-6 cursor-pointer hover:border-orange-500/50 transition-all"
      onClick={() => router.push("/review")}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center">
            <AlertCircle className="w-6 h-6 text-orange-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Pending Reviews</h3>
            <p className="text-sm text-white/60">Requires human attention</p>
          </div>
        </div>
        <ArrowRight className="w-5 h-5 text-white/40" />
      </div>

      {isLoading ? (
        <div className="text-white/60">Loading...</div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-3xl font-bold text-white">{pendingCount}</span>
            <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30">
              {highPriorityCount} High Priority
            </Badge>
          </div>
          {pendingCount === 0 && (
            <p className="text-sm text-white/60">All reviews completed</p>
          )}
        </div>
      )}
    </Card>
  );
}

