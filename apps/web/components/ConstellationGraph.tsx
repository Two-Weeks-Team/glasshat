"use client";

import { Canvas } from "@react-three/fiber";

import type { Node3D } from "@/lib/projection";

function Points({ nodes }: { nodes: Node3D[] }) {
  return (
    <>
      {nodes.map((n) => (
        <mesh key={n.id} position={[n.x, n.y, n.z]}>
          <sphereGeometry args={[0.07, 16, 16]} />
          <meshStandardMaterial color="#7c5cff" />
        </mesh>
      ))}
    </>
  );
}

export default function ConstellationGraph({ nodes }: { nodes: Node3D[] }) {
  return (
    <div style={{ height: 360 }} data-testid="constellation">
      <Canvas camera={{ position: [2.2, 2.2, 2.2], fov: 50 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[5, 5, 5]} />
        <Points nodes={nodes} />
      </Canvas>
    </div>
  );
}
