"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StageBadge } from "@/components/workflow/stage-badge";
import { useWorkflow } from "@/hooks/use-workflows";
import { useWorkflowLogs } from "@/hooks/use-workflow-logs";
import { STAGES, STAGE_LABELS, STATUS_BADGE_COLORS } from "@/lib/constants";
import { format } from "date-fns";
import { ArrowLeft, RefreshCw, Wifi, WifiOff } from "lucide-react";

export default function WorkflowDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { data: workflow, isLoading, refetch } = useWorkflow(id);
  const { logs, isConnected } = useWorkflowLogs(id);

  if (isLoading) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="glass p-12 text-center">
            <p className="text-white/60">Loading workflow...</p>
          </Card>
        </div>
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="glass p-12 text-center">
            <p className="text-white/60 mb-4">Workflow not found</p>
            <Button onClick={() => router.push("/workflows")}>
              Back to Workflows
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  const currentStageIndex = workflow.current_stage
    ? STAGES.indexOf(workflow.current_stage)
    : -1;

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
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
              <h1 className="text-3xl font-bold text-white">{workflow.invoice_id}</h1>
              <p className="text-white/60">Workflow ID: {workflow.workflow_id}</p>
            </div>
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
              onClick={() => refetch()}
              className="text-white/60 hover:text-white"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Status Card */}
        <Card className="glass p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-white/60 text-sm mb-1">Status</p>
              <Badge className={STATUS_BADGE_COLORS[workflow.status]}>
                {workflow.status}
              </Badge>
            </div>
            <div>
              <p className="text-white/60 text-sm mb-1">Current Stage</p>
              {workflow.current_stage ? (
                <StageBadge stage={workflow.current_stage} status={workflow.status} isCurrent />
              ) : (
                <span className="text-white/40">-</span>
              )}
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
                  ? format(new Date(workflow.started_at), "MMM dd, yyyy HH:mm")
                  : "-"}
              </p>
            </div>
          </div>
        </Card>

        {/* Stage Progress */}
        <Card className="glass p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Stage Progress</h2>
          <div className="space-y-2">
            {STAGES.map((stage, index) => {
              const isCompleted = index < currentStageIndex;
              const isCurrent = index === currentStageIndex;
              const isPending = index > currentStageIndex;

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

        {/* Logs */}
        <Card className="glass p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Execution Logs</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-white/40 text-center py-8">No logs yet</p>
            ) : (
              logs.map((log, index) => (
                <div
                  key={index}
                  className="p-3 bg-white/5 rounded border border-white/10"
                >
                  <div className="flex items-start justify-between mb-1">
                    <span className="text-sm font-medium text-white">
                      {log.stage_id || "System"}
                    </span>
                    <span className="text-xs text-white/40">
                      {format(new Date(log.created_at), "HH:mm:ss")}
                    </span>
                  </div>
                  <p className="text-sm text-white/80">{log.message}</p>
                  {log.details && (
                    <pre className="mt-2 text-xs text-white/60 overflow-x-auto">
                      {JSON.stringify(log.details, null, 2)}
                    </pre>
                  )}
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}

