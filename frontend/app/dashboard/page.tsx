"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  Clock, 
  TrendingUp, 
  AlertTriangle, 
  Play, 
  PlusCircle, 
  ArrowUpRight, 
  ExternalLink,
  RefreshCw,
  Cpu,
  Layers,
  ChevronRight,
  ShieldCheck,
  Server,
  Zap,
  Info
} from "lucide-react";
import { 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from "recharts";
import { api } from "@/lib/api-client";
import { DashboardMetrics } from "@/types";
import { SEED_DASHBOARD_METRICS } from "@/lib/mock-data";
import { formatDuration, formatDate, getStatusBadgeVariant } from "@/lib/utils";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics>(SEED_DASHBOARD_METRICS);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchMetrics = async () => {
    try {
      const data = await api.getDashboard();
      setMetrics(data);
    } catch {
      // fallback handled inside api.getDashboard()
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 12000);
    return () => clearInterval(interval);
  }, []);

  const handleManualRefresh = () => {
    setRefreshing(true);
    fetchMetrics();
  };

  const chartData = metrics.trends.dates.map((date, index) => ({
    date,
    passRate: metrics.trends.passRates[index],
    healedRate: metrics.trends.healedRates[index],
    failureRate: metrics.trends.failureRates[index],
  }));

  const healingBarData = metrics.healingActivity.map((item) => ({
    date: item.date,
    healed: item.healedCount,
    failed: item.failedHealCount,
  }));

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Simulation Fallback Banner if Backend is Offline */}
      {!metrics.isBackendConnected && (
        <div className="rounded-xl bg-amber-950/30 border border-amber-500/30 px-4 py-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-amber-200">
          <div className="flex items-center gap-2.5">
            <Info className="h-4 w-4 text-amber-400 shrink-0" />
            <div>
              <span className="font-semibold text-amber-300">Simulated Runner Active: </span>
              Backend server at <code className="font-mono bg-amber-950/80 px-1 py-0.5 rounded text-amber-300">{api.getBaseUrl()}</code> is offline or unreachable. Results shown are simulated fallback data.
            </div>
          </div>
          <Link
            href="/settings"
            className="shrink-0 px-3 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 font-medium transition-colors"
          >
            Configure Backend URL
          </Link>
        </div>
      )}

      {/* Top Header & Quick Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            Testing & Self-Healing Telemetry
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time health, intent-aware test execution, and DOM repair analytics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleManualRefresh}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs text-slate-300 transition-colors"
            title="Refresh metrics"
          >
            <RefreshCw className={`h-3.5 w-3.5 text-slate-400 ${refreshing ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>

          <Link
            href="/demo-lab"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-glow-violet transition-all transform hover:-translate-y-0.5"
          >
            <Play className="h-3.5 w-3.5 fill-white" />
            <span>Run A/B Demo</span>
          </Link>

          <Link
            href="/tests/new"
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 transition-all"
          >
            <PlusCircle className="h-3.5 w-3.5 text-cyan-400" />
            <span>Create Test</span>
          </Link>
        </div>
      </div>

      {/* Primary Analytics KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {/* Total Tests */}
        <div className="rounded-2xl glass-panel p-4 border border-slate-800 space-y-1">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Total Tests</div>
          <div className="text-2xl font-extrabold text-white">{metrics.totalTests}</div>
          <div className="text-[10px] text-slate-400 flex items-center gap-1">
            <span>Catalog count</span>
          </div>
        </div>

        {/* Passed Tests */}
        <div className="rounded-2xl glass-panel p-4 border border-emerald-500/20 space-y-1">
          <div className="text-[11px] font-medium text-emerald-400 uppercase tracking-wider flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3" />
            <span>Passed</span>
          </div>
          <div className="text-2xl font-extrabold text-emerald-400">{metrics.passedTests}</div>
          <div className="text-[10px] text-emerald-400/80">Direct passes</div>
        </div>

        {/* Self-Healed Tests */}
        <div className="rounded-2xl glass-panel p-4 border border-violet-500/30 space-y-1 shadow-glow-violet/10">
          <div className="text-[11px] font-medium text-violet-300 uppercase tracking-wider flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-cyan-400" />
            <span>Healed</span>
          </div>
          <div className="text-2xl font-extrabold text-violet-300">{metrics.selfHealedTests}</div>
          <div className="text-[10px] text-cyan-300/80">Saved from failing</div>
        </div>

        {/* Failed Tests */}
        <div className="rounded-2xl glass-panel p-4 border border-rose-500/20 space-y-1">
          <div className="text-[11px] font-medium text-rose-400 uppercase tracking-wider flex items-center gap-1">
            <XCircle className="h-3 w-3" />
            <span>Failed</span>
          </div>
          <div className="text-2xl font-extrabold text-rose-400">{metrics.failedTests}</div>
          <div className="text-[10px] text-rose-400/80">Authentic bugs</div>
        </div>

        {/* Success Rate */}
        <div className="rounded-2xl glass-panel p-4 border border-slate-800 space-y-1">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Success Rate</div>
          <div className="text-2xl font-extrabold text-white">{metrics.testSuccessRate}%</div>
          <div className="text-[10px] text-emerald-400 flex items-center gap-0.5">
            <TrendingUp className="h-3 w-3" />
            <span>+4.2% with AI</span>
          </div>
        </div>

        {/* Avg Execution Time */}
        <div className="rounded-2xl glass-panel p-4 border border-slate-800 space-y-1">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Clock className="h-3 w-3 text-slate-400" />
            <span>Avg Duration</span>
          </div>
          <div className="text-2xl font-extrabold text-white">{formatDuration(metrics.averageExecutionTimeMs)}</div>
          <div className="text-[10px] text-slate-400">Headless Chromium</div>
        </div>

        {/* Healing Success Rate */}
        <div className="rounded-2xl glass-panel p-4 border border-cyan-500/30 space-y-1 shadow-glow-cyan/10">
          <div className="text-[11px] font-medium text-cyan-300 uppercase tracking-wider flex items-center gap-1">
            <Zap className="h-3 w-3" />
            <span>Heal Rate</span>
          </div>
          <div className="text-2xl font-extrabold text-cyan-300">{metrics.healingSuccessRate}%</div>
          <div className="text-[10px] text-cyan-400/80">AI confidence &gt;0.85</div>
        </div>
      </div>

      {/* Charts Row: Pass/Fail Trends & Self-Healing Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Pass/Fail Trend Chart */}
        <div className="lg:col-span-7 rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Execution Stability & Healing Impact</h3>
              <p className="text-xs text-slate-400">7-day breakdown of direct passes, healed tests, and true failures</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="h-2 w-2 rounded-full bg-emerald-400" /> Pass Rate
              </span>
              <span className="flex items-center gap-1.5 text-violet-300">
                <span className="h-2 w-2 rounded-full bg-violet-400" /> Healed %
              </span>
            </div>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="passGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="healGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                  itemStyle={{ color: "#F8FAFC" }}
                />
                <Area type="monotone" dataKey="passRate" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#passGrad)" name="Total Pass %" />
                <Area type="monotone" dataKey="healedRate" stroke="#8B5CF6" strokeWidth={2} fillOpacity={1} fill="url(#healGrad)" name="Self-Healed %" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Self-Healing Activity Bar Chart */}
        <div className="lg:col-span-5 rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Daily Self-Healing Repaired Steps</h3>
              <p className="text-xs text-slate-400">Mutations repaired vs unresolvable application failures</p>
            </div>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30">
              Autonomous
            </span>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={healingBarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                  itemStyle={{ color: "#F8FAFC" }}
                />
                <Bar dataKey="healed" fill="#06B6D4" radius={[4, 4, 0, 0]} name="Repaired Steps" />
                <Bar dataKey="failed" fill="#F43F5E" radius={[4, 4, 0, 0]} name="App Errors" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Two Column Section: Recent Test Runs & Detected UI Changes */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Test Runs */}
        <div className="lg:col-span-7 rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Recent Test Runs</h3>
              <p className="text-xs text-slate-400">Live workflow executions and auto-healed steps</p>
            </div>
            <Link
              href="/tests"
              className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1"
            >
              <span>View All</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-800/80">
            {metrics.recentRuns.map((run) => (
              <div key={run.id} className="py-3.5 flex items-center justify-between gap-4 group">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-slate-200 group-hover:text-cyan-300 transition-colors truncate">
                      {run.testName}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${getStatusBadgeVariant(
                        run.finalResult
                      )}`}
                    >
                      {run.finalResult === "healed" ? "HEALED" : run.finalResult.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span>Target: {run.targetApp}</span>
                    <span>•</span>
                    <span>{run.durationFormatted}</span>
                    <span>•</span>
                    <span>{formatDate(run.executedAt)}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {run.repairedStepsCount > 0 && (
                    <span className="text-[11px] font-mono px-2 py-1 rounded bg-violet-500/10 text-violet-300 border border-violet-500/30">
                      {run.repairedStepsCount} step healed
                    </span>
                  )}
                  <Link
                    href={`/runs/${run.id}`}
                    className="p-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                    title="View Run Trace"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Latest Detected UI Changes */}
        <div className="lg:col-span-5 rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white">Latest Detected UI Changes</h3>
              <p className="text-xs text-slate-400">Mutations intercepted by semantic agent</p>
            </div>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
              Live Feed
            </span>
          </div>

          <div className="space-y-3">
            {metrics.latestUiChanges.map((change) => (
              <div
                key={change.id}
                className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200">{change.elementDescription}</span>
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                      change.impactScore === "high"
                        ? "bg-rose-500/20 text-rose-300"
                        : "bg-amber-500/20 text-amber-300"
                    }`}
                  >
                    {change.impactScore.toUpperCase()} IMPACT
                  </span>
                </div>

                <div className="space-y-1 font-mono text-[11px]">
                  <div className="text-rose-400/90 truncate">
                    <span className="text-slate-500">- Old: </span>
                    {change.previousDomSnippet}
                  </div>
                  <div className="text-cyan-300 truncate">
                    <span className="text-slate-500">+ Healed: </span>
                    {change.newDomSnippet}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Failures & Recommended Actions */}
      <div className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
            <div>
              <h3 className="text-base font-bold text-white">Recent Failures & AI Root-Cause Diagnostic</h3>
              <p className="text-xs text-slate-400">Authentic application defects vs configuration constraints</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {metrics.recentFailures.map((failure) => (
            <div
              key={failure.id}
              className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">{failure.testName}</span>
                <span className="text-[10px] text-slate-500">{formatDate(failure.occurredAt)}</span>
              </div>
              <p className="text-rose-300 font-mono text-[11px]">{failure.failureReason}</p>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-cyan-300 flex items-start gap-2">
                <Sparkles className="h-4 w-4 shrink-0 text-cyan-400 mt-0.5" />
                <div>
                  <span className="font-semibold text-slate-300">Recommended Action: </span>
                  {failure.recommendedAction}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
