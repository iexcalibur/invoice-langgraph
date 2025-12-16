"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { WorkflowCard } from "@/components/workflow/workflow-card";
import { useWorkflows } from "@/hooks/use-workflows";
import { useRouter } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export function RecentWorkflows() {
  const router = useRouter();
  const { data: workflowsData, isLoading } = useWorkflows({ page: 1, page_size: 5 });

  const workflows = workflowsData?.items || [];

  return (
    <Card className="glass p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">Recent Workflows</h2>
        <Button
          variant="ghost"
          onClick={() => router.push("/workflows")}
          className="text-white/60 hover:text-white"
        >
          View All
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>

      {isLoading ? (
        <div className="text-white/60 text-center py-8">Loading workflows...</div>
      ) : workflows.length === 0 ? (
        <div className="text-white/60 text-center py-8">
          <p className="mb-4">No workflows yet</p>
          <Button
            onClick={() => router.push("/invoke")}
            className="bg-white text-slate-900 hover:bg-white/90"
          >
            Process First Invoice
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {workflows.map((workflow) => (
            <WorkflowCard
              key={workflow.id}
              workflow={workflow}
              onClick={() => router.push(`/workflows/${workflow.workflow_id}`)}
            />
          ))}
        </div>
      )}
    </Card>
  );
}

