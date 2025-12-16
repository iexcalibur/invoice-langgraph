"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { HumanReview } from "@/lib/types";
import { formatIST } from "@/lib/utils";
import { Building2, DollarSign, Calendar, AlertTriangle } from "lucide-react";

interface ReviewDetailProps {
  review: HumanReview;
}

export function ReviewDetail({ review }: ReviewDetailProps) {
  return (
    <div className="space-y-6">
      {/* Invoice Info */}
      <Card className="glass p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Invoice Information</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-start gap-3">
            <Building2 className="w-5 h-5 text-white/60 mt-0.5" />
            <div>
              <p className="text-white/60 text-sm">Vendor</p>
              <p className="text-white font-medium">{review.vendor_name}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <DollarSign className="w-5 h-5 text-white/60 mt-0.5" />
            <div>
              <p className="text-white/60 text-sm">Amount</p>
              <p className="text-white font-medium text-xl">
                {review.currency} {review.amount.toLocaleString()}
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Calendar className="w-5 h-5 text-white/60 mt-0.5" />
            <div>
              <p className="text-white/60 text-sm">Created</p>
              <p className="text-white font-medium">
                {formatIST(review.created_at, "datetime")}
              </p>
            </div>
          </div>
          {review.match_score !== null && (
            <div>
              <p className="text-white/60 text-sm mb-2">Match Score</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-3 bg-white/10 rounded-full overflow-hidden">
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
                <span className="text-white font-medium">
                  {Math.round(review.match_score * 100)}%
                </span>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Reason for Hold */}
      <Card className="glass p-6 border-orange-500/30">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-orange-400 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-2">Reason for Hold</h3>
            <p className="text-white/80">{review.reason_for_hold}</p>
          </div>
        </div>
      </Card>

      {/* Status */}
      <Card className="glass p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/60 text-sm">Status</p>
            <Badge
              className={
                review.status === "PENDING"
                  ? "bg-orange-500/20 text-orange-400 border-orange-500/30"
                  : "bg-green-500/20 text-green-400 border-green-500/30"
              }
            >
              {review.status}
            </Badge>
          </div>
          {review.expires_at && (
            <div className="text-right">
              <p className="text-white/60 text-sm">Expires</p>
              <p className="text-white">
                {formatIST(review.expires_at, "date")}
              </p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}

