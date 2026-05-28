import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";

export const runtime = "nodejs";

// GET → order status + latest report public_url (if ready).
export async function GET(_req: NextRequest, { params }: { params: { id: string } }) {
  const sb = supabaseAdmin();
  const { data: order, error } = await sb
    .from("los_orders")
    .select("id, full_name, pack_id, status, created_at, paid_at, generated_at, delivered_at")
    .eq("id", params.id)
    .single();
  if (error || !order) return NextResponse.json({ error: "not found" }, { status: 404 });

  const { data: report } = await sb
    .from("los_reports")
    .select("public_url, page_count, generated_at, version")
    .eq("order_id", params.id)
    .order("version", { ascending: false })
    .limit(1)
    .maybeSingle();

  return NextResponse.json({ order, report: report ?? null });
}
