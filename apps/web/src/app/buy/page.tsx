"use client";

import Link from "next/link";
import { motion, type Variants } from "framer-motion";
import CosmicBackground from "@/components/CosmicBackground";
import { PACKS } from "@/lib/packs";

const ease = [0.22, 1, 0.36, 1] as const;
const fadeUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  show: (i = 0) => ({ opacity: 1, y: 0, transition: { duration: 0.7, ease, delay: i * 0.08 } }),
};

export default function Buy() {
  const order = ["core", "full", "super"];
  return (
    <>
      <CosmicBackground />
      <header className="nav nav-fixed">
        <Link href="/" className="nav-logo"><b>108</b> <span className="logo-text">Life&apos;s Operating System</span></Link>
      </header>

      <section className="section" style={{ borderTop: "none", paddingTop: 120, position: "relative", zIndex: 1 }}>
        <div className="wrap">
          <motion.div className="section-narrow center" variants={fadeUp} initial="hidden" animate="show">
            <p className="eyebrow">Your Reading</p>
            <h2>Choose your depth</h2>
            <p className="lead">One-time payment. Computed from your exact birth moment and delivered as a printed-quality PDF.</p>
          </motion.div>

          <motion.div className="plans" initial="hidden" animate="show">
            {order.map((id, i) => {
              const p = PACKS[id];
              const featured = id === "full";
              return (
                <motion.div className={`plan ${featured ? "featured" : ""}`} key={id} variants={fadeUp} custom={i} whileHover={{ y: -6 }}>
                  {featured && <div className="tag">Most chosen</div>}
                  <h3 className="serif">{p.name}</h3>
                  <div className="pages">{p.pages}</div>
                  <div className="price"><small>₹</small>{(p.amount_inr / 100).toFixed(0)}</div>
                  <p className="tagline">{p.tagline}</p>
                  <ul>{p.includes.map((x) => <li key={x}>{x}</li>)}</ul>
                  <Link href={`/checkout?pack=${id}`} className={`btn ${featured ? "" : "ghost"}`} style={{ justifyContent: "center" }}>
                    Select {p.name}
                  </Link>
                </motion.div>
              );
            })}
          </motion.div>
          <p className="swipe-hint">← swipe the plans →</p>
        </div>
      </section>

      <footer>108 — Life&apos;s Operating System</footer>
    </>
  );
}
