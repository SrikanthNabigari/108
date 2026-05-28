import crypto from "crypto";

// Cashfree PG (Orders API v2023-08-01). Creating an order returns a
// payment_session_id used to redirect the customer to the hosted checkout.
// Cashfree auto-sends email + SMS notifications for the order when
// customer_details include email + phone.
const CF_BASE: Record<string, string> = {
  test: "https://sandbox.cashfree.com/pg",
  production: "https://api.cashfree.com/pg",
};

export function cashfreeConfig() {
  const appId = process.env.CASHFREE_APP_ID;
  const secret = process.env.CASHFREE_SECRET_KEY;
  const env = (process.env.CASHFREE_ENV || "test").toLowerCase();
  if (!appId || !secret) throw new Error("CASHFREE_APP_ID / CASHFREE_SECRET_KEY not set");
  return { appId, secret, env, base: CF_BASE[env] || CF_BASE.test };
}

export async function createCashfreeOrder(args: {
  orderId: string;
  amountRupees: number;
  customerId: string;
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  returnUrl: string;
}) {
  const { appId, secret, base } = cashfreeConfig();
  const res = await fetch(`${base}/orders`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-version": "2023-08-01",
      "x-client-id": appId,
      "x-client-secret": secret,
    },
    body: JSON.stringify({
      order_id: args.orderId,
      order_amount: args.amountRupees,
      order_currency: "INR",
      customer_details: {
        customer_id: args.customerId,
        customer_name: args.customerName,
        customer_email: args.customerEmail,
        customer_phone: args.customerPhone,
      },
      order_meta: {
        return_url: `${args.returnUrl}?order_id={order_id}`,
        // Cashfree sends email + SMS automatically when notify is enabled
        notify_url: `${process.env.NEXT_PUBLIC_SITE_URL}/api/payment/cashfree/webhook`,
      },
      order_note: "108 — Life's Operating System Reading",
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Cashfree order create failed (${res.status}): ${text}`);
  }
  return res.json() as Promise<{
    order_id: string;
    payment_session_id: string;
    order_status: string;
  }>;
}

// Verify Cashfree webhook signature: HMAC-SHA256(base64) of (timestamp + rawBody) with secret
export function verifyCashfreeWebhook(rawBody: string, signature: string, timestamp: string): boolean {
  const { secret } = cashfreeConfig();
  const payload = timestamp + rawBody;
  const expected = crypto.createHmac("sha256", secret).update(payload).digest("base64");
  return expected === signature;
}

export async function fetchCashfreeOrder(orderId: string) {
  const { appId, secret, base } = cashfreeConfig();
  const res = await fetch(`${base}/orders/${orderId}`, {
    headers: {
      "x-api-version": "2023-08-01",
      "x-client-id": appId,
      "x-client-secret": secret,
    },
  });
  if (!res.ok) throw new Error(`Cashfree order fetch failed: ${res.status}`);
  return res.json();
}
