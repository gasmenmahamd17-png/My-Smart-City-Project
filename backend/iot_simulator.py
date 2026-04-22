import asyncio
import random
import time
from datetime import datetime
from typing import List, Dict, Any
from database import Database

class IoTSimulator:
    def __init__(self, db: Database):
        self.db = db
        self.running = False
        self.tick_rate = 1.0  # Seconds between updates
        
        # Simulation state
        self.zones = [
            {"id": 1, "name": "Downtown", "lights": 50, "activity": 0.8},
            {"id": 2, "name": "Residential A", "lights": 120, "activity": 0.3},
            {"id": 3, "name": "Industrial Park", "lights": 80, "activity": 0.1},
            {"id": 4, "name": "Main Highway", "lights": 200, "activity": 0.5}
        ]
        
    async def start(self):
        """Start the IoT simulation loop"""
        self.running = True
        print("[v0] IoT Simulator started")
        
        while self.running:
            try:
                await self.update_simulation()
                await asyncio.sleep(self.tick_rate)
            except Exception as e:
                print(f"[v0] Simulation error: {e}")
                await asyncio.sleep(5)

    def stop(self):
        """Stop the simulation"""
        self.running = False
        print("[v0] IoT Simulator stopped")

    async def update_simulation(self):
        """Update sensor data and save to database"""
        timestamp = int(time.time())
        total_power = 0
        total_lights = 0
        active_lights = 0
        
        for zone in self.zones:
            # Simulate real-time data
            # Higher activity = more lights on, higher brightness
            current_activity = self.get_current_activity(zone)
            
            zone_active_lights = int(zone["lights"] * (0.2 + current_activity * 0.8))
            avg_brightness = 0.3 + (current_activity * 0.7)
            
            # Power calculation (approx 60W per light at full brightness)
            zone_power = zone_active_lights * 60 * avg_brightness
            
            # Calculate savings (compared to 100% on at 100% brightness)
            max_power = zone["lights"] * 60
            savings_pct = (1 - (zone_power / max_power)) * 100 if max_power > 0 else 0
            
            # Save zone statistics
            stats = {
                "zone_id": zone["id"],
                "zone_name": zone["name"],
                "total_lights": zone["lights"],
                "active_lights": zone_active_lights,
                "avg_brightness": round(avg_brightness, 2),
                "total_power_watts": round(zone_power, 2),
                "energy_savings_percent": round(savings_pct, 2)
            }
            
            await self.db.save_zone_stats(stats)
            
            # Accumulate totals
            total_power += zone_power
            total_lights += zone["lights"]
            active_lights += zone_active_lights

        # Save aggregate energy record
        total_savings_pct = (1 - (total_power / (total_lights * 60))) * 100
        energy_record = {
            "timestamp": timestamp,
            "total_power_watts": round(total_power, 2),
            "active_lights": active_lights,
            "energy_savings_percent": round(total_savings_pct, 2)
        }
        
        await self.db.save_energy_record(energy_record)
        
        # Randomly log events
        if random.random() < 0.05:
            await self.db.log_event(
                "SENSOR_UPDATE",
                "INFO",
                f"Updated stats for {len(self.zones)} zones",
                {"total_power": total_power}
            )

    def get_current_activity(self, zone: Dict) -> float:
        """Simulate activity based on time of day and zone type"""
        hour = datetime.now().hour
        
        # Base activity level (night time is busier for street lights)
        if 6 <= hour <= 18:
            # Daytime - minimal light needed
            base_activity = 0.05
        else:
            # Nighttime - activity depends on zone
            if hour > 22 or hour < 4:
                # Late night
                base_activity = zone["activity"] * 0.4
            else:
                # Evening/Early morning
                base_activity = zone["activity"]
                
        # Add some randomness
        variation = random.uniform(-0.1, 0.1)
        return max(0.0, min(1.0, base_activity + variation))

    async def simulate_ai_intervention(self):
        """Simulate an AI model making a decision to optimize power"""
        for zone in self.zones:
            if random.random() < 0.1: # 10% chance per tick
                old_brightness = 0.8 # Assume previous
                new_brightness = old_brightness * 0.7 # 30% reduction
                
                decision = {
                    "zone_id": zone["id"],
                    "action": "REDUCE_BRIGHTNESS",
                    "reason": "LOW_ACTIVITY_DETECTED",
                    "impact_estimate": "200W_SAVED",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self.db.save_ai_decision(decision)
                await self.db.log_event(
                    "AI_OPTIMIZATION",
                    "SUCCESS",
                    f"Reduced brightness in {zone['name']} due to low activity"
                )
            
            query = "UPDATE motion_sensors SET detected = %s WHERE id = %s"
            await self.db.execute_query(query, (detected, sensor['id']))

        # Simulate light sensors
        cycle_position = (math.sin(self.system_time * 0.02) + 1) / 2
        ambient_level = 0.05 + cycle_position * 0.15

        for sensor in light_sensors:
            query = "UPDATE light_sensors SET ambient_level = %s, reading = %s WHERE id = %s"
            await self.db.execute_query(query, (ambient_level, ambient_level * 1000, sensor['id']))

    async def run_ai_engine(self):
        """Run AI decision engine"""
        lights = await self.db.get_all_lights()
        motion_sensors = await self.db.get_all_motion_sensors()
        light_sensors = await self.db.get_all_light_sensors()

        for light in lights:
            motion_sensor = next((s for s in motion_sensors if s['id'] == f"MS-{light['id'][3:]}"), None)
            light_sensor = next((s for s in light_sensors if s['id'] == f"LS-{light['id'][3:]}"), None)

            if not motion_sensor or not light_sensor:
                continue

            # AI Decision Logic
            target_brightness = 0.15
            action = "maintain"
            reason = "Standby mode"
            confidence = 0.9

            if motion_sensor['detected']:
                target_brightness = 1.0
                action = "increase"
                reason = "Motion detected"
                confidence = 0.95
            elif light_sensor['ambient_level'] > 0.3:
                target_brightness = max(0.1, 0.5 - light_sensor['ambient_level'] * 0.5)
                action = "decrease"
                reason = "High ambient light"
                confidence = 0.85

            # Update light brightness
            new_brightness = light['brightness'] + (target_brightness - light['brightness']) * 0.1
            new_brightness = max(0.1, min(1.0, new_brightness))

            query = "UPDATE street_lights SET brightness = %s WHERE id = %s"
            await self.db.execute_query(query, (new_brightness, light['id']))

            # Record AI decision
            decision_data = {
                'light_id': light['id'],
                'action': action,
                'target_brightness': target_brightness,
                'reason': reason,
                'confidence': confidence
            }
            await self.db.add_ai_decision(decision_data)

    async def record_metrics(self):
        """Record energy and zone metrics"""
        lights = await self.db.get_all_lights()
        motion_sensors = await self.db.get_all_motion_sensors()

        total_power = sum(l['power_consumption'] for l in lights) if lights else 0
        active_lights = sum(1 for l in lights if l['brightness'] > 0.3) if lights else 0
        avg_brightness = (sum(l['brightness'] for l in lights) / len(lights)) if lights else 0
        motion_events = sum(1 for s in motion_sensors if s.get('detected')) if motion_sensors else 0
        max_power = len(lights) * 150 if lights else 0
        savings = ((max_power - total_power) / max_power * 100) if max_power > 0 else 0

        energy_record = {
            'total_power': total_power,
            'active_lights': active_lights,
            'avg_brightness': avg_brightness,
            'motion_events': motion_events,
            'savings_percentage': savings
        }

        await self.db.add_energy_record(energy_record)

        # Record zone statistics
        zones = ["central", "residential", "tech", "industrial", "green"]
        for zone in zones:
            zone_lights = [l for l in lights if l['zone'] == zone]
            if zone_lights:
                zone_power = sum(l['power_consumption'] for l in zone_lights)
                zone_max = len(zone_lights) * 150
                zone_savings = ((zone_max - zone_power) / zone_max * 100) if zone_max > 0 else 0
                zone_avg_brightness = sum(l['brightness'] for l in zone_lights) / len(zone_lights)

                zone_data = {
                    'zone_name': zone,
                    'lights_count': len(zone_lights),
                    'total_power': zone_power,
                    'savings_percentage': zone_savings,
                    'avg_brightness': zone_avg_brightness
                }
                await self.db.add_zone_statistics(zone_data)

    def stop(self):
        """Stop the simulator"""
        self.is_running = False
