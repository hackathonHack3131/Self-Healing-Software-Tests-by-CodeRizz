"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLandingPage = pathname === "/";
  const isLoginPage = pathname === "/login" || pathname === "/signup";

  if (isLandingPage || isLoginPage) {
    return <main className="min-h-screen bg-[#070A11] text-slate-100">{children}</main>;
  }

  return (
    <div className="flex min-h-screen bg-[#070A11] text-slate-100 antialiased selection:bg-violet-500 selection:text-white">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        <main className="flex-1 p-6 md:p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
