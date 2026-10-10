"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  FlaskConical, 
  Play, 
  RotateCcw, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Layers, 
  Code2, 
  Sliders, 
  ArrowRight, 
  Terminal, 
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  Check,
  Zap,
  ShoppingBag,
  CreditCard,
  Truck,
  User,
  Copy,
  Info
} from "lucide-react";
import confetti from "canvas-confetti";
import { api, DemoComparisonResult } from "@/lib/api-client";
import { TestRun, CandidateElement } from "@/types";
import { formatDuration } from "@/lib/utils";

export default function DemoLabPage() {
  const [version, setVersion] = useState<"A" | "B">("A");
  const [selfHealingEnabled, setSelfHealingEnabled] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [currentRun, setCurrentRun] = useState<TestRun | null>(null);
  const [activeStepIndex, setActiveStepIndex] = useState<number>(-1);
  const [comparisonModalOpen, setComparisonModalOpen] = useState(false);
  const [comparisonData, setComparisonData] = useState<DemoComparisonResult | null>(null);

  // Simulated target store state
  const [customerName, setCustomerName] = useState("Alex Morgan");
  const [shippingMethod, setShippingMethod] = useState("express");
  const [cardNumber, setCardNumber] = useState("•••• •••• •••• 4242");
  const [orderConfirmed, setOrderConfirmed] = useState(false);
  const [orderId, setOrderId] = useState("ORD-84920");

  // Load comparison data on mount
  useEffect(() => {
    api.compareDemo().then(setComparisonData);
  }, []);

  // Reset to Version A
  const handleResetToVersionA = async () => {
    setIsRunning(false);
    setVersion("A");
    setOrderConfirmed(false);
    setCurrentRun(null);
    setActiveStepIndex(-1);
    await api.resetDemo();
  };

  // Switch to Version B
  const handleSwitchToVersionB = async () => {
    setIsRunning(false);
    setVersion("B");
    setOrderConfirmed(false);
    setCurrentRun(null);
    setActiveStepIndex(-1);
    await api.setDemoVersionB();
  };

  // Run Test (either on Version A or Version B)
  const handleRunTest = async () => {
    setIsRunning(true);
    setOrderConfirmed(false);
    setActiveStepIndex(0);

    // Call backend API / demo endpoint
    const runResult = await api.runDemo(version, selfHealingEnabled);

    // Animate execution step-by-step for great demo feel
    for (let i = 0; i < runResult.steps.length; i++) {
      setActiveStepIndex(i);
      await new Promise((r) => setTimeout(r, 650));
    }

    setCurrentRun(runResult);
    setIsRunning(false);

    if (runResult.finalResult === "passed" || runResult.finalResult === "healed") {
      setOrderConfirmed(true);
      if (runResult.finalResult === "healed") {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ["#8B5CF6", "#06B6D4", "#10B981"],
        });
      }
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Top Banner & Control Deck */}
      <div className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                STAR DEMO LAB
              </span>
              <span className="text-xs font-mono text-slate-400">Controlled E-Commerce Test Environment</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
              Version A vs. Version B Self-Healing Lab
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
              Simulate interface redesigns. Watch how traditional selector-based tests fail when <code className="text-rose-400 font-mono">#checkout-button</code> is removed, while AegisTest autonomously synthesizes the repaired locator.
            </p>
          </div>

          {/* Action Button Bar */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => setComparisonModalOpen(true)}
              className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700/80 hover:border-slate-600 text-xs text-slate-300 font-medium flex items-center gap-1.5 transition-colors"
            >
              <Code2 className="h-3.5 w-3.5 text-cyan-400" />
              <span>Compare DOM Diff</span>
            </button>

            <button
              onClick={handleResetToVersionA}
              className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700/80 hover:border-slate-600 text-xs text-slate-300 font-medium flex items-center gap-1.5 transition-colors"
            >
              <RotateCcw className="h-3.5 w-3.5 text-slate-400" />
              <span>Reset to Version A</span>
            </button>

            <button
              onClick={handleRunTest}
              disabled={isRunning}
              className={`px-5 py-2 rounded-xl font-bold text-xs flex items-center gap-2 transition-all shadow-glow-violet ${
                isRunning
                  ? "bg-slate-800 text-slate-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white transform hover:-translate-y-0.5"
              }`}
            >
              {isRunning ? (
                <>
                  <div className="h-3.5 w-3.5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
                  <span>Executing Workflow...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-white" />
                  <span>Run Test on Version {version}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Configuration Bar */}
        <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs">
          {/* Target Version Selector */}
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium">Target UI Version:</span>
            <div className="inline-flex rounded-xl p-1 bg-slate-950 border border-slate-800">
              <button
                onClick={handleResetToVersionA}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                  version === "A"
                    ? "bg-violet-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Version A (Baseline DOM)
              </button>
              <button
                onClick={handleSwitchToVersionB}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-all flex items-center gap-1.5 ${
                  version === "B"
                    ? "bg-cyan-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <span>Version B (Mutated UI)</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-900 text-cyan-200">New</span>
              </button>
            </div>
          </div>

          {/* Self-Healing Switch */}
          <div className="flex items-center gap-3">
            <span className="text-slate-400 font-medium">Self-Healing Engine:</span>
            <button
              onClick={() => setSelfHealingEnabled(!selfHealingEnabled)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border font-semibold transition-all ${
                selfHealingEnabled
                  ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300"
                  : "bg-rose-950/40 border-rose-500/40 text-rose-300"
              }`}
            >
              <div
                className={`h-2.5 w-2.5 rounded-full ${
                  selfHealingEnabled ? "bg-emerald-400 shadow-[0_0_8px_#34d399]" : "bg-rose-400"
                }`}
              />
              <span>{selfHealingEnabled ? "Self-Healing ENABLED" : "Self-Healing DISABLED"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Two-Column Interactive Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column (5 Cols): Live Embedded Target Checkout Web App */}
        <div className="lg:col-span-5 rounded-2xl glass-panel p-5 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <ShoppingBag className="h-4 w-4 text-cyan-400" />
              <span className="font-bold text-sm text-white">NovaShop Checkout</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                UI v{version === "A" ? "1.0" : "2.0"}
              </span>
            </div>

            <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-mono">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Target Viewport</span>
            </div>
          </div>

          {/* Checkout Screen Content */}
          {orderConfirmed ? (
            <div className="p-8 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-center space-y-3">
              <div className="h-12 w-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
                <CheckCircle2 className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-bold text-white">Order Confirmed!</h3>
              <p className="text-xs text-slate-300">
                Thank you for your purchase, {customerName}. Your order has been placed successfully.
              </p>
              <div className="inline-block p-2 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-cyan-300">
                Confirmation ID: {orderId}
              </div>
              <div className="pt-2">
                <button
                  onClick={() => setOrderConfirmed(false)}
                  className="text-xs text-slate-400 hover:text-white underline"
                >
                  Return to checkout form
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4 text-xs">
              {/* Customer Info Section */}
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center gap-2 text-slate-300 font-semibold">
                  <User className="h-3.5 w-3.5 text-violet-400" />
                  <span>Customer Details</span>
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block mb-1">Full Name</label>
                  <input
                    type="text"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-500"
                    placeholder="Enter full name"
                  />
                </div>
              </div>

              {/* Shipping Method Section */}
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center gap-2 text-slate-300 font-semibold">
                  <Truck className="h-3.5 w-3.5 text-indigo-400" />
                  <span>Shipping Method</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <label
                    className={`p-2 rounded-lg border flex items-center gap-2 cursor-pointer ${
                      shippingMethod === "standard"
                        ? "bg-violet-950/40 border-violet-500 text-white"
                        : "bg-slate-950 border-slate-800 text-slate-400"
                    }`}
                  >
                    <input
                      type="radio"
                      name="shipping"
                      value="standard"
                      checked={shippingMethod === "standard"}
                      onChange={() => setShippingMethod("standard")}
                      className="hidden"
                    />
                    <span>Standard ($4.99)</span>
                  </label>
                  <label
                    className={`p-2 rounded-lg border flex items-center gap-2 cursor-pointer ${
                      shippingMethod === "express"
                        ? "bg-cyan-950/40 border-cyan-500 text-white"
                        : "bg-slate-950 border-slate-800 text-slate-400"
                    }`}
                  >
                    <input
                      type="radio"
                      name="shipping"
                      value="express"
                      checked={shippingMethod === "express"}
                      onChange={() => setShippingMethod("express")}
                      className="hidden"
                    />
                    <span>Express ($12.00)</span>
                  </label>
                </div>
              </div>

              {/* Payment Section */}
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center gap-2 text-slate-300 font-semibold">
                  <CreditCard className="h-3.5 w-3.5 text-cyan-400" />
                  <span>Payment Information</span>
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block mb-1">Card Number (Test Simulation)</label>
                  <input
                    type="text"
                    value={cardNumber}
                    readOnly
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 font-mono text-xs"
                  />
                </div>
              </div>

              {/* Version A Button vs Version B Button Rendering */}
              {version === "A" ? (
                /* Version A: Classic flat container with baseline selector #checkout-button */
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-center space-y-2">
                  <div className="text-[10px] font-mono text-slate-500">
                    Selector: <code className="text-violet-300">#checkout-button</code>
                  </div>
                  <button
                    id="checkout-button"
                    onClick={() => setOrderConfirmed(true)}
                    className="w-full py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-bold transition-all shadow-md"
                  >
                    Complete Purchase — $149.00
                  </button>
                </div>
              ) : (
                /* Version B: Mutated DOM. Button renamed 'Place My Order', new class btn-primary-gradient-v2, inside .action-dock wrapper */
                <div className="p-4 rounded-xl bg-cyan-950/20 border border-cyan-500/30 space-y-2">
                  <div className="flex items-center justify-between text-[10px] font-mono">
                    <span className="text-cyan-300 font-semibold">Redesigned UI Dock (v2.0)</span>
                    <span className="text-rose-400">#checkout-button REMOVED</span>
                  </div>
                  <div className="action-dock p-2 rounded-xl bg-slate-950/80 border border-slate-800/80 flex items-center justify-between gap-3">
                    <div className="text-left pl-1">
                      <div className="text-[10px] text-slate-400">Total Due</div>
                      <div className="text-sm font-extrabold text-white">$149.00</div>
                    </div>
                    <button
                      data-testid="place-order-cta"
                      onClick={() => setOrderConfirmed(true)}
                      className="btn-primary-gradient-v2 flex-1 py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-white font-extrabold shadow-glow-cyan transition-all text-xs"
                    >
                      Place My Order
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column (7 Cols): The Autonomous AI Test Execution Engine */}
        <div className="lg:col-span-7 space-y-4">
          {/* Engine Header Card */}
          <div className="rounded-2xl glass-panel p-5 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal className="h-4 w-4 text-violet-400" />
                <span className="font-bold text-sm text-white">AI Test Agent Trace</span>
              </div>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                Intent: &quot;Complete checkout with a valid card&quot;
              </span>
            </div>

            {/* Workflow Steps Progress Timeline */}
            <div className="space-y-2 pt-1">
              {[
                { num: 1, title: "Populate customer shipping information", locator: "input#customer-name" },
                { num: 2, title: "Select express shipping radio method", locator: "input[name='shipping'][value='express']" },
                { num: 3, title: "Fill tokenized payment card details", locator: "input#card-number" },
                {
                  num: 4,
                  title: "Click checkout confirmation button",
                  locator: version === "A" ? "#checkout-button" : "#checkout-button (Original)",
                  healedLocator: "div.action-dock > button.btn-primary-gradient-v2",
                },
              ].map((step, idx) => {
                const isActive = activeStepIndex === idx && isRunning;
                const isPast = (activeStepIndex > idx || (currentRun && !isRunning));
                const isStep4 = idx === 3;
                const isStep4Healed = isStep4 && version === "B" && selfHealingEnabled && currentRun?.finalResult === "healed";
                const isStep4Failed = isStep4 && version === "B" && !selfHealingEnabled && currentRun?.finalResult === "failed";

                return (
                  <div
                    key={step.num}
                    className={`p-3 rounded-xl border transition-all text-xs ${
                      isActive
                        ? "bg-violet-950/40 border-violet-500 shadow-glow-violet/30"
                        : isStep4Failed
                        ? "bg-rose-950/20 border-rose-500/40"
                        : isStep4Healed
                        ? "bg-cyan-950/20 border-cyan-500/40"
                        : isPast
                        ? "bg-slate-900/60 border-slate-800/80"
                        : "bg-slate-950/40 border-slate-900 text-slate-500"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 font-semibold">
                        {isActive ? (
                          <div className="h-4 w-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin shrink-0" />
                        ) : isStep4Failed ? (
                          <XCircle className="h-4 w-4 text-rose-400 shrink-0" />
                        ) : isStep4Healed ? (
                          <Sparkles className="h-4 w-4 text-cyan-400 shrink-0" />
                        ) : isPast ? (
                          <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                        ) : (
                          <div className="h-4 w-4 rounded-full border border-slate-700 flex items-center justify-center text-[10px] text-slate-600 shrink-0">
                            {step.num}
                          </div>
                        )}
                        <span className={isPast || isActive ? "text-slate-200" : "text-slate-500"}>
                          Step {step.num}: {step.title}
                        </span>
                      </div>

                      {/* Status Tag */}
                      <span className="font-mono text-[10px]">
                        {isActive && <span className="text-cyan-400 animate-pulse">EXECUTING...</span>}
                        {isStep4Failed && <span className="text-rose-400 font-bold">SELECTOR FAILED</span>}
                        {isStep4Healed && <span className="text-cyan-300 font-bold">AUTO-HEALED</span>}
                        {isPast && !isStep4Failed && !isStep4Healed && <span className="text-emerald-400">PASSED</span>}
                      </span>
                    </div>

                    {/* Step details for Step 4 */}
                    {isStep4 && isStep4Healed && currentRun?.steps[3]?.healingAttempt && (
                      <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-cyan-500/30 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-cyan-300 flex items-center gap-1.5">
                            <Sparkles className="h-3.5 w-3.5" />
                            <span>Self-Healing Engine Intercept</span>
                          </span>
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-200 border border-cyan-800">
                            Confidence: 96.4%
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-300">
                          Baseline locator <code className="text-rose-400 font-mono">#checkout-button</code> was not found. Semantic vector synthesis scanned the DOM and discovered <code className="text-cyan-300 font-mono">Place My Order</code> inside container <code className="text-cyan-300 font-mono">div.action-dock</code>.
                        </p>
                        <div className="font-mono text-[11px] text-emerald-400 bg-emerald-950/30 p-1.5 rounded border border-emerald-500/20 truncate">
                          Repaired Action: click(&apos;div.action-dock &gt; button.btn-primary-gradient-v2&apos;)
                        </div>
                      </div>
                    )}

                    {isStep4 && isStep4Failed && (
                      <div className="mt-3 p-3 rounded-lg bg-rose-950/40 border border-rose-500/30 space-y-1.5">
                        <div className="font-bold text-rose-300 flex items-center gap-1.5">
                          <AlertTriangle className="h-3.5 w-3.5" />
                          <span>Test Failure: Traditional Locator Timed Out</span>
                        </div>
                        <p className="text-[11px] text-slate-300 font-mono">
                          TimeoutError: Element &apos;#checkout-button&apos; not found in DOM after 5000ms. Self-healing was disabled in settings.
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* AI Candidate Elements Scoring Matrix */}
          {version === "B" && selfHealingEnabled && (
            <div className="rounded-2xl glass-panel p-5 border border-violet-500/30 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-sm text-white flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-cyan-400" />
                    <span>Candidate Element Scoring & Confidence Ranking</span>
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    How AegisTest resolved the broken selector to the correct button
                  </p>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30">
                  Semantic Tree
                </span>
              </div>

              <div className="divide-y divide-slate-800 text-xs">
                {/* Winner Candidate */}
                <div className="py-2.5 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="h-5 w-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px] font-bold">
                        1
                      </span>
                      <span className="font-mono font-semibold text-slate-200">
                        div.action-dock &gt; button.btn-primary-gradient-v2
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 text-[10px] font-bold border border-emerald-800">
                        CHOSEN MATCH
                      </span>
                    </div>
                    <span className="font-mono font-bold text-cyan-300">96.4%</span>
                  </div>
                  <div className="grid grid-cols-4 gap-2 text-[10px] text-slate-400 font-mono">
                    <div>Text Match: 94%</div>
                    <div>Semantic Role: 98%</div>
                    <div>Container Prox: 95%</div>
                    <div>Visual Weight: 98%</div>
                  </div>
                  <p className="text-[11px] text-slate-300">
                    Text &apos;Place My Order&apos; matches original checkout intent. Action commits transaction with highest visual focus.
                  </p>
                </div>

                {/* Candidate 2 */}
                <div className="py-2.5 space-y-1 text-slate-400">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="h-5 w-5 rounded-full bg-slate-800 text-slate-500 flex items-center justify-center text-[10px]">
                        2
                      </span>
                      <span className="font-mono text-slate-400">button.btn-secondary-outline</span>
                    </div>
                    <span className="font-mono text-slate-500">38.2%</span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Label &apos;Return to Cart&apos; has negative semantic alignment with transaction completion intent.
                  </p>
                </div>

                {/* Candidate 3 */}
                <div className="py-2.5 space-y-1 text-slate-400">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="h-5 w-5 rounded-full bg-slate-800 text-slate-500 flex items-center justify-center text-[10px]">
                        3
                      </span>
                      <span className="font-mono text-slate-400">a.link-terms</span>
                    </div>
                    <span className="font-mono text-slate-500">12.5%</span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Anchor element &apos;Terms & conditions&apos; is informational hyperlink, not action submit trigger.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Console Diagnostic Stream */}
          {currentRun && (
            <div className="rounded-2xl bg-[#080C14] border border-slate-800 p-4 font-mono text-xs space-y-2">
              <div className="flex items-center justify-between text-slate-400 text-[11px] pb-2 border-b border-slate-800">
                <div className="flex items-center gap-1.5">
                  <Terminal className="h-3.5 w-3.5" />
                  <span>Real-Time Diagnostic Console</span>
                </div>
                <span>Duration: {formatDuration(currentRun.durationMs || 1500)}</span>
              </div>
              <div className="max-h-40 overflow-y-auto space-y-1 pt-1 text-slate-300">
                {currentRun.logs.map((log) => (
                  <div key={log.id} className="flex items-start gap-2 leading-relaxed">
                    <span className="text-slate-600 text-[10px] shrink-0">{log.timestamp}</span>
                    <span
                      className={`text-[10px] uppercase font-bold shrink-0 px-1 py-0.2 rounded ${
                        log.level === "ai"
                          ? "bg-violet-950 text-cyan-300"
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
                    <span className="truncate">{log.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* DOM Diff Comparison Modal */}
      {comparisonModalOpen && comparisonData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="w-full max-w-4xl rounded-2xl glass-panel p-6 border border-slate-700 shadow-2xl space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Code2 className="h-5 w-5 text-cyan-400" />
                  <span>DOM Mutation Diff: Baseline Version A vs. Mutated Version B</span>
                </h3>
                <p className="text-xs text-slate-400">
                  Inspect the DOM modifications that break traditional tests
                </p>
              </div>
              <button
                onClick={() => setComparisonModalOpen(false)}
                className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
              >
                Close Diff
              </button>
            </div>

            {/* Side-by-side Code Diff */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-[#090D16] border border-slate-800 space-y-2">
                <div className="text-rose-400 font-bold flex items-center gap-1.5">
                  <XCircle className="h-4 w-4" />
                  <span>Version A (Baseline DOM)</span>
                </div>
                <pre className="text-slate-300 overflow-x-auto whitespace-pre-wrap leading-relaxed text-[11px]">
                  {comparisonData.versionA.domTree}
                </pre>
                <div className="pt-2 text-slate-500 text-[10px]">
                  Selector: <code className="text-slate-300">#checkout-button</code>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[#090D16] border border-cyan-500/30 space-y-2">
                <div className="text-cyan-400 font-bold flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4" />
                  <span>Version B (Mutated DOM)</span>
                </div>
                <pre className="text-slate-300 overflow-x-auto whitespace-pre-wrap leading-relaxed text-[11px]">
                  {comparisonData.versionB.domTree}
                </pre>
                <div className="pt-2 text-cyan-300 text-[10px]">
                  Repaired: <code className="text-cyan-200">{comparisonData.versionB.checkoutSelector}</code>
                </div>
              </div>
            </div>

            {/* Structural Differences Table */}
            <div className="rounded-xl border border-slate-800 overflow-hidden text-xs">
              <table className="w-full text-left">
                <thead className="bg-slate-900/90 text-slate-400 text-[11px]">
                  <tr>
                    <th className="p-2.5">Field / Attribute</th>
                    <th className="p-2.5">Severity</th>
                    <th className="p-2.5">Version A Value</th>
                    <th className="p-2.5">Version B Value</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-300">
                  {comparisonData.structuralDifferences.map((diff, i) => (
                    <tr key={i} className="hover:bg-slate-900/40">
                      <td className="p-2.5 font-semibold">{diff.field}</td>
                      <td className="p-2.5">
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-violet-950 text-cyan-300 border border-violet-800">
                          {diff.impact}
                        </span>
                      </td>
                      <td className="p-2.5 font-mono text-[11px] text-rose-300">{diff.original}</td>
                      <td className="p-2.5 font-mono text-[11px] text-cyan-300">{diff.modified}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
