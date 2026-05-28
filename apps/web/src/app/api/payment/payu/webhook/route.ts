import { NextRequest, NextResponse } from "next/server";
import { verifyPayuResponse } from "@/lib/payu";
import { onPaymentConfirmed } from "@/lib/onPaid";

export const runtime = "nodejs";

// PayU server-to-server webhook (form-encoded). Mirror of success route but
// no redirect — returns 200 so PayU stops retrying.
export async function POST(req: NextRequest) {
  const form = await req.formData();
  const p: Record<string, string> = {};
  form.forEach((v, k) => (p[k] = String(v)));
  const orderId = p.udf1 || p.txnid;

  if (verifyPayuResponse(p) && p.status === "success") {
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
      console.error("payu webhook onPaid failed:", e);
    }
  }
  return NextResponse.json({ ok: true });
}
