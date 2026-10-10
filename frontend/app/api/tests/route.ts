import { NextResponse } from "next/server";
import { SEED_TESTS } from "@/lib/mock-data";

export async function GET() {
  return NextResponse.json(SEED_TESTS);
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const newTest = {
      id: `test-${Date.now().toString(36)}`,
      name: body.name || "Untitled Intent Test",
      targetUrl: body.targetUrl || "http://localhost:5173",
      intent: body.intent || "",
      environment: body.environment || "staging",
      browser: body.browser || "chromium",
      selfHealingEnabled: body.selfHealingEnabled ?? true,
      maxHealingAttempts: body.maxHealingAttempts || 3,
      expectedOutcome: body.expectedOutcome || "Verification achieved",
      createdAt: new Date().toISOString(),
      status: "never_run",
    };
    return NextResponse.json(newTest, { status: 201 });
  } catch {
    return NextResponse.json({ error: "Invalid request payload" }, { status: 400 });
  }
}
