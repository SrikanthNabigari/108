"use client";
import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { PACKS, packTotal } from "@/lib/packs";

declare global {
  interface Window { Cashfree?: any; Razorpay?: any; }
}

// Sandbox mode: clicking any gateway simulates a successful payment (no real
// charge) via /api/payment/sandbox/confirm. Set NEXT_PUBLIC_PAYMENT_MODE=sandbox
// (and PAYMENT_MODE=sandbox server-side) to enable. Defaults to production.
const PAYMENT_MODE = process.env.NEXT_PUBLIC_PAYMENT_MODE || "production";
const IS_SANDBOX = PAYMENT_MODE === "sandbox";

function CheckoutForm() {
  const params = useSearchParams();
  const packId = params.get("pack") || "core";
  const pack = PACKS[packId] || PACKS.core;
  const amount = packTotal(packId, []);

  const [f, setF] = useState({
    full_name: "", email: "", phone: "", gender: "",
    birth_date: "", birth_time: "", birth_place_name: "",
    birth_latitude: "", birth_longitude: "", user_question: "",
  });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [placeResults, setPlaceResults] = useState<{ description: string; lat: number; lng: number }[]>([]);

  const upd = (k: string) => (e: any) => setF({ ...f, [k]: e.target.value });

  // Debounced place search → auto-fills lat/long via /api/geocode
  async function onPlaceType(e: any) {
    const v = e.target.value;
    setF((prev) => ({ ...prev, birth_place_name: v }));
    if (v.length < 3) { setPlaceResults([]); return; }
    const res = await fetch(`/api/geocode?q=${encodeURIComponent(v)}`);
    const data = await res.json();
    setPlaceResults(data.results || []);
  }
  function pickPlace(r: { description: string; lat: number; lng: number }) {
    setF((prev) => ({
      ...prev,
      birth_place_name: r.description,
      birth_latitude: String(r.lat),
      birth_longitude: String(r.lng),
    }));
    setPlaceResults([]);
  }

  async function createOrder() {
    setErr("");
    if (!f.full_name || !f.email || !f.birth_date || !f.birth_time) {
      setErr("Please fill name, email, birth date and time.");
      return null;
    }
    // Compose ISO datetime with +05:30 default (IST)
    const iso = `${f.birth_date}T${f.birth_time}:00+05:30`;
    const res = await fetch("/api/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: f.full_name,
        email: f.email,
        phone: f.phone,
        gender: f.gender,
        birth_datetime: iso,
        birth_latitude: parseFloat(f.birth_latitude || "0"),
        birth_longitude: parseFloat(f.birth_longitude || "0"),
        birth_place_name: f.birth_place_name,
        timezone: "Asia/Kolkata",
        pack_id: packId,
        addons: [],
        user_question: f.user_question,
      }),
    });
    const data = await res.json();
    if (!res.ok) { setErr(data.error || "order failed"); return null; }
    return data.orderId as string;
  }

  // Sandbox bypass — simulates success for whichever gateway was clicked.
  async function paySandbox(gateway: string) {
    setBusy(true);
    const orderId = await createOrder();
    if (!orderId) return setBusy(false);
    const res = await fetch("/api/payment/sandbox/confirm", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ orderId, gateway }),
    });
    const data = await res.json();
    if (!res.ok) { setErr(data.error || "sandbox payment failed"); return setBusy(false); }
    window.location.href = `/thanks?status=success&order_id=${orderId}`;
  }

  async function payPayu() {
    if (IS_SANDBOX) return paySandbox("payu");
    setBusy(true);
    const orderId = await createOrder();
    if (!orderId) return setBusy(false);
    // PayU create returns a self-submitting HTML form
    const res = await fetch("/api/payment/payu/create", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ orderId }),
    });
    const html = await res.text();
    document.open(); document.write(html); document.close();
  }

  async function payCashfree() {
    if (IS_SANDBOX) return paySandbox("cashfree");
    setBusy(true);
    const orderId = await createOrder();
    if (!orderId) return setBusy(false);
    const res = await fetch("/api/payment/cashfree/create", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ orderId }),
    });
    const data = await res.json();
    if (!res.ok) { setErr(data.error || "cashfree failed"); return setBusy(false); }
    // load Cashfree SDK and open checkout
    await loadScript("https://sdk.cashfree.com/js/v3/cashfree.js");
    const cashfree = window.Cashfree({ mode: data.env === "production" ? "production" : "sandbox" });
    cashfree.checkout({ paymentSessionId: data.payment_session_id, redirectTarget: "_self" });
  }

  async function payRazorpay() {
    if (IS_SANDBOX) return paySandbox("razorpay");
    setBusy(true);
    const orderId = await createOrder();
    if (!orderId) return setBusy(false);
    const res = await fetch("/api/payment/razorpay/create", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ orderId }),
    });
    const data = await res.json();
    if (!res.ok) { setErr(data.error || "razorpay failed"); return setBusy(false); }
    await loadScript("https://checkout.razorpay.com/v1/checkout.js");
    const rzp = new window.Razorpay({
      key: data.keyId, amount: data.amount, currency: "INR",
      name: "108 — Life's Operating System", order_id: data.rzpOrderId,
      prefill: { name: f.full_name, email: f.email, contact: f.phone },
      handler: () => { window.location.href = `/thanks?status=success&order_id=${orderId}`; },
      theme: { color: "#b8860b" },
    });
    rzp.open();
    setBusy(false);
  }

  return (
    <>
    <header className="nav">
      <a href="/" className="nav-logo"><b>108</b> Life&apos;s Operating System</a>
    </header>
    <main className="wrap" style={{ maxWidth: 600, paddingTop: 32, paddingBottom: 40 }}>
      <p className="eyebrow">Your Details</p>
      <h2 className="serif" style={{ fontSize: 38 }}>{pack.name}</h2>
      <p className="muted" style={{ marginBottom: 28 }}>
        ₹{(amount / 100).toFixed(0)} · one-time · {pack.pages}
      </p>

      <div className="field"><label>Full name *</label><input value={f.full_name} onChange={upd("full_name")} /></div>
      <div className="row">
        <div className="field"><label>Email *</label><input type="email" value={f.email} onChange={upd("email")} /></div>
        <div className="field"><label>Phone (for SMS)</label><input value={f.phone} onChange={upd("phone")} /></div>
      </div>
      <div className="row">
        <div className="field"><label>Birth date *</label><input type="date" value={f.birth_date} onChange={upd("birth_date")} /></div>
        <div className="field"><label>Birth time *</label><input type="time" value={f.birth_time} onChange={upd("birth_time")} /></div>
      </div>
      <div className="field" style={{ position: "relative" }}>
        <label>Birth place * (start typing your city)</label>
        <input placeholder="e.g. Bhimavaram, Andhra Pradesh" value={f.birth_place_name} onChange={onPlaceType} autoComplete="off" />
        {placeResults.length > 0 && (
          <div style={{ position: "absolute", zIndex: 10, left: 0, right: 0, background: "#0e0e12", border: "1px solid var(--line)", borderRadius: 2, marginTop: 4, overflow: "hidden" }}>
            {placeResults.map((r) => (
              <div key={r.description} onClick={() => pickPlace(r)}
                style={{ padding: "11px 14px", cursor: "pointer", fontSize: 14, borderBottom: "1px solid var(--line)" }}>
                {r.description}
              </div>
            ))}
          </div>
        )}
        {f.birth_latitude && (
          <p style={{ color: "var(--muted)", fontSize: 12, marginTop: 6 }}>
            📍 {parseFloat(f.birth_latitude).toFixed(4)}, {parseFloat(f.birth_longitude).toFixed(4)}
          </p>
        )}
      </div>
      <div className="field"><label>Your question (optional)</label><textarea rows={2} value={f.user_question} onChange={upd("user_question")} /></div>

      {err && <p style={{ color: "#e36", fontSize: 14 }}>{err}</p>}

      {IS_SANDBOX && (
        <p style={{ background: "var(--gold-soft)", border: "1px solid var(--line)", borderRadius: 2, padding: "11px 14px", fontSize: 13, color: "var(--gold)", marginTop: 20 }}>
          Sandbox mode — payments are simulated. Clicking any button completes the order without a real charge.
        </p>
      )}
      <p className="eyebrow" style={{ marginTop: 24, marginBottom: 12 }}>
        {IS_SANDBOX ? "Simulate payment with" : "Pay securely with"}
      </p>
      <div className="gateways">
        <button className="btn" disabled={busy} onClick={payRazorpay}>Razorpay</button>
        <button className="btn ghost" disabled={busy} onClick={payCashfree}>Cashfree</button>
        <button className="btn ghost" disabled={busy} onClick={payPayu}>PayU</button>
      </div>

    </main>
    <footer>108 — Life&apos;s Operating System</footer>
    </>
  );
}

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) return resolve();
    const s = document.createElement("script");
    s.src = src; s.onload = () => resolve(); s.onerror = reject;
    document.body.appendChild(s);
  });
}

export default function Checkout() {
  return (
    <Suspense fallback={<main className="wrap"><p style={{ padding: 40 }}>Loading…</p></main>}>
      <CheckoutForm />
    </Suspense>
  );
}
