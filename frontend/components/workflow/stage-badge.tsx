"use client";

import { Badge } from "@/components/ui/badge";
import { StageID, WorkflowStatus } from "@/lib/types";
import { STAGE_LABELS, STAGE_COLORS, STATUS_BADGE_COLORS } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface StageBadgeProps {
  stage: StageID;
  status?: WorkflowStatus;
  isCurrent?: boolean;
  className?: string;
}

export function StageBadge({ stage, status, isCurrent, className }: StageBadgeProps) {
  const label = STAGE_LABELS[stage];
  const color = STAGE_COLORS[stage];
  
  return (
    <Badge
      className={cn(
        "border",
        isCurrent && "ring-2 ring-purple-500",
        status === "COMPLETED" && "bg-green-500/20 text-green-400 border-green-500/30",
        status === "FAILED" && "bg-red-500/20 text-red-400 border-red-500/30",
        status === "RUNNING" && "bg-blue-500/20 text-blue-400 border-blue-500/30 animate-pulse",
        status === "PAUSED" && "bg-orange-500/20 text-orange-400 border-orange-500/30",
        !status && `bg-${color}/20 text-white/60 border-${color}/30`,
        className
      )}
    >
      {label}
    </Badge>
  );
}

