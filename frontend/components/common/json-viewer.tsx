"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CopyButton } from "./copy-button";
import { ChevronDown, ChevronRight } from "lucide-react";

interface JsonViewerProps {
  data: any;
  title?: string;
  defaultExpanded?: boolean;
  className?: string;
}

function JsonNode({ data, level = 0 }: { data: any; level?: number }) {
  const [expanded, setExpanded] = useState(level < 2);

  if (data === null) {
    return <span className="text-purple-400">null</span>;
  }

  if (typeof data === "string") {
    return <span className="text-green-400">"{data}"</span>;
  }

  if (typeof data === "number") {
    return <span className="text-blue-400">{data}</span>;
  }

  if (typeof data === "boolean") {
    return <span className="text-orange-400">{data.toString()}</span>;
  }

  if (Array.isArray(data)) {
    return (
      <div className="ml-4">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-1 text-white/60 hover:text-white"
        >
          {expanded ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
          <span>[{data.length}]</span>
        </button>
        {expanded && (
          <div className="ml-4 border-l border-white/10 pl-2">
            {data.map((item, index) => (
              <div key={index} className="py-1">
                <span className="text-white/40">{index}: </span>
                <JsonNode data={item} level={level + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (typeof data === "object") {
    const keys = Object.keys(data);
    return (
      <div className="ml-4">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-1 text-white/60 hover:text-white"
        >
          {expanded ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
          <span>{`{${keys.length}}`}</span>
        </button>
        {expanded && (
          <div className="ml-4 border-l border-white/10 pl-2">
            {keys.map((key) => (
              <div key={key} className="py-1">
                <span className="text-white/60">"{key}": </span>
                <JsonNode data={data[key]} level={level + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return <span className="text-white/40">{String(data)}</span>;
}

export function JsonViewer({ data, title, defaultExpanded = true, className }: JsonViewerProps) {
  const jsonString = JSON.stringify(data, null, 2);

  return (
    <Card className={`glass p-4 ${className}`}>
      {(title || jsonString) && (
        <div className="flex items-center justify-between mb-4">
          {title && <h3 className="text-sm font-semibold text-white">{title}</h3>}
          <CopyButton text={jsonString} label="Copy JSON" />
        </div>
      )}
      <div className="font-mono text-sm overflow-x-auto">
        <JsonNode data={data} level={0} />
      </div>
    </Card>
  );
}

