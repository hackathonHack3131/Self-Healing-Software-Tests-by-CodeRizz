"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  FolderGit2, 
  Search, 
  Filter, 
  PlusCircle, 
  Play, 
  ExternalLink, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  RotateCcw,
  SlidersHorizontal,
  ChevronRight,
  FileText
} from "lucide-react";
import { api } from "@/lib/api-client";
import { TestCase } from "@/types";
import { SEED_TESTS } from "@/lib/mock-data";
import { formatDate, getStatusBadgeVariant } from "@/lib/utils";

export default function TestsPage() {
  const [tests, setTests] = useState<TestCase[]>(SEED_TESTS);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTests().then((data) => {
      setTests(data);
      setLoading(false);
    });
  }, []);

  const filteredTests = tests.filter((t) => {
    const matchesSearch =
      t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.intent.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.targetUrl.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return false;
    if (statusFilter === "all") return true;
    return t.status === statusFilter;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            Test Catalog & Intent Repository
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Maintainable natural-language test specifications with automated self-healing telemetry.
          </p>
        </div>

        <Link
          href="/tests/new"
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-glow-violet transition-all transform hover:-translate-y-0.5"
        >
          <PlusCircle className="h-4 w-4" />
          <span>New Intent Test</span>
        </Link>
      </div>

      {/* Filter & Search Bar */}
      <div className="rounded-2xl glass-panel p-4 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative w-full md:w-96">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search tests by name, intent, or URL..."
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-500 transition-colors"
          />
          <Search className="h-4 w-4 text-slate-500 absolute left-3 top-2.5" />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-2 self-start md:self-auto overflow-x-auto w-full md:w-auto text-xs">
          <span className="text-slate-500 text-[11px] uppercase font-mono mr-1">Filter:</span>
          {[
            { id: "all", label: "All Tests" },
            { id: "healed", label: "Self-Healed" },
            { id: "passed", label: "Direct Passed" },
            { id: "failed", label: "Failed" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStatusFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors shrink-0 ${
                statusFilter === tab.id
                  ? "bg-violet-600/30 text-cyan-300 border border-violet-500/40"
                  : "bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Test Table Card */}
      <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#090D16] text-slate-400 font-mono text-[11px] border-b border-slate-800">
              <tr>
                <th className="p-4">Test Specification</th>
                <th className="p-4">Target Application</th>
                <th className="p-4">Environment</th>
                <th className="p-4">Self-Healing</th>
                <th className="p-4">Status</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-slate-300">
              {filteredTests.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-500">
                    No tests match your filter criteria.
                  </td>
                </tr>
              ) : (
                filteredTests.map((test) => (
                  <tr key={test.id} className="hover:bg-slate-900/40 transition-colors group">
                    <td className="p-4">
                      <div className="font-semibold text-white group-hover:text-cyan-300 transition-colors">
                        {test.name}
                      </div>
                      <p className="text-[11px] text-slate-400 line-clamp-1 max-w-md mt-0.5 font-medium">
                        {test.intent}
                      </p>
                    </td>

                    <td className="p-4 font-mono text-[11px] text-slate-400">
                      <span className="truncate max-w-[200px] block">{test.targetUrl}</span>
                    </td>

                    <td className="p-4">
                      <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 uppercase">
                        {test.environment}
                      </span>
                    </td>

                    <td className="p-4">
                      {test.selfHealingEnabled ? (
                        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
                          <Sparkles className="h-3 w-3 text-cyan-400" />
                          <span>Enabled ({test.maxHealingAttempts}x)</span>
                        </span>
                      ) : (
                        <span className="text-slate-500 text-[11px]">Disabled</span>
                      )}
                    </td>

                    <td className="p-4">
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${getStatusBadgeVariant(
                          test.status || "never_run"
                        )}`}
                      >
                        {(test.status || "never_run").toUpperCase()}
                      </span>
                    </td>

                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/runs/${test.id}`}
                          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors flex items-center gap-1 font-medium text-[11px]"
                        >
                          <Play className="h-3 w-3 fill-slate-300" />
                          <span>Run</span>
                        </Link>
                        <Link
                          href={`/reports/${test.id}`}
                          className="p-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                          title="View Report"
                        >
                          <FileText className="h-3.5 w-3.5" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
