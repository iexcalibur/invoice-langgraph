/**
 * React Query hooks for invoice invocation
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { invokeWorkflow, validateInvoice } from "@/lib/api";
import { InvoicePayload, InvokeResponse } from "@/lib/types";
import { useToast } from "./use-toast";

// ============================================
// Invoke Workflow
// ============================================

export function useInvoke() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation<InvokeResponse, Error, InvoicePayload>({
    mutationFn: invokeWorkflow,
    onSuccess: (data) => {
      // Invalidate workflows list
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
      
      // Show success toast
      toast({
        title: "Workflow Started",
        description: `Invoice ${data.invoice_id} processing started`,
      });
      
      // Navigate to workflow detail
      router.push(`/workflows/${data.workflow_id}`);
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message || "Failed to start workflow",
        variant: "destructive",
      });
    },
  });
}

// ============================================
// Validate Invoice
// ============================================

export function useValidateInvoice() {
  return useMutation<{ valid: boolean; errors?: string[] }, Error, InvoicePayload>({
    mutationFn: validateInvoice,
  });
}

