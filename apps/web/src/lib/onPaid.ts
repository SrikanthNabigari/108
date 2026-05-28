import { supabaseAdmin } from "./supabase";
import { sendEmail, paymentConfirmedEmail } from "./notify";
import { PACKS } from "./packs";

// Single idempotent entry point called by every gateway's success/webhook
// path once payment is confirmed. Marks the order paid, records the payment,
// fires the confirmation email, and enqueues report generation.
//
// No WhatsApp intake step — we generate straight off the purchase form fields.
export async function onPaymentConfirmed(args: {
  orderId: string;
  gateway: "razorpay" | "payu" | "cashfree";
  gatewayPaymentId: string;
  gatewayOrderId?: string;
  amountInr: number; // paise
  raw: Record<string, unknown>;
}) {
  const sb = supabaseAdmin();

  // Idempotency: if order already paid, no-op.
  const { data: order } = await sb
    .from("los_orders")
    .select("*")
    .eq("id", args.orderId)
    .single();
  if (!order) throw new Error(`order ${args.orderId} not found`);
  if (order.status !== "created") {
    return { alreadyProcessed: true, status: order.status };
  }

  // Record the payment row.
  await sb.from("los_payments").insert({
    order_id: args.orderId,
    gateway: args.gateway,
    gateway_order_id: args.gatewayOrderId ?? null,
    gateway_payment_id: args.gatewayPaymentId,
    amount_inr: args.amountInr,
    status: "success",
    raw_response: args.raw,
    completed_at: new Date().toISOString(),
  });

  // Flip order → paid (triggers the generation worker that polls this status).
  await sb
    .from("los_orders")
    .update({ status: "paid", paid_at: new Date().toISOString() })
    .eq("id", args.orderId);

  // Fire confirmation email (best-effort; never block the webhook on it).
  try {
    const pack = PACKS[order.pack_id];
    const mail = paymentConfirmedEmail(
      order.full_name,
      pack?.name ?? order.pack_id,
      order.amount_inr / 100,
    );
    await sendEmail({
      orderId: args.orderId,
      to: order.email,
      subject: mail.subject,
      html: mail.html,
      template: "payment_confirmed",
    });
  } catch (e) {
    console.error("payment_confirmed email failed:", e);
  }

  return { ok: true };
}
