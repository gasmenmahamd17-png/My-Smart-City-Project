"""
Data models for Smart City IoT Backend
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class LightStatus(str, Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    FAULT = "fault"


class ActionType(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"
    EMERGENCY = "emergency"


class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ==================== Sensor Models ====================

class MotionSensor(BaseModel):
    id: str
    position_x: float
    position_y: float
    position_z: float
    detected: bool
    last_detection: Optional[float] = None
    sensitivity: float


class LightSensor(BaseModel):
    id: str
    position_x: float
    position_y: float
    position_z: float
    ambient_level: float
    reading: float


# ==================== Light Models ====================

class StreetLightStatus(BaseModel):
    id: str
    position_x: float
    position_y: float
    position_z: float
    brightness: float
    target_brightness: float
    power_consumption: float
    status: LightStatus
    zone: str
    motion_sensor_id: str
    light_sensor_id: str


class LightUpdate(BaseModel):
    light_id: str
    brightness: float
    power_consumption: float
    status: LightStatus


# ==================== Energy Models ====================

class EnergyRecord(BaseModel):
    timestamp: float
    total_power_watts: int
    active_lights: int
    avg_brightness: float
    motion_events: int
    energy_savings_percent: float


class EnergyStats(BaseModel):
    current_power: float
    total_power: int
    max_power: int
    active_lights: int
    total_lights: int
    avg_brightness: float
    energy_saved_percent: float
    motion_active: int
    power_history: List[float]
    savings_history: List[float]


# ==================== AI Decision Models ====================

class AIDecision(BaseModel):
    light_id: str
    action: ActionType
    target_brightness: float
    reason: str
    confidence: float
    timestamp: float


class AIDecisionLog(BaseModel):
    id: Optional[int] = None
    light_id: str
    action: ActionType
    target_brightness: float
    reason: str
    confidence: float
    timestamp: float
    decision_time: str


# ==================== Zone Models ====================

class ZoneStatistic(BaseModel):
    zone: str
    total_lights: int
    active_lights: int
    total_power_watts: int
    avg_brightness: float
    energy_savings_percent: float
    motion_events: int


class ZoneStatistics(BaseModel):
    zones: List[ZoneStatistic]
    recorded_at: str


# ==================== System Models ====================

class SystemStats(BaseModel):
    total_power: int
    max_power: int
    active_lights: int
    total_lights: int
    avg_brightness: int
    motion_active: int
    energy_saved: float
    zone_stats: List[Dict[str, Any]]
    sensor_count: int
    ai_decision_count: int
    power_history: List[float]
    savings_history: List[float]
    system_uptime: float
    last_update: str


class SystemEvent(BaseModel):
    id: Optional[int] = None
    event_type: str
    severity: SeverityLevel
    description: str
    data: Optional[Dict[str, Any]] = None
    event_time: str


# ==================== Request Models ====================

class SetBrightnessRequest(BaseModel):
    light_id: str
    brightness: float


class ExportReportRequest(BaseModel):
    start_time: int
    end_time: int
    include_analytics: bool = True


# ==================== Response Models ====================

class SuccessResponse(BaseModel):
    status: str
    message: str
    timestamp: str


class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str
    request_id: Optional[str] = None


class PaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[Dict[str, Any]]
