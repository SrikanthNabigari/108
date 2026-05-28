import nodemailer from "nodemailer";
import { supabaseAdmin } from "./supabase";

// SMTP transactional email (Gmail app password or any SMTP).
// Gateway-side SMS/email (Cashfree) is automatic; this covers our own
// "report ready" + "payment confirmed" mails and logs every send.

function transport() {
  const host = process.env.SMTP_HOST;
  const port = Number(process.env.SMTP_PORT || 587);
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;
  if (!host || !user || !pass) throw new Error("SMTP_* env not set");
  return nodemailer.createTransport({
    host,
    port,
    secure: port === 465,
    auth: { user, pass },
  });
}

export async function sendEmail(args: {
  orderId?: string;
  to: string;
  subject: string;
  html: string;
  template?: string;
}) {
  const fromName = process.env.SMTP_FROM_NAME || "108 — Life's Operating System";
  const fromEmail = process.env.SMTP_FROM_EMAIL || process.env.SMTP_USER!;
  const sb = supabaseAdmin();

  // de-dup: skip if this template already sent for this order
  if (args.orderId && args.template) {
    const { data } = await sb
      .from("los_notifications")
      .select("id")
      .eq("order_id", args.orderId)
      .eq("template", args.template)
      .eq("status", "sent")
      .limit(1);
    if (data && data.length) return { skipped: true };
  }

  let status = "sent";
  let error: string | null = null;
  let messageId: string | null = null;
  try {
    const info = await transport().sendMail({
      from: `"${fromName}" <${fromEmail}>`,
      to: args.to,
      subject: args.subject,
      html: args.html,
    });
    messageId = info.messageId;
  } catch (e: any) {
    status = "failed";
    error = String(e?.message || e);
  }

  await sb.from("los_notifications").insert({
    order_id: args.orderId ?? null,
    channel: "email",
    template: args.template ?? null,
    recipient: args.to,
    subject: args.subject,
    provider: "smtp",
    provider_msg_id: messageId,
    status,
    error_message: error,
    sent_at: status === "sent" ? new Date().toISOString() : null,
  });

  if (status === "failed") throw new Error(error || "email failed");
  return { messageId };
}

export function reportReadyEmail(name: string, downloadUrl: string) {
  return {
    subject: "Your 108 Life Reading is ready",
    html: `<div style="font-family:Georgia,serif;max-width:520px;margin:auto;color:#1a1a1a">
      <h2 style="color:#b8860b">Namaste ${name},</h2>
      <p>Your 108 Life Reading has been decoded and is ready to download.</p>
      <p style="margin:28px 0"><a href="${downloadUrl}"
        style="background:#b8860b;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none">
        Download your reading (PDF)</a></p>
      <p style="color:#666;font-size:13px">This link is private to you. Save the PDF — the link expires in 30 days.</p>
      <p style="color:#999;font-size:12px;margin-top:32px">108 — Life's Operating System</p>
    </div>`,
  };
}

export function paymentConfirmedEmail(name: string, packName: string, amountRupees: number) {
  return {
    subject: "Payment received — your 108 reading is being prepared",
    html: `<div style="font-family:Georgia,serif;max-width:520px;margin:auto;color:#1a1a1a">
      <h2 style="color:#b8860b">Namaste ${name},</h2>
      <p>We've received your payment of <b>₹${amountRupees.toFixed(0)}</b> for the
      <b>${packName}</b>.</p>
      <p>Your chart is being decoded now. You'll receive a second email with your
      download link shortly — usually within a few minutes.</p>
      <p style="color:#999;font-size:12px;margin-top:32px">108 — Life's Operating System</p>
    </div>`,
  };
}
