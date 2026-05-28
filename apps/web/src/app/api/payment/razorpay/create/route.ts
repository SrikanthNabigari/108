import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";

export const runtime = "nodejs";

// POST { orderId } → { rzpOrderId, keyId, amount } for the Razorpay checkout.js
// Uses the REST Orders API directly (the node SDK drags in a broken legacy
// `request` dependency that doesn't bundle on Next.js).
export async function POST(req: NextRequest) {
  try {
    const { orderId } = await req.json();
    const sb = supabaseAdmin();
    const { data: order, error } = await sb
      .from("los_orders").select("*").eq("id", orderId).single();
    if (error || !order) return NextResponse.json({ error: "order not found" }, { status: 404 });

    const keyId = process.env.RAZORPAY_KEY_ID;
    const keySecret = process.env.RAZORPAY_KEY_SECRET;
    if (!keyId || !keySecret) return NextResponse.json({ error: "razorpay not configured" }, { status: 500 });

    const auth = Buffer.from(`${keyId}:${keySecret}`).toString("base64");
    const res = await fetch("https://api.razorpay.com/v1/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Basic ${auth}` },
      body: JSON.stringify({
        amount: order.amount_inr, // paise
        currency: "INR",
        receipt: orderId,
        notes: { los_order_id: orderId, pack: order.pack_id },
      }),
    });
    if (!res.ok) {
      const text = await res.text();
      return NextResponse.json({ error: `razorpay create failed: ${text}` }, { status: 502 });
    }
    const rzpOrder = await res.json();

    await sb.from("los_payments").insert({
      order_id: orderId,
      gateway: "razorpay",
      gateway_order_id: rzpOrder.id,
      amount_inr: order.amount_inr,
      status: "initiated",
      raw_response: rzpOrder as any,
    });

    return NextResponse.json({ rzpOrderId: rzpOrder.id, keyId, amount: order.amount_inr });
  } catch (e: any) {
    return NextResponse.json({ error: String(e?.message || e) }, { status: 500 });
  }
}
