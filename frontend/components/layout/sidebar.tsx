"use client";

import { NavItem } from "./nav-item";
import { Home, Sparkles, Shield, FileText } from "lucide-react";
import { usePathname } from "next/navigation";
import Link from "next/link";

export function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "Home", icon: Home, exact: true },
    { href: "/workflows", label: "Workflows", icon: Sparkles },
    { href: "/review", label: "Review Queue", icon: Shield },
    { href: "/invoke", label: "Process Invoice", icon: FileText },
  ];

  return (
    <aside className="w-64 border-r border-purple-900/20 p-6">
      <Link href="/" className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-xl">I</span>
        </div>
        <span className="text-white text-xl font-semibold">Invoice Agent</span>
      </Link>

      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavItem key={item.href} {...item} />
        ))}
      </nav>
    </aside>
  );
}

