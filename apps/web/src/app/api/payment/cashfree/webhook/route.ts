import { NextRequest, NextResponse } from "next/server";
import { verifyCashfreeWebhook } from "@/lib/cashfree";
import { onPaymentConfirmed } from "@/lib/onPaid";

export const runtime = "nodejs";

// Cashfree S2S webhook. Signature in x-webhook-signature, timestamp in
// x-webhook-timestamp. Payload type PAYMENT_SUCCESS_WEBHOOK confirms payment.
export async function POST(req: NextRequest) {
  const raw = await req.text();
  const sig = req.headers.get("x-webhook-signature") || "";
  const ts = req.headers.get("x-webhook-timestamp") || "";

  if (!verifyCashfreeWebhook(raw, sig, ts)) {
    return NextResponse.json({ error: "bad signature" }, { status: 401 });
  }

  let body: any;
  try { body = JSON.parse(raw); } catch { return NextResponse.json({ error: "bad json" }, { status: 400 }); }

  const type = body?.type;
  const data: any = body?.data;
  if (type === "PAYMENT_SUCCESS_WEBHOOK" && data?.order) {
    try {
      await onPaymentConfirmed({
        orderId: data.order.order_id,
        gateway: "cashfree",
        gatewayPaymentId: String(data.payment?.cf_payment_id ?? ""),
        gatewayOrderId: data.order.order_id,
        amountInr: Math.round(Number(data.order.order_amount) * 100),
        raw: body,
      });
    } catch (e) {
      console.error("cashfree webhook onPaid failed:", e);
    }
  }
  return NextResponse.json({ ok: true });
}
