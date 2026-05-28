import { NextRequest, NextResponse } from "next/server";
import { verifyPayuResponse } from "@/lib/payu";
import { onPaymentConfirmed } from "@/lib/onPaid";

export const runtime = "nodejs";

// PayU posts form-encoded data back here on success.
export async function POST(req: NextRequest) {
  const site = process.env.NEXT_PUBLIC_SITE_URL!;
  const form = await req.formData();
  const p: Record<string, string> = {};
  form.forEach((v, k) => (p[k] = String(v)));

  const orderId = p.udf1 || p.txnid;
  if (!verifyPayuResponse(p)) {
    return NextResponse.redirect(`${site}/thanks?status=invalid&order_id=${orderId}`, 303);
  }
  if (p.status === "success") {
    try {
      await onPaymentConfirmed({
        orderId,
        gateway: "payu",
        gatewayPaymentId: p.mihpayid || p.txnid,
        gatewayOrderId: p.txnid,
        amountInr: Math.round(parseFloat(p.amount) * 100),
        raw: p,
      });
    } catch (e) {
      console.error("payu onPaid failed:", e);
    }
    return NextResponse.redirect(`${site}/thanks?status=success&order_id=${orderId}`, 303);
  }
  return NextResponse.redirect(`${site}/thanks?status=failed&order_id=${orderId}`, 303);
}

// PayU sometimes does GET for testing
export async function GET(req: NextRequest) {
  const site = process.env.NEXT_PUBLIC_SITE_URL!;
  return NextResponse.redirect(`${site}/thanks`, 303);
}
