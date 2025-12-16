"use client";

import { Card } from "@/components/ui/card";
import { JsonViewer } from "@/components/common/json-viewer";
import { Badge } from "@/components/ui/badge";
import { Database } from "lucide-react";

interface StateViewerProps {
  state: Record<string, any>;
  title?: string;
}

export function StateViewer({ state, title = "Workflow State" }: StateViewerProps) {
  return (
    <Card className="glass p-6">
      <div className="flex items-center gap-2 mb-4">
        <Database className="w-5 h-5 text-white/60" />
        <h2 className="text-xl font-semibold text-white">{title}</h2>
        <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">
          {Object.keys(state).length} fields
        </Badge>
      </div>
      <JsonViewer data={state} defaultExpanded={false} />
    </Card>
  );
}

