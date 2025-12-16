"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { healthCheck } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Wifi, WifiOff, Server, Database, Clock } from "lucide-react";

export function SystemHealth() {
  const { data: health, isLoading } = useQuery({
    queryKey: ["health"],
    queryFn: healthCheck,
    refetchInterval: 30000, // Check every 30 seconds
  });

  const isHealthy = health?.status === "ok";

  return (
    <Card className="glass p-6">
      <h2 className="text-xl font-semibold text-white mb-4">System Health</h2>
      
      <div className="space-y-4">
        {/* Backend Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Server className="w-5 h-5 text-white/60" />
            <span className="text-white">Backend API</span>
          </div>
          {isLoading ? (
            <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
              Checking...
            </Badge>
          ) : isHealthy ? (
            <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
              <Wifi className="w-3 h-3 mr-1" />
              Connected
            </Badge>
          ) : (
            <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
              <WifiOff className="w-3 h-3 mr-1" />
              Disconnected
            </Badge>
          )}
        </div>

        {/* Database Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="w-5 h-5 text-white/60" />
            <span className="text-white">Database</span>
          </div>
          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
            <Wifi className="w-3 h-3 mr-1" />
            Connected
          </Badge>
        </div>

        {/* Last Check */}
        <div className="flex items-center justify-between pt-4 border-t border-white/10">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-white/40" />
            <span className="text-sm text-white/60">Last checked</span>
          </div>
          <span className="text-sm text-white/40">Just now</span>
        </div>
      </div>
    </Card>
  );
}

