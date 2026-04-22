"use client"

import { useRef, useMemo } from "react"
import { useFrame } from "@react-three/fiber"
import type * as THREE from "three"

function Building({
  position,
  width,
  height,
  depth,
  color,
  emissiveColor,
  windowRows = 8,
}: {
  position: [number, number, number]
  width: number
  height: number
  depth: number
  color: string
  emissiveColor: string
  windowRows?: number
}) {
  const meshRef = useRef<THREE.Mesh>(null)
  const windowsRef = useRef<THREE.Group>(null)
  const pulseRef = useRef(Math.random() * Math.PI * 2)

  useFrame((_, delta) => {
    pulseRef.current += delta * 0.5
    if (windowsRef.current) {
      windowsRef.current.children.forEach((child, i) => {
        const mesh = child as THREE.Mesh
        if (mesh.material && "emissiveIntensity" in mesh.material) {
          ;(mesh.material as THREE.MeshStandardMaterial).emissiveIntensity =
            0.3 + Math.sin(pulseRef.current + i * 0.3) * 0.2
        }
      })
    }
  })

  const windows = useMemo(() => {
    const wins: { pos: [number, number, number]; side: "x" | "z" }[] = []
    const rows = windowRows
    const colsX = Math.max(2, Math.floor(width * 2))
    const colsZ = Math.max(2, Math.floor(depth * 2))

    for (let row = 0; row < rows; row++) {
      const y = (row + 1) * (height / (rows + 1)) - height / 2
      for (let col = 0; col < colsX; col++) {
        const x = (col + 1) * (width / (colsX + 1)) - width / 2
        wins.push({ pos: [x, y, depth / 2 + 0.01], side: "z" })
        wins.push({ pos: [x, y, -depth / 2 - 0.01], side: "z" })
      }
      for (let col = 0; col < colsZ; col++) {
        const z = (col + 1) * (depth / (colsZ + 1)) - depth / 2
        wins.push({ pos: [width / 2 + 0.01, y, z], side: "x" })
        wins.push({ pos: [-width / 2 - 0.01, y, z], side: "x" })
      }
    }
    return wins
  }, [width, height, depth, windowRows])

  return (
    <group position={position}>
      <mesh ref={meshRef} position={[0, height / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[width, height, depth]} />
        <meshStandardMaterial color={color} roughness={0.4} metalness={0.6} />
      </mesh>

      <group ref={windowsRef} position={[0, height / 2, 0]}>
        {windows.map((w, i) => (
          <mesh key={i} position={w.pos} rotation={w.side === "x" ? [0, Math.PI / 2, 0] : [0, 0, 0]}>
            <planeGeometry args={[0.2, 0.15]} />
            <meshStandardMaterial
              color={emissiveColor}
              emissive={emissiveColor}
              emissiveIntensity={0.5}
              transparent
              opacity={0.9}
            />
          </mesh>
        ))}
      </group>

      {/* Rooftop antenna/light */}
      <mesh position={[0, height + 0.3, 0]}>
        <cylinderGeometry args={[0.02, 0.02, 0.6]} />
        <meshStandardMaterial color="#334455" />
      </mesh>
      <mesh position={[0, height + 0.6, 0]}>
        <sphereGeometry args={[0.06]} />
        <meshStandardMaterial color={emissiveColor} emissive={emissiveColor} emissiveIntensity={2} />
      </mesh>
    </group>
  )
}

function Skyscraper({
  position,
  height,
}: {
  position: [number, number, number]
  height: number
}) {
  const ringRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (ringRef.current) {
      ringRef.current.rotation.y = state.clock.elapsedTime * 0.3
    }
  })

  return (
    <group position={position}>
      {/* Main tower */}
      <mesh position={[0, height / 2, 0]} castShadow>
        <cylinderGeometry args={[0.6, 0.8, height, 6]} />
        <meshStandardMaterial color="#0a1628" roughness={0.3} metalness={0.8} />
      </mesh>

      {/* Glowing ring */}
      <mesh ref={ringRef} position={[0, height * 0.7, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1, 0.03, 8, 32]} />
        <meshStandardMaterial color="#00d4ff" emissive="#00d4ff" emissiveIntensity={2} />
      </mesh>

      {/* Glowing bands */}
      {[0.3, 0.5, 0.8].map((h, i) => (
        <mesh key={i} position={[0, height * h, 0]}>
          <cylinderGeometry args={[0.62 + i * 0.01, 0.62 + i * 0.01, 0.08, 6]} />
          <meshStandardMaterial color="#00d4ff" emissive="#00d4ff" emissiveIntensity={1.5} transparent opacity={0.7} />
        </mesh>
      ))}

      {/* Top beacon */}
      <pointLight position={[0, height + 0.5, 0]} color="#00d4ff" intensity={3} distance={8} />
      <mesh position={[0, height + 0.2, 0]}>
        <sphereGeometry args={[0.15]} />
        <meshStandardMaterial color="#00d4ff" emissive="#00d4ff" emissiveIntensity={3} />
      </mesh>
    </group>
  )
}

