"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { 
  Sparkles, 
  Save, 
  Play, 
  Sliders, 
  Globe, 
  Terminal, 
  ShieldCheck, 
  CheckCircle2, 
  Layers, 
  ArrowRight,
  Info,
  Check,
  Code
} from "lucide-react";
import { testCaseFormSchema, TestCaseFormValues, createZodResolver } from "@/lib/validators";
import { api } from "@/lib/api-client";

const INTENT_TEMPLATES = [
  {
    label: "E-Commerce Checkout",
    name: "Full Checkout & Order Confirmation",
    url: "http://localhost:5173/checkout",
    intent: "Complete checkout with a valid credit card and confirm that the order confirmation page is displayed.",
    outcome: "Order confirmation screen shows 'Thank you for your order' with generated Order ID.",
    steps: [
      "Navigate to /checkout",
      "Fill customer shipping inputs [Name, Address]",
      "Select Shipping method (Express)",
      "Populate test payment card credentials",
      "Click checkout submission action",
      "Assert confirmation screen and order ID",
    ],
  },
  {
    label: "User Authentication",
    name: "Standard User Login & Dashboard Check",
    url: "https://app.demo.io/login",
    intent: "Submit login form with standard tester credentials and verify user profile widget renders in top nav.",
    outcome: "Nav bar displays logged-in user avatar and workspace name.",
    steps: [
      "Navigate to /login",
      "Fill email: tester@example.com",
      "Fill password: [secure-token]",
      "Click submit login button",
      "Assert authenticated dashboard header",
    ],
  },
  {
    label: "Cart Recalculation",
    name: "Cart Quantity Increment & Price Update",
    url: "http://localhost:5173/cart",
    intent: "Increment item quantity from 1 to 2, wait for debounce recalculation, and verify subtotal updates accurately.",
    outcome: "Subtotal reflects 2x item price without full page reload.",
    steps: [
      "Navigate to /cart",
      "Click quantity '+' button",
      "Wait for network sync / debounce",
      "Assert subtotal matches $298.00",
    ],
  },
];

