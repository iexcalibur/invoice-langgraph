"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StageBadge } from "./stage-badge";
import { StageID, WorkflowStatus } from "@/lib/types";
import { STAGES, STAGE_LABELS } from "@/lib/constants";

interface StageProgressProps {
  currentStage: StageID | null;
  status: WorkflowStatus;
  stages?: StageID[];
}

export function StageProgress({
  currentStage,
  status,
  stages = STAGES,
}: StageProgressProps) {
  const currentIndex = currentStage ? stages.indexOf(currentStage) : -1;

  return (
    <Card className="glass p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Stage Progress</h2>
      <div className="space-y-3">
        {stages.map((stage, index) => {
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;
          const isPending = index > currentIndex;

          return (
            <div key={stage} className="flex items-center gap-4">
              <div className="w-32 text-sm text-white/60">
                {STAGE_LABELS[stage]}
              </div>
              <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    isCompleted
                      ? "bg-green-500"
                      : isCurrent
                      ? "bg-blue-500 animate-pulse"
                      : "bg-white/10"
                  }`}
                  style={{
                    width: isCompleted || isCurrent ? "100%" : "0%",
                  }}
                />
              </div>
              <div className="w-24 text-right">
                {isCompleted && (
                  <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                    Done
                  </Badge>
                )}
                {isCurrent && (
                  <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                    Running
                  </Badge>
                )}
                {isPending && (
                  <span className="text-white/40 text-sm">Pending</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

