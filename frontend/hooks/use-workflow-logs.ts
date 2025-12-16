/**
 * Hook for subscribing to workflow logs via SSE
 */

import { useEffect, useState, useRef } from "react";
import { SSEClient } from "@/lib/sse";
import { LogEntry } from "@/lib/types";

export function useWorkflowLogs(workflowId: string | null) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const sseClientRef = useRef<SSEClient | null>(null);

  useEffect(() => {
    if (!workflowId) {
      return;
    }

    const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/workflows/${workflowId}/logs/stream`;
    
    const client = new SSEClient(url, {
      onOpen: () => {
        setIsConnected(true);
      },
      onMessage: (data: LogEntry) => {
        setLogs((prev) => [...prev, data]);
      },
      onError: (error) => {
        console.error("SSE error:", error);
        setIsConnected(false);
      },
      onClose: () => {
        setIsConnected(false);
      },
    });

    client.connect();
    sseClientRef.current = client;

    return () => {
      client.close();
      sseClientRef.current = null;
    };
  }, [workflowId]);

  const clearLogs = () => {
    setLogs([]);
  };

  return {
    logs,
    isConnected,
    clearLogs,
  };
}

