"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { HumanReview } from "@/lib/types";
import { format } from "date-fns";
import { AlertCircle, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";

interface ReviewCardProps {
  review: HumanReview;
  onClick?: () => void;
}

export function ReviewCard({ review, onClick }: ReviewCardProps) {
  const router = useRouter();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      router.push(`/review/${review.checkpoint_id}`);
    }
  };

  return (
    <Card
      className="glass p-6 cursor-pointer hover:border-purple-500/50 transition-all"
      onClick={handleClick}
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

      <div className="pt-4 border-t border-white/10 mb-4">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-orange-400 mt-0.5" />
          <p className="text-sm text-white/80 line-clamp-2">
            {review.reason_for_hold}
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-white/40">
        <span>
          Created {format(new Date(review.created_at), "MMM dd, HH:mm")}
        </span>
        <ArrowRight className="w-4 h-4" />
      </div>
    </Card>
  );
}

