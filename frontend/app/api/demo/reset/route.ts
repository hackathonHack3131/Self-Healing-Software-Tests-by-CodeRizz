import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({
    version: "A",
    message: "Demo reset to baseline Version A successfully.",
    timestamp: new Date().toISOString(),
  });
}
