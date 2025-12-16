"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StageID, WorkflowStatus } from "@/lib/types";
import { STAGE_LABELS, STATUS_BADGE_COLORS } from "@/lib/constants";
import { format } from "date-fns";
import { Clock, CheckCircle, XCircle, Loader2 } from "lucide-react";

interface StageDetailProps {
  stage: StageID;
  status: WorkflowStatus;
  startedAt?: string | null;
  completedAt?: string | null;
  output?: Record<string, any>;
  error?: string | null;
}

export function StageDetail({
  stage,
  status,
  startedAt,
  completedAt,
  output,
  error,
}: StageDetailProps) {
  const getStatusIcon = () => {
    if (error) return <XCircle className="w-5 h-5 text-red-400" />;
    if (completedAt) return <CheckCircle className="w-5 h-5 text-green-400" />;
    if (startedAt) return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
    return <Clock className="w-5 h-5 text-white/40" />;
  };

  const getStatusBadge = () => {
    if (error) return "bg-red-500/20 text-red-400 border-red-500/30";
    if (completedAt) return "bg-green-500/20 text-green-400 border-green-500/30";
    if (startedAt) return "bg-blue-500/20 text-blue-400 border-blue-500/30";
    return "bg-white/10 text-white/60 border-white/20";
  };

  return (
    <Card className="glass p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-lg font-semibold text-white">
              {STAGE_LABELS[stage]}
            </h3>
            <p className="text-sm text-white/60">Stage: {stage}</p>
          </div>
        </div>
        <Badge className={getStatusBadge()}>
          {error ? "Failed" : completedAt ? "Completed" : startedAt ? "Running" : "Pending"}
        </Badge>
      </div>

      <div className="space-y-3 pt-4 border-t border-white/10">
        {startedAt && (
          <div>
            <p className="text-white/60 text-sm mb-1">Started</p>
            <p className="text-white">
              {format(new Date(startedAt), "MMM dd, yyyy HH:mm:ss")}
            </p>
          </div>
        )}
        {completedAt && (
          <div>
            <p className="text-white/60 text-sm mb-1">Completed</p>
            <p className="text-white">
              {format(new Date(completedAt), "MMM dd, yyyy HH:mm:ss")}
            </p>
          </div>
        )}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded">
            <p className="text-red-400 text-sm font-medium mb-1">Error</p>
            <p className="text-white/80 text-sm">{error}</p>
          </div>
        )}
        {output && Object.keys(output).length > 0 && (
          <div>
            <p className="text-white/60 text-sm mb-2">Output</p>
            <pre className="text-xs text-white/60 bg-black/20 p-3 rounded overflow-x-auto">
              {JSON.stringify(output, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </Card>
  );
}

