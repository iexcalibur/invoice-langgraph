"use client";

import { WorkflowDetail as WorkflowDetailType } from "@/lib/types";
import { StageProgress } from "./stage-progress";
import { LogViewer } from "./log-viewer";
import { StateViewer } from "./state-viewer";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useWorkflow } from "@/hooks/use-workflows";
import { STATUS_BADGE_COLORS } from "@/lib/constants";
import { format } from "date-fns";
import { RefreshCw, Wifi, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WorkflowDetailProps {
  workflowId: string;
}

export function WorkflowDetail({ workflowId }: WorkflowDetailProps) {
  const { data: workflow, isLoading, refetch } = useWorkflow(workflowId);
  const { isConnected } = useWorkflowLogs(workflowId);

  if (isLoading) {
    return (
      <Card className="glass p-12 text-center">
        <p className="text-white/60">Loading workflow...</p>
      </Card>
    );
  }

  if (!workflow) {
    return (
      <Card className="glass p-12 text-center">
        <p className="text-white/60 mb-4">Workflow not found</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="glass p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">
              {workflow.invoice_id}
            </h1>
            <p className="text-white/60">Workflow ID: {workflow.workflow_id}</p>
          </div>
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                <Wifi className="w-3 h-3 mr-1" />
                Live
              </Badge>
            ) : (
              <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                <WifiOff className="w-3 h-3 mr-1" />
                Disconnected
              </Badge>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => refetch()}
              className="text-white/60 hover:text-white"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-white/60 text-sm mb-1">Status</p>
            <Badge className={STATUS_BADGE_COLORS[workflow.status]}>
              {workflow.status}
            </Badge>
          </div>
          {workflow.match_score !== null && (
            <div>
              <p className="text-white/60 text-sm mb-1">Match Score</p>
              <p className="text-xl font-bold text-white">
                {Math.round(workflow.match_score * 100)}%
              </p>
            </div>
          )}
          <div>
            <p className="text-white/60 text-sm mb-1">Started</p>
            <p className="text-white">
              {workflow.started_at
                ? format(new Date(workflow.started_at), "MMM dd, HH:mm")
                : "-"}
            </p>
          </div>
          <div>
            <p className="text-white/60 text-sm mb-1">Completed</p>
            <p className="text-white">
              {workflow.completed_at
                ? format(new Date(workflow.completed_at), "MMM dd, HH:mm")
                : "-"}
            </p>
          </div>
        </div>
      </Card>

      {/* Stage Progress */}
      <StageProgress
        currentStage={workflow.current_stage}
        status={workflow.status}
      />

      {/* State Viewer */}
      {workflow.state_data && (
        <StateViewer state={workflow.state_data} />
      )}

      {/* Logs */}
      <LogViewer workflowId={workflowId} />
    </div>
  );
}

