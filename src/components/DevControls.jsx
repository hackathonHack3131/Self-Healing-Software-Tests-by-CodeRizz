import React, { useState } from 'react';
import { useDemo } from '../context/DemoContext';
import {
  Sliders,
  RotateCcw,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Cpu,
  Layers,
  Sparkles
} from 'lucide-react';

export const DevControls = () => {
  const {
    version,
    setVersion,
    preset,
    setPreset,
    simulatePaymentFailure,
    setSimulatePaymentFailure,
    resetDemoState,
    checkoutButtonId,
    placeOrderButtonId
  } = useDemo();

  const [isExpanded, setIsExpanded] = useState(true);

  const presets = [
    {
      id: 'baseline',
      label: 'Baseline (vA)',
      desc: 'Original IDs & Standard Layout',
      version: 'A'
    },
    {
      id: 'renamed',
      label: 'Renamed IDs',
      desc: 'Modified IDs & Text, Base Layout',
      version: 'A*'
    },
    {
      id: 'layout',
      label: 'Layout Changed',
      desc: 'Rearranged Layout, Base IDs',
      version: 'A+'
    },
    {
      id: 'combined',
      label: 'Combined (vB)',
      desc: 'Full Version B Redesign',
      version: 'B'
    }
  ];

  return (
    <aside
      aria-label="Developer Testing Toolbar"
      data-testid="healtest-dev-toolbar"
      className="sticky top-0 z-50 bg-slate-900 border-b border-slate-800 text-slate-100 shadow-xl backdrop-blur-md bg-opacity-95 text-xs transition-all duration-300"
    >
      <div className="max-w-7xl mx-auto px-4 py-2 flex flex-wrap items-center justify-between gap-3">
        {/* Left: Branding & Status Badge */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 font-bold tracking-wider text-cyan-400">
            <Cpu className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span className="uppercase tracking-widest text-[11px] font-mono">HealTest AI Target</span>
          </div>
          <span className="h-4 w-px bg-slate-700 hidden sm:block"></span>

          {/* Version Switcher Buttons */}
          <div className="flex items-center bg-slate-800/80 p-0.5 rounded-lg border border-slate-700">
            <button
              type="button"
              id="dev-switch-version-a"
              onClick={() => setVersion('A')}
              className={`px-2.5 py-1 rounded-md font-semibold text-[11px] transition-smooth flex items-center space-x-1 ${
                version === 'A'
                  ? 'bg-cyan-500 text-slate-950 shadow-sm shadow-cyan-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <span>Version A</span>
              {version === 'A' && <CheckCircle2 className="w-3 h-3 ml-0.5" />}
            </button>
            <button
              type="button"
              id="dev-switch-version-b"
              onClick={() => setVersion('B')}
              className={`px-2.5 py-1 rounded-md font-semibold text-[11px] transition-smooth flex items-center space-x-1 ${
                version === 'B'
                  ? 'bg-indigo-500 text-white shadow-sm shadow-indigo-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <span>Version B</span>
              {version === 'B' && <CheckCircle2 className="w-3 h-3 ml-0.5" />}
            </button>
          </div>
        </div>

        {/* Center: Presets */}
        <div className="hidden lg:flex items-center space-x-1 bg-slate-800/50 p-0.5 rounded-lg border border-slate-700/60">
          <span className="text-[10px] text-slate-400 font-mono px-2 uppercase tracking-wider flex items-center gap-1">
            <Layers className="w-3 h-3" /> Presets:
          </span>
          {presets.map((p) => {
            const isSelected = preset === p.id;
            return (
              <button
                key={p.id}
                type="button"
                id={`dev-preset-${p.id}`}
                onClick={() => setPreset(p.id)}
                title={p.desc}
                className={`px-2 py-1 rounded text-[11px] font-medium transition-smooth ${
                  isSelected
                    ? 'bg-slate-700 text-cyan-300 font-semibold border border-cyan-500/30 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/40'
                }`}
              >
                {p.label}
              </button>
            );
          })}
        </div>

        {/* Right: Payment Failure Simulator Toggle & Reset Demo */}
        <div className="flex items-center space-x-2.5">
          {/* Simulated Payment Failure Toggle */}
          <button
            type="button"
            id="simulate-payment-failure-toggle"
            role="switch"
            aria-checked={simulatePaymentFailure}
            onClick={() => setSimulatePaymentFailure(!simulatePaymentFailure)}
            className={`flex items-center space-x-2 px-2.5 py-1 rounded-lg border cursor-pointer select-none transition-smooth ${
              simulatePaymentFailure
                ? 'bg-rose-950/60 border-rose-600/80 text-rose-300'
                : 'bg-slate-800/60 border-slate-700 text-slate-300 hover:bg-slate-800'
            }`}
          >
            <AlertTriangle
              className={`w-3.5 h-3.5 ${
                simulatePaymentFailure ? 'text-rose-400 animate-bounce' : 'text-slate-400'
              }`}
            />
            <span className="text-[11px] font-medium">
              Simulate Failure:
            </span>
            <span
              className={`font-mono font-bold text-[10px] uppercase px-1.5 py-0.5 rounded ${
                simulatePaymentFailure
                  ? 'bg-rose-500 text-white'
                  : 'bg-slate-700 text-slate-400'
              }`}
            >
              {simulatePaymentFailure ? 'ON' : 'OFF'}
            </span>
          </button>

          {/* Reset Demo Button */}
          <button
            type="button"
            id="reset-demo-button"
            onClick={resetDemoState}
            className="flex items-center space-x-1.5 px-3 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-lg font-medium text-[11px] transition-smooth active:scale-95"
            title="Reset Cart, Checkout, and Order states to baseline"
          >
            <RotateCcw className="w-3 h-3 text-amber-400" />
            <span>Reset Demo</span>
          </button>

          {/* Collapse/Expand Toggle */}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
            title="Toggle details"
          >
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Sub-bar showing active DOM target locators (Useful for automated testing visualization) */}
      {isExpanded && (
        <div className="bg-slate-950/80 border-t border-slate-800/80 px-4 py-1.5 text-[10px] font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center space-x-4">
            <span className="flex items-center gap-1">
              <span className="text-slate-500">Active Preset:</span>
              <span className="text-cyan-300 font-semibold uppercase">{preset}</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="text-slate-500">Cart Checkout Button:</span>
              <code className="text-amber-300 bg-slate-900 px-1 py-0.5 rounded border border-slate-800">
                #{checkoutButtonId}
              </code>
            </span>
            <span className="flex items-center gap-1">
              <span className="text-slate-500">Order Submit Button:</span>
              <code className="text-emerald-300 bg-slate-900 px-1 py-0.5 rounded border border-slate-800">
                #{placeOrderButtonId}
              </code>
            </span>
          </div>

          <div className="hidden md:flex items-center space-x-2 text-slate-500">
            <span>URL:</span>
            <code className="text-slate-300 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
              ?version={version}
            </code>
          </div>
        </div>
      )}
    </aside>
  );
};
