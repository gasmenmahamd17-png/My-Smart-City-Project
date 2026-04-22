"use client"

import { useRef, useMemo } from "react"
import { useFrame } from "@react-three/fiber"
import type * as THREE from "three"
import type { StreetLight as StreetLightData, MotionSensor } from "@/lib/iot-simulation"

function SmartStreetLight({
  light,
  motionSensor,
}: {
  light: StreetLightData
  motionSensor: MotionSensor | undefined
}) {
  const lightRef = useRef<THREE.PointLight>(null)
  const coneRef = useRef<THREE.Mesh>(null)
  const indicatorRef = useRef<THREE.Mesh>(null)
  const pulseRef = useRef(0)

  const isMotionDetected = motionSensor?.detected ?? false

  useFrame((_, delta) => {
    pulseRef.current += delta

    // Animate the light intensity based on brightness
    if (lightRef.current) {
      lightRef.current.intensity = light.brightness * 4
    }

    // Animate the light cone opacity
    if (coneRef.current) {
      const mat = coneRef.current.material as THREE.MeshStandardMaterial
      mat.opacity = light.brightness * 0.15
      mat.emissiveIntensity = light.brightness * 0.5
    }

    // Motion indicator pulse
    if (indicatorRef.current) {
      const mat = indicatorRef.current.material as THREE.MeshStandardMaterial
      if (isMotionDetected) {
        mat.emissiveIntensity = 2 + Math.sin(pulseRef.current * 8) * 1
      } else {
        mat.emissiveIntensity = 0.3
      }
    }
  })

  const lightColor = useMemo(() => {
    if (light.brightness > 0.7) return "#ffe4a0"
    if (light.brightness > 0.4) return "#ffd080"
    return "#ff9020"
  }, [light.brightness])

  const indicatorColor = isMotionDetected ? "#00ff88" : "#ff4444"

  return (
    <group position={[light.position[0], 0, light.position[2]]}>
      {/* Pole */}
      <mesh position={[0, 1.5, 0]} castShadow>
        <cylinderGeometry args={[0.03, 0.04, 3, 8]} />
        <meshStandardMaterial color="#2a3545" metalness={0.8} roughness={0.3} />
      </mesh>

      {/* Arm */}
      <mesh position={[0.15, 2.9, 0]} rotation={[0, 0, -Math.PI / 6]}>
        <cylinderGeometry args={[0.02, 0.02, 0.4, 6]} />
        <meshStandardMaterial color="#2a3545" metalness={0.8} roughness={0.3} />
      </mesh>

      {/* Light housing */}
      <mesh position={[0.25, 3, 0]}>
        <boxGeometry args={[0.15, 0.05, 0.1]} />
        <meshStandardMaterial color="#1a2535" metalness={0.7} roughness={0.3} />
      </mesh>

      {/* Light bulb (emissive) */}
      <mesh position={[0.25, 2.96, 0]}>
        <sphereGeometry args={[0.04, 8, 8]} />
        <meshStandardMaterial
          color={lightColor}
          emissive={lightColor}
          emissiveIntensity={light.brightness * 3}
        />
      </mesh>

      {/* Point light for illumination */}
      <pointLight
        ref={lightRef}
        position={[0.25, 2.9, 0]}
        color={lightColor}
        intensity={light.brightness * 4}
        distance={5}
        decay={2}
        castShadow={light.brightness > 0.5}
      />

      {/* Light cone (visible beam) */}
      <mesh ref={coneRef} position={[0.25, 1.5, 0]} rotation={[Math.PI, 0, 0]}>
        <coneGeometry args={[1.2, 3, 16, 1, true]} />
        <meshStandardMaterial
          color={lightColor}
          emissive={lightColor}
          emissiveIntensity={light.brightness * 0.5}
          transparent
          opacity={light.brightness * 0.15}
          side={2}
          depthWrite={false}
        />
      </mesh>

      {/* Motion sensor indicator (small LED on pole) */}
      <mesh ref={indicatorRef} position={[0.06, 2.5, 0]}>
        <sphereGeometry args={[0.02, 6, 6]} />
        <meshStandardMaterial
          color={indicatorColor}
          emissive={indicatorColor}
          emissiveIntensity={isMotionDetected ? 2 : 0.3}
        />
      </mesh>

      {/* Sensor dome (PIR motion sensor) */}
      <mesh position={[0.25, 3.05, 0]}>
        <sphereGeometry args={[0.03, 8, 4, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshStandardMaterial
          color="#1a3050"
          metalness={0.5}
          roughness={0.5}
          transparent
          opacity={0.7}
        />
      </mesh>

      {/* Ground glow circle */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0.25, 0.02, 0]}>
        <circleGeometry args={[1.5, 16]} />
        <meshStandardMaterial
          color={lightColor}
          emissive={lightColor}
          emissiveIntensity={light.brightness * 0.2}
          transparent
          opacity={light.brightness * 0.08}
          depthWrite={false}
        />
      </mesh>
    </group>
  )
}

export function SmartStreetLights({
  lights,
  motionSensors,
}: {
  lights: StreetLightData[]
  motionSensors: MotionSensor[]
}) {
  return (
    <group>
      {lights.map((light) => (
        <SmartStreetLight
          key={light.id}
          light={light}
          motionSensor={motionSensors.find((s) => s.id === light.motionSensorId)}
        />
      ))}
    </group>
  )
                                                 }
                             
