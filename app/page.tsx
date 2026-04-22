"use client"

import { CityScene } from "@/components/smart-city/city-scene"
import { IoTPanel } from "@/components/smart-city/iot-panel"
import { useIoTSimulation } from "@/lib/iot-simulation"

export default function SmartCityPage() {
  const { iotState, updateDevice } = useIoTSimulation()

  return (
    <main className="flex h-screen w-full bg-slate-950 text-slate-50 overflow-hidden">
      <div className="relative flex-1 h-full">
        <CityScene iotState={iotState} onIoTUpdate={updateDevice} />
      </div>
      <div className="w-96 h-full border-l border-slate-800 bg-slate-900/50 backdrop-blur-md overflow-y-auto p-6">
        <IoTPanel state={iotState} onUpdate={updateDevice} />
      </div>
    </main>
  )
}
