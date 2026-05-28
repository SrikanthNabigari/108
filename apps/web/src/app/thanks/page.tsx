"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import CosmicBackground from "@/components/CosmicBackground";

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
    <>
      <CosmicBackground />
      <header className="nav nav-fixed">
        <a href="/" className="nav-logo"><b>108</b> <span className="logo-text">Life&apos;s Operating System</span></a>
      </header>
      <motion.main className="wrap" style={{ maxWidth: 620, textAlign: "center", padding: "130px 24px 80px", position: "relative", zIndex: 1 }}
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
        {status === "success" ? (
          <>
            <p className="eyebrow">Payment received</p>
            <h2 className="serif">Your reading is being decoded</h2>
            <p className="lead" style={{ marginTop: 18 }}>
              We&apos;ve emailed your confirmation — your download link arrives shortly.
            </p>
          </>
        ) : status === "failed" ? (
          <>
            <p className="eyebrow">Payment</p>
            <h2 className="serif">It didn&apos;t go through</h2>
            <p className="lead" style={{ marginTop: 18 }}>
              No charge was made. You can try again from the checkout page.
            </p>
          </>
        ) : (
          <>
            <p className="eyebrow">One moment</p>
            <h2 className="serif">Confirming your payment…</h2>
            <p className="lead" style={{ marginTop: 18 }}>This takes a few seconds.</p>
          </>
        )}

        {report?.public_url && (
          <div style={{ marginTop: 34 }}>
            <a href={report.public_url} className="btn lg">Download your reading (PDF)</a>
          </div>
        )}
        {!report && status === "success" && (
          <p className="muted" style={{ fontSize: 14, marginTop: 28 }}>
            Generating{orderStatus && ` · ${orderStatus}`} — this page updates automatically.
          </p>
        )}
      </motion.main>
      <footer>108 — Life&apos;s Operating System</footer>
    </>
  );
}

export default function ThanksPage() {
  return (
    <Suspense fallback={<main className="wrap"><p style={{ padding: 40 }}>Loading…</p></main>}>
      <Thanks />
    </Suspense>
  );
}
