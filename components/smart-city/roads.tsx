"use client"

import { useRef, useMemo } from "react"
import { useFrame } from "@react-three/fiber"
import type * as THREE from "three"

function GlowingRoad({
  start,
  end,
  width = 0.8,
}: {
  start: [number, number, number]
  end: [number, number, number]
  width?: number
}) {
  const dx = end[0] - start[0]
  const dz = end[2] - start[2]
  const length = Math.sqrt(dx * dx + dz * dz)
  const angle = Math.atan2(dx, dz)
  const cx = (start[0] + end[0]) / 2
  const cz = (start[2] + end[2]) / 2

  return (
    <group position={[cx, 0.01, cz]} rotation={[0, angle, 0]}>
      {/* Road surface */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[width, length]} />
        <meshStandardMaterial color="#0a1225" roughness={0.8} />
      </mesh>

      {/* Center line glow */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.005, 0]}>
        <planeGeometry args={[0.03, length]} />
        <meshStandardMaterial
          color="#00d4ff"
          emissive="#00d4ff"
          emissiveIntensity={1}
          transparent
          opacity={0.6}
        />
      </mesh>

      {/* Edge lines */}
      {[-width / 2 + 0.02, width / 2 - 0.02].map((x, i) => (
        <mesh key={i} rotation={[-Math.PI / 2, 0, 0]} position={[x, 0.005, 0]}>
          <planeGeometry args={[0.02, length]} />
          <meshStandardMaterial
            color="#00d4ff"
            emissive="#00d4ff"
            emissiveIntensity={0.5}
            transparent
            opacity={0.3}
          />
        </mesh>
      ))}
    </group>
  )
}

function DataStream({
  points,
  color = "#00d4ff",
}: {
  points: [number, number, number][]
  color?: string
}) {
  const particlesRef = useRef<THREE.Points>(null)
  const count = 40

  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const t = i / count
      const segIndex = Math.floor(t * (points.length - 1))
      const segT = (t * (points.length - 1)) % 1
      const p1 = points[Math.min(segIndex, points.length - 1)]
      const p2 = points[Math.min(segIndex + 1, points.length - 1)]

      pos[i * 3] = p1[0] + (p2[0] - p1[0]) * segT
      pos[i * 3 + 1] = p1[1] + (p2[1] - p1[1]) * segT + 0.1
      pos[i * 3 + 2] = p1[2] + (p2[2] - p1[2]) * segT
    }
    return pos
  }, [points, count])

  useFrame((_, delta) => {
    if (particlesRef.current) {
      const geo = particlesRef.current.geometry
      const posAttr = geo.attributes.position
      if (!posAttr) return

      for (let i = 0; i < count; i++) {
        let t = ((i / count + delta * 0.2) % 1)
        if (t < 0) t += 1
        const segIndex = Math.floor(t * (points.length - 1))
        const segT = (t * (points.length - 1)) % 1
        const p1 = points[Math.min(segIndex, points.length - 1)]
        const p2 = points[Math.min(segIndex + 1, points.length - 1)]

        posAttr.setXYZ(
          i,
          p1[0] + (p2[0] - p1[0]) * segT,
          p1[1] + (p2[1] - p1[1]) * segT + 0.1,
          p1[2] + (p2[2] - p1[2]) * segT
        )
      }
      posAttr.needsUpdate = true
    }
  })

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial color={color} size={0.06} transparent opacity={0.8} sizeAttenuation />
    </points>
  )
}

export function CityRoads() {
  const roads: { start: [number, number, number]; end: [number, number, number] }[] = useMemo(
    () => [
      // Main horizontal roads
      { start: [-12, 0, -1], end: [12, 0, -1] },
      { start: [-12, 0, 6], end: [12, 0, 6] },
      { start: [-12, 0, -7], end: [12, 0, -7] },

      // Main vertical roads
      { start: [-2, 0, -10], end: [-2, 0, 10] },
      { start: [3, 0, -10], end: [3, 0, 10] },
      { start: [8, 0, -10], end: [8, 0, 10] },
      { start: [-7, 0, -10], end: [-7, 0, 10] },
    ],
    []
  )

  const dataStreams: [number, number, number][][] = useMemo(
    () => [
      [
        [-12, 0.5, -1],
        [-4, 0.5, -1],
        [-4, 0.5, -2],
        [-1, 2, -6],
        [4, 2, -3],
        [12, 0.5, -1],
      ],
      [
        [-12, 0.3, 6],
        [0, 0.3, 6],
        [1, 1, 2],
        [3, 0.3, 3],
        [12, 0.3, 6],
      ],
    ],
    []
  )

  return (
    <group>
      {/* Ground plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[30, 25]} />
        <meshStandardMaterial color="#060d17" roughness={0.9} />
      </mesh>

      {roads.map((r, i) => (
        <GlowingRoad key={i} start={r.start} end={r.end} />
      ))}

      {/* Data streams above roads */}
      {dataStreams.map((stream, i) => (
        <DataStream key={i} points={stream} color={i === 0 ? "#00d4ff" : "#ff6b35"} />
      ))}

      {/* Intersection highlights */}
      {[
        [-2, -1],
        [-2, 6],
        [3, -1],
        [3, 6],
        [8, -1],
        [8, 6],
      ].map(([x, z], i) => (
        <mesh key={i} rotation={[-Math.PI / 2, 0, 0]} position={[x, 0.02, z]}>
          <circleGeometry args={[0.5, 16]} />
          <meshStandardMaterial
            color="#00d4ff"
            emissive="#00d4ff"
            emissiveIntensity={0.3}
            transparent
            opacity={0.15}
          />
        </mesh>
      ))}
    </group>
  )
      }
    
