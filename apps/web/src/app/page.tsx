"use client";

import Link from "next/link";
import { motion, useScroll, useTransform, type Variants } from "framer-motion";
import CosmicBackground from "@/components/CosmicBackground";
import { PACKS } from "@/lib/packs";

const PROPS = [
  { n: "I", h: "Computed, never generic", p: "Every line is derived from your exact birth moment — Lagna, nakshatras, dasha periods, sixteen divisional charts. No sun-sign clichés." },
  { n: "II", h: "Read against the classics", p: "Your chart is interpreted through the canonical texts of Jyotish — the same sources studied, unbroken, for two thousand years." },
  { n: "III", h: "Predictive, with dates", p: "A 120-year life arc, slow-transit windows, and a month-by-month year ahead — timing you can actually plan around." },
];

const TEXTS = [
  { meta: "The Root · Maharishi Parāśara", name: "Bṛhat Parāśara Horā Śāstra", author: "the foundation of all Jyotish", p: "Defines the entire grammar — grahas, rashis, bhavas, the Vimshottari dasha clock, the divisional charts, and the laws of yoga and dosha." },
  { meta: "Jaimini School", name: "Upadeśa Sūtras", author: "Maharishi Jaimini", p: "The soul's significators — Atmakaraka and chara karakas — the Arudha padas that separate image from reality, and the sign-based Chara dasha." },
  { meta: "6th century · Ujjain", name: "Bṛhat Jātaka", author: "Varāhamihira", p: "The poet-astronomer's classic of natal judgement: the nature of each planet, its aspects, and the yogas that shape a life." },
  { meta: "Practical Manual", name: "Phaladeepika", author: "Mantreśvara", p: "The most complete manual of results — house by house, dasha by dasha. The working astrologer's companion for two centuries." },
  { meta: "~10th century", name: "Sāravalī", author: "Kalyāṇa Varma", p: "An encyclopedia of combination — every planet in every sign and house, and the precise result each placement produces." },
  { meta: "The Predictive Lineage", name: "Bhṛgu & Nāḍī", author: "Maharishi Bhṛgu", p: "Reads a life as a sequence of dated events unfolding through the dasha — the source of the timing woven through your forecast." },
];

const ease = [0.22, 1, 0.36, 1] as const;

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 36 },
  show: (i = 0) => ({ opacity: 1, y: 0, transition: { duration: 0.8, ease, delay: i * 0.08 } }),
};

function Section({ children, className = "", id }: { children: React.ReactNode; className?: string; id?: string }) {
  return (
    <section id={id} className={`section ${className}`}>
      <div className="wrap">{children}</div>
    </section>
  );
}

export default function Home() {
  const { scrollYProgress } = useScroll();
  const navOpacity = useTransform(scrollYProgress, [0.04, 0.09], [0, 1]);
  const heroText = useTransform(scrollYProgress, [0, 0.12], [1, 0]);
  const heroY = useTransform(scrollYProgress, [0, 0.12], [0, -60]);
  const cueOpacity = useTransform(scrollYProgress, [0, 0.05], [1, 0]);
  const order = ["core", "full", "super"];

  return (
    <>
      <CosmicBackground />

      {/* scroll progress */}
      <motion.div className="scroll-progress" style={{ scaleX: scrollYProgress }} />

      {/* nav — fades in after hero */}
      <motion.header className="nav nav-fixed" style={{ opacity: navOpacity }}>
        <div className="nav-logo"><b>108</b> <span className="logo-text">Life&apos;s Operating System</span></div>
        <Link href="/buy" className="btn ghost sm">See your reading</Link>
      </motion.header>

      {/* HERO */}
      <section className="hero-cine">
        <motion.div className="hero-inner" style={{ opacity: heroText, y: heroY }}>
          <motion.p className="eyebrow" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3, duration: 1 }}>
            Vedic Jyotish · Decoded
          </motion.p>
          <motion.h1 initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45, duration: 1, ease }}>
            The architecture<br />of your life.
          </motion.h1>
          <motion.p className="lead" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8, duration: 1 }}>
            Not a horoscope — the blueprint. Your exact birth sky, read against the
            classical texts of Jyotish, written for a modern mind.
          </motion.p>
          <motion.div className="hero-cta" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.05, duration: 0.9, ease }}>
            <Link href="/buy" className="btn lg">See your reading →</Link>
            <Link href="#texts" className="btn ghost lg">The texts we read</Link>
          </motion.div>
        </motion.div>
        <motion.div className="scroll-cue" style={{ opacity: cueOpacity }}>
          <span /> scroll
        </motion.div>
      </section>

      {/* MANIFESTO */}
      <Section className="manifesto">
        <div className="section-narrow">
          {[
            "You were born under a specific sky.",
            "Every planet, at a precise degree.",
            "That arrangement is still running — quietly, like an operating system underneath your life.",
            "This reading decodes it.",
          ].map((line, i) => (
            <motion.p
              key={i}
              className="manifesto-line"
              variants={fadeUp}
              custom={i}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true, amount: 0.6 }}
            >
              {line}
            </motion.p>
          ))}
        </div>
      </Section>

      {/* VALUE PROPS */}
      <Section>
        <motion.div className="props" initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.3 }}>
          {PROPS.map((p, i) => (
            <motion.div className="prop" key={p.n} variants={fadeUp} custom={i}>
              <div className="n">{p.n}</div>
              <h3>{p.h}</h3>
              <p>{p.p}</p>
            </motion.div>
          ))}
        </motion.div>
      </Section>

      {/* SOURCES */}
      <Section id="texts">
        <motion.div className="section-narrow center" variants={fadeUp} initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.5 }}>
          <p className="eyebrow">The Sources</p>
          <h2>The texts we read</h2>
          <p className="lead">
            Your reading is not invented. It is drawn from the canon of Jyotish — the
            works of the rishis and the great medieval masters, each a distinct lens on the same sky.
          </p>
        </motion.div>
        <motion.div className="texts" initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.15 }}>
          {TEXTS.map((t, i) => (
            <motion.div className="text-card" key={t.name} variants={fadeUp} custom={i % 3}>
              <div className="meta">{t.meta}</div>
              <h3 className="serif">{t.name}</h3>
              <div className="author">{t.author}</div>
              <p>{t.p}</p>
            </motion.div>
          ))}
        </motion.div>
        <p className="swipe-hint">← swipe the texts →</p>
      </Section>

      {/* PRICING */}
      <Section id="pricing">
        <motion.div className="section-narrow center" variants={fadeUp} initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.5 }}>
          <p className="eyebrow">Your Reading</p>
          <h2>Choose your depth</h2>
          <p className="lead">One-time. Computed from your birth moment, delivered as a printed-quality PDF.</p>
        </motion.div>
        <motion.div className="plans" initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.2 }}>
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
      </Section>

      {/* CLOSING */}
      <Section className="closing">
        <motion.div className="section-narrow center" variants={fadeUp} initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.5 }}>
          <h2>Your chart is already written.</h2>
          <p className="lead">It has been since the moment you were born. The only question is whether you read it.</p>
          <Link href="/buy" className="btn lg">Begin →</Link>
        </motion.div>
      </Section>

      <footer>108 — Life&apos;s Operating System · Grounded in classical Jyotish</footer>
    </>
  );
}
