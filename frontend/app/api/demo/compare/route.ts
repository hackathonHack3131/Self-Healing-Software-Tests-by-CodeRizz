import { NextResponse } from "next/server";
import { api } from "@/lib/api-client";

export async function GET() {
  const result = await api.compareDemo();
  return NextResponse.json(result);
}
