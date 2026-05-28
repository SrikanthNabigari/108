import { NextRequest, NextResponse } from "next/server";
import { buildPayuForm } from "@/lib/payu";
import { supabaseAdmin } from "@/lib/supabase";

export const runtime = "nodejs";

// POST { orderId } → returns a self-submitting PayU form (HTML) the browser posts.
export async function POST(req: NextRequest) {
  try {
    const { orderId } = await req.json();
    const sb = supabaseAdmin();
    const { data: order, error } = await sb
      .from("los_orders").select("*").eq("id", orderId).single();
    if (error || !order) return NextResponse.json({ error: "order not found" }, { status: 404 });

    const site = process.env.NEXT_PUBLIC_SITE_URL!;
    const { action, fields } = buildPayuForm({
      txnid: orderId,
      amount: (order.amount_inr / 100).toFixed(2),
      productinfo: `108 ${order.pack_id} reading`,
      firstname: order.full_name,
      email: order.email,
      phone: order.phone || "",
      surl: `${site}/api/payment/payu/success`,
      furl: `${site}/api/payment/payu/failure`,
      udf1: orderId,
    });

    // self-submitting form
    const inputs = Object.entries(fields)
      .map(([k, v]) => `<input type="hidden" name="${k}" value="${String(v).replace(/"/g, "&quot;")}"/>`)
      .join("");
    const html = `<!doctype html><html><body onload="document.forms[0].submit()">
      <form method="post" action="${action}">${inputs}</form>
      <p style="font-family:sans-serif">Redirecting to PayU…</p></body></html>`;
    return new NextResponse(html, { headers: { "Content-Type": "text/html" } });
  } catch (e: any) {
    return NextResponse.json({ error: String(e?.message || e) }, { status: 500 });
  }
}
