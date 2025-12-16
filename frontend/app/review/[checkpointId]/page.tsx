"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useReview } from "@/hooks/use-reviews";
import { useDecision } from "@/hooks/use-decision";
import { format } from "date-fns";
import { ArrowLeft, CheckCircle, XCircle, AlertTriangle } from "lucide-react";

export default function ReviewDetailPage({ params }: { params: Promise<{ checkpointId: string }> }) {
  const { checkpointId } = use(params);
  const router = useRouter();
  const { data: review, isLoading } = useReview(checkpointId);
  const { mutate: submitDecision, isPending } = useDecision();
  const [notes, setNotes] = useState("");
  const [decision, setDecision] = useState<"ACCEPT" | "REJECT" | null>(null);

  if (isLoading) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-4xl mx-auto">
          <Card className="glass p-12 text-center">
            <p className="text-white/60">Loading review...</p>
          </Card>
        </div>
      </div>
    );
  }

  if (!review) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-4xl mx-auto">
          <Card className="glass p-12 text-center">
            <p className="text-white/60 mb-4">Review not found</p>
            <Button onClick={() => router.push("/review")}>
              Back to Reviews
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  const handleSubmit = () => {
    if (!decision) return;

    submitDecision({
      checkpoint_id: checkpointId,
      decision,
      reviewer_id: "reviewer_001", // TODO: Get from auth context
      notes: notes || undefined,
    });
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="text-white/60 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-white">Review Invoice</h1>
            <p className="text-white/60">{review.invoice_id}</p>
          </div>
        </div>

        {/* Invoice Details */}
        <Card className="glass p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Invoice Details</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-white/60 text-sm mb-1">Vendor</p>
              <p className="text-white font-medium">{review.vendor_name}</p>
            </div>
            <div>
              <p className="text-white/60 text-sm mb-1">Amount</p>
              <p className="text-white font-medium text-xl">
                {review.currency} {review.amount.toLocaleString()}
              </p>
            </div>
            {review.match_score !== null && (
              <div className="col-span-2">
                <p className="text-white/60 text-sm mb-2">Match Score</p>
                <div className="flex items-center gap-4">
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
                  <span className="text-white/60">
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

        {/* Decision */}
        <Card className="glass p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Your Decision</h2>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <button
              onClick={() => setDecision("ACCEPT")}
              className={`p-6 rounded-lg border-2 transition-all ${
                decision === "ACCEPT"
                  ? "border-green-500 bg-green-500/20"
                  : "border-white/10 hover:border-green-500/50"
              }`}
            >
              <CheckCircle className={`w-8 h-8 mx-auto mb-2 ${
                decision === "ACCEPT" ? "text-green-400" : "text-white/40"
              }`} />
              <p className={`font-semibold ${
                decision === "ACCEPT" ? "text-green-400" : "text-white/60"
              }`}>
                Accept
              </p>
              <p className="text-sm text-white/40 mt-1">
                Approve and continue workflow
              </p>
            </button>

            <button
              onClick={() => setDecision("REJECT")}
              className={`p-6 rounded-lg border-2 transition-all ${
                decision === "REJECT"
                  ? "border-red-500 bg-red-500/20"
                  : "border-white/10 hover:border-red-500/50"
              }`}
            >
              <XCircle className={`w-8 h-8 mx-auto mb-2 ${
                decision === "REJECT" ? "text-red-400" : "text-white/40"
              }`} />
              <p className={`font-semibold ${
                decision === "REJECT" ? "text-red-400" : "text-white/60"
              }`}>
                Reject
              </p>
              <p className="text-sm text-white/40 mt-1">
                Reject and stop workflow
              </p>
            </button>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes" className="text-white/80">
              Notes (Optional)
            </Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any additional notes about your decision..."
              className="bg-white/5 border-purple-500/20 text-white min-h-[100px]"
            />
          </div>
        </Card>

        {/* Submit */}
        <div className="flex justify-end gap-4">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="text-white/60 hover:text-white"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!decision || isPending}
            className={`${
              decision === "ACCEPT"
                ? "bg-green-500 hover:bg-green-600"
                : decision === "REJECT"
                ? "bg-red-500 hover:bg-red-600"
                : "bg-white/10"
            }`}
          >
            {isPending ? "Submitting..." : `Submit ${decision || "Decision"}`}
          </Button>
        </div>
      </div>
    </div>
  );
}

