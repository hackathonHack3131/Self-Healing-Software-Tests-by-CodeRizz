"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ShieldCheck, Sparkles, ArrowRight, Lock, Mail, Play } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("tester@aegistest.dev");
  const [password, setPassword] = useState("••••••••••••");
  const [loading, setLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      router.push("/dashboard");
    }, 600);
  };

  const handleDemoAccess = () => {
    router.push("/demo-lab");
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative">
      <div className="absolute inset-0 bg-grid-pattern opacity-60 pointer-events-none" />
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 bg-violet-600/10 blur-3xl pointer-events-none" />

      <div className="relative z-10 w-full max-w-md rounded-3xl glass-panel p-8 border border-slate-800 shadow-2xl space-y-6">
        {/* Logo */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 via-indigo-600 to-cyan-500 shadow-glow-violet mx-auto">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-2xl font-extrabold text-white">Sign In to AegisTest</h1>
          <p className="text-xs text-slate-400">Autonomous Intent-Aware Testing Platform</p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-4 text-xs">
          <div className="space-y-1.5">
            <label className="text-slate-300 font-semibold">Email Address</label>
            <div className="relative">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                placeholder="name@company.com"
              />
              <Mail className="h-4 w-4 text-slate-500 absolute left-3 top-3" />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-slate-300 font-semibold">Password</label>
            <div className="relative">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              />
              <Lock className="h-4 w-4 text-slate-500 absolute left-3 top-3" />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2"
          >
            <span>{loading ? "Signing In..." : "Sign In with Credentials"}</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </form>

        <div className="relative flex items-center justify-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800" />
          </div>
          <span className="relative bg-[#090D16] px-3 text-[11px] font-mono text-slate-500">
            HACKATHON QUICK ACCESS
          </span>
        </div>

        {/* One-Click Demo Access Button */}
        <button
          onClick={handleDemoAccess}
          className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-bold text-xs shadow-glow-cyan transition-all flex items-center justify-center gap-2"
        >
          <Play className="h-3.5 w-3.5 fill-white" />
          <span>Continue as Demo Engineer (No Auth Needed)</span>
        </button>

        <div className="text-center text-[11px] text-slate-500">
          <Link href="/" className="hover:text-cyan-400 transition-colors">
            Back to Public Overview
          </Link>
        </div>
      </div>
    </div>
  );
}
