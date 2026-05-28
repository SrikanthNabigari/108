"use client";

import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";

const RASHI = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];

// Deterministic seeded RNG → identical server/client render (no hydration drift).
function seeded(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
}

function StarLayer({ count, seed, size, opacity }: { count: number; seed: number; size: number; opacity: number }) {
  const rnd = seeded(seed);
  const stars = Array.from({ length: count }, () => ({
    x: rnd() * 100,
    y: rnd() * 100,
    r: size * (0.5 + rnd()),
    d: rnd() * 5,
    dur: 3 + rnd() * 4,
  }));
  return (
    <div style={{ position: "absolute", inset: 0, opacity }}>
      {stars.map((st, i) => (
        <span
          key={i}
          style={{
            position: "absolute",
            left: `${st.x}%`,
            top: `${st.y}%`,
            width: st.r,
            height: st.r,
            borderRadius: "50%",
            background: "#fff",
            animation: `twinkle ${st.dur}s ease-in-out ${st.d}s infinite`,
          }}
        />
      ))}
    </div>
  );
}

export default function CosmicBackground() {
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll();

  // Parallax: each layer drifts at a different rate as the page scrolls.
  const farY = useTransform(scrollYProgress, [0, 1], ["0%", "-12%"]);
  const midY = useTransform(scrollYProgress, [0, 1], ["0%", "-30%"]);
  const nearY = useTransform(scrollYProgress, [0, 1], ["0%", "-55%"]);
  // The zodiac wheel slowly turns and recedes through the scroll.
  const wheelRotate = useTransform(scrollYProgress, [0, 1], [0, 90]);
  const wheelScale = useTransform(scrollYProgress, [0, 1], [1, 1.55]);
  const wheelOpacity = useTransform(scrollYProgress, [0, 0.55, 1], [0.55, 0.22, 0.07]);
  const glowOpacity = useTransform(scrollYProgress, [0, 0.5, 1], [0.9, 0.5, 0.25]);

  const pts = (r: number, n: number) =>
    Array.from({ length: n }, (_, i) => {
      const a = (i / n) * Math.PI * 2 - Math.PI / 2;
      return { x: 300 + r * Math.cos(a), y: 300 + r * Math.sin(a), a };
    });
  const ring = pts(262, 12);
  const nak = pts(212, 27);

  return (
    <div
      aria-hidden
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 0,
        overflow: "hidden",
        pointerEvents: "none",
        background:
          "radial-gradient(circle at 50% 38%, #0a0a0f 0%, #050507 55%, #000 100%)",
      }}
    >
      {/* central glow */}
      <motion.div
        style={{
          position: "absolute",
          inset: 0,
          opacity: reduce ? 0.6 : glowOpacity,
          background:
            "radial-gradient(ellipse 50% 40% at 50% 42%, rgba(201,168,92,0.16), rgba(0,0,0,0) 70%)",
        }}
      />

      {/* parallax starfields */}
      <motion.div style={{ position: "absolute", inset: "-10% 0", y: reduce ? 0 : farY }}>
        <StarLayer count={70} seed={11} size={1} opacity={0.5} />
      </motion.div>
      <motion.div style={{ position: "absolute", inset: "-10% 0", y: reduce ? 0 : midY }}>
        <StarLayer count={45} seed={29} size={1.6} opacity={0.7} />
      </motion.div>
      <motion.div style={{ position: "absolute", inset: "-10% 0", y: reduce ? 0 : nearY }}>
        <StarLayer count={22} seed={47} size={2.4} opacity={0.9} />
      </motion.div>

      {/* zodiac wheel — turns + recedes on scroll */}
      <motion.div
        style={{
          position: "absolute",
          top: "42%",
          left: "50%",
          x: "-50%",
          y: "-50%",
          rotate: reduce ? 0 : wheelRotate,
          scale: reduce ? 1.1 : wheelScale,
          opacity: reduce ? 0.18 : wheelOpacity,
          width: "min(125vh, 125vw)",
          height: "min(125vh, 125vw)",
        }}
      >
        <svg viewBox="0 0 600 600" width="100%" height="100%">
          <g className="rot-slow" style={{ transformOrigin: "300px 300px" }}>
            <circle cx="300" cy="300" r="284" fill="none" stroke="rgba(201,168,92,0.45)" strokeWidth="0.7" />
            <circle cx="300" cy="300" r="240" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="0.5" />
            {ring.map((p, i) => (
              <g key={i}>
                <line
                  x1={300 + 240 * Math.cos(p.a)} y1={300 + 240 * Math.sin(p.a)}
                  x2={300 + 284 * Math.cos(p.a)} y2={300 + 284 * Math.sin(p.a)}
                  stroke="rgba(201,168,92,0.22)" strokeWidth="0.6"
                />
                <text x={p.x} y={p.y} fill="rgba(244,243,239,0.5)" fontSize="16" textAnchor="middle" dominantBaseline="central">
                  {RASHI[i]}
                </text>
              </g>
            ))}
          </g>
          <g className="rot-mid" style={{ transformOrigin: "300px 300px" }}>
            <circle cx="300" cy="300" r="204" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="0.5" />
            {nak.map((p, i) => (
              <line key={i}
                x1={300 + 198 * Math.cos(p.a)} y1={300 + 198 * Math.sin(p.a)}
                x2={300 + 204 * Math.cos(p.a)} y2={300 + 204 * Math.sin(p.a)}
                stroke="rgba(255,255,255,0.18)" strokeWidth="0.6"
              />
            ))}
          </g>
          <g className="rot-fast" style={{ transformOrigin: "300px 300px" }}>
            <circle cx="300" cy="300" r="150" fill="none" stroke="rgba(201,168,92,0.3)" strokeWidth="0.7" strokeDasharray="2 9" />
          </g>
        </svg>
      </motion.div>

      {/* vignette to seat content */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 78%, rgba(0,0,0,0.6) 100%)",
        }}
      />
    </div>
  );
}
