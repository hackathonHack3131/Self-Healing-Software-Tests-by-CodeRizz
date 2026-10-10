import { NextResponse } from "next/server";
import { SEED_DASHBOARD_METRICS } from "@/lib/mock-data";

export async function GET() {
  return NextResponse.json({
    ...SEED_DASHBOARD_METRICS,
    isBackendConnected: true,
  });
}
