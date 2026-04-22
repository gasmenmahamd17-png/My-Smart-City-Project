"""
Smart City IoT Backend Service
FastAPI Backend for handling IoT simulations, database, and AI decisions
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
import json
from typing import Optional, List, Dict, Any

from database import Database
from iot_simulator import IoTSimulator
from models import (
    StreetLightStatus,
    EnergyRecord,
    AIDecisionLog,
    ZoneStatistics,
    SystemStats
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Smart City IoT Backend",
    description="Backend service for virtual smart city with IoT sensors and AI engine",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db: Optional[Database] = None
iot_simulator: Optional[IoTSimulator] = None
simulation_task: Optional[asyncio.Task] = None


@app.on_event("startup")
async def startup_event():
    """Initialize database and IoT simulator on startup"""
    global db, iot_simulator, simulation_task
    
    try:
        # Initialize database connection
        db = Database(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "smart_city_iot"),
            port=int(os.getenv("DB_PORT", "3306"))
        )
        
        await db.connect()
        print("[v0] Database connected successfully")
        
        # Initialize IoT simulator
        iot_simulator = IoTSimulator(db=db)
        
        # Start simulation loop
        simulation_task = asyncio.create_task(simulation_loop())
        print("[v0] IoT simulation started")
        
    except Exception as e:
        print(f"[v0] Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global db, simulation_task
    
    if simulation_task:
        simulation_task.cancel()
        
    if db:
        await db.close()
        print("[v0] Database connection closed")


async def simulation_loop():
    """Main simulation loop that runs continuously"""
    while True:
        try:
            if iot_simulator:
                # Run simulation tick
                await iot_simulator.tick(delta_time=1.0)  # 1 second per tick
                
            await asyncio.sleep(1)  # 1 second interval
            
        except Exception as e:
            print(f"[v0] Simulation loop error: {e}")
            await asyncio.sleep(1)


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Smart City IoT Backend",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_connected = False
    if db:
        try:
            await db.query("SELECT 1")
            db_connected = True
        except:
            db_connected = False
    
    return {
        "status": "healthy",
        "database": "connected" if db_connected else "disconnected",
        "simulator": "running" if iot_simulator else "not_running"
    }


@app.get("/api/lights", response_model=List[StreetLightStatus])
async def get_all_lights():
    """Get all street lights current status"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_all_lights()


@app.get("/api/lights/{light_id}", response_model=StreetLightStatus)
async def get_light_status(light_id: str):
    """Get specific light status"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    light = iot_simulator.get_light(light_id)
    if not light:
        raise HTTPException(status_code=404, detail=f"Light {light_id} not found")
    
    return light


@app.get("/api/sensors/motion")
async def get_motion_sensors():
    """Get all motion sensor readings"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_motion_sensors()


@app.get("/api/sensors/light")
async def get_light_sensors():
    """Get all light sensor readings"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_light_sensors()


@app.get("/api/energy/current")
async def get_current_energy():
    """Get current energy consumption data"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_energy_stats()


@app.get("/api/energy/history")
async def get_energy_history(limit: int = 100):
    """Get historical energy records"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    records = await db.fetch_all(
        "SELECT * FROM energy_records ORDER BY timestamp DESC LIMIT %s",
        (limit,)
    )
    
    return [dict(r) for r in records]


@app.get("/api/ai/decisions")
async def get_ai_decisions(limit: int = 20):
    """Get latest AI decisions"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    decisions = iot_simulator.get_latest_decisions(limit)
    return decisions


@app.get("/api/zones/statistics")
async def get_zone_statistics():
    """Get statistics for each zone"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_zone_statistics()


@app.get("/api/system/stats", response_model=SystemStats)
async def get_system_stats():
    """Get overall system statistics"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_system_stats()


@app.post("/api/lights/{light_id}/set-brightness")
async def set_light_brightness(light_id: str, brightness: float):
    """Manually set light brightness (0.0 - 1.0)"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    if brightness < 0 or brightness > 1.0:
        raise HTTPException(status_code=400, detail="Brightness must be between 0 and 1")
    
    success = iot_simulator.set_light_brightness(light_id, brightness)
    if not success:
        raise HTTPException(status_code=404, detail=f"Light {light_id} not found")
    
    return {"light_id": light_id, "brightness": brightness, "status": "updated"}


@app.get("/api/events/system")
async def get_system_events(limit: int = 50):
    """Get system event logs"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    events = await db.fetch_all(
        "SELECT * FROM system_events ORDER BY event_time DESC LIMIT %s",
        (limit,)
    )
    
    return [dict(e) for e in events]


