"use client";

import { OrbitControls } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { useEffect, useRef, useState } from "react";
import type { Mesh } from "three";

import type { ConstellationNode } from "@/lib/participate-state";

/** Track `prefers-reduced-motion` so the auto-rotating camera can be stilled for
 *  users who opt out of motion (WCAG 2.3.3). Defaults to false during SSR/first
 *  paint, then syncs to the media query. */
function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    // Guard: matchMedia is undefined in some test environments / older browsers.
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

const ACCENT = "#9b87ff";
const CORRECTED = "#f0b429";

/** One criterion sphere with a soft emissive halo. Corrected nodes ease from
 *  their pre-correction x (the over-confident origin) into the calibrated place. */
function NodeMesh({ node }: { node: ConstellationNode }) {
  const ref = useRef<Mesh>(null);
  const halo = useRef<Mesh>(null);
  const t = useRef(0);

  useFrame((_, delta) => {
    if (!node.corrected) return;
    if (t.current < 1) {
      t.current = Math.min(1, t.current + delta / 1.4);
      const eased = 1 - Math.pow(1 - t.current, 3);
      const x = node.fromX + (node.x - node.fromX) * eased;
      if (ref.current) ref.current.position.x = x;
      if (halo.current) halo.current.position.x = x;
    }
  });

  const color = node.corrected ? CORRECTED : ACCENT;
  const start: [number, number, number] = [node.corrected ? node.fromX : node.x, node.y, node.z];
  return (
    <group>
      {/* glow halo — a larger, faint additive sphere behind the node */}
      <mesh ref={halo} position={start}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshBasicMaterial color={color} transparent opacity={0.16} depthWrite={false} />
      </mesh>
      <mesh ref={ref} position={start}>
        <sphereGeometry args={[0.085, 24, 24]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} />
      </mesh>
    </group>
  );
}

/** Orientation axes (score · weight · evidence) + the criterion nodes. */
function Scene({ nodes }: { nodes: ConstellationNode[] }) {
  return (
    <group>
      <axesHelper args={[1.25]} />
      {nodes.map((n) => (
        <NodeMesh key={n.id} node={n} />
      ))}
    </group>
  );
}

export interface ConstellationGraphProps {
  nodes: ConstellationNode[];
}

/**
 * The 3D self-correction graph. Axes = score (x) · weight (y) · evidence depth (z).
 * Amber nodes were self-corrected and animate from their over-confident origin to
 * the calibrated position — the live "graph reshape". Drag to orbit.
 *
 * Labels/legend render as an HTML overlay (not in-canvas text) so the lazy 3D
 * chunk stays light — no troika-three-text — keeping the Lighthouse perf budget.
 */
export default function ConstellationGraph({ nodes }: ConstellationGraphProps) {
  const corrected = nodes.filter((n) => n.corrected).length;
  const reducedMotion = usePrefersReducedMotion();
  // The <canvas> is opaque to assistive tech, so describe the whole graph as an
  // image. role="img" makes it a leaf in the a11y tree (the decorative overlay
  // legend below isn't announced separately); the label conveys the same data.
  const ariaLabel =
    `3D evaluation constellation: ${nodes.length} ${nodes.length === 1 ? "criterion" : "criteria"} ` +
    "plotted by score (x), weight (y), and evidence depth (z). " +
    (corrected > 0
      ? `${corrected} self-corrected from an over-confident position to a calibrated one.`
      : "No criteria required self-correction.");
  return (
    <div
      style={{ height: 380 }}
      data-testid="constellation"
      role="img"
      aria-label={ariaLabel}
      className="relative overflow-hidden rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)]"
    >
      <Canvas camera={{ position: [2.4, 2.0, 2.6], fov: 50 }}>
        <ambientLight intensity={0.75} />
        <pointLight position={[5, 5, 5]} intensity={1.1} />
        <Scene nodes={nodes} />
        <OrbitControls
          enablePan={false}
          enableZoom
          autoRotate={!reducedMotion}
          autoRotateSpeed={0.9}
          minDistance={2.2}
          maxDistance={6}
        />
      </Canvas>

      {/* Axis legend (HTML overlay, no 3D text) */}
      <div className="pointer-events-none absolute left-3 top-3 flex flex-col gap-0.5 font-mono text-[10px] uppercase tracking-wide">
        <span className="text-[var(--color-bad)]">x · score</span>
        <span className="text-[var(--color-good)]">y · weight</span>
        <span className="text-[var(--color-accent-2)]">z · evidence depth</span>
      </div>
      <div className="pointer-events-none absolute bottom-3 right-3 flex items-center gap-3 font-mono text-[10px]">
        <span className="flex items-center gap-1 text-[var(--color-muted)]">
          <i className="inline-block h-2 w-2 rounded-full" style={{ background: ACCENT }} /> calibrated
        </span>
        <span className="flex items-center gap-1 text-[var(--color-muted)]">
          <i className="inline-block h-2 w-2 rounded-full" style={{ background: CORRECTED }} />
          corrected{corrected > 0 ? ` (${corrected})` : ""}
        </span>
      </div>
      {corrected > 0 && (
        <span className="pointer-events-none absolute left-1/2 top-3 -translate-x-1/2 font-mono text-[10px] text-[var(--color-warn)]">
          amber nodes slide: over-confident → calibrated
        </span>
      )}
    </div>
  );
}
