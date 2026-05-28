"use client";
import Link from "next/link";
import { PACKS } from "@/lib/packs";

export default function Buy() {
  const packs = Object.values(PACKS);
  return (
    <main className="wrap">
      <section className="hero" style={{ paddingBottom: 24 }}>
        <h1 style={{ fontSize: 34 }}>Choose your reading</h1>
        <p>One-time payment. Your PDF is generated and emailed within minutes.</p>
      </section>
      <div className="grid">
        {packs.map((p) => (
          <div className="pack" key={p.id}>
            <h3>{p.name}</h3>
            <div className="price">₹{(p.amount_inr / 100).toFixed(0)}</div>
            <p style={{ color: "var(--muted)", fontSize: 14, marginBottom: 12 }}>{p.tagline}</p>
            <ul>
              {p.includes.map((x) => (
                <li key={x}>✓ {x}</li>
              ))}
            </ul>
            <Link href={`/checkout?pack=${p.id}`} className="btn" style={{ marginTop: 18, textAlign: "center" }}>
              Select {p.name}
            </Link>
          </div>
        ))}
      </div>
      <footer>108 — Life&apos;s Operating System</footer>
    </main>
  );
}
