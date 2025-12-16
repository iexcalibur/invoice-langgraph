"use client";

import { InvoicePayload, LineItem } from "@/lib/types";
import { InvoiceForm as InvoiceFormComponent } from "./invoice-form-internal";

interface InvoiceFormProps {
  initialData?: Partial<InvoicePayload>;
  onSubmit: (data: InvoicePayload) => void;
  isSubmitting?: boolean;
}

export function InvoiceForm({ initialData, onSubmit, isSubmitting }: InvoiceFormProps) {
  return (
    <InvoiceFormComponent
      initialData={initialData}
      onSubmit={onSubmit}
      isSubmitting={isSubmitting}
    />
  );
}

// Internal form component (can be extracted to separate file if needed)
function InvoiceFormInternal({ initialData, onSubmit, isSubmitting }: InvoiceFormProps) {
  // This is a wrapper - actual form logic is in the invoke page
  // This component can be extended for reuse
  return null;
}

