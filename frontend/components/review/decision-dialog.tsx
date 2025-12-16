"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { CheckCircle, XCircle } from "lucide-react";
import { HumanDecision } from "@/lib/types";

interface DecisionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (decision: HumanDecision) => void;
  isSubmitting?: boolean;
}

export function DecisionDialog({
  open,
  onOpenChange,
  onSubmit,
  isSubmitting,
}: DecisionDialogProps) {
  const [decision, setDecision] = useState<"ACCEPT" | "REJECT" | null>(null);
  const [notes, setNotes] = useState("");

  const handleSubmit = () => {
    if (!decision) return;

    onSubmit({
      checkpoint_id: "", // Should be passed as prop
      decision,
      reviewer_id: "reviewer_001", // TODO: Get from auth
      notes: notes || undefined,
    });

    // Reset form
    setDecision(null);
    setNotes("");
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="glass border-purple-500/20">
        <DialogHeader>
          <DialogTitle className="text-white">Submit Review Decision</DialogTitle>
          <DialogDescription className="text-white/60">
            Choose to accept or reject this invoice
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setDecision("ACCEPT")}
              className={`p-4 rounded-lg border-2 transition-all ${
                decision === "ACCEPT"
                  ? "border-green-500 bg-green-500/20"
                  : "border-white/10 hover:border-green-500/50"
              }`}
            >
              <CheckCircle
                className={`w-6 h-6 mx-auto mb-2 ${
                  decision === "ACCEPT" ? "text-green-400" : "text-white/40"
                }`}
              />
              <p
                className={`font-semibold ${
                  decision === "ACCEPT" ? "text-green-400" : "text-white/60"
                }`}
              >
                Accept
              </p>
            </button>

            <button
              onClick={() => setDecision("REJECT")}
              className={`p-4 rounded-lg border-2 transition-all ${
                decision === "REJECT"
                  ? "border-red-500 bg-red-500/20"
                  : "border-white/10 hover:border-red-500/50"
              }`}
            >
              <XCircle
                className={`w-6 h-6 mx-auto mb-2 ${
                  decision === "REJECT" ? "text-red-400" : "text-white/40"
                }`}
              />
              <p
                className={`font-semibold ${
                  decision === "REJECT" ? "text-red-400" : "text-white/60"
                }`}
              >
                Reject
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
              placeholder="Add any additional notes..."
              className="bg-white/5 border-purple-500/20 text-white"
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="ghost"
            onClick={() => onOpenChange(false)}
            className="text-white/60 hover:text-white"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!decision || isSubmitting}
            className={`${
              decision === "ACCEPT"
                ? "bg-green-500 hover:bg-green-600"
                : decision === "REJECT"
                ? "bg-red-500 hover:bg-red-600"
                : "bg-white/10"
            }`}
          >
            {isSubmitting ? "Submitting..." : `Submit ${decision || "Decision"}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

