"use client";

import React, { useState } from "react";
import Link from "next/link";
import { 
  ShieldCheck, 
  Sparkles, 
  ArrowRight, 
  Play, 
  Cpu, 
  Activity, 
  Layers, 
  Zap, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Terminal, 
  Sliders,
  ChevronRight,
  GitBranch,
  Search,
  Eye,
  Check,
  Code,
  ShieldAlert
} from "lucide-react";
import { motion } from "framer-motion";

export default function LandingPage() {
  const [activeWorkflowStep, setActiveWorkflowStep] = useState(3); // Start on "Heal"

  const workflowSteps = [
    {
      step: "01",
      name: "Intent",
      summary: "Natural Language Specification",
      description: "Write human objectives instead of brittle CSS/XPath strings. Example: 'Complete checkout with standard credit card'.",
      code: `test("checkout") {\n  intent: "Complete checkout with valid card and verify confirmation"\n}`,
      icon: Terminal,
      color: "from-blue-500 to-indigo-500",
    },
    {
      step: "02",
      name: "Understand",
      summary: "Autonomous DOM & State Parsing",
      description: "The AI inspects interactive accessibility trees, form controls, and visual boundaries to synthesize user journeys.",
      code: `[Agent] Analyzing DOM tree: 48 interactive nodes detected\n[Agent] Synthesizing action pipeline: [Fill Shipping, Select Method, Commit]`,
      icon: Eye,
      color: "from-indigo-500 to-violet-500",
    },
    {
      step: "03",
      name: "Execute",
      summary: "Deterministic Headless Execution",
      description: "Runs real browser actions in Chromium, Firefox, or WebKit with real-time screenshot capture and console recording.",
      code: `✓ step_1: input#fullName -> "Alex Morgan"\n✓ step_2: radio[name=shipping] -> "express"\n✓ step_3: input#card -> 4242••••4242`,
      icon: Play,
      color: "from-violet-500 to-purple-500",
    },
    {
      step: "04",
      name: "Heal",
      summary: "Self-Healing AI Engine",
      description: "When a button renames or moves into a new container, the agent detects the mutation, scores candidate elements, and repairs the step on the fly.",
      code: `⚠ #checkout-button missing!\n✦ AI Agent inspecting candidate elements:\n  → button.btn-primary-gradient-v2 ('Place My Order') [96.4% confidence]\n✓ Repaired action synthesized: click(div.action-dock > button)`,
      icon: Sparkles,
      color: "from-purple-500 to-cyan-500",
    },
    {
      step: "05",
      name: "Verify",
      summary: "Trustworthy Outcome Assurance",
      description: "Verifies the ultimate user goal (e.g. Order #ORD-84920 rendered) and generates an automated Pull Request to update the test baseline.",
      code: `✓ Goal verified: Order confirmed screen reached (#ORD-84920)\n✦ Suggested baseline patch generated for git repo`,
      icon: CheckCircle2,
      color: "from-cyan-500 to-emerald-500",
    },
  ];

  return (
    <div className="relative min-h-screen bg-[#070A11] text-slate-100 overflow-x-hidden">
      {/* Background ambient lighting & grid */}
      <div className="absolute inset-0 bg-grid-pattern opacity-60 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[450px] bg-gradient-to-b from-violet-600/20 via-cyan-500/10 to-transparent blur-3xl pointer-events-none -z-10" />

      {/* Top Navigation */}
      <header className="relative z-20 flex h-20 items-center justify-between px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 via-indigo-600 to-cyan-500 shadow-glow-violet">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <div>
            <span className="font-extrabold text-lg tracking-tight text-white flex items-center gap-2">
              AegisTest
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/40">
                HACKATHON EDITION
              </span>
            </span>
            <p className="text-xs text-slate-400">Self-Healing E2E Test Platform</p>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-8 text-sm text-slate-300 font-medium">
          <a href="#workflow" className="hover:text-cyan-400 transition-colors">How It Works</a>
          <a href="#comparison" className="hover:text-cyan-400 transition-colors">Comparison</a>
          <a href="#benefits" className="hover:text-cyan-400 transition-colors">Key Benefits</a>
          <Link href="/demo-lab" className="hover:text-cyan-400 transition-colors flex items-center gap-1 text-cyan-300">
            <Sparkles className="h-4 w-4" />
            <span>Interactive Lab</span>
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 border border-slate-700/80 text-xs font-semibold transition-all"
          >
            Dashboard
          </Link>
          <Link
            href="/demo-lab"
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-glow-violet transition-all transform hover:-translate-y-0.5 flex items-center gap-2"
          >
            <span>Live Demo</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 pt-16 pb-20 px-6 max-w-6xl mx-auto text-center">
        {/* Release Tag Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-violet-950/40 border border-violet-500/30 text-violet-300 text-xs font-mono mb-8 backdrop-blur-md shadow-sm">
          <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
          <span>Intent-Aware Testing • Goodbye Flaky CSS Selectors</span>
        </div>

        {/* Hero Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.12]">
          Tests That <span className="text-gradient-violet-cyan">Heal Themselves</span>.
        </h1>

        {/* Supporting Text */}
        <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto font-normal leading-relaxed">
          Traditional E2E tests break whenever a developer renames a button or redesigns a component.
          <strong className="text-slate-200 font-semibold"> AegisTest</strong> understands natural-language user intent, detects DOM mutations, heals broken steps in real-time, and guarantees continuous verification.
        </p>

        {/* CTA Buttons */}
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-semibold text-sm shadow-glow-violet transition-all transform hover:-translate-y-0.5 flex items-center justify-center gap-2"
          >
            <Zap className="h-4 w-4" />
            <span>Launch Dashboard</span>
          </Link>
          <Link
            href="/demo-lab"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 border border-slate-700/80 hover:border-cyan-500/40 font-semibold text-sm transition-all flex items-center justify-center gap-2 group"
          >
            <Play className="h-4 w-4 fill-cyan-400 text-cyan-400 group-hover:scale-110 transition-transform" />
            <span>Watch Live Version A/B Demo</span>
          </Link>
        </div>

        {/* Terminal Quick Teaser */}
        <div className="mt-14 max-w-3xl mx-auto rounded-2xl glass-panel-glow p-4 text-left font-mono text-xs shadow-2xl">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-rose-500/70" />
              <div className="h-3 w-3 rounded-full bg-amber-500/70" />
              <div className="h-3 w-3 rounded-full bg-emerald-500/70" />
              <span className="ml-2 text-slate-400 text-[11px]">aegis-intent-runner :: checkout-spec.ai</span>
            </div>
            <span className="text-[10px] text-cyan-400 font-semibold px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800">
              SELF-HEALING ACTIVE
            </span>
          </div>
          <div className="pt-3 space-y-1.5 text-slate-300">
            <p className="text-slate-500"># User Goal: "Complete checkout with a valid credit card"</p>
            <p className="text-emerald-400">✓ [00:00.620] Input customer details: name="Alex Morgan"</p>
            <p className="text-emerald-400">✓ [00:00.820] Selected shipping option: method="express"</p>
            <p className="text-rose-400 font-semibold">✗ [00:01.320] Traditional Selector Failed: &apos;#checkout-button&apos; not found in DOM</p>
            <p className="text-cyan-300 bg-cyan-950/30 p-1.5 rounded border border-cyan-500/20 font-semibold">
              ✦ [00:01.520] AI REPAIR TRIGGERED: Identified new button &apos;Place My Order&apos; (confidence 96.4%) in &apos;div.action-dock&apos;
            </p>
            <p className="text-emerald-400 font-semibold">
              ✓ [00:02.820] Repaired action dispatched. Target achieved: Order #ORD-84920 verified!
            </p>
          </div>
        </div>
      </section>

      {/* Visual Workflow Section */}
      <section id="workflow" className="relative z-10 py-20 px-6 max-w-6xl mx-auto border-t border-slate-800/80">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-xs font-mono font-semibold text-cyan-400 uppercase tracking-widest">
            AUTONOMOUS TESTING ARCHITECTURE
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">
            The 5-Stage Intent Lifecycle
          </h2>
          <p className="text-slate-400 text-sm mt-3">
            From natural language instruction to continuous verification and automated PR updates.
          </p>
        </div>

        {/* Step Tabs */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 mb-8">
          {workflowSteps.map((s, idx) => {
            const Icon = s.icon;
            const isSelected = activeWorkflowStep === idx;
            return (
              <button
                key={s.step}
                onClick={() => setActiveWorkflowStep(idx)}
                className={`p-3.5 rounded-xl border text-left transition-all ${
                  isSelected
                    ? "bg-violet-950/40 border-violet-500 shadow-glow-violet text-white"
                    : "bg-slate-900/40 border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200"
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-mono text-cyan-400 font-bold">{s.step}</span>
                  <Icon className={`h-4 w-4 ${isSelected ? "text-violet-400" : "text-slate-500"}`} />
                </div>
                <div className="text-sm font-bold tracking-tight">{s.name}</div>
                <div className="text-[11px] text-slate-400 truncate mt-0.5">{s.summary}</div>
              </button>
            );
          })}
        </div>

        {/* Step Detail Card */}
        <div className="rounded-2xl glass-panel p-6 sm:p-8 border border-violet-500/20">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-5 space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/30 text-violet-300 text-xs font-mono">
                Stage {workflowSteps[activeWorkflowStep].step} of 05
              </div>
              <h3 className="text-2xl font-bold text-white">
                {workflowSteps[activeWorkflowStep].name} — {workflowSteps[activeWorkflowStep].summary}
              </h3>
              <p className="text-slate-300 text-sm leading-relaxed">
                {workflowSteps[activeWorkflowStep].description}
              </p>
              <div className="pt-2">
                <Link
                  href="/demo-lab"
                  className="inline-flex items-center gap-2 text-cyan-400 text-xs font-semibold hover:text-cyan-300 transition-colors"
                >
                  <span>Experience this live in Demo Lab</span>
                  <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
            </div>

            <div className="lg:col-span-7">
              <div className="rounded-xl bg-[#090D16] border border-slate-800 p-4 font-mono text-xs">
                <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-800 text-slate-500 text-[11px]">
                  <span>Execution Trace Inspection</span>
                  <span className="text-cyan-400">Step {activeWorkflowStep + 1} / 5</span>
                </div>
                <pre className="text-slate-200 overflow-x-auto whitespace-pre-wrap leading-relaxed">
                  {workflowSteps[activeWorkflowStep].code}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Selector-Based vs Intent-Aware Comparison Matrix */}
      <section id="comparison" className="relative z-10 py-20 px-6 max-w-6xl mx-auto border-t border-slate-800/80">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-xs font-mono font-semibold text-cyan-400 uppercase tracking-widest">
            PARADIGM SHIFT
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">
            Traditional vs. Intent-Aware Tests
          </h2>
          <p className="text-slate-400 text-sm mt-3">
            Why rigid CSS/XPath selectors cause 80% of CI/CD test flake, and how semantic testing solves it forever.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Traditional Card */}
          <div className="rounded-2xl bg-rose-950/10 border border-rose-500/20 p-6 sm:p-8 space-y-5">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-rose-500/20 flex items-center justify-center text-rose-400">
                <XCircle className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Traditional Selector Tests</h3>
                <p className="text-xs text-rose-300/80">Cypress / Selenium / Playwright hardcoded locators</p>
              </div>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3">
                <XCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200">Brittle DOM Locators:</strong> Fails instantly if a developer renames <code className="text-rose-400">#checkout-button</code> or migrates to Tailwind classes.
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3">
                <XCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200">Maintenance Nightmare:</strong> Engineers spend 30%+ of their sprint updating stale test selectors after simple UI refactors.
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3">
                <XCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200">False-Alarm CI Blockers:</strong> Build fails and blocks releases even though the user checkout flow works flawlessly.
                </div>
              </div>
            </div>
          </div>

          {/* Intent-Aware Card */}
          <div className="rounded-2xl bg-violet-950/20 border border-violet-500/30 p-6 sm:p-8 space-y-5 shadow-glow-violet/20">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-cyan-500/20 flex items-center justify-center text-cyan-400 shadow-glow-cyan">
                <CheckCircle2 className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">AegisTest Intent-Aware Tests</h3>
                <p className="text-xs text-cyan-300">Semantic reasoning with autonomous self-healing</p>
              </div>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-violet-500/30 flex items-start gap-3">
                <CheckCircle2 className="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200">Survives Redesigns:</strong> Understands &apos;Complete checkout&apos; regardless of whether button is named &apos;Place My Order&apos; or moved into a modal dock.
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-violet-500/30 flex items-start gap-3">
                <CheckCircle2 className="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200">Autonomous Candidate Ranking:</strong> Scans accessibility tree, text similarity, and visual layout to pick replacement elements with &gt;95% confidence.
                </div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-violet-500/30 flex items-start gap-3">
                <CheckCircle2 className="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-slate-200">Distinguishes Real Bugs:</strong> Accurately flags authentic backend 500 crashes and broken business logic while ignoring benign DOM restyling.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Benefits Grid */}
      <section id="benefits" className="relative z-10 py-20 px-6 max-w-6xl mx-auto border-t border-slate-800/80">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-xs font-mono font-semibold text-cyan-400 uppercase tracking-widest">
            ENGINEERING VALUE
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">
            Built for Modern Fast-Paced Teams
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="rounded-2xl glass-panel p-6 border border-slate-800 hover:border-violet-500/40 transition-all">
            <div className="h-10 w-10 rounded-xl bg-violet-500/20 flex items-center justify-center text-violet-400 mb-4">
              <Zap className="h-5 w-5" />
            </div>
            <h4 className="text-base font-bold text-white mb-2">90% Less Flaky Tests</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              No more random CI red builds caused by tiny CSS updates, dynamic IDs, or third-party badge wrappers.
            </p>
          </div>

          <div className="rounded-2xl glass-panel p-6 border border-slate-800 hover:border-cyan-500/40 transition-all">
            <div className="h-10 w-10 rounded-xl bg-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4">
              <RefreshCw className="h-5 w-5" />
            </div>
            <h4 className="text-base font-bold text-white mb-2">Automatic Locator Repair</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Synthesizes healed locators on the fly and generates git commit suggestions to update your test repository.
            </p>
          </div>

          <div className="rounded-2xl glass-panel p-6 border border-slate-800 hover:border-violet-500/40 transition-all">
            <div className="h-10 w-10 rounded-xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
              <Activity className="h-5 w-5" />
            </div>
            <h4 className="text-base font-bold text-white mb-2">Faster Root-Cause Debug</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Comprehensive side-by-side DOM diffs, candidate confidence rankings, and console logs at every lifecycle step.
            </p>
          </div>

          <div className="rounded-2xl glass-panel p-6 border border-slate-800 hover:border-cyan-500/40 transition-all">
            <div className="h-10 w-10 rounded-xl bg-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <h4 className="text-base font-bold text-white mb-2">Trustworthy Verification</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Verifies true business end-states rather than superficial button clicks, safeguarding real user workflows.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Bottom Banner */}
      <section className="relative z-10 py-16 px-6 max-w-5xl mx-auto mb-16">
        <div className="rounded-3xl glass-panel-glow p-8 sm:p-12 text-center relative overflow-hidden border border-violet-500/30">
          <div className="relative z-10 max-w-2xl mx-auto space-y-5">
            <h3 className="text-3xl font-extrabold text-white">
              Ready to witness intent-aware self-healing in action?
            </h3>
            <p className="text-sm text-slate-300">
              Run the interactive Version A vs. Version B checkout experiment right now and watch the AI agent detect changes and heal in real time.
            </p>
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/demo-lab"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-bold text-sm shadow-glow-violet transition-all transform hover:-translate-y-0.5 flex items-center justify-center gap-2"
              >
                <Sparkles className="h-4 w-4" />
                <span>Open Star Demo Lab</span>
              </Link>
              <Link
                href="/dashboard"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 hover:bg-slate-800 font-semibold text-sm transition-all"
              >
                Explore Analytics Dashboard
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800/80 py-10 px-6 max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-violet-400" />
          <span className="font-semibold text-slate-400">AegisTest Project</span>
          <span>• Intent-Aware Self-Healing End-to-End Testing</span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/demo-lab" className="hover:text-slate-300 transition-colors">Demo Lab</Link>
          <Link href="/dashboard" className="hover:text-slate-300 transition-colors">Dashboard</Link>
          <Link href="/tests/new" className="hover:text-slate-300 transition-colors">Test Builder</Link>
          <Link href="/settings" className="hover:text-slate-300 transition-colors">API Settings</Link>
        </div>
      </footer>
    </div>
  );
}
