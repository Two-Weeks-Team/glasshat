/**
 * Decorative hero motif that *shows* the product: four criterion nodes on a score
 * field, one of which over-shoots (amber, over-confident) and then drops to its
 * calibrated position (accent) — the self-correction, on a loop. Pure SVG + CSS
 * (no 3D bundle), aria-hidden, frozen calibrated under reduced-motion.
 */
export function HeroGraphic() {
  return (
    <svg
      viewBox="0 0 520 340"
      role="img"
      aria-label="Animated diagram: an over-confident score self-correcting downward"
      className="h-auto w-full"
    >
      <defs>
        <radialGradient id="glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="oklch(0.72 0.17 290 / 0.55)" />
          <stop offset="100%" stopColor="oklch(0.72 0.17 290 / 0)" />
        </radialGradient>
        <linearGradient id="link" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="oklch(0.82 0.13 205 / 0.5)" />
          <stop offset="100%" stopColor="oklch(0.72 0.17 290 / 0.5)" />
        </linearGradient>
      </defs>

      {/* faint score grid */}
      <g stroke="oklch(0.33 0.03 265 / 0.7)" strokeWidth="1">
        <line x1="40" y1="70" x2="490" y2="70" />
        <line x1="40" y1="140" x2="490" y2="140" />
        <line x1="40" y1="210" x2="490" y2="210" />
        <line x1="40" y1="280" x2="490" y2="280" />
      </g>

      {/* connecting shape through the static nodes + the corrected node target */}
      <polyline
        points="90,250 210,160 320,178 430,120"
        fill="none"
        stroke="url(#link)"
        strokeWidth="2"
        strokeLinejoin="round"
      />

      {/* static criterion nodes */}
      <g>
        {[
          [90, 250],
          [210, 160],
          [430, 120],
        ].map(([x, y]) => (
          <circle key={`${x}`} cx={x} cy={y} r="7" fill="oklch(0.72 0.17 290)" />
        ))}
      </g>

      {/* correction guide: dashed path from over-confident to calibrated */}
      <line
        x1="320"
        y1="120"
        x2="320"
        y2="178"
        stroke="oklch(0.82 0.15 85 / 0.6)"
        strokeWidth="1.5"
        strokeDasharray="4 4"
      />
      <text x="332" y="130" fill="oklch(0.72 0.02 265)" fontSize="13" fontFamily="ui-monospace, monospace">
        over-confident
      </text>
      <text x="332" y="196" fill="oklch(0.72 0.02 265)" fontSize="13" fontFamily="ui-monospace, monospace">
        calibrated
      </text>

      {/* the self-correcting node (starts at y=120, animates down to ~178) */}
      <g className="hero-node-correct" style={{ transformBox: "view-box" }}>
        <circle cx="320" cy="120" r="22" fill="url(#glow)" />
        <circle className="hero-node-dot" cx="320" cy="120" r="9" fill="oklch(0.82 0.15 85)" />
      </g>
    </svg>
  );
}
