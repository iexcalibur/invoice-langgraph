"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { useInvoke } from "@/hooks/use-invoke";
import { InvoicePayload, LineItem } from "@/lib/types";
import { ArrowLeft, Plus, Trash2, Upload, FileText, AlertTriangle, CheckCircle, Beaker } from "lucide-react";

// ============================================
// SAMPLE INVOICES FOR TESTING
// ============================================

const SAMPLE_INVOICES = {
  matched: {
    name: "Happy Path - Will Match",
    description: "Invoice matches PO exactly, will complete successfully",
    icon: CheckCircle,
    color: "text-green-400",
    bgColor: "bg-green-500/20",
    borderColor: "border-green-500/30",
    data: {
      invoice_id: "INV-2024-001",
      vendor_name: "Acme Corporation",
      vendor_tax_id: "12-3456789",
      invoice_date: "2024-01-15",
      due_date: "2024-02-14",
      amount: 15000.00,
      currency: "USD",
      line_items: [
        { desc: "Widget Type A - Industrial Grade", qty: 100, unit_price: 100.00, total: 10000.00 },
        { desc: "Widget Type B - Premium", qty: 50, unit_price: 100.00, total: 5000.00 }
      ],
      attachments: ["invoice_acme_001.pdf"]
    }
  },
  failed: {
    name: "HITL Trigger - Will Fail Match",
    description: "Invoice will fail 2-way matching and require human review",
    icon: AlertTriangle,
    color: "text-orange-400",
    bgColor: "bg-orange-500/20",
    borderColor: "border-orange-500/30",
    data: {
      invoice_id: "INV-2024-002",
      vendor_name: "Unknown Vendor LLC",
      vendor_tax_id: "",
      invoice_date: "2024-01-20",
      due_date: "2024-02-19",
      amount: 75000.00,
      currency: "USD",
      line_items: [
        { desc: "Consulting Services - Phase 1", qty: 1, unit_price: 45000.00, total: 45000.00 },
        { desc: "Implementation Support", qty: 1, unit_price: 30000.00, total: 30000.00 }
      ],
      attachments: ["invoice_unknown_002.pdf"]
    }
  },
  tolerance: {
    name: "Within Tolerance - Edge Case",
    description: "Amount is within 5% tolerance, should match",
    icon: Beaker,
    color: "text-blue-400",
    bgColor: "bg-blue-500/20",
    borderColor: "border-blue-500/30",
    data: {
      invoice_id: "INV-2024-E02",
      vendor_name: "Acme Corporation",
      vendor_tax_id: "12-3456789",
      invoice_date: "2024-01-26",
      due_date: "2024-02-25",
      amount: 15500.00,
      currency: "USD",
      line_items: [
        { desc: "Widget Type A", qty: 100, unit_price: 100.00, total: 10000.00 },
        { desc: "Widget Type B", qty: 55, unit_price: 100.00, total: 5500.00 }
      ],
      attachments: ["invoice_e02.pdf"]
    }
  },
  highRisk: {
    name: "High Risk - Escalation",
    description: "High amount + new vendor = requires escalated approval",
    icon: AlertTriangle,
    color: "text-red-400",
    bgColor: "bg-red-500/20",
    borderColor: "border-red-500/30",
    data: {
      invoice_id: "INV-2024-E05",
      vendor_name: "New Startup Co",
      vendor_tax_id: "55-1234567",
      invoice_date: "2024-01-29",
      due_date: "2024-02-28",
      amount: 100000.00,
      currency: "USD",
      line_items: [
        { desc: "Enterprise License", qty: 1, unit_price: 100000.00, total: 100000.00 }
      ],
      attachments: ["invoice_e05.pdf"]
    }
  },
  foreignCurrency: {
    name: "Foreign Currency - EUR",
    description: "Euro invoice for testing currency handling",
    icon: FileText,
    color: "text-purple-400",
    bgColor: "bg-purple-500/20",
    borderColor: "border-purple-500/30",
    data: {
      invoice_id: "INV-2024-E06",
      vendor_name: "Euro Supplies GmbH",
      vendor_tax_id: "DE123456789",
      invoice_date: "2024-01-30",
      due_date: "2024-03-01",
      amount: 8500.00,
      currency: "EUR",
      line_items: [
        { desc: "European Components", qty: 100, unit_price: 85.00, total: 8500.00 }
      ],
      attachments: ["invoice_e06.pdf"]
    }
  },
  missingInfo: {
    name: "Missing Tax ID",
    description: "Missing vendor tax ID, tests flag computation",
    icon: Beaker,
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/20",
    borderColor: "border-yellow-500/30",
    data: {
      invoice_id: "INV-2024-E01",
      vendor_name: "TechSupply Inc",
      vendor_tax_id: "",
      invoice_date: "2024-01-25",
      due_date: "2024-02-24",
      amount: 5000.00,
      currency: "USD",
      line_items: [
        { desc: "Office Supplies", qty: 100, unit_price: 50.00, total: 5000.00 }
      ],
      attachments: []
    }
  }
};

