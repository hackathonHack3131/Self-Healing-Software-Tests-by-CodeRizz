"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  ChevronRight, 
  Home, 
  Sparkles, 
  Activity, 
  Search, 
  Play, 
  Bell,
  Code2
} from "lucide-react";

export function Navbar() {
  const pathname = usePathname();

  // Generate breadcrumb items
  const getBreadcrumbs = () => {
    const parts = pathname.split("/").filter(Boolean);
    if (parts.length === 0) return [{ label: "Home", href: "/" }];

    return [
      { label: "Home", href: "/" },
      ...parts.map((p, index) => {
        const href = "/" + parts.slice(0, index + 1).join("/");
        const label = p.charAt(0).toUpperCase() + p.slice(1).replace("-", " ");
        return { label, href };
      }),
    ];
  };

  const breadcrumbs = getBreadcrumbs();

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-800/80 bg-[#070A11]/80 px-6 backdrop-blur-md">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center space-x-1.5 text-xs text-slate-400">
        {breadcrumbs.map((crumb, idx) => (
          <React.Fragment key={crumb.href}>
            {idx > 0 && <ChevronRight className="h-3.5 w-3.5 text-slate-600" />}
            {idx === breadcrumbs.length - 1 ? (
              <span className="font-semibold text-slate-200">{crumb.label}</span>
            ) : (
              <Link
                href={crumb.href}
                className="hover:text-cyan-400 transition-colors flex items-center gap-1"
              >
                {idx === 0 && <Home className="h-3.5 w-3.5" />}
                <span>{crumb.label}</span>
              </Link>
            )}
          </React.Fragment>
        ))}
      </nav>

      {/* Right Action Tools */}
      <div className="flex items-center gap-3">
        {/* Quick Demo CTA */}
        <Link
          href="/demo-lab"
          className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-medium transition-all"
        >
          <Play className="h-3 w-3 fill-cyan-400 text-cyan-400" />
          <span>Interactive Version A/B</span>
        </Link>

        {/* Create Test CTA */}
        <Link
          href="/tests/new"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-violet-600/30 hover:bg-violet-600/40 text-violet-200 border border-violet-500/30 text-xs font-medium transition-all"
        >
          <Sparkles className="h-3 w-3 text-violet-300" />
          <span>New Intent Test</span>
        </Link>

        {/* Divider */}
        <div className="h-5 w-[1px] bg-slate-800" />

        {/* Status Pill */}
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-400">
          <Activity className="h-3 w-3 text-cyan-400 animate-pulse" />
          <span>E2E Agent v2.4</span>
        </div>

        {/* User Avatar */}
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-tr from-violet-600 to-indigo-500 text-white font-semibold text-xs border border-violet-400/30 shadow-sm">
          AG
        </div>
      </div>
    </header>
  );
}
