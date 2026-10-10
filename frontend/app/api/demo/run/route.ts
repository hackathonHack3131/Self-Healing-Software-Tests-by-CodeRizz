import { NextResponse } from "next/server";
import { api } from "@/lib/api-client";

export async function POST(req: Request) {
  try {
    const { version = "A", selfHealing = true } = await req.json();
    const result = api.generateDemoRun(version as "A" | "B", Boolean(selfHealing));
    return NextResponse.json(result);
  } catch {
    const result = api.generateDemoRun("A", true);
    return NextResponse.json(result);
  }
}
