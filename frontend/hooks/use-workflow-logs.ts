/**
 * Hook for subscribing to workflow logs via SSE
 */

import { useEffect, useState, useRef, useCallback } from "react";
import { SSEClient } from "@/lib/sse";
import { LogEntry } from "@/lib/types";

export function useWorkflowLogs(workflowId: string | null) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const sseClientRef = useRef<SSEClient | null>(null);
  const seenLogIds = useRef<Set<number>>(new Set());
  const isCompleteRef = useRef(false);

  useEffect(() => {
    if (!workflowId) {
      return;
    }

    // Reset state when workflow changes
    seenLogIds.current = new Set();
    isCompleteRef.current = false;
    setLogs([]);
    setIsComplete(false);

    const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/logs/${workflowId}/stream`;
    
    const client = new SSEClient(url, {
      onOpen: () => {
        setIsConnected(true);
      },
      onMessage: (data: LogEntry & { event?: string; id?: number }) => {
        // Handle workflow completion - stop reconnecting
        if (data.event === "workflow_complete") {
          isCompleteRef.current = true;
          setIsComplete(true);
          setIsConnected(true); // Mark as "connected" (complete)
          client.close();
          return;
        }
        
        // Skip other system events
        if (data.event === "timeout" || data.event === "workflow_paused" || data.event === "error") {
          return;
        }
        
        // Deduplicate by log ID if available
        if (data.id && seenLogIds.current.has(data.id)) {
          return;
        }
        
        if (data.id) {
          seenLogIds.current.add(data.id);
        }
        
        setLogs((prev) => [...prev, data]);
      },
      onError: () => {
        // Don't show disconnected if workflow is already complete
        if (!isCompleteRef.current) {
          setIsConnected(false);
        }
      },
      onClose: () => {
        // Don't show disconnected if workflow is already complete
        if (!isCompleteRef.current) {
          setIsConnected(false);
        }
      },
    });

    client.connect();
    sseClientRef.current = client;

    return () => {
      client.close();
      sseClientRef.current = null;
    };
  }, [workflowId]);

  const clearLogs = useCallback(() => {
    setLogs([]);
    seenLogIds.current = new Set();
  }, []);

  return {
    logs,
    isConnected,
    isComplete,
    clearLogs,
  };
}

