"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <Card className="glass p-12 text-center">
      {Icon && (
        <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon className="w-8 h-8 text-white/40" />
        </div>
      )}
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      {description && (
        <p className="text-white/60 mb-6 max-w-md mx-auto">{description}</p>
      )}
      {action && (
        <Button
          onClick={action.onClick}
          className="bg-white text-slate-900 hover:bg-white/90"
        >
          {action.label}
        </Button>
      )}
    </Card>
  );
}

