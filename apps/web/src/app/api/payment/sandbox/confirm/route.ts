import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";
import { onPaymentConfirmed } from "@/lib/onPaid";

export const runtime = "nodejs";

// Sandbox / test-pay bypass. Active ONLY when PAYMENT_MODE=sandbox on the
// server. Marks the order paid via the same idempotent fulfilment path used
// by the real gateways (recorded as gateway 'manual'). Flip PAYMENT_MODE to
// 'production' once real gateway keys are configured to disable this.
export async function POST(req: NextRequest) {
  if (process.env.PAYMENT_MODE !== "sandbox") {
    return NextResponse.json({ error: "sandbox payments disabled" }, { status: 403 });
  }
  try {
    const { orderId, gateway } = await req.json();
    if (!orderId) return NextResponse.json({ error: "orderId required" }, { status: 400 });

    const sb = supabaseAdmin();
    const { data: order, error } = await sb
      .from("los_orders").select("*").eq("id", orderId).single();
    if (error || !order) return NextResponse.json({ error: "order not found" }, { status: 404 });

    await onPaymentConfirmed({
      orderId,
      gateway: "manual",
      gatewayPaymentId: `SANDBOX-${Date.now()}`,
      amountInr: order.amount_inr,
      raw: { sandbox: true, clicked_gateway: gateway ?? null },
    });

    return NextResponse.json({ ok: true, sandbox: true });
  } catch (e: any) {
    return NextResponse.json({ error: String(e?.message || e) }, { status: 500 });
  }
}