export function CityBuildings() {
  const buildingData = useMemo(
    () => [
      // District 1 - Central business
      { pos: [-6, 0, -4] as [number, number, number], w: 1.5, h: 6, d: 1.5, c: "#0d1b2a", e: "#00d4ff" },
      { pos: [-3, 0, -5] as [number, number, number], w: 1.2, h: 4.5, d: 1.2, c: "#1b2838", e: "#00bcd4" },
      { pos: [-1, 0, -6] as [number, number, number], w: 1.8, h: 7, d: 1.8, c: "#0d1b2a", e: "#00d4ff" },
      { pos: [2, 0, -4] as [number, number, number], w: 1.4, h: 5, d: 1.4, c: "#162232", e: "#4dd0e1" },
      { pos: [5, 0, -5] as [number, number, number], w: 1.6, h: 8, d: 1.6, c: "#0a1628", e: "#00d4ff" },
      { pos: [7, 0, -3] as [number, number, number], w: 1.2, h: 3.5, d: 1.2, c: "#1b2838", e: "#ff6b35" },

      // District 2 - Residential
      { pos: [-7, 0, 2] as [number, number, number], w: 1.3, h: 3, d: 1.3, c: "#162232", e: "#ff6b35" },
      { pos: [-5, 0, 4] as [number, number, number], w: 1.0, h: 2.5, d: 1.0, c: "#1b2838", e: "#ffab40" },
      { pos: [-3, 0, 3] as [number, number, number], w: 1.5, h: 4, d: 1.5, c: "#0d1b2a", e: "#00d4ff" },
      { pos: [-1, 0, 5] as [number, number, number], w: 1.2, h: 3.5, d: 1.2, c: "#162232", e: "#4dd0e1" },

      // District 3 - Tech hub
      { pos: [3, 0, 3] as [number, number, number], w: 1.8, h: 5.5, d: 1.8, c: "#0a1628", e: "#00d4ff" },
      { pos: [6, 0, 4] as [number, number, number], w: 1.4, h: 4, d: 1.4, c: "#0d1b2a", e: "#00bcd4" },
      { pos: [5, 0, 1] as [number, number, number], w: 1.0, h: 3, d: 1.0, c: "#1b2838", e: "#ff6b35" },
      { pos: [8, 0, 2] as [number, number, number], w: 1.6, h: 6, d: 1.6, c: "#0d1b2a", e: "#00d4ff" },

      // Scattered smaller buildings
      { pos: [-8, 0, -1] as [number, number, number], w: 0.8, h: 2, d: 0.8, c: "#1b2838", e: "#4dd0e1" },
      { pos: [0, 0, 0] as [number, number, number], w: 1.0, h: 2.5, d: 1.0, c: "#162232", e: "#00d4ff" },
      { pos: [9, 0, -1] as [number, number, number], w: 1.2, h: 3, d: 1.2, c: "#0d1b2a", e: "#00bcd4" },
    ],
    []
  )

  return (
    <group>
      {buildingData.map((b, i) => (
        <Building
          key={i}
          position={b.pos}
          width={b.w}
          height={b.h}
          depth={b.d}
          color={b.c}
          emissiveColor={b.e}
          windowRows={Math.floor(b.h * 1.5)}
        />
      ))}

      {/* Signature skyscrapers */}
      <Skyscraper position={[-4, 0, -2]} height={10} />
      <Skyscraper position={[4, 0, -3]} height={12} />
      <Skyscraper position={[1, 0, 2]} height={9} />
    </group>
  )
          }
    
