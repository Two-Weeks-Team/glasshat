"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { useRef } from "react";
import type { Group, Mesh } from "three";

import type { ConstellationNode } from "@/lib/participate-state";

const ACCENT = "#9b87ff";
const CORRECTED = "#f0b429";

/** One criterion sphere. Corrected nodes ease from their pre-correction x into place. */
function NodeMesh({ node }: { node: ConstellationNode }) {
  const ref = useRef<Mesh>(null);
  const t = useRef(0);

  useFrame((_, delta) => {
    if (!ref.current || !node.corrected) return;
    if (t.current < 1) {
      t.current = Math.min(1, t.current + delta / 1.4);
      const eased = 1 - Math.pow(1 - t.current, 3);
      ref.current.position.x = node.fromX + (node.x - node.fromX) * eased;
    }
  });

  const color = node.corrected ? CORRECTED : ACCENT;
  return (
    <mesh ref={ref} position={[node.corrected ? node.fromX : node.x, node.y, node.z]}>
      <sphereGeometry args={[0.085, 24, 24]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.45} />
    </mesh>
  );
}

/** Slowly rotating group with orientation axes. */
function Scene({ nodes }: { nodes: ConstellationNode[] }) {
  const group = useRef<Group>(null);
  useFrame((_, delta) => {
    if (group.current) group.current.rotation.y += delta * 0.18;
  });
  return (
    <group ref={group}>
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
 * the calibrated position — the live "graph reshape".
 */
export default function ConstellationGraph({ nodes }: ConstellationGraphProps) {
  return (
    <div
      style={{ height: 380 }}
      data-testid="constellation"
      className="overflow-hidden rounded-2xl border border-[var(--color-border)]/60 bg-[var(--color-surface)]"
    >
      <Canvas camera={{ position: [2.4, 2.0, 2.6], fov: 50 }}>
        <ambientLight intensity={0.75} />
        <pointLight position={[5, 5, 5]} intensity={1.1} />
        <Scene nodes={nodes} />
      </Canvas>
    </div>
  );
}
