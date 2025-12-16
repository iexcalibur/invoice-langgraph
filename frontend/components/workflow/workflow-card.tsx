"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StageBadge } from "./stage-badge";
import { Workflow } from "@/lib/types";
import { STATUS_BADGE_COLORS, STAGE_LABELS } from "@/lib/constants";
import { cn, formatIST } from "@/lib/utils";
import { ArrowRight, Clock, CheckCircle, XCircle, Pause } from "lucide-react";

interface WorkflowCardProps {
  workflow: Workflow;
  onClick?: () => void;
}

const statusIcons = {
  PENDING: Clock,
  RUNNING: Clock,
  COMPLETED: CheckCircle,
  FAILED: XCircle,
  PAUSED: Pause,
  MANUAL_HANDOFF: Pause,
};

export function WorkflowCard({ workflow, onClick }: WorkflowCardProps) {
  const StatusIcon = statusIcons[workflow.status] || Clock;
  
  return (
    <Card
      className={cn(
        "p-6 cursor-pointer transition-all hover:border-purple-500/50 hover:shadow-lg",
        onClick && "hover:scale-[1.02]"
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-white">
              {workflow.invoice_id}
            </h3>
            <Badge className={cn("border", STATUS_BADGE_COLORS[workflow.status])}>
              <StatusIcon className="w-3 h-3 mr-1" />
              {workflow.status}
            </Badge>
          </div>
          <p className="text-sm text-white/60">
            Workflow ID: {workflow.workflow_id}
          </p>
        </div>
        {onClick && (
          <ArrowRight className="w-5 h-5 text-white/40" />
        )}
      </div>

      {workflow.current_stage && (
        <div className="mb-4">
          <p className="text-xs text-white/40 mb-2">Current Stage</p>
          <StageBadge
            stage={workflow.current_stage}
            status={workflow.status}
            isCurrent={true}
          />
        </div>
      )}

      {workflow.match_score !== null && (
        <div className="mb-4">
          <p className="text-xs text-white/40 mb-1">Match Score</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full transition-all",
                  workflow.match_score >= 0.8
                    ? "bg-green-500"
                    : workflow.match_score >= 0.5
                    ? "bg-yellow-500"
                    : "bg-red-500"
                )}
                style={{ width: `${workflow.match_score * 100}%` }}
              />
            </div>
            <span className="text-sm text-white/60">
              {Math.round(workflow.match_score * 100)}%
            </span>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-white/40">
        <span>
          {workflow.started_at
            ? `Started ${formatIST(workflow.started_at, "short")}`
            : "Not started"}
        </span>
        {workflow.completed_at && (
          <span>
            Completed {formatIST(workflow.completed_at, "short")}
          </span>
        )}
      </div>
    </Card>
  );
}

