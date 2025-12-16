"use client";

import { Table } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { StageBadge } from "./stage-badge";
import { Workflow } from "@/lib/types";
import { STATUS_BADGE_COLORS } from "@/lib/constants";
import { formatIST } from "@/lib/utils";
import { useRouter } from "next/navigation";

interface WorkflowTableProps {
  workflows: Workflow[];
}

export function WorkflowTable({ workflows }: WorkflowTableProps) {
  const router = useRouter();

  return (
    <div className="rounded-lg border border-purple-500/20 overflow-hidden">
      <Table>
        <thead className="bg-white/5">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
              Invoice ID
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
              Current Stage
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
              Match Score
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
              Started
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-white/60 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/10">
          {workflows.map((workflow) => (
            <tr
              key={workflow.id}
              className="hover:bg-white/5 cursor-pointer transition-colors"
              onClick={() => router.push(`/workflows/${workflow.workflow_id}`)}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-white">
                  {workflow.invoice_id}
                </div>
                <div className="text-xs text-white/40">
                  {workflow.workflow_id}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <Badge className={STATUS_BADGE_COLORS[workflow.status]}>
                  {workflow.status}
                </Badge>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {workflow.current_stage ? (
                  <StageBadge
                    stage={workflow.current_stage}
                    status={workflow.status}
                    isCurrent={true}
                  />
                ) : (
                  <span className="text-sm text-white/40">-</span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {workflow.match_score !== null ? (
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          workflow.match_score >= 0.8
                            ? "bg-green-500"
                            : workflow.match_score >= 0.5
                            ? "bg-yellow-500"
                            : "bg-red-500"
                        }`}
                        style={{ width: `${workflow.match_score * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-white/60">
                      {Math.round(workflow.match_score * 100)}%
                    </span>
                  </div>
                ) : (
                  <span className="text-sm text-white/40">-</span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-white/60">
                {formatIST(workflow.started_at, "short")}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    router.push(`/workflows/${workflow.workflow_id}`);
                  }}
                  className="text-purple-400 hover:text-purple-300"
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

