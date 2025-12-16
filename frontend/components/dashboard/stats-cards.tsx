"use client";

import { Card } from "@/components/ui/card";
import { useStats } from "@/hooks/use-stats";
import { TrendingUp, CheckCircle, Pause, XCircle, Activity } from "lucide-react";

const statConfigs = [
  {
    key: "total_workflows" as const,
    label: "Total Workflows",
    icon: Activity,
    color: "text-white",
  },
  {
    key: "running" as const,
    label: "Running",
    icon: TrendingUp,
    color: "text-blue-400",
  },
  {
    key: "completed" as const,
    label: "Completed",
    icon: CheckCircle,
    color: "text-green-400",
  },
  {
    key: "paused" as const,
    label: "Paused",
    icon: Pause,
    color: "text-orange-400",
  },
  {
    key: "failed" as const,
    label: "Failed",
    icon: XCircle,
    color: "text-red-400",
  },
];

export function StatsCards() {
  const { data: stats, isLoading } = useStats();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {statConfigs.map((config) => (
          <Card key={config.key} className="glass p-4">
            <div className="animate-pulse">
              <div className="h-4 bg-white/10 rounded mb-2 w-20"></div>
              <div className="h-8 bg-white/10 rounded w-16"></div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
      {statConfigs.map((config) => {
        const Icon = config.icon;
        const value = stats?.[config.key] || 0;

        return (
          <Card key={config.key} className="glass p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-white/60 text-sm">{config.label}</p>
              <Icon className={`w-5 h-5 ${config.color}`} />
            </div>
            <p className={`text-2xl font-bold ${config.color}`}>{value}</p>
          </Card>
        );
      })}
    </div>
  );
}

