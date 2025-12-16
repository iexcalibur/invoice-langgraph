/**
 * Server-Sent Events (SSE) helper for real-time log streaming
 */

export interface SSEOptions {
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

export class SSEClient {
  private eventSource: EventSource | null = null;
  private url: string;
  private options: SSEOptions;

  constructor(url: string, options: SSEOptions = {}) {
    this.url = url;
    this.options = options;
  }

  connect(): void {
    if (this.eventSource) {
      this.close();
    }

    this.eventSource = new EventSource(this.url);

    this.eventSource.onopen = () => {
      this.options.onOpen?.();
    };

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.options.onMessage?.(data);
      } catch (error) {
        console.error("Failed to parse SSE message:", error);
      }
    };

    this.eventSource.onerror = (error) => {
      this.options.onError?.(error);
    };
  }

  close(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.options.onClose?.();
    }
  }

  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}

export function createSSEConnection(
  workflowId: string,
  options: SSEOptions
): SSEClient {
  const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/workflows/${workflowId}/logs/stream`;
  const client = new SSEClient(url, options);
  client.connect();
  return client;
}

