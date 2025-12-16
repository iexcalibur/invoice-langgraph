/**
 * React Query hooks for human review decisions
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { submitDecision } from "@/lib/api";
import { ReviewDecision } from "@/lib/types";
import { useToast } from "./use-toast";

export function useDecision() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation<
    { resume_token: string; next_stage: string; workflow_status: string },
    Error,
    ReviewDecision
  >({
    mutationFn: submitDecision,
    onSuccess: (data, variables) => {
      // Invalidate reviews and workflows
      queryClient.invalidateQueries({ queryKey: ["reviews"] });
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
      
      // Show success toast
      toast({
        title: "Decision Submitted",
        description: `Invoice ${variables.decision === "ACCEPT" ? "accepted" : "rejected"}`,
      });
      
      // Navigate based on decision
      if (data.next_stage === "COMPLETE") {
        router.push("/workflows");
      } else {
        // Navigate to workflow detail
        router.push(`/workflows/${variables.checkpoint_id.split("_")[1]}`);
      }
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to submit decision",
        variant: "destructive",
      });
    },
  });
}

