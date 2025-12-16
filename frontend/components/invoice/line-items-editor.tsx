"use client";

import { LineItem } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Plus, Trash2 } from "lucide-react";

interface LineItemsEditorProps {
  items: LineItem[];
  currency: string;
  onChange: (items: LineItem[]) => void;
}

export function LineItemsEditor({ items, currency, onChange }: LineItemsEditorProps) {
  const addItem = () => {
    onChange([...items, { desc: "", qty: 1, unit_price: 0, total: 0 }]);
  };

  const updateItem = (index: number, field: keyof LineItem, value: any) => {
    const updated = [...items];
    updated[index] = { ...updated[index], [field]: value };
    
    if (field === "qty" || field === "unit_price") {
      updated[index].total = updated[index].qty * updated[index].unit_price;
    }
    
    onChange(updated);
  };

  const removeItem = (index: number) => {
    onChange(items.filter((_, i) => i !== index));
  };

  const total = items.reduce((sum, item) => sum + item.total, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Line Items</h3>
        <Button
          type="button"
          onClick={addItem}
          size="sm"
          className="bg-purple-500 hover:bg-purple-600"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Item
        </Button>
      </div>

      <div className="space-y-3">
        {items.map((item, index) => (
          <Card key={index} className="glass p-4">
            <div className="grid grid-cols-12 gap-4 items-end">
              <div className="col-span-5">
                <Label className="text-white/80 text-sm">Description</Label>
                <Input
                  value={item.desc}
                  onChange={(e) => updateItem(index, "desc", e.target.value)}
                  placeholder="Item description"
                  className="bg-white/5 border-purple-500/20 text-white"
                />
              </div>
              <div className="col-span-2">
                <Label className="text-white/80 text-sm">Quantity</Label>
                <Input
                  type="number"
                  min="0"
                  step="1"
                  value={item.qty}
                  onChange={(e) => updateItem(index, "qty", parseFloat(e.target.value) || 0)}
                  className="bg-white/5 border-purple-500/20 text-white"
                />
              </div>
              <div className="col-span-2">
                <Label className="text-white/80 text-sm">Unit Price</Label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={item.unit_price}
                  onChange={(e) => updateItem(index, "unit_price", parseFloat(e.target.value) || 0)}
                  className="bg-white/5 border-purple-500/20 text-white"
                />
              </div>
              <div className="col-span-2">
                <Label className="text-white/80 text-sm">Total</Label>
                <Input
                  value={`${currency} ${item.total.toFixed(2)}`}
                  disabled
                  className="bg-white/10 border-purple-500/20 text-white"
                />
              </div>
              <div className="col-span-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeItem(index)}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {items.length === 0 && (
        <Card className="glass p-8 text-center">
          <p className="text-white/60 mb-4">No line items added</p>
          <Button
            type="button"
            onClick={addItem}
            className="bg-purple-500 hover:bg-purple-600"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add First Item
          </Button>
        </Card>
      )}

      {items.length > 0 && (
        <Card className="glass p-4">
          <div className="flex items-center justify-between">
            <span className="text-white/60 font-medium">Total Amount</span>
            <span className="text-2xl font-bold text-white">
              {currency} {total.toFixed(2)}
            </span>
          </div>
        </Card>
      )}
    </div>
  );
}

