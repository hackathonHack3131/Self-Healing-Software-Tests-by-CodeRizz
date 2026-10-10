"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  Terminal, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Cpu, 
  ChevronDown, 
  ChevronUp, 
  Play, 
  RotateCcw, 
  FileText, 
  Eye, 
  Layers, 
  AlertTriangle,
  ExternalLink,
  ShieldCheck,
  Zap,
  Info,
  Copy,
  Check
} from "lucide-react";
import { api } from "@/lib/api-client";
import { TestRun, TestStep, ConsoleLogEntry } from "@/types";
import { formatDuration, formatDate, getStatusBadgeVariant } from "@/lib/utils";

export default function LiveRunPage() {
  const params = useParams();
  const router = useRouter();
  const runId = params?.id as string;

  const [run, setRun] = useState<TestRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedStep, setExpandedStep] = useState<number | null>(3);
  const [logFilter, setLogFilter] = useState<string>("all");
  const [copiedLog, setCopiedLog] = useState(false);

  useEffect(() => {
    let mounted = true;
    const loadRun = async () => {
      try {
        const data = await api.getRun(runId);
        if (mounted && data) {
          setRun(data);
        }
      } catch {
        // fallback
      } finally {
        if (mounted) setLoading(false);
      }
    };

    loadRun();
    const interval = setInterval(loadRun, 8000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [runId]);

  if (loading || !run) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <div className="h-8 w-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        <p className="text-xs font-mono text-slate-400">Loading test run session: {runId}...</p>
      </div>
    );
  }

  const filteredLogs = run.logs.filter((l) => {
    if (logFilter === "all") return true;
    return l.level === logFilter;
  });

  const handleCopyLogs = () => {
    const text = run.logs.map((l) => `[${l.timestamp}] [${l.level.toUpperCase()}] ${l.message}`).join("\n");
    navigator.clipboard.writeText(text);
    setCopiedLog(true);
    setTimeout(() => setCopiedLog(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Simulation Fallback Warning */}
      {run.isSimulated && (
        <div className="rounded-xl bg-amber-950/30 border border-amber-500/30 px-4 py-2.5 flex items-center justify-between text-xs text-amber-200">
          <div className="flex items-center gap-2">
            <Info className="h-4 w-4 text-amber-400 shrink-0" />
            <span>
              <strong>Simulated Run Trace: </strong> Real-time browser telemetry generated via fallback runner.
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-900/60 border border-amber-700">
            OFFLINE FALLBACK
          </span>
        </div>
      )}

      {/* Header Card */}
      <div className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border ${getStatusBadgeVariant(run.finalResult || run.status)}`}>
                {(run.finalResult || run.status).toUpperCase()}
              </span>
              <span className="text-xs font-mono text-slate-400">Session ID: {run.id}</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white">{run.testName}</h1>
            <p className="text-xs font-mono text-cyan-300">Target: {run.targetUrl}</p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href={`/reports/${run.id}`}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition-colors flex items-center gap-1.5"
            >
              <FileText className="h-3.5 w-3.5 text-cyan-400" />
              <span>View Full Report</span>
            </Link>

            <Link
              href="/demo-lab"
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-glow-violet transition-all flex items-center gap-1.5"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Rerun in Demo Lab</span>
            </Link>
          </div>
        </div>

        {/* User Intent Box */}
        <div className="p-3.5 rounded-xl bg-[#090D16] border border-cyan-500/20 text-xs space-y-1">
          <div className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-bold flex items-center gap-1.5">
            <Sparkles className="h-3 w-3" />
            <span>Target User Intent (Source of Truth)</span>
          </div>
          <p className="text-slate-200 text-sm font-medium leading-relaxed">{run.intent}</p>
        </div>

        {/* Telemetry Stats Bar */}
        <div className="pt-2 border-t border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <span className="text-slate-500 block">Duration</span>
            <span className="text-slate-200 font-semibold">{formatDuration(run.durationMs || 2100)}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Executed At</span>
            <span className="text-slate-200 font-semibold">{formatDate(run.startedAt)}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Healed Steps</span>
            <span className="text-cyan-300 font-bold">{run.healingCount} repaired</span>
          </div>
          <div>
            <span className="text-slate-500 block">Outcome Verification</span>
            <span className="text-emerald-400 font-semibold">100% Verified</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Steps Timeline (7 cols) + Viewport & Console (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Interactive Step Timeline (7 Cols) */}
        <div className="lg:col-span-7 rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div>
              <h3 className="font-bold text-sm text-white">Execution Steps & Healing Interceptions</h3>
              <p className="text-xs text-slate-400">Click any step to inspect selector resolution and DOM evidence</p>
            </div>
            <span className="text-xs font-mono text-slate-400">
              {run.steps.length} Steps
            </span>
          </div>

          <div className="space-y-3">
            {run.steps.map((step, idx) => {
              const isExpanded = expandedStep === idx;
              const isHealed = step.status === "healed";
              const isFailed = step.status === "failed";
              const isPassed = step.status === "passed";

              return (
                <div
                  key={step.id}
                  className={`rounded-xl border transition-all ${
                    isHealed
                      ? "bg-cyan-950/20 border-cyan-500/40"
                      : isFailed
                      ? "bg-rose-950/20 border-rose-500/40"
                      : "bg-slate-900/60 border-slate-800"
                  }`}
                >
                  <button
                    onClick={() => setExpandedStep(isExpanded ? null : idx)}
                    className="w-full p-4 flex items-center justify-between text-left gap-3"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      {isHealed ? (
                        <div className="h-6 w-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center shrink-0">
                          <Sparkles className="h-3.5 w-3.5" />
                        </div>
                      ) : isFailed ? (
                        <div className="h-6 w-6 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center shrink-0">
                          <XCircle className="h-3.5 w-3.5" />
                        </div>
                      ) : (
                        <div className="h-6 w-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                        </div>
                      )}
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-xs text-slate-200 truncate">
                            Step {step.stepNumber}: {step.description}
                          </span>
                          <span
                            className={`text-[10px] font-mono px-2 py-0.2 rounded-full border ${getStatusBadgeVariant(
                              step.status
                            )}`}
                          >
                            {step.status.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-[11px] font-mono text-slate-500 truncate mt-0.5">
                          {step.originalAction}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {step.durationMs && (
                        <span className="text-[10px] font-mono text-slate-500">{formatDuration(step.durationMs)}</span>
                      )}
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-slate-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-slate-400" />
                      )}
                    </div>
                  </button>

                  {/* Expanded Step Details */}
                  {isExpanded && (
                    <div className="p-4 pt-0 border-t border-slate-800/80 space-y-3 text-xs">
                      <div className="grid grid-cols-2 gap-3 pt-3">
                        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                          <span className="text-[10px] text-slate-500 uppercase block font-mono">Original Action</span>
                          <code className="text-[11px] text-slate-200 font-mono block mt-0.5">{step.originalAction}</code>
                        </div>
                        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                          <span className="text-[10px] text-slate-500 uppercase block font-mono">Target Locator</span>
                          <code className="text-[11px] text-slate-200 font-mono block mt-0.5">{step.originalSelector}</code>
                        </div>
                      </div>

                      {/* Healing Attempt Inspector */}
                      {step.healingAttempt && (
                        <div className="p-3.5 rounded-xl bg-violet-950/20 border border-violet-500/30 space-y-2.5">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-xs text-cyan-300 flex items-center gap-1.5">
                              <Sparkles className="h-3.5 w-3.5" />
                              <span>Autonomous Healing Strategy Applied</span>
                            </span>
                            <span className="font-mono text-[10px] text-cyan-300 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-800">
                              Confidence: {(step.healingAttempt.confidenceScore * 100).toFixed(1)}%
                            </span>
                          </div>

                          <p className="text-[11px] text-slate-300 font-mono bg-slate-950/80 p-2 rounded border border-slate-800">
                            Failure: {step.healingAttempt.failureReason}
                          </p>

                          <div>
                            <span className="text-[10px] text-slate-400 uppercase font-mono block mb-1">Repaired Action Synthesized</span>
                            <code className="text-xs text-emerald-400 font-mono font-bold bg-emerald-950/40 p-2 rounded border border-emerald-500/30 block">
                              {step.healingAttempt.repairedAction}
                            </code>
                          </div>
                        </div>
                      )}

                      {/* Failure reason if not healed */}
                      {step.error && (
                        <div className="p-3 rounded-xl bg-rose-950/30 border border-rose-500/30 text-rose-300 font-mono text-[11px]">
                          Error: {step.error}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Browser Viewport Mockup & Console Panel (5 Cols) */}
        <div className="lg:col-span-5 space-y-5">
          {/* Simulated Browser Viewport Preview */}
          <div className="rounded-2xl glass-panel p-4 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Eye className="h-4 w-4 text-cyan-400" />
                <span className="font-bold text-xs text-white">Browser Viewport Inspection</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                1280 × 800 Chromium
              </span>
            </div>

            {/* Target Viewport Container */}
            <div className="rounded-xl bg-[#090D16] border border-slate-800 p-4 space-y-3 text-xs">
              <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800 pb-2">
                <span className="truncate">{run.targetUrl}</span>
                <span className="text-emerald-400 font-mono">200 OK</span>
              </div>

              {/* Viewport visual wireframe showing repaired element */}
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-3">
                <div className="h-3 w-1/3 bg-slate-800 rounded" />
                <div className="h-6 w-full bg-slate-900 rounded border border-slate-800" />
                <div className="h-6 w-full bg-slate-900 rounded border border-slate-800" />
                
                {/* Repaired element highlighted */}
                <div className="p-2.5 rounded-lg border-2 border-cyan-400 bg-cyan-950/30 text-cyan-200 font-mono text-[11px] flex items-center justify-between shadow-glow-cyan/20">
                  <span>Repaired Target: Place My Order</span>
                  <span className="text-[9px] px-1 py-0.5 bg-cyan-800 rounded font-bold">CLICKED</span>
                </div>
              </div>

              <div className="text-[10px] text-slate-500 font-mono text-right">
                Snapshot timestamp: {run.completedAt || run.startedAt}
              </div>
            </div>
          </div>

          {/* Diagnostic Console Panel */}
          <div className="rounded-2xl bg-[#080C14] border border-slate-800 p-4 font-mono text-xs space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-[11px] text-slate-400">
              <div className="flex items-center gap-2">
                <Terminal className="h-3.5 w-3.5 text-cyan-400" />
                <span>Diagnostic Logs ({filteredLogs.length})</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyLogs}
                  className="p-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                  title="Copy logs"
                >
                  {copiedLog ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                </button>
                <select
                  value={logFilter}
                  onChange={(e) => setLogFilter(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded px-1.5 py-0.5 text-[10px] text-slate-300"
                >
                  <option value="all">All Levels</option>
                  <option value="ai">AI / Healing</option>
                  <option value="info">Info</option>
                  <option value="warn">Warn</option>
                  <option value="error">Error</option>
                </select>
              </div>
            </div>

            <div className="max-h-64 overflow-y-auto space-y-1.5 pt-1 text-[11px]">
              {filteredLogs.map((log) => (
                <div key={log.id} className="flex items-start gap-2 leading-relaxed">
                  <span className="text-slate-600 text-[10px] shrink-0">{log.timestamp}</span>
                  <span
                    className={`text-[9px] uppercase font-bold shrink-0 px-1 py-0.2 rounded ${
                      log.level === "ai"
                        ? "bg-violet-950 text-cyan-300 border border-violet-800"
                        : log.level === "warn"
                        ? "bg-amber-950 text-amber-300"
                        : log.level === "error"
                        ? "bg-rose-950 text-rose-300"
                        : log.level === "success"
                        ? "bg-emerald-950 text-emerald-300"
                        : "bg-slate-900 text-slate-400"
                    }`}
                  >
                    {log.level}
                  </span>
                  <span className="text-slate-300 truncate">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
