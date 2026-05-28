import Link from "next/link";

export default function Home() {
  return (
    <main>
      <section className="hero">
        <h1>108 — Life&apos;s Operating System</h1>
        <p>
          Your Vedic chart, fully decoded. Not a horoscope — the architecture of
          your life: who you are, the chapter you&apos;re in, and exactly what to
          do next. Grounded in classical Jyotish, written for a modern mind.
        </p>
        <Link href="/buy" className="btn">See your reading →</Link>
      </section>

      <section className="wrap">
        <div className="grid">
          <div className="pack">
            <h3>Decoded, not generic</h3>
            <p style={{ color: "var(--muted)", fontSize: 14 }}>
              Every line is computed from your exact birth moment — Lagna,
              nakshatras, dasha periods, divisional charts. No Barnum statements.
            </p>
          </div>
          <div className="pack">
            <h3>Predictive, with dates</h3>
            <p style={{ color: "var(--muted)", fontSize: 14 }}>
              A 20-year Life Story Spine, slow-transit calendar, and a month-by-month
              year ahead — windows you can plan around.
            </p>
          </div>
          <div className="pack">
            <h3>Yours in minutes</h3>
            <p style={{ color: "var(--muted)", fontSize: 14 }}>
              Pay, and your PDF is generated and emailed to you automatically.
              No appointment, no waiting.
            </p>
          </div>
        </div>
        <div style={{ textAlign: "center" }}>
          <Link href="/buy" className="btn">Choose your reading →</Link>
        </div>
      </section>

      <footer>108 — Life&apos;s Operating System · Built with cosmic intention</footer>
    </main>
  );
}
