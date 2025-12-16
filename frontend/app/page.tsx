"use client";

import { useRouter } from "next/navigation";
import { ArrowRight, FileText, TrendingUp, Shield, Wifi, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function HomePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-6 py-20">
        <div className="max-w-4xl w-full space-y-8">
          {/* Hero Section */}
          <div className="text-center space-y-6">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-white leading-tight">
              The Autonomous{" "}
              <span className="gradient-text">Invoice Agent</span>
            </h1>
            
            <p className="text-lg md:text-xl text-white/80 max-w-3xl mx-auto leading-relaxed font-medium mb-2">
              Intelligent processing with human control.
            </p>
            
            <p className="text-base md:text-lg text-white/70 max-w-3xl mx-auto leading-relaxed">
              Automate the messy 90% with AI, and handle the critical 10% with seamless{" "}
              <span className="text-purple-400 font-medium">Human-in-the-Loop</span> checkpoints.
            </p>
          </div>

          {/* Single CTA */}
          <div className="flex justify-center pt-4">
            <Button
              onClick={() => router.push("/invoke")}
              className="h-14 px-8 bg-white text-slate-900 hover:bg-white/90 rounded-xl font-semibold flex items-center gap-2 transition-all hover:scale-105"
            >
              <Plus className="w-5 h-5" />
              Process New Invoice
              <ArrowRight className="w-5 h-5" />
            </Button>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-4 mt-12">
            <Card className="glass p-6 border-purple-500/20 hover:border-purple-500/40 transition-all">
              <div className="space-y-2">
                <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-purple-400" />
                </div>
                <h3 className="text-white font-semibold">12-Stage Pipeline</h3>
                <p className="text-white/60 text-sm">
                  Automated invoice processing from intake to completion
                </p>
              </div>
            </Card>

            <Card className="glass p-6 border-purple-500/20 hover:border-purple-500/40 transition-all">
              <div className="space-y-2">
                <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <Shield className="w-5 h-5 text-blue-400" />
                </div>
                <h3 className="text-white font-semibold">Human-in-the-Loop</h3>
                <p className="text-white/60 text-sm">
                  Smart checkpoints for manual review when needed
                </p>
              </div>
            </Card>

            <Card className="glass p-6 border-purple-500/20 hover:border-purple-500/40 transition-all">
              <div className="space-y-2">
                <div className="w-10 h-10 bg-pink-500/20 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-pink-400" />
                </div>
                <h3 className="text-white font-semibold">Real-time Tracking</h3>
                <p className="text-white/60 text-sm">
                  Live workflow monitoring with SSE streaming logs
                </p>
              </div>
            </Card>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full px-6 py-4 flex items-center justify-between border-t border-purple-900/20">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded flex items-center justify-center">
            <span className="text-white text-xs font-bold">I</span>
          </div>
          <span className="text-white/60 text-sm">Invoice LangGraph Agent</span>
        </div>
        
        <div className="flex items-center gap-2 text-green-400">
          <Wifi className="w-4 h-4" />
          <span className="text-sm font-medium">Backend Connected</span>
        </div>
      </footer>
    </div>
  );
}