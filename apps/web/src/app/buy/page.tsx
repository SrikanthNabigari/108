import Link from "next/link";
import { PACKS } from "@/lib/packs";

export default function Buy() {
  const order = ["core", "full", "super"];
  return (
    <>
      <header className="nav">
        <Link href="/" className="nav-logo">
          <b>108</b> Life&apos;s Operating System
        </Link>
      </header>

      <section className="section" style={{ borderTop: "none", paddingTop: 56 }}>
        <div className="wrap">
          <div className="section-narrow" style={{ textAlign: "center" }}>
            <p className="eyebrow">Your Reading</p>
            <h2>Choose your depth</h2>
            <p className="lead" style={{ marginTop: 18 }}>
              One-time payment. Computed from your exact birth moment and delivered as a
              printed-quality PDF.
            </p>
          </div>

          <div className="plans">
            {order.map((id) => {
              const p = PACKS[id];
              const featured = id === "full";
              return (
                <div className={`plan ${featured ? "featured" : ""}`} key={id}>
                  {featured && <div className="tag">Most chosen</div>}
                  <h3 className="serif">{p.name}</h3>
                  <div className="pages">{p.pages}</div>
                  <div className="price">
                    <small>₹</small>
                    {(p.amount_inr / 100).toFixed(0)}
                  </div>
                  <p className="tagline">{p.tagline}</p>
                  <ul>
                    {p.includes.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                  <Link
                    href={`/checkout?pack=${id}`}
                    className={`btn ${featured ? "" : "ghost"}`}
                    style={{ justifyContent: "center" }}
                  >
                    Select {p.name}
                  </Link>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <footer>108 — Life&apos;s Operating System</footer>
    </>
  );
}
