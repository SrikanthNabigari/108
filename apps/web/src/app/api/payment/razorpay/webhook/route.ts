import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";
import { onPaymentConfirmed } from "@/lib/onPaid";

export const runtime = "nodejs";

// Razorpay webhook. Signature is HMAC-SHA256(rawBody, RAZORPAY_WEBHOOK_SECRET)
// in x-razorpay-signature. payment.captured event confirms payment.
export async function POST(req: NextRequest) {
  const raw = await req.text();
  const sig = req.headers.get("x-razorpay-signature") || "";
  const secret = process.env.RAZORPAY_WEBHOOK_SECRET;
  if (!secret) return NextResponse.json({ error: "webhook secret not set" }, { status: 500 });

  const expected = crypto.createHmac("sha256", secret).update(raw).digest("hex");
  if (expected !== sig) return NextResponse.json({ error: "bad signature" }, { status: 401 });

  let body: any;
  try { body = JSON.parse(raw); } catch { return NextResponse.json({ error: "bad json" }, { status: 400 }); }

  if (body?.event === "payment.captured") {
    const pay = body.payload?.payment?.entity;
    const orderId = pay?.notes?.los_order_id || pay?.receipt;
    if (orderId) {
      try {
        await onPaymentConfirmed({
          orderId,
          gateway: "razorpay",
          gatewayPaymentId: pay.id,
          gatewayOrderId: pay.order_id,
          amountInr: pay.amount, // already paise
          raw: body,
        });
      } catch (e) {
        console.error("razorpay webhook onPaid failed:", e);
      }
    }
  }
  return NextResponse.json({ ok: true });
}
