import { NextRequest, NextResponse } from "next/server";
import { createCashfreeOrder } from "@/lib/cashfree";
import { supabaseAdmin } from "@/lib/supabase";

export const runtime = "nodejs";

// POST { orderId } → returns { payment_session_id } for Cashfree JS checkout.
export async function POST(req: NextRequest) {
  try {
    const { orderId } = await req.json();
    const sb = supabaseAdmin();
    const { data: order, error } = await sb
      .from("los_orders").select("*").eq("id", orderId).single();
    if (error || !order) return NextResponse.json({ error: "order not found" }, { status: 404 });

    const site = process.env.NEXT_PUBLIC_SITE_URL!;
    const cf = await createCashfreeOrder({
      orderId,
      amountRupees: order.amount_inr / 100,
      customerId: orderId,
      customerName: order.full_name,
      customerEmail: order.email,
      customerPhone: order.phone || "9999999999",
      returnUrl: `${site}/api/payment/cashfree/success`,
    });

    await sb.from("los_payments").insert({
      order_id: orderId,
      gateway: "cashfree",
      gateway_order_id: cf.order_id,
      amount_inr: order.amount_inr,
      status: "initiated",
      raw_response: cf as any,
    });

    return NextResponse.json({
      payment_session_id: cf.payment_session_id,
      order_id: cf.order_id,
      env: (process.env.CASHFREE_ENV || "test").toLowerCase(),
    });
  } catch (e: any) {
    return NextResponse.json({ error: String(e?.message || e) }, { status: 500 });
  }
}
