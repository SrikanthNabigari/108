import { NextRequest, NextResponse } from "next/server";
import { fetchCashfreeOrder } from "@/lib/cashfree";
import { onPaymentConfirmed } from "@/lib/onPaid";

export const runtime = "nodejs";

// Customer return URL after Cashfree checkout. We confirm status server-side
// (don't trust the redirect alone) then bounce to /thanks. The webhook is the
// source of truth; this is a UX convenience + fallback if webhook is delayed.
export async function GET(req: NextRequest) {
  const site = process.env.NEXT_PUBLIC_SITE_URL!;
  const orderId = req.nextUrl.searchParams.get("order_id") || "";
  if (!orderId) return NextResponse.redirect(`${site}/thanks`, 303);

  try {
    const order: any = await fetchCashfreeOrder(orderId);
    if (order?.order_status === "PAID") {
      await onPaymentConfirmed({
        orderId,
        gateway: "cashfree",
        gatewayPaymentId: String(order?.cf_order_id ?? ""),
        gatewayOrderId: orderId,
        amountInr: Math.round(Number(order.order_amount) * 100),
        raw: order,
      });
      return NextResponse.redirect(`${site}/thanks?status=success&order_id=${orderId}`, 303);
    }
  } catch (e) {
    console.error("cashfree success check failed:", e);
  }
  return NextResponse.redirect(`${site}/thanks?status=pending&order_id=${orderId}`, 303);
}
