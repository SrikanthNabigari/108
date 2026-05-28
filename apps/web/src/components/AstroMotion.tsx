// Pure SVG + CSS motion graphics. No client interactivity, no animation libs.
// Stars are deterministic (seeded) so server and client render identically.

const RASHI = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];

// Deterministic pseudo-random star field (no Math.random → no hydration drift).
function stars(count: number) {
  const out: { x: number; y: number; r: number; d: number }[] = [];
  let s = 1337;
  const rnd = () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
  for (let i = 0; i < count; i++) {
    out.push({
      x: rnd() * 600,
      y: rnd() * 600,
      r: 0.4 + rnd() * 1.4,
      d: rnd() * 4,
    });
  }
  return out;
}

const center = { transformBox: "view-box" as const, transformOrigin: "300px 300px" };

export default function AstroMotion() {
  const pts = (r: number, n: number) =>
    Array.from({ length: n }, (_, i) => {
      const a = (i / n) * Math.PI * 2 - Math.PI / 2;
      return { x: 300 + r * Math.cos(a), y: 300 + r * Math.sin(a), a };
    });

  const sky = stars(90);
  const ring1 = pts(258, 12); // rashi
  const nak = pts(206, 27); // nakshatra ticks

  return (
    <svg
      viewBox="0 0 600 600"
      width="min(118vh, 118vw)"
      height="min(118vh, 118vw)"
      style={{ maxWidth: 980, maxHeight: 980, display: "block" }}
      aria-hidden="true"
    >
      <defs>
        <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgba(201,168,92,0.30)" />
          <stop offset="55%" stopColor="rgba(201,168,92,0.05)" />
          <stop offset="100%" stopColor="rgba(0,0,0,0)" />
        </radialGradient>
      </defs>

      {/* starfield */}
      <g>
        {sky.map((st, i) => (
          <circle
            key={i}
            cx={st.x}
            cy={st.y}
            r={st.r}
            fill="#ffffff"
            style={{ animation: `twinkle ${3 + st.d}s ease-in-out ${st.d}s infinite` }}
          />
        ))}
      </g>

      <circle cx="300" cy="300" r="200" fill="url(#coreGlow)" />

      {/* outer zodiac ring — rashi glyphs, slow CW */}
      <g className="rot-slow" style={center}>
        <circle cx="300" cy="300" r="278" fill="none" stroke="rgba(201,168,92,0.5)" strokeWidth="0.8" />
        <circle cx="300" cy="300" r="238" fill="none" stroke="rgba(255,255,255,0.10)" strokeWidth="0.6" />
        {ring1.map((p, i) => (
          <g key={i}>
            <line
              x1={300 + 238 * Math.cos(p.a)}
              y1={300 + 238 * Math.sin(p.a)}
              x2={300 + 278 * Math.cos(p.a)}
              y2={300 + 278 * Math.sin(p.a)}
              stroke="rgba(201,168,92,0.28)"
              strokeWidth="0.7"
            />
            <text
              x={p.x}
              y={p.y}
              fill="rgba(244,243,239,0.62)"
              fontSize="17"
              textAnchor="middle"
              dominantBaseline="central"
            >
              {RASHI[i]}
            </text>
          </g>
        ))}
      </g>

      {/* nakshatra ticks — mid CCW */}
      <g className="rot-mid" style={center}>
        <circle cx="300" cy="300" r="200" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="0.6" />
        {nak.map((p, i) => (
          <line
            key={i}
            x1={300 + 194 * Math.cos(p.a)}
            y1={300 + 194 * Math.sin(p.a)}
            x2={300 + 200 * Math.cos(p.a)}
            y2={300 + 200 * Math.sin(p.a)}
            stroke="rgba(255,255,255,0.22)"
            strokeWidth="0.7"
          />
        ))}
      </g>

      {/* inner dashed ring — fast CW */}
      <g className="rot-fast" style={center}>
        <circle
          cx="300"
          cy="300"
          r="150"
          fill="none"
          stroke="rgba(201,168,92,0.35)"
          strokeWidth="0.8"
          strokeDasharray="2 8"
        />
      </g>

      {/* orbiting grahas on 3 orbits */}
      <g className="rot-mid" style={center}>
        <circle cx="300" cy="118" r="3.4" fill="var(--gold)" />
      </g>
      <g className="rot-slow" style={center}>
        <circle cx="478" cy="300" r="2.6" fill="#ffffff" />
        <circle cx="138" cy="300" r="2" fill="rgba(255,255,255,0.7)" />
      </g>
      <g className="rot-fast" style={center}>
        <circle cx="300" cy="450" r="2.4" fill="var(--gold)" />
      </g>

      {/* still center mark */}
      <circle cx="300" cy="300" r="92" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="0.6" />
      <text
        x="300"
        y="300"
        fill="var(--gold)"
        fontSize="46"
        textAnchor="middle"
        dominantBaseline="central"
        style={{ fontFamily: "var(--font-display), serif", letterSpacing: "2px" }}
      >
        108
      </text>
    </svg>
  );
}
