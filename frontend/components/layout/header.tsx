"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Sparkles, Shield, PlusCircle } from "lucide-react";

export function Header() {
  const pathname = usePathname();

  const navItems = [
    { href: "/invoke", label: "New Invoice", icon: PlusCircle },
    { href: "/workflows", label: "Workflows", icon: Sparkles },
    { href: "/review", label: "Review Queue", icon: Shield },
  ];

  return (
    <header className="w-full px-6 py-4 flex items-center justify-between border-b border-purple-900/20">
      <Link href="/" className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-xl">I</span>
        </div>
        <span className="text-white text-xl font-semibold">Invoice Agent</span>
      </Link>

      <nav className="flex items-center gap-6">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 transition-colors ${
                isActive
                  ? "text-white"
                  : "text-white/80 hover:text-white"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </header>
  );
}