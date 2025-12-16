"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto">
          <AlertCircle className="w-8 h-8 text-red-400" />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-white">Something went wrong!</h2>
          <p className="text-white/60">{error.message || "An unexpected error occurred"}</p>
        </div>
        <Button onClick={reset} className="bg-white text-slate-900 hover:bg-white/90">
          Try again
        </Button>
      </div>
    </div>
  );
}

