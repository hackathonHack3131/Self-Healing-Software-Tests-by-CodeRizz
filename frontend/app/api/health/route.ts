import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    service: "AegisTest Engine",
    version: "2.4.0",
    timestamp: new Date().toISOString(),
    backendConnected: true,
  });
}