export default function InvokePage() {
  const router = useRouter();
  const { mutate: invoke, isPending } = useInvoke();
  const [selectedSample, setSelectedSample] = useState<string | null>(null);
  
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

  // Generate unique invoice ID with timestamp
  const generateUniqueId = (baseId: string) => {
    const timestamp = Date.now().toString(36).toUpperCase();
    return `${baseId}-${timestamp}`;
  };

  // Load sample invoice data
  const loadSampleInvoice = (key: string) => {
    const sample = SAMPLE_INVOICES[key as keyof typeof SAMPLE_INVOICES];
    if (sample) {
      setFormData({
        invoice_id: generateUniqueId(sample.data.invoice_id),
        vendor_name: sample.data.vendor_name,
        vendor_tax_id: sample.data.vendor_tax_id || "",
        invoice_date: sample.data.invoice_date,
        due_date: sample.data.due_date,
        amount: sample.data.amount,
        currency: sample.data.currency,
        line_items: sample.data.line_items,
        attachments: sample.data.attachments,
      });
      setLineItems(sample.data.line_items);
      setSelectedSample(key);
    }
  };

  // Clear form
  const clearForm = () => {
    setFormData({
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
    setLineItems([]);
    setSelectedSample(null);
  };

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
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
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
          {selectedSample && (
            <Button
              variant="ghost"
              onClick={clearForm}
              className="text-white/60 hover:text-white"
            >
              Clear Form
            </Button>
          )}
        </div>

        {/* Sample Invoice Selector */}
        <Card className="glass p-6 border-purple-500/30">
          <div className="flex items-center gap-2 mb-4">
            <Beaker className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-white">Quick Test Scenarios</h2>
            <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/30">
              Demo Data
            </Badge>
          </div>
          <p className="text-sm text-white/60 mb-4">
            Select a sample invoice to test different workflow scenarios. Each scenario demonstrates different paths through the 12-stage pipeline.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(SAMPLE_INVOICES).map(([key, sample]) => {
              const Icon = sample.icon;
              const isSelected = selectedSample === key;
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => loadSampleInvoice(key)}
                  className={`p-4 rounded-lg border text-left transition-all ${
                    isSelected
                      ? `${sample.bgColor} ${sample.borderColor} ring-2 ring-offset-2 ring-offset-slate-900 ring-purple-500`
                      : `bg-white/5 border-white/10 hover:border-purple-500/30 hover:bg-white/10`
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`w-4 h-4 ${sample.color}`} />
                    <span className={`text-sm font-medium ${isSelected ? 'text-white' : 'text-white/80'}`}>
                      {sample.name}
                    </span>
                  </div>
                  <p className="text-xs text-white/50 line-clamp-2">
                    {sample.description}
                  </p>
                </button>
              );
            })}
          </div>
        </Card>

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
          <Card className="glass p-6">
            <div className="flex items-center justify-between">
              <div>
                {selectedSample && (
                  <div className="flex items-center gap-2">
                    <Badge className={`${SAMPLE_INVOICES[selectedSample as keyof typeof SAMPLE_INVOICES].bgColor} ${SAMPLE_INVOICES[selectedSample as keyof typeof SAMPLE_INVOICES].color} border ${SAMPLE_INVOICES[selectedSample as keyof typeof SAMPLE_INVOICES].borderColor}`}>
                      {SAMPLE_INVOICES[selectedSample as keyof typeof SAMPLE_INVOICES].name}
                    </Badge>
                    <span className="text-sm text-white/60">
                      {SAMPLE_INVOICES[selectedSample as keyof typeof SAMPLE_INVOICES].description}
                    </span>
                  </div>
                )}
                {!selectedSample && (
                  <span className="text-sm text-white/60">
                    Fill in the form or select a test scenario above
                  </span>
                )}
              </div>
              <div className="flex gap-4">
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
                  className="bg-white text-slate-900 hover:bg-white/90 min-w-[160px]"
                >
                  {isPending ? (
                    <>
                      <span className="animate-pulse">Processing...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Process Invoice
                    </>
                  )}
                </Button>
              </div>
            </div>
          </Card>
        </form>
      </div>
    </div>
  );
}

