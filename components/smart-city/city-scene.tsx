"use client"

import { useRef, useCallback } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { OrbitControls, Stars, Float } from "@react-three/drei"
import type * as THREE from "three"
import { CityBuildings } from "./buildings"
import { CityRoads } from "./roads"
import { CityVehicles } from "./vehicles"
import { DataOverlays } from "./data-overlays"
import { SmartStreetLights } from "./street-lights"
import type { IoTSystemState } from "@/lib/iot-simulation"
import { simulationTick } from "@/lib/iot-simulation"

function GridFloor() {
  return (
    <group position={[0, -0.02, 0]}>
      <gridHelper
        args={[40, 80, "#00d4ff", "#00d4ff"]}
        rotation={[0, 0, 0]}
        // @ts-expect-error Three.js GridHelper material
        material-opacity={0.04}
        // @ts-expect-error Three.js GridHelper material
        material-transparent={true}
      />
    </group>
  )
}

function CityLights() {
  return (
    <group>
      <ambientLight intensity={0.15} color="#0a1628" />

      <directionalLight
        position={[10, 20, 5]}
        intensity={0.3}
        color="#4488cc"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={50}
        shadow-camera-left={-15}
        shadow-camera-right={15}
        shadow-camera-top={15}
        shadow-camera-bottom={-15}
      />

      <pointLight position={[-4, 3, -2]} color="#00d4ff" intensity={2} distance={10} />
      <pointLight position={[4, 4, -3]} color="#00d4ff" intensity={2} distance={12} />
      <pointLight position={[1, 2.5, 2]} color="#4dd0e1" intensity={1.5} distance={8} />
      <pointLight position={[-6, 2, 4]} color="#ff6b35" intensity={1} distance={6} />
      <pointLight position={[7, 2, -1]} color="#00d4ff" intensity={1} distance={8} />

      <pointLight position={[0, 0.5, 0]} color="#00d4ff" intensity={0.5} distance={15} />
    </group>
  )
}

function FloatingOrb({ position, color }: { position: [number, number, number]; color: string }) {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.5 + position[0]) * 0.5
    }
  })

  return (
    <Float speed={1.5} floatIntensity={0.5}>
      <mesh ref={meshRef} position={position}>
        <sphereGeometry args={[0.1, 16, 16]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2} transparent opacity={0.6} />
      </mesh>
      <pointLight position={position} color={color} intensity={0.3} distance={3} />
    </Float>
  )
}

function IoTSimulationLoop({
  iotState,
  onUpdate,
}: {
  iotState: IoTSystemState
  onUpdate: (state: IoTSystemState) => void
}) {
  const stateRef = useRef(iotState)
  stateRef.current = iotState

  useFrame((_, delta) => {
    const clampedDelta = Math.min(delta, 0.1)
    const newState = simulationTick(stateRef.current, clampedDelta)
    onUpdate(newState)
  })

  return null
}

function Scene({
  iotState,
  onIoTUpdate,
}: {
  iotState: IoTSystemState
  onIoTUpdate: (state: IoTSystemState) => void
}) {
  return (
    <>
      <fog attach="fog" args={["#060d17", 15, 35]} />
      <color attach="background" args={["#060d17"]} />

      <Stars radius={50} depth={30} count={3000} factor={3} saturation={0} fade speed={0.5} />

      <CityLights />
      <GridFloor />
      <CityBuildings />
      <CityRoads />
      <CityVehicles />
      <DataOverlays />

      {/* IoT Smart Street Lights */}
      <SmartStreetLights lights={iotState.lights} motionSensors={iotState.motionSensors} />

      {/* IoT Simulation Loop */}
      <IoTSimulationLoop iotState={iotState} onUpdate={onIoTUpdate} />

      <FloatingOrb position={[-8, 4, -6]} color="#00d4ff" />
      <FloatingOrb position={[9, 5, -4]} color="#ff6b35" />
      <FloatingOrb position={[-3, 6, 7]} color="#4dd0e1" />
      <FloatingOrb position={[6, 3, 7]} color="#00d4ff" />

      <OrbitControls
        makeDefault
        enablePan
        enableZoom
        enableRotate
        minDistance={5}
        maxDistance={30}
        minPolarAngle={0.2}
        maxPolarAngle={Math.PI / 2.2}
        target={[0, 2, 0]}
        autoRotate
        autoRotateSpeed={0.3}
      />
    </>
  )
}

export function CityScene({
  iotState,
  onIoTUpdate,
}: {
  iotState: IoTSystemState
  onIoTUpdate: (state: IoTSystemState) => void
}) {
  const handleUpdate = useCallback(
    (state: IoTSystemState) => {
      onIoTUpdate(state)
    },
    [onIoTUpdate]
  )

  return (
    <Canvas
      shadows
      camera={{ position: [12, 10, 12], fov: 50, near: 0.1, far: 100 }}
      gl={{ antialias: true, alpha: false }}
      dpr={[1, 1.5]}
    >
      <Scene iotState={iotState} onIoTUpdate={handleUpdate} />
    </Canvas>
  )
}
  
