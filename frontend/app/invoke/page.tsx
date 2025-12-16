"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useInvoke } from "@/hooks/use-invoke";
import { InvoicePayload, LineItem } from "@/lib/types";
import { ArrowLeft, Plus, Trash2, Upload } from "lucide-react";

export default function InvokePage() {
  const router = useRouter();
  const { mutate: invoke, isPending } = useInvoke();
  
  const [formData, setFormData] = useState<InvoicePayload>({
    invoice_id: "",
    vendor_name: "",
    vendor_tax_id: "",
    invoice_date: new Date().toISOString().split("T")[0],
    due_date: "",
    amount: 0,
    currency: "USD",
    line_items: [],
    attachments: [],
  });

  const [lineItems, setLineItems] = useState<LineItem[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const payload: InvoicePayload = {
      ...formData,
      line_items: lineItems,
      amount: lineItems.reduce((sum, item) => sum + item.total, 0),
    };

    invoke(payload);
  };

  const addLineItem = () => {
    setLineItems([...lineItems, { desc: "", qty: 1, unit_price: 0, total: 0 }]);
  };

  const updateLineItem = (index: number, field: keyof LineItem, value: any) => {
    const updated = [...lineItems];
    updated[index] = { ...updated[index], [field]: value };
    if (field === "qty" || field === "unit_price") {
      updated[index].total = updated[index].qty * updated[index].unit_price;
    }
    setLineItems(updated);
  };

  const removeLineItem = (index: number) => {
    setLineItems(lineItems.filter((_, i) => i !== index));
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="text-white/60 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-3xl font-bold text-white">Process Invoice</h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <Card className="glass p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Invoice Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="invoice_id" className="text-white/80">
                  Invoice ID *
                </Label>
                <Input
                  id="invoice_id"
                  required
                  value={formData.invoice_id}
                  onChange={(e) => setFormData({ ...formData, invoice_id: e.target.value })}
                  className="bg-white/5 border-purple-500/20 text-white"
                />
              </div>
              <div>
                <Label htmlFor="vendor_name" className="text-white/80">
                  Vendor Name *
                </Label>
                <Input
                  id="vendor_name"
                  required
                  value={formData.vendor_name}
                  onChange={(e) => setFormData({ ...formData, vendor_name: e.target.value })}
                  className="bg-white/5 border-purple-500/20 text-white"
                />
              </div>
              <div>
                <Label htmlFor="vendor_tax_id" className="text-white/80">
                  Vendor Tax ID
                </Label>
                <Input
                  id="vendor_tax_id"
                  value={formData.vendor_tax_id}
                  onChange={(e) => setFormData({ ...formData, vendor_tax_id: e.target.value })}
                  className="bg-white/5 border-purple-500/20 text-white"
                />
              </div>
              <div>
                <Label htmlFor="currency" className="text-white/80">
                  Currency *
                </Label>
                <Input
                  id="currency"
                  required
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  className="bg-white/5 border-purple-500/20 text-white"
                />
              </div>
              <div>
                <Label htmlFor="invoice_date" className="text-white/80">
                  Invoice Date *
                </Label>
                <Input
                  id="invoice_date"
                  type="date"
                  required
                  value={formData.invoice_date}
                  onChange={(e) => setFormData({ ...formData, invoice_date: e.target.value })}
                  className="bg-white/5 border-purple-500/20 text-white"
                />
              </div>
              <div>
                <Label htmlFor="due_date" className="text-white/80">
                  Due Date *
                </Label>
                <Input
                  id="due_date"
                  type="date"
                  required
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                  className="bg-white/5 border-purple-500/20 text-white"
                />
              </div>
            </div>
          </Card>

          {/* Line Items */}
          <Card className="glass p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">Line Items</h2>
              <Button
                type="button"
                onClick={addLineItem}
                className="bg-purple-500 hover:bg-purple-600"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Item
              </Button>
            </div>

            <div className="space-y-4">
              {lineItems.map((item, index) => (
                <div key={index} className="grid grid-cols-12 gap-4 items-end">
                  <div className="col-span-5">
                    <Label className="text-white/80">Description</Label>
                    <Input
                      value={item.desc}
                      onChange={(e) => updateLineItem(index, "desc", e.target.value)}
                      className="bg-white/5 border-purple-500/20 text-white"
                    />
                  </div>
                  <div className="col-span-2">
                    <Label className="text-white/80">Quantity</Label>
                    <Input
                      type="number"
                      value={item.qty}
                      onChange={(e) => updateLineItem(index, "qty", parseFloat(e.target.value) || 0)}
                      className="bg-white/5 border-purple-500/20 text-white"
                    />
                  </div>
                  <div className="col-span-2">
                    <Label className="text-white/80">Unit Price</Label>
                    <Input
                      type="number"
                      step="0.01"
                      value={item.unit_price}
                      onChange={(e) => updateLineItem(index, "unit_price", parseFloat(e.target.value) || 0)}
                      className="bg-white/5 border-purple-500/20 text-white"
                    />
                  </div>
                  <div className="col-span-2">
                    <Label className="text-white/80">Total</Label>
                    <Input
                      value={item.total.toFixed(2)}
                      disabled
                      className="bg-white/10 border-purple-500/20 text-white"
                    />
                  </div>
                  <div className="col-span-1">
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => removeLineItem(index)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            {lineItems.length === 0 && (
              <p className="text-white/40 text-center py-8">
                No line items added. Click "Add Item" to add invoice line items.
              </p>
            )}

            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="flex justify-end">
                <div className="text-right">
                  <p className="text-white/60 text-sm">Total Amount</p>
                  <p className="text-2xl font-bold text-white">
                    {formData.currency} {lineItems.reduce((sum, item) => sum + item.total, 0).toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
          </Card>

          {/* Submit */}
          <div className="flex justify-end gap-4">
            <Button
              type="button"
              variant="ghost"
              onClick={() => router.back()}
              className="text-white/60 hover:text-white"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isPending || lineItems.length === 0}
              className="bg-white text-slate-900 hover:bg-white/90"
            >
              {isPending ? "Processing..." : "Process Invoice"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

