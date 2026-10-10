import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  const sec = (ms / 1000).toFixed(1);
  return `${sec}s`;
}

export function formatDate(dateString: string): string {
  try {
    const d = new Date(dateString);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateString;
  }
}

export function getStatusBadgeVariant(status: string) {
  switch (status) {
    case "passed":
      return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    case "healed":
      return "bg-violet-500/15 text-violet-300 border-violet-500/30";
    case "failed":
      return "bg-rose-500/15 text-rose-400 border-rose-500/30";
    case "healing":
    case "detecting_change":
      return "bg-cyan-500/15 text-cyan-300 border-cyan-500/30 animate-pulse";
    case "running":
      return "bg-amber-500/15 text-amber-300 border-amber-500/30 animate-pulse";
    default:
      return "bg-slate-700/30 text-slate-400 border-slate-700/50";
  }
}
