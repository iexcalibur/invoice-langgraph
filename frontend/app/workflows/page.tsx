"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { WorkflowTable } from "@/components/workflow/workflow-table";
import { useWorkflows, useStats } from "@/hooks/use-workflows";
import { Plus, RefreshCw, Search } from "lucide-react";

export default function WorkflowsPage() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");

  const { data: workflowsData, isLoading, refetch } = useWorkflows({
    page,
    page_size: 20,
    status: statusFilter || undefined,
  });

  const { data: stats } = useStats();

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Workflows</h1>
            <p className="text-white/60">Monitor invoice processing workflows</p>
          </div>
          <Button
            onClick={() => router.push("/invoke")}
            className="bg-white text-slate-900 hover:bg-white/90"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Invoice
          </Button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Card className="glass p-4">
              <p className="text-white/60 text-sm mb-1">Total</p>
              <p className="text-2xl font-bold text-white">{stats.total_workflows}</p>
            </Card>
            <Card className="glass p-4">
              <p className="text-white/60 text-sm mb-1">Running</p>
              <p className="text-2xl font-bold text-blue-400">{stats.running}</p>
            </Card>
            <Card className="glass p-4">
              <p className="text-white/60 text-sm mb-1">Completed</p>
              <p className="text-2xl font-bold text-green-400">{stats.completed}</p>
            </Card>
            <Card className="glass p-4">
              <p className="text-white/60 text-sm mb-1">Paused</p>
              <p className="text-2xl font-bold text-orange-400">{stats.paused}</p>
            </Card>
            <Card className="glass p-4">
              <p className="text-white/60 text-sm mb-1">Failed</p>
              <p className="text-2xl font-bold text-red-400">{stats.failed}</p>
            </Card>
          </div>
        )}

        {/* Filters */}
        <Card className="glass p-4">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/40" />
              <Input
                placeholder="Search by invoice ID or workflow ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-white/5 border-purple-500/20 text-white pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 bg-white/5 border border-purple-500/20 rounded-md text-white"
            >
              <option value="">All Status</option>
              <option value="PENDING">Pending</option>
              <option value="RUNNING">Running</option>
              <option value="PAUSED">Paused</option>
              <option value="COMPLETED">Completed</option>
              <option value="FAILED">Failed</option>
            </select>
            <Button
              variant="ghost"
              onClick={() => refetch()}
              className="text-white/60 hover:text-white"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </Card>

        {/* Workflows Table */}
        {isLoading ? (
          <Card className="glass p-12 text-center">
            <p className="text-white/60">Loading workflows...</p>
          </Card>
        ) : workflowsData?.items.length === 0 ? (
          <Card className="glass p-12 text-center">
            <p className="text-white/60 mb-4">No workflows found</p>
            <Button
              onClick={() => router.push("/invoke")}
              className="bg-white text-slate-900 hover:bg-white/90"
            >
              Process First Invoice
            </Button>
          </Card>
        ) : (
          <>
            <WorkflowTable workflows={workflowsData?.items || []} />
            
            {/* Pagination */}
            {workflowsData && workflowsData.total > workflowsData.page_size && (
              <div className="flex items-center justify-between">
                <p className="text-white/60 text-sm">
                  Showing {((page - 1) * workflowsData.page_size) + 1} to{" "}
                  {Math.min(page * workflowsData.page_size, workflowsData.total)} of{" "}
                  {workflowsData.total} workflows
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="text-white/60 hover:text-white"
                  >
                    Previous
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page * workflowsData.page_size >= workflowsData.total}
                    className="text-white/60 hover:text-white"
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

