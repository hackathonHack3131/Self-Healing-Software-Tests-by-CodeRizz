"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  FlaskConical, 
  PlusCircle, 
  FolderGit2, 
  FileCheck2, 
  Settings, 
  Sparkles, 
  ChevronLeft, 
  ChevronRight, 
  Cpu, 
  Layers, 
  ExternalLink,
  ShieldCheck,
  Radio
} from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api-client";

const navItems = [
  { name: "Overview", href: "/", icon: Layers },
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { 
    name: "Version A/B Lab", 
    href: "/demo-lab", 
    icon: FlaskConical,
    badge: "STAR DEMO",
    badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
  },
  { name: "Test Builder", href: "/tests/new", icon: PlusCircle },
  { name: "Test Catalog", href: "/tests", icon: FolderGit2 },
  { name: "Healing Reports", href: "/reports", icon: FileCheck2 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [backendStatus, setBackendStatus] = useState<"checking" | "connected" | "simulated">("checking");
  const [latency, setLatency] = useState(0);

  useEffect(() => {
    let mounted = true;
    const check = async () => {
      const res = await api.getHealth();
      if (!mounted) return;
      if (res.backendConnected) {
        setBackendStatus("connected");
        setLatency(res.latencyMs);
      } else {
        setBackendStatus("simulated");
      }
    };
    check();
    const timer = setInterval(check, 10000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  return (
    <aside
      className={cn(
        "h-screen sticky top-0 z-40 flex flex-col justify-between border-r border-slate-800/80 bg-[#0B0F19]/95 backdrop-blur-xl transition-all duration-300 select-none",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Top Header & Logo */}
      <div>
        <div className="flex h-16 items-center justify-between px-4 border-b border-slate-800/80">
          <Link href="/" className="flex items-center gap-3 overflow-hidden">
            <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 via-indigo-600 to-cyan-500 shadow-glow-violet">
              <ShieldCheck className="h-5 w-5 text-white" />
              <div className="absolute -inset-0.5 rounded-xl bg-violet-500/20 blur-sm -z-10" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                  AegisTest
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30">AI</span>
                </span>
                <span className="text-[11px] text-slate-400 font-medium truncate">
                  Self-Healing E2E Engine
                </span>
              </div>
            )}
          </Link>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-gradient-to-r from-violet-600/20 to-cyan-500/10 text-white border border-violet-500/30 shadow-glow-violet/20"
                    : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/40"
                )}
                title={collapsed ? item.name : undefined}
              >
                <Icon
                  className={cn(
                    "h-5 w-5 shrink-0 transition-colors",
                    isActive ? "text-cyan-400" : "text-slate-400 group-hover:text-slate-200"
                  )}
                />
                {!collapsed && (
                  <span className="flex-1 truncate">{item.name}</span>
                )}
                {!collapsed && item.badge && (
                  <span
                    className={cn(
                      "text-[10px] uppercase font-mono px-1.5 py-0.5 rounded-full border font-semibold",
                      item.badgeColor
                    )}
                  >
                    {item.badge}
                  </span>
                )}
                {isActive && (
                  <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-cyan-400 shadow-[0_0_8px_#22d3ee]" />
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer & Connection Status */}
      <div className="p-3 border-t border-slate-800/80 space-y-3">
        {/* Quick Launch Demo Button */}
        {!collapsed && (
          <Link
            href="/demo-lab"
            className="flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-medium text-xs shadow-glow-violet transition-all duration-200 transform hover:-translate-y-0.5"
          >
            <Sparkles className="h-3.5 w-3.5 text-cyan-200 animate-pulse" />
            <span>Launch Version A/B Demo</span>
          </Link>
        )}

        {/* Engine Status Indicator */}
        <div
          className={cn(
            "rounded-xl border p-2.5 transition-all",
            backendStatus === "connected"
              ? "bg-emerald-950/20 border-emerald-500/30"
              : "bg-slate-900/60 border-slate-800"
          )}
        >
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span
                className={cn(
                  "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
                  backendStatus === "connected" ? "bg-emerald-400" : "bg-cyan-400"
                )}
              />
              <span
                className={cn(
                  "relative inline-flex rounded-full h-2.5 w-2.5",
                  backendStatus === "connected" ? "bg-emerald-500" : "bg-cyan-500"
                )}
              />
            </span>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-slate-300">
                    {backendStatus === "connected" ? "REST API Online" : "Simulated Engine"}
                  </span>
                  {backendStatus === "connected" && (
                    <span className="text-[10px] font-mono text-emerald-400">{latency}ms</span>
                  )}
                </div>
                <p className="text-[10px] text-slate-400 truncate">
                  {backendStatus === "connected" ? "Connected to port 8000" : "Self-contained runner"}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}
