import Link from "next/link";
import AstroMotion from "@/components/AstroMotion";
import Reveal from "@/components/Reveal";
import { PACKS } from "@/lib/packs";

const PROPS = [
  {
    n: "I",
    h: "Computed, never generic",
    p: "Every line is derived from your exact birth moment — Lagna, nakshatras, dasha periods and sixteen divisional charts. No sun-sign clichés.",
  },
  {
    n: "II",
    h: "Read against the classics",
    p: "Your chart is interpreted through the canonical texts of Jyotish — the same sources studied, unbroken, for two thousand years.",
  },
  {
    n: "III",
    h: "Predictive, with dates",
    p: "A 120-year life arc, slow-transit windows and a month-by-month year ahead — timing you can actually plan around.",
  },
];

const TEXTS = [
  {
    meta: "The Root · Maharishi Parashara",
    name: "Brihat Parashara Hora Shastra",
    author: "the foundation of all Jyotish",
    p: "Defines the entire grammar — grahas, rashis and bhavas, the Vimshottari dasha clock, the divisional charts, and the laws of yoga and dosha. Every reading begins here.",
  },
  {
    meta: "Jaimini School",
    name: "Upadesha Sutras",
    author: "Maharishi Jaimini",
    p: "The soul's significators — the Atmakaraka and chara karakas — the Arudha padas that separate image from reality, and the sign-based Chara dasha.",
  },
  {
    meta: "6th century · Ujjain",
    name: "Brihat Jataka",
    author: "Varāhamihira",
    p: "The poet-astronomer's classic of natal judgement: the nature of each planet, its aspects, and the yogas that shape a life — precision in few words.",
  },
  {
    meta: "Practical Manual",
    name: "Phaladeepika",
    author: "Mantreśvara",
    p: "The most complete manual of results — house by house, dasha by dasha. For two centuries the working astrologer's companion.",
  },
  {
    meta: "~10th century",
    name: "Sāravalī",
    author: "Kalyāṇa Varma",
    p: "An encyclopedia of combination — every planet in every sign and house, and the precise result each placement produces.",
  },
  {
    meta: "Classical Compendium",
    name: "Jātaka Pārijāta",
    author: "Vaidyanātha Dīkṣita",
    p: "A vast harmonization of the earlier masters — yogas, dignities and life-results gathered into a single ordered system.",
  },
  {
    meta: "Aphoristic",
    name: "Uttara Kālāmṛta",
    author: "Kālidāsa",
    p: "Concise and exact — the karakas, the special lagnas, and the finer nuances of timing that sharpen every prediction.",
  },
  {
    meta: "The Predictive Lineage",
    name: "Bhṛgu & Nāḍī Tradition",
    author: "Maharishi Bhṛgu",
    p: "Reads a life as a sequence of dated events, unfolding through the dasha — the source of the timing texture woven through your forecast.",
  },
];

export default function Home() {
  const order = ["core", "full", "super"];

  return (
    <>
      <header className="nav">
        <div className="nav-logo">
          <b>108</b> Life&apos;s Operating System
        </div>
        <Link href="/buy" className="btn ghost">
          See your reading
        </Link>
      </header>

      {/* HERO */}
      <section className="hero">
        <div className="hero-motion">
          <AstroMotion />
        </div>
        <div className="scrim" />
        <div className="hero-inner">
          <p className="eyebrow">Vedic Jyotish · Decoded</p>
          <h1>
            The architecture
            <br /> of your life.
          </h1>
          <p className="lead">
            Not a horoscope — the blueprint. Your exact birth sky, read against the
            classical texts of Jyotish, written for a modern mind.
          </p>
          <div className="hero-cta">
            <Link href="/buy" className="btn lg">
              See your reading →
            </Link>
            <Link href="#texts" className="btn ghost lg">
              The texts we read
            </Link>
          </div>
        </div>
      </section>

      {/* VALUE PROPS */}
      <section className="section">
        <div className="wrap">
          <Reveal>
            <div className="props">
              {PROPS.map((p) => (
                <div className="prop" key={p.n}>
                  <div className="n">{p.n}</div>
                  <h3>{p.h}</h3>
                  <p>{p.p}</p>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      {/* SOURCES / TEXTS */}
      <section className="section" id="texts">
        <div className="wrap">
          <Reveal>
            <div className="section-narrow" style={{ textAlign: "center" }}>
              <p className="eyebrow">The Sources</p>
              <h2>The texts we read</h2>
              <p className="lead" style={{ marginTop: 18 }}>
                Your reading is not invented. It is drawn from the canon of Jyotish —
                the works of the rishis and the great medieval masters, each adding a
                distinct lens to the same sky.
              </p>
            </div>
          </Reveal>
          <Reveal delay={80}>
            <div className="texts">
              {TEXTS.map((t) => (
                <div className="text-card" key={t.name}>
                  <div className="meta">{t.meta}</div>
                  <h3 className="serif">{t.name}</h3>
                  <div className="author">{t.author}</div>
                  <p>{t.p}</p>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      {/* PRICING */}
      <section className="section" id="pricing">
        <div className="wrap">
          <Reveal>
            <div className="section-narrow" style={{ textAlign: "center" }}>
              <p className="eyebrow">Your Reading</p>
              <h2>Choose your depth</h2>
              <p className="lead" style={{ marginTop: 18 }}>
                One-time. Computed from your birth moment and delivered as a printed-quality PDF.
              </p>
            </div>
          </Reveal>
          <Reveal delay={80}>
            <div className="plans">
              {order.map((id, i) => {
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
          </Reveal>
        </div>
      </section>

      {/* CLOSING */}
      <section className="section">
        <div className="wrap">
          <Reveal>
            <div className="section-narrow" style={{ textAlign: "center" }}>
              <h2>Your chart is already written.</h2>
              <p className="lead" style={{ marginTop: 18, marginBottom: 34 }}>
                It has been since the moment you were born. The only question is whether
                you read it.
              </p>
              <Link href="/buy" className="btn lg">
                Begin →
              </Link>
            </div>
          </Reveal>
        </div>
      </section>

      <footer>108 — Life&apos;s Operating System · Grounded in classical Jyotish</footer>
    </>
  );
}
