"use client";

import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useState } from "react";

interface ReviewerNotesProps {
  value?: string;
  onChange: (notes: string) => void;
  placeholder?: string;
}

export function ReviewerNotes({
  value = "",
  onChange,
  placeholder = "Add your review notes here...",
}: ReviewerNotesProps) {
  return (
    <Card className="glass p-6">
      <Label htmlFor="reviewer-notes" className="text-white/80 mb-2 block">
        Reviewer Notes
      </Label>
      <Textarea
        id="reviewer-notes"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="bg-white/5 border-purple-500/20 text-white min-h-[120px]"
      />
      <p className="text-xs text-white/40 mt-2">
        These notes will be saved with your decision
      </p>
    </Card>
  );
}

