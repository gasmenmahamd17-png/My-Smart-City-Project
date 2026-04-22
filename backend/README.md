# Smart City IoT Backend

Python FastAPI backend service for the virtual smart city with IoT simulation and AI decision engine.

## Features

- **IoT Simulation**: 22 smart street lights with motion (PIR) and light (LDR) sensors
- **AI Decision Engine**: Intelligent brightness control based on 4+ factors
- **Real-time Data Processing**: Energy consumption tracking and analysis
- **MySQL Database**: Persistent storage of sensor data and analytics
- **RESTful API**: Complete API for frontend integration
- **Zone Management**: Individual statistics per city zone

## Requirements

- Python 3.10+
- MySQL 8.0+
- pip or uv package manager

## Installation

### 1. Setup Database

```bash
# Install MySQL and create database
mysql -u root -p < scripts/init_database.sql
```

### 2. Install Python Dependencies

```bash
cd backend

# Using uv (recommended)
uv init
uv add fastapi uvicorn python-multipart mysql-connector-python python-dotenv pydantic sqlalchemy pytz

# Or using pip
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

### 4. Run Backend

```bash
# Using uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or
python main.py
```

Backend will start at `http://localhost:8000`

## API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check

### Street Lights
- `GET /api/lights` - Get all lights
- `GET /api/lights/{light_id}` - Get specific light
- `POST /api/lights/{light_id}/set-brightness` - Set light brightness

### Sensors
- `GET /api/sensors/motion` - Get motion sensors
- `GET /api/sensors/light` - Get light sensors

### Energy
- `GET /api/energy/current` - Current energy stats
- `GET /api/energy/history` - Historical energy records

### AI & Analytics
- `GET /api/ai/decisions` - Latest AI decisions
- `GET /api/zones/statistics` - Zone statistics
- `GET /api/system/stats` - Overall system stats

### Events & Reports
- `GET /api/events/system` - System event logs
- `POST /api/export/energy-report` - Export energy report
- `GET /api/realtime/stream` - Real-time data stream

## Database Schema

Tables:
- `street_lights` - Light configurations and status
- `motion_sensors` - PIR sensor data
- `light_sensors` - LDR sensor data
- `energy_records` - Energy consumption logs
- `ai_decisions` - AI decision history
- `zone_statistics` - Zone-based analytics
- `system_events` - System event logs
- `user_sessions` - User session tracking

## AI Decision Engine

The AI makes decisions based on:

1. **Motion Detection** - Activates full brightness when motion detected
2. **Ambient Light Level** - Reduces brightness during daylight
3. **Time-based Patterns** - Gradual dimming after activity
4. **Zone Rules** - Central areas maintain minimum brightness
5. **Neighbor Coordination** - Ensures uniform lighting patterns

## Performance

- Handles 22+ street lights simultaneously
- Real-time sensor updates
- Sub-second decision latency
- Optimized database queries with indexes
- Connection pooling for better throughput

## Configuration

Edit `iot_simulator.py` to:
- Add/remove street lights
- Adjust sensor sensitivity
- Modify AI decision weights
- Change power consumption values

## Development

```bash
# Run with debug logging
DEBUG=True uvicorn main:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/system/stats
```

## Troubleshooting

**Database Connection Error**
```
Check .env file database credentials
Ensure MySQL service is running
Verify database exists: USE smart_city_iot;
```

**Port Already in Use**
```
uvicorn main:app --port 8001
```

**Module Import Error**
```
uv add <missing_module>
# or
pip install <missing_module>
```

## Frontend Integration

Connect Next.js frontend with:

```typescript
const API_URL = 'http://localhost:8000'

// Example API call
const response = await fetch(`${API_URL}/api/system/stats`)
const data = await response.json()
```

## License

MIT
