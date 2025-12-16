"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useWorkflowLogs } from "@/hooks/use-workflow-logs";
import { LogEntry } from "@/lib/types";
import { formatIST } from "@/lib/utils";
import { Trash2, Wifi, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface LogViewerProps {
  workflowId: string | null;
  autoScroll?: boolean;
}

export function LogViewer({ workflowId, autoScroll = true }: LogViewerProps) {
  const { logs, isConnected, clearLogs } = useWorkflowLogs(workflowId);

  return (
    <Card className="glass p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h2 className="text-xl font-semibold text-white">Execution Logs</h2>
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
        </div>
        {logs.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearLogs}
            className="text-white/60 hover:text-white"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear
          </Button>
        )}
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {logs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-white/60">No logs yet</p>
            <p className="text-white/40 text-sm mt-2">
              Logs will appear here as the workflow executes
            </p>
          </div>
        ) : (
          logs.map((log, index) => (
            <LogEntryItem key={index} log={log} />
          ))
        )}
      </div>
    </Card>
  );
}

function LogEntryItem({ log }: { log: LogEntry }) {
  const getLogColor = (eventType: string) => {
    if (eventType.includes("error") || eventType.includes("fail")) {
      return "border-red-500/30 bg-red-500/10";
    }
    if (eventType.includes("success") || eventType.includes("complete")) {
      return "border-green-500/30 bg-green-500/10";
    }
    return "border-white/10 bg-white/5";
  };

  return (
    <div
      className={`p-3 rounded border ${getLogColor(log.event_type)} transition-all`}
    >
      <div className="flex items-start justify-between mb-1">
        <div className="flex items-center gap-2">
          {log.stage_id && (
            <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
              {log.stage_id}
            </Badge>
          )}
          <span className="text-xs text-white/60">{log.event_type}</span>
        </div>
        <span className="text-xs text-white/40">
          {formatIST(log.created_at, "time")}
        </span>
      </div>
      <p className="text-sm text-white/80">{log.message}</p>
      {log.details && (
        <details className="mt-2">
          <summary className="text-xs text-white/60 cursor-pointer hover:text-white/80">
            View Details
          </summary>
          <pre className="mt-2 text-xs text-white/60 overflow-x-auto p-2 bg-black/20 rounded">
            {JSON.stringify(log.details, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}

