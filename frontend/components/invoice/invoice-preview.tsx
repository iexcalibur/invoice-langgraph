"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { InvoicePayload } from "@/lib/types";
import { formatIST } from "@/lib/utils";
import { FileText, Calendar, DollarSign, Building2 } from "lucide-react";

interface InvoicePreviewProps {
  invoice: InvoicePayload;
  className?: string;
}

export function InvoicePreview({ invoice, className }: InvoicePreviewProps) {
  const totalAmount = invoice.line_items.reduce((sum, item) => sum + item.total, 0);

  return (
    <Card className={`glass p-6 ${className}`}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-white mb-1">{invoice.invoice_id}</h3>
          <p className="text-white/60">Invoice Preview</p>
        </div>
        <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">
          Draft
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="flex items-start gap-3">
          <Building2 className="w-5 h-5 text-white/60 mt-0.5" />
          <div>
            <p className="text-white/60 text-sm">Vendor</p>
            <p className="text-white font-medium">{invoice.vendor_name}</p>
            {invoice.vendor_tax_id && (
              <p className="text-white/40 text-xs">Tax ID: {invoice.vendor_tax_id}</p>
            )}
          </div>
        </div>

        <div className="flex items-start gap-3">
          <Calendar className="w-5 h-5 text-white/60 mt-0.5" />
          <div>
            <p className="text-white/60 text-sm">Dates</p>
            <p className="text-white text-sm">
              Invoice: {formatIST(invoice.invoice_date, "date")}
            </p>
            <p className="text-white text-sm">
              Due: {formatIST(invoice.due_date, "date")}
            </p>
          </div>
        </div>
      </div>

      {/* Line Items */}
      <div className="mb-6">
        <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
          <FileText className="w-4 h-4" />
          Line Items
        </h4>
        <div className="space-y-2">
          {invoice.line_items.map((item, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-white/5 rounded border border-white/10"
            >
              <div className="flex-1">
                <p className="text-white font-medium">{item.desc}</p>
                <p className="text-white/60 text-sm">
                  {item.qty} × {invoice.currency} {item.unit_price.toFixed(2)}
                </p>
              </div>
              <p className="text-white font-semibold">
                {invoice.currency} {item.total.toFixed(2)}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Total */}
      <div className="pt-4 border-t border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <DollarSign className="w-5 h-5 text-white/60" />
            <span className="text-white/60">Total Amount</span>
          </div>
          <p className="text-2xl font-bold text-white">
            {invoice.currency} {totalAmount.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Attachments */}
      {invoice.attachments && invoice.attachments.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <p className="text-white/60 text-sm mb-2">Attachments</p>
          <div className="flex flex-wrap gap-2">
            {invoice.attachments.map((attachment, index) => (
              <Badge
                key={index}
                className="bg-white/5 text-white/60 border-white/10"
              >
                {attachment}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

