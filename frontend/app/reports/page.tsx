"use client";

import React from "react";
import Link from "next/link";
import { 
  FileCheck2, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  ArrowRight, 
  Download, 
  ShieldCheck, 
  Layers,
  ChevronRight,
  ExternalLink
} from "lucide-react";
import { formatDate, getStatusBadgeVariant } from "@/lib/utils";

const SAMPLE_REPORTS = [
  {
    id: "rep-chk-902",
    runId: "run-chk-902",
    testName: "E-Commerce Checkout & Order Confirmation",
    intent: "Complete checkout with a valid credit card and confirm that the order confirmation page is displayed.",
    date: "2026-10-10T17:45:00Z",
    initialStatus: "failed",
    finalStatus: "healed",
    repairedSteps: 1,
    durationFormatted: "2.8s",
    repairedSelector: "div.action-dock > button.btn-primary-gradient-v2",
  },
  {
    id: "rep-ath-889",
    runId: "run-ath-889",
    testName: "User Login & Dashboard Authorization",
    intent: "Submit login form with standard tester credentials and verify user profile widget renders in top nav.",
    date: "2026-10-10T16:12:00Z",
    initialStatus: "passed",
    finalStatus: "passed",
    repairedSteps: 0,
    durationFormatted: "1.9s",
    repairedSelector: null,
  },
  {
    id: "rep-crt-772",
    runId: "run-crt-772",
    testName: "Shopping Cart Quantity Increment",
    intent: "Increment item quantity from 1 to 2, wait for debounce recalculation, and verify subtotal updates accurately.",
    date: "2026-10-10T12:05:00Z",
    initialStatus: "failed",
    finalStatus: "healed",
    repairedSteps: 1,
    durationFormatted: "3.1s",
    repairedSelector: "button.qty-plus-btn",
  },
  {
    id: "rep-pay-651",
    runId: "run-pay-651",
    testName: "Payment Gateway 3D Secure Challenge Modal",
    intent: "Enter SMS OTP code '123456' inside iframe modal and confirm processing indicator completes.",
    date: "2026-10-09T18:22:00Z",
    initialStatus: "failed",
    finalStatus: "failed",
    repairedSteps: 0,
    durationFormatted: "5.4s",
    repairedSelector: null,
  },
];

export default function ReportsIndexPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-widest">
            POST-MORTEM & AUDIT EVIDENCE
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
          Healing Audit Reports
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Deep diagnostic documentation of UI mutations, AI candidate resolution, and verifiable business outcomes.
        </p>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {SAMPLE_REPORTS.map((rep) => (
          <div
            key={rep.id}
            className="rounded-2xl glass-panel p-5 border border-slate-800 hover:border-slate-700 transition-all space-y-4 group"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${getStatusBadgeVariant(
                      rep.finalStatus
                    )}`}
                  >
                    {rep.finalStatus === "healed" ? "SELF-HEALED" : rep.finalStatus.toUpperCase()}
                  </span>
                  <span className="text-[11px] font-mono text-slate-500">{formatDate(rep.date)}</span>
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-cyan-300 transition-colors mt-1.5">
                  {rep.testName}
                </h3>
              </div>
              <span className="text-xs font-mono text-slate-400 shrink-0">{rep.durationFormatted}</span>
            </div>

            <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{rep.intent}</p>

            {rep.repairedSelector && (
              <div className="p-2.5 rounded-lg bg-slate-950 border border-violet-500/30 text-xs font-mono">
                <span className="text-[10px] text-cyan-300 font-semibold block mb-0.5">Auto-Repaired Locator:</span>
                <span className="text-emerald-400 truncate block text-[11px]">{rep.repairedSelector}</span>
              </div>
            )}

            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[11px] text-slate-500 font-mono">
                {rep.repairedSteps > 0 ? `${rep.repairedSteps} repaired mutation` : "Direct pass (No DOM drift)"}
              </span>

              <Link
                href={`/reports/${rep.runId}`}
                className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-semibold transition-colors"
              >
                <span>Read Audit Report</span>
                <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
