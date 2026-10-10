"use client";

import React, { useState, useEffect } from "react";
import { 
  Settings, 
  Server, 
  Sliders, 
  ShieldCheck, 
  Save, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  Layers, 
  Cpu, 
  Radio,
  Sparkles,
  Info
} from "lucide-react";
import { api } from "@/lib/api-client";

export default function SettingsPage() {
  const [backendUrl, setBackendUrl] = useState("http://localhost:8000");
  const [defaultBrowser, setDefaultBrowser] = useState("chromium");
  const [defaultEnv, setDefaultEnv] = useState("staging");
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.85);
  const [maxRetries, setMaxRetries] = useState(3);
  const [captureScreenshots, setCaptureScreenshots] = useState(true);
  const [autoUpdateBaseline, setAutoUpdateBaseline] = useState(true);
  const [demoMode, setDemoMode] = useState(true);

  // Ping state
  const [pingStatus, setPingStatus] = useState<"idle" | "testing" | "success" | "failed">("idle");
  const [pingLatency, setPingLatency] = useState(0);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("aegis_backend_url");
      if (stored) setBackendUrl(stored);
    }
  }, []);

  const handleTestConnection = async () => {
    setPingStatus("testing");
    api.setBaseUrl(backendUrl);
    const res = await api.getHealth();
    if (res.backendConnected) {
      setPingStatus("success");
      setPingLatency(res.latencyMs);
    } else {
      setPingStatus("failed");
    }
  };

  const handleSave = () => {
    api.setBaseUrl(backendUrl);
    if (typeof window !== "undefined") {
      localStorage.setItem("aegis_backend_url", backendUrl);
      localStorage.setItem(
        "aegis_settings",
        JSON.stringify({
          backendUrl,
          defaultBrowser,
          defaultEnv,
          confidenceThreshold,
          maxRetries,
          captureScreenshots,
          autoUpdateBaseline,
          demoMode,
        })
      );
    }
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold text-violet-400 uppercase tracking-widest">
            ENGINE CONFIGURATION
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
          Settings & Backend Preferences
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Configure REST API integration endpoints, self-healing heuristic thresholds, and telemetry options.
        </p>
      </div>

      <div className="space-y-6">
        {/* Backend API Connection Card */}
        <div className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2 font-bold text-sm text-white">
              <Server className="h-4 w-4 text-cyan-400" />
              <span>Backend REST API Service</span>
            </div>
            <span className="text-[11px] font-mono text-slate-400">REST Contract v1.0</span>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300">Backend Server URL</label>
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <input
                type="text"
                value={backendUrl}
                onChange={(e) => setBackendUrl(e.target.value)}
                placeholder="http://localhost:8000"
                className="flex-1 px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
              />
              <button
                type="button"
                onClick={handleTestConnection}
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-colors flex items-center justify-center gap-2 shrink-0"
              >
                {pingStatus === "testing" ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin text-cyan-400" />
                ) : (
                  <Radio className="h-3.5 w-3.5 text-cyan-400" />
                )}
                <span>Test Connection</span>
              </button>
            </div>
          </div>

          {/* Connection Test Result Feedback */}
          {pingStatus === "success" && (
            <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
              <span>Connected to backend at {backendUrl} ({pingLatency}ms latency). Ready for live runs.</span>
            </div>
          )}

          {pingStatus === "failed" && (
            <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/40 text-amber-300 text-xs flex items-center gap-2">
              <Info className="h-4 w-4 shrink-0 text-amber-400" />
              <span>
                Backend server is unreachable on {backendUrl}. AegisTest will automatically use high-fidelity simulated fallback mode.
              </span>
            </div>
          )}
        </div>

        {/* Self-Healing Heuristic Thresholds Card */}
        <div className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 font-bold text-sm text-white pb-2 border-b border-slate-800">
            <Sparkles className="h-4 w-4 text-violet-400" />
            <span>AI Self-Healing Engine Preferences</span>
          </div>

          {/* Confidence Slider */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-300">Minimum AI Candidate Confidence Threshold</span>
              <span className="font-mono text-cyan-300 font-bold">{(confidenceThreshold * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="0.99"
              step="0.01"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">
              Only candidates with match scores exceeding this threshold will be selected for dynamic step repair.
            </p>
          </div>

          {/* Max Healing Attempts */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 text-xs">
            <div className="space-y-1.5">
              <label className="font-semibold text-slate-300">Max Healing Attempts per Broken Step</label>
              <select
                value={maxRetries}
                onChange={(e) => setMaxRetries(parseInt(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-xs"
              >
                <option value={1}>1 Attempt</option>
                <option value={2}>2 Attempts</option>
                <option value={3}>3 Attempts (Standard)</option>
                <option value={5}>5 Attempts (Aggressive)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-slate-300">Default Execution Browser</label>
              <select
                value={defaultBrowser}
                onChange={(e) => setDefaultBrowser(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-xs"
              >
                <option value="chromium">Chromium</option>
                <option value="firefox">Firefox</option>
                <option value="webkit">WebKit (Safari)</option>
              </select>
            </div>
          </div>

          {/* Checkboxes */}
          <div className="space-y-3 pt-3 border-t border-slate-800/80 text-xs">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={captureScreenshots}
                onChange={(e) => setCaptureScreenshots(e.target.checked)}
                className="h-4 w-4 rounded accent-cyan-500"
              />
              <span className="text-slate-300">Capture DOM Screenshots for Before/After Healing Verification</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={autoUpdateBaseline}
                onChange={(e) => setAutoUpdateBaseline(e.target.checked)}
                className="h-4 w-4 rounded accent-cyan-500"
              />
              <span className="text-slate-300">Generate Git baseline pull request patch when test heals</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={demoMode}
                onChange={(e) => setDemoMode(e.target.checked)}
                className="h-4 w-4 rounded accent-cyan-500"
              />
              <span className="text-slate-300">Enable high-fidelity simulated fallback when offline (Demo Mode)</span>
            </label>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-between pt-2">
          {savedSuccess ? (
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4" />
              <span>Preferences saved successfully!</span>
            </span>
          ) : (
            <span className="text-xs text-slate-500">Settings are persisted to your local browser storage.</span>
          )}

          <button
            type="button"
            onClick={handleSave}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-xs font-bold shadow-glow-violet transition-all transform hover:-translate-y-0.5 flex items-center gap-2"
          >
            <Save className="h-3.5 w-3.5" />
            <span>Save Preferences</span>
          </button>
        </div>
      </div>
    </div>
  );
}