@app.post("/api/export/energy-report")
async def export_energy_report(start_time: int, end_time: int):
    """Export energy consumption report for time range"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    records = await db.fetch_all(
        "SELECT * FROM energy_records WHERE timestamp BETWEEN %s AND %s ORDER BY timestamp",
        (start_time, end_time)
    )
    
    if not records:
        raise HTTPException(status_code=404, detail="No data found for time range")
    
    # Calculate statistics
    total_power = sum(r['total_power_watts'] for r in records)
    avg_savings = sum(r['energy_savings_percent'] for r in records) / len(records)
    
    return {
        "start_time": start_time,
        "end_time": end_time,
        "record_count": len(records),
        "total_power_watts": total_power,
        "average_savings_percent": avg_savings,
        "records": [dict(r) for r in records]
    }


@app.get("/api/realtime/stream")
async def realtime_stream():
    """WebSocket-like endpoint for real-time updates"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return {
        "lights": iot_simulator.get_all_lights(),
        "energy": iot_simulator.get_energy_stats(),
        "decisions": iot_simulator.get_latest_decisions(5),
        "zones": iot_simulator.get_zone_statistics(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
        )
        
        await db.connect()
        print("[v0] Database connected successfully")
        
        # Initialize IoT simulator
        iot_simulator = IoTSimulator(db=db)
        
        # Start simulation loop
        simulation_task = asyncio.create_task(simulation_loop())
        print("[v0] IoT simulation started")
        
    except Exception as e:
        print(f"[v0] Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global db, simulation_task
    
    if simulation_task:
        simulation_task.cancel()
        
    if db:
        await db.close()
        print("[v0] Database connection closed")


async def simulation_loop():
    """Main simulation loop that runs continuously"""
    while True:
        try:
            if iot_simulator:
                # Run simulation tick
                await iot_simulator.tick(delta_time=1.0)  # 1 second per tick
                
            await asyncio.sleep(1)  # 1 second interval
            
        except Exception as e:
            print(f"[v0] Simulation loop error: {e}")
            await asyncio.sleep(1)


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Smart City IoT Backend",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_connected = False
    if db:
        try:
            await db.query("SELECT 1")
            db_connected = True
        except:
            db_connected = False
    
    return {
        "status": "healthy",
        "database": "connected" if db_connected else "disconnected",
        "simulator": "running" if iot_simulator else "not_running"
    }


@app.get("/api/lights", response_model=List[StreetLightStatus])
async def get_all_lights():
    """Get all street lights current status"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_all_lights()


@app.get("/api/lights/{light_id}", response_model=StreetLightStatus)
async def get_light_status(light_id: str):
    """Get specific light status"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    light = iot_simulator.get_light(light_id)
    if not light:
        raise HTTPException(status_code=404, detail=f"Light {light_id} not found")
    
    return light


@app.get("/api/sensors/motion")
async def get_motion_sensors():
    """Get all motion sensor readings"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_motion_sensors()


@app.get("/api/sensors/light")
async def get_light_sensors():
    """Get all light sensor readings"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_light_sensors()


@app.get("/api/energy/current")
async def get_current_energy():
    """Get current energy consumption data"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_energy_stats()


@app.get("/api/energy/history")
async def get_energy_history(limit: int = 100):
    """Get historical energy records"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    records = await db.fetch_all(
        "SELECT * FROM energy_records ORDER BY timestamp DESC LIMIT %s",
        (limit,)
    )
    
    return [dict(r) for r in records]


@app.get("/api/ai/decisions")
async def get_ai_decisions(limit: int = 20):
    """Get latest AI decisions"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    decisions = iot_simulator.get_latest_decisions(limit)
    return decisions


@app.get("/api/zones/statistics")
async def get_zone_statistics():
    """Get statistics for each zone"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_zone_statistics()


@app.get("/api/system/stats", response_model=SystemStats)
async def get_system_stats():
    """Get overall system statistics"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return iot_simulator.get_system_stats()


@app.post("/api/lights/{light_id}/set-brightness")
async def set_light_brightness(light_id: str, brightness: float):
    """Manually set light brightness (0.0 - 1.0)"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    if brightness < 0 or brightness > 1.0:
        raise HTTPException(status_code=400, detail="Brightness must be between 0 and 1")
    
    success = iot_simulator.set_light_brightness(light_id, brightness)
    if not success:
        raise HTTPException(status_code=404, detail=f"Light {light_id} not found")
    
    return {"light_id": light_id, "brightness": brightness, "status": "updated"}


@app.get("/api/events/system")
async def get_system_events(limit: int = 50):
    """Get system event logs"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    events = await db.fetch_all(
        "SELECT * FROM system_events ORDER BY event_time DESC LIMIT %s",
        (limit,)
    )
    
    return [dict(e) for e in events]


@app.post("/api/export/energy-report")
async def export_energy_report(start_time: int, end_time: int):
    """Export energy consumption report for time range"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    records = await db.fetch_all(
        "SELECT * FROM energy_records WHERE timestamp BETWEEN %s AND %s ORDER BY timestamp",
        (start_time, end_time)
    )
    
    if not records:
        raise HTTPException(status_code=404, detail="No data found for time range")
    
    # Calculate statistics
    total_power = sum(r['total_power_watts'] for r in records)
    avg_savings = sum(r['energy_savings_percent'] for r in records) / len(records)
    
    return {
        "start_time": start_time,
        "end_time": end_time,
        "record_count": len(records),
        "total_power_watts": total_power,
        "average_savings_percent": avg_savings,
        "records": [dict(r) for r in records]
    }


@app.get("/api/realtime/stream")
async def realtime_stream():
    """WebSocket-like endpoint for real-time updates"""
    if not iot_simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    return {
        "lights": iot_simulator.get_all_lights(),
        "energy": iot_simulator.get_energy_stats(),
        "decisions": iot_simulator.get_latest_decisions(5),
        "zones": iot_simulator.get_zone_statistics(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
