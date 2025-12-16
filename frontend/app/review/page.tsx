"use client";

import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useReviews } from "@/hooks/use-reviews";
import { formatIST } from "@/lib/utils";
import { AlertCircle, CheckCircle, XCircle, RefreshCw } from "lucide-react";

export default function ReviewPage() {
  const router = useRouter();
  const { data: reviewsData, isLoading, refetch } = useReviews({ page: 1, page_size: 50 });

  if (isLoading) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="glass p-12 text-center">
            <p className="text-white/60">Loading reviews...</p>
          </Card>
        </div>
      </div>
    );
  }

  const reviews = reviewsData?.items || [];

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Review Queue</h1>
            <p className="text-white/60">
              {reviews.length} pending review{reviews.length !== 1 ? "s" : ""}
            </p>
          </div>
          <Button
            variant="ghost"
            onClick={() => refetch()}
            className="text-white/60 hover:text-white"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>

        {/* Reviews Grid */}
        {reviews.length === 0 ? (
          <Card className="glass p-12 text-center">
            <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
            <p className="text-white/60 text-lg mb-2">All caught up!</p>
            <p className="text-white/40">No pending reviews at this time.</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {reviews.map((review) => (
              <Card
                key={review.checkpoint_id}
                className="glass p-6 cursor-pointer hover:border-purple-500/50 transition-all"
                onClick={() => router.push(`/review/${review.checkpoint_id}`)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">
                      {review.invoice_id}
                    </h3>
                    <p className="text-sm text-white/60">{review.vendor_name}</p>
                  </div>
                  <Badge
                    className={
                      review.priority > 7
                        ? "bg-red-500/20 text-red-400 border-red-500/30"
                        : review.priority > 4
                        ? "bg-orange-500/20 text-orange-400 border-orange-500/30"
                        : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                    }
                  >
                    Priority {review.priority}
                  </Badge>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-white/60">Amount</span>
                    <span className="text-lg font-bold text-white">
                      {review.currency} {review.amount.toLocaleString()}
                    </span>
                  </div>
                  {review.match_score !== null && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-white/60">Match Score</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-2 bg-white/10 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              review.match_score >= 0.8
                                ? "bg-green-500"
                                : review.match_score >= 0.5
                                ? "bg-yellow-500"
                                : "bg-red-500"
                            }`}
                            style={{ width: `${review.match_score * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-white/60">
                          {Math.round(review.match_score * 100)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="pt-4 border-t border-white/10">
                  <p className="text-sm text-white/60 mb-2">Reason for Hold</p>
                  <p className="text-sm text-white/80">{review.reason_for_hold}</p>
                </div>

                <div className="mt-4 flex items-center justify-between text-xs text-white/40">
                  <span>
                    Created {formatIST(review.created_at, "short")}
                  </span>
                  {review.expires_at && (
                    <span>
                      Expires {formatIST(review.expires_at, "date")}
                    </span>
                  )}
                </div>

                <Button
                  className="w-full mt-4 bg-purple-500 hover:bg-purple-600"
                  onClick={(e) => {
                    e.stopPropagation();
                    router.push(`/review/${review.checkpoint_id}`);
                  }}
                >
                  Review Now
                </Button>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

