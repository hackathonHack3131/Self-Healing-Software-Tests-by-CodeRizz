"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  FileCheck2, 
  Sparkles, 
  Download, 
  Printer, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  ArrowLeft, 
  ShieldCheck, 
  Terminal, 
  Clock, 
  ExternalLink,
  Code2,
  Copy,
  Check,
  Zap,
  Info
} from "lucide-react";
import { api } from "@/lib/api-client";
import { TestReport } from "@/types";
import { formatDuration, formatDate, getStatusBadgeVariant } from "@/lib/utils";

export default function DetailedReportPage() {
  const params = useParams();
  const router = useRouter();
  const runId = params?.id as string;

  const [report, setReport] = useState<TestReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [copiedJson, setCopiedJson] = useState(false);

  useEffect(() => {
    api.getRunReport(runId).then((data) => {
      setReport(data);
      setLoading(false);
    });
  }, [runId]);

  if (loading || !report) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <div className="h-8 w-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        <p className="text-xs font-mono text-slate-400">Loading audit report...</p>
      </div>
    );
  }

  const handleDownloadJson = () => {
    const jsonStr = JSON.stringify(report, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `aegis-report-${report.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16 print:p-0 print:m-0">
      {/* Back button & Action buttons */}
      <div className="flex items-center justify-between no-print">
        <Link
          href="/reports"
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Back to All Reports</span>
        </Link>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownloadJson}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 hover:border-slate-600 text-xs text-slate-300 font-medium flex items-center gap-1.5 transition-colors"
          >
            <Download className="h-3.5 w-3.5 text-cyan-400" />
            <span>Download JSON</span>
          </button>
          <button
            onClick={handlePrint}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-white font-medium flex items-center gap-1.5 transition-colors"
          >
            <Printer className="h-3.5 w-3.5 text-slate-300" />
            <span>Print / PDF Export</span>
          </button>
        </div>
      </div>

      {/* Main Report Document Container */}
      <div className="rounded-3xl glass-panel p-6 sm:p-10 border border-slate-800 space-y-8 bg-[#090D16]">
        {/* Document Header */}
        <div className="pb-6 border-b border-slate-800 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border ${getStatusBadgeVariant(report.finalExecutionStatus)}`}>
                {report.finalExecutionStatus === "healed" ? "SELF-HEALED AUDIT" : report.finalExecutionStatus.toUpperCase()}
              </span>
              <span className="text-xs font-mono text-slate-500">Report ID: {report.id}</span>
            </div>
            <span className="text-xs font-mono text-slate-400">{formatDate(report.executedAt)}</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">{report.testName}</h1>

          {/* Test Intent Box */}
          <div className="p-4 rounded-xl bg-slate-950 border border-cyan-500/20 text-xs space-y-1">
            <span className="text-[10px] font-mono uppercase text-cyan-400 font-bold block">
              Original User Intent (Source of Truth)
            </span>
            <p className="text-slate-200 text-sm font-medium">{report.testIntent}</p>
          </div>
        </div>

        {/* Telemetry Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 block text-[11px]">Initial Status</span>
            <span className="text-rose-400 font-bold uppercase mt-0.5 block">{report.initialExecutionStatus}</span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 block text-[11px]">Final Verified Status</span>
            <span className="text-cyan-300 font-bold uppercase mt-0.5 block">{report.finalExecutionStatus}</span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 block text-[11px]">Duration</span>
            <span className="text-slate-200 font-bold mt-0.5 block">{formatDuration(report.durationMs)}</span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 block text-[11px]">Repaired Steps</span>
            <span className="text-violet-300 font-bold mt-0.5 block">{report.repairedSteps} repaired</span>
          </div>
        </div>

        {/* Healing Attempts & Reasoning Section */}
        {report.healingAttempts.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-cyan-400" />
              <h2 className="text-base font-bold text-white">Autonomous Healing Resolution</h2>
            </div>

            {report.healingAttempts.map((att) => (
              <div key={att.id} className="p-5 rounded-2xl bg-slate-950 border border-violet-500/30 space-y-4 text-xs">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <span className="font-semibold text-slate-200">
                    Step {att.stepNumber}: Selector Timed Out
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                    Confidence: {(att.confidenceScore * 100).toFixed(1)}%
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/20 text-rose-300 font-mono text-[11px]">
                  <strong>Failure Reason: </strong>{att.failureReason}
                </div>

                {/* Candidate Selection Breakdown */}
                <div className="space-y-2">
                  <span className="text-slate-400 font-semibold block text-[11px]">
                    Top Candidate Element Match & Scoring:
                  </span>
                  <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between font-mono">
                      <span className="text-cyan-300 font-bold">{att.selectedCandidate.selector}</span>
                      <span className="text-emerald-400">Score: {att.selectedCandidate.confidence}</span>
                    </div>
                    <p className="text-slate-300 text-[11px]">{att.selectedCandidate.reasoning}</p>
                  </div>
                </div>

                <div>
                  <span className="text-slate-400 font-semibold block text-[11px] mb-1">Repaired Browser Action</span>
                  <code className="p-2.5 rounded-lg bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 font-mono font-bold block text-xs">
                    {att.repairedAction}
                  </code>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Assertion Results & Business Outcome Verification */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <h2 className="text-base font-bold text-white">Business Assertions & Goal Verification</h2>
          </div>

          <div className="rounded-xl border border-slate-800 divide-y divide-slate-800 text-xs">
            {report.assertionResults.map((assert, i) => (
              <div key={i} className="p-3.5 flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="font-semibold text-slate-200">{assert.assertion}</div>
                  <div className="font-mono text-[11px] text-slate-500">Evidence: {assert.evidence}</div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold shrink-0">
                  VERIFIED
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Remaining Risks & Maintenance Suggestions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Remaining Risks */}
          <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/20 space-y-2">
            <div className="font-bold text-amber-300 flex items-center gap-1.5">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
              <span>Remaining Architectural Risks</span>
            </div>
            <ul className="space-y-1 text-slate-400 list-disc list-inside text-[11px]">
              {report.remainingRisks.map((risk, i) => (
                <li key={i}>{risk}</li>
              ))}
            </ul>
          </div>

          {/* Maintenance Suggestions */}
          <div className="p-4 rounded-xl bg-slate-950 border border-cyan-500/20 space-y-2">
            <div className="font-bold text-cyan-300 flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5 text-cyan-400" />
              <span>CI Maintenance Recommendations</span>
            </div>
            <ul className="space-y-1 text-slate-400 list-disc list-inside text-[11px]">
              {report.maintenanceSuggestions.map((sug, i) => (
                <li key={i}>{sug}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