export default function NewTestPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [runningNow, setRunningNow] = useState(false);
  const [generatedSteps, setGeneratedSteps] = useState<string[]>(INTENT_TEMPLATES[0].steps);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<TestCaseFormValues>({
    resolver: createZodResolver(testCaseFormSchema),
    defaultValues: {
      name: INTENT_TEMPLATES[0].name,
      targetUrl: INTENT_TEMPLATES[0].url,
      intent: INTENT_TEMPLATES[0].intent,
      environment: "staging",
      browser: "chromium",
      selfHealingEnabled: true,
      maxHealingAttempts: 3,
      expectedOutcome: INTENT_TEMPLATES[0].outcome,
      testDataJson: '{\n  "fullName": "Alex Morgan",\n  "card": "4242••••••••4242"\n}',
    },
  });

  const currentIntent = watch("intent");
  const selfHealingEnabled = watch("selfHealingEnabled");
  const maxAttempts = watch("maxHealingAttempts");

  const applyTemplate = (tmpl: typeof INTENT_TEMPLATES[0]) => {
    setValue("name", tmpl.name);
    setValue("targetUrl", tmpl.url);
    setValue("intent", tmpl.intent);
    setValue("expectedOutcome", tmpl.outcome);
    setGeneratedSteps(tmpl.steps);
  };

  const onSubmit = async (data: TestCaseFormValues) => {
    setSubmitting(true);
    try {
      const created = await api.createTest(data);
      router.push("/tests");
    } finally {
      setSubmitting(false);
    }
  };

  const onSaveAndRun = async () => {
    setRunningNow(true);
    try {
      const data = watch();
      const created = await api.createTest(data);
      router.push(`/runs/${created.id}`);
    } finally {
      setRunningNow(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
      {/* Page Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold text-violet-400 uppercase tracking-widest">
            TEST SPECIFICATION ENGINE
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
          Create Intent-Based Test
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Specify what the test should accomplish in natural language. AegisTest synthesizes headless browser actions and heals broken locators autonomously.
        </p>
      </div>

      {/* Template Quick-Select Pills */}
      <div className="p-4 rounded-2xl glass-panel border border-slate-800 space-y-2.5">
        <div className="text-xs font-semibold text-slate-300 flex items-center gap-2">
          <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
          <span>Quick-Fill from Intent Templates:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {INTENT_TEMPLATES.map((tmpl) => (
            <button
              key={tmpl.label}
              type="button"
              onClick={() => applyTemplate(tmpl)}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-cyan-500/50 text-xs text-slate-300 transition-all flex items-center gap-1.5"
            >
              <span>{tmpl.label}</span>
              <ArrowRight className="h-3 w-3 text-cyan-400" />
            </button>
          ))}
        </div>
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Form Column (7 Cols) */}
          <div className="lg:col-span-7 space-y-5">
            {/* Test Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Test Name</label>
              <input
                {...register("name")}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-cyan-500 transition-colors"
                placeholder="e.g. User Checkout & Confirmation Flow"
              />
              {errors.name && <p className="text-rose-400 text-[11px]">{errors.name.message}</p>}
            </div>

            {/* Target URL */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Target Application URL</label>
              <div className="relative">
                <input
                  {...register("targetUrl")}
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-cyan-500 font-mono transition-colors"
                  placeholder="https://app.yourdomain.com or http://localhost:5173"
                />
                <Globe className="h-4 w-4 text-slate-500 absolute left-3 top-3" />
              </div>
              {errors.targetUrl && <p className="text-rose-400 text-[11px]">{errors.targetUrl.message}</p>}
            </div>

            {/* Natural-Language Intent (Source of Truth) */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-cyan-300 flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>Natural-Language Test Intent (Source of Truth)</span>
                </label>
                <span className="text-[10px] font-mono text-slate-500">Immutable Core</span>
              </div>
              <textarea
                {...register("intent")}
                rows={3}
                className="w-full p-3.5 rounded-xl bg-[#0B0F19] border border-cyan-500/40 text-slate-100 text-xs focus:outline-none focus:border-cyan-400 transition-colors leading-relaxed"
                placeholder="Describe what the tester or user intends to achieve in plain English..."
              />
              {errors.intent && <p className="text-rose-400 text-[11px]">{errors.intent.message}</p>}
            </div>

            {/* Expected Outcome */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Expected Outcome / Verification Rule</label>
              <textarea
                {...register("expectedOutcome")}
                rows={2}
                className="w-full p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:border-cyan-500 transition-colors"
                placeholder="e.g. Order confirmation screen shows 'Thank you for your order' with generated Order ID."
              />
              {errors.expectedOutcome && <p className="text-rose-400 text-[11px]">{errors.expectedOutcome.message}</p>}
            </div>

            {/* Environment & Browser Row */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Environment</label>
                <select
                  {...register("environment")}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-500"
                >
                  <option value="staging">Staging</option>
                  <option value="local">Local Development</option>
                  <option value="production">Production</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Browser Engine</label>
                <select
                  {...register("browser")}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-500"
                >
                  <option value="chromium">Chromium Headless</option>
                  <option value="firefox">Firefox Headless</option>
                  <option value="webkit">WebKit (Safari)</option>
                </select>
              </div>
            </div>

            {/* Self-Healing Controls */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-1.5">
                    <ShieldCheck className="h-4 w-4 text-emerald-400" />
                    <span>Autonomous Self-Healing</span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Repair broken locators dynamically if DOM mutations occur.
                  </p>
                </div>
                <input
                  type="checkbox"
                  {...register("selfHealingEnabled")}
                  className="h-4 w-4 rounded accent-cyan-500 cursor-pointer"
                />
              </div>

              {selfHealingEnabled && (
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <span className="text-slate-400">Max Healing Retries per Step:</span>
                  <select
                    {...register("maxHealingAttempts", { valueAsNumber: true })}
                    className="px-2 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs font-mono"
                  >
                    <option value={1}>1 Retry</option>
                    <option value={3}>3 Retries (Recommended)</option>
                    <option value={5}>5 Retries</option>
                  </select>
                </div>
              )}
            </div>
          </div>

          {/* Right Column (5 Cols): Live Step Synthesizer Preview */}
          <div className="lg:col-span-5 space-y-4">
            <div className="rounded-2xl glass-panel p-5 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-cyan-400" />
                  <span className="font-bold text-xs text-white">Synthesized Action Pipeline</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                  Preview
                </span>
              </div>

              <p className="text-[11px] text-slate-400">
                These browser steps are derived dynamically from your user intent. They will adapt if target selectors change.
              </p>

              <div className="space-y-2 pt-1 font-mono text-xs">
                {generatedSteps.map((step, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 flex items-start gap-2.5"
                  >
                    <span className="text-slate-600 text-[10px] font-bold mt-0.5">{idx + 1}</span>
                    <span className="text-[11px] text-slate-200 leading-snug">{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Test Data JSON Config */}
            <div className="rounded-2xl glass-panel p-5 border border-slate-800 space-y-2">
              <label className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                <Code className="h-3.5 w-3.5 text-violet-400" />
                <span>Test Fixture & Dataset (JSON)</span>
              </label>
              <textarea
                {...register("testDataJson")}
                rows={4}
                className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={() => router.push("/tests")}
            className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold border border-slate-800 transition-colors"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={submitting}
            className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 transition-all flex items-center gap-2"
          >
            <Save className="h-3.5 w-3.5 text-slate-300" />
            <span>{submitting ? "Saving..." : "Save Test"}</span>
          </button>

          <button
            type="button"
            onClick={onSaveAndRun}
            disabled={runningNow}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-xs font-bold shadow-glow-violet transition-all transform hover:-translate-y-0.5 flex items-center gap-2"
          >
            <Play className="h-3.5 w-3.5 fill-white" />
            <span>{runningNow ? "Launching Runner..." : "Save & Run Test"}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
