"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, AlertTriangle } from "lucide-react";

interface MatchComparisonProps {
  invoiceAmount: number;
  poAmount: number;
  tolerance: number;
  matchScore: number;
  currency: string;
}

export function MatchComparison({
  invoiceAmount,
  poAmount,
  tolerance,
  matchScore,
  currency,
}: MatchComparisonProps) {
  const difference = Math.abs(invoiceAmount - poAmount);
  const percentageDiff = (difference / poAmount) * 100;
  const isWithinTolerance = percentageDiff <= tolerance;
  const isMatched = matchScore >= 0.8;

  return (
    <Card className="glass p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Match Comparison</h3>

      <div className="space-y-4">
        {/* Amounts */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-white/60 text-sm mb-1">Invoice Amount</p>
            <p className="text-xl font-bold text-white">
              {currency} {invoiceAmount.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-white/60 text-sm mb-1">PO Amount</p>
            <p className="text-xl font-bold text-white">
              {currency} {poAmount.toLocaleString()}
            </p>
          </div>
        </div>

        {/* Difference */}
        <div className="pt-4 border-t border-white/10">
          <div className="flex items-center justify-between mb-2">
            <span className="text-white/60">Difference</span>
            <span className="text-white font-semibold">
              {currency} {difference.toLocaleString()} ({percentageDiff.toFixed(2)}%)
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-white/60">Tolerance</span>
            <Badge
              className={
                isWithinTolerance
                  ? "bg-green-500/20 text-green-400 border-green-500/30"
                  : "bg-red-500/20 text-red-400 border-red-500/30"
              }
            >
              {tolerance}%
            </Badge>
          </div>
        </div>

        {/* Match Status */}
        <div className="pt-4 border-t border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {isMatched ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <XCircle className="w-5 h-5 text-red-400" />
              )}
              <span className="text-white font-semibold">
                {isMatched ? "Matched" : "Mismatch"}
              </span>
            </div>
            <Badge
              className={
                isMatched
                  ? "bg-green-500/20 text-green-400 border-green-500/30"
                  : "bg-red-500/20 text-red-400 border-red-500/30"
              }
            >
              Score: {Math.round(matchScore * 100)}%
            </Badge>
          </div>
          {!isMatched && (
            <div className="mt-3 p-3 bg-orange-500/10 border border-orange-500/20 rounded flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-400 mt-0.5" />
              <p className="text-sm text-white/80">
                Amount difference exceeds tolerance threshold. Manual review required.
              </p>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

