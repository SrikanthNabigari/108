"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

function Thanks() {
  const params = useSearchParams();
  const status = params.get("status") || "pending";
  const orderId = params.get("order_id") || "";
  const [report, setReport] = useState<{ public_url?: string } | null>(null);
  const [orderStatus, setOrderStatus] = useState("");

  useEffect(() => {
    if (!orderId) return;
    let tries = 0;
    const poll = setInterval(async () => {
      tries++;
      const res = await fetch(`/api/order/${orderId}`);
      if (res.ok) {
        const data = await res.json();
        setOrderStatus(data.order?.status || "");
        if (data.report?.public_url) {
          setReport(data.report);
          clearInterval(poll);
        }
      }
      if (tries > 40) clearInterval(poll); // ~3.5 min
    }, 5000);
    return () => clearInterval(poll);
  }, [orderId]);

  return (
    <main className="wrap" style={{ maxWidth: 600 }}>
      <section className="hero">
        {status === "success" ? (
          <>
            <h1 style={{ fontSize: 32 }}>Payment received 🙏</h1>
            <p>
              Your 108 reading is being decoded now. We&apos;ve emailed your
              confirmation — your download link arrives shortly.
            </p>
          </>
        ) : status === "failed" ? (
          <>
            <h1 style={{ fontSize: 32 }}>Payment didn&apos;t go through</h1>
            <p>No charge was made. You can try again from the checkout page.</p>
          </>
        ) : (
          <>
            <h1 style={{ fontSize: 32 }}>Confirming your payment…</h1>
            <p>This takes a few seconds.</p>
          </>
        )}

        {report?.public_url && (
          <a href={report.public_url} className="btn">Download your reading (PDF)</a>
        )}
        {!report && status === "success" && (
          <p style={{ color: "var(--muted)", fontSize: 14, marginTop: 24 }}>
            Generating… {orderStatus && `(status: ${orderStatus})`} This page will
            update automatically.
          </p>
        )}
      </section>
      <footer>108 — Life&apos;s Operating System</footer>
    </main>
  );
}

export default function ThanksPage() {
  return (
    <Suspense fallback={<main className="wrap"><p style={{ padding: 40 }}>Loading…</p></main>}>
      <Thanks />
    </Suspense>
  );
}
