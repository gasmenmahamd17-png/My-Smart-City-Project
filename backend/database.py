import mysql.connector
from mysql.connector import pooling, Error
from typing import Optional, List, Dict, Any, Tuple
import asyncio
from datetime import datetime

class Database:
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.pool: Optional[pooling.MySQLConnectionPool] = None
        self.connection: Optional[mysql.connector.MySQLConnection] = None

    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="smart_city_pool",
                pool_size=5,
                pool_reset_session=True,
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True
            )

            # Test connection
            self.connection = self.pool.get_connection()
            self.connection.close()

            print(f"[v0] Database connected: {self.host}:{self.port}/{self.database}")
            return True

        except Error as e:
            print(f"[v0] Database connection error: {e}")
            return False

    async def close(self):
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
                print("[v0] Database connection closed")
            except Error as e:
                print(f"[v0] Error closing connection: {e}")

    async def query(self, sql: str, params: Tuple = None) -> bool:
        """Execute a query (INSERT, UPDATE, DELETE)"""
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            result = cursor.rowcount
            cursor.close()
            conn.close()

            return result > 0

        except Error as e:
            print(f"[v0] Query error: {e}")
            return False

    async def fetch_one(self, sql: str, params: Tuple = None) -> Optional[Dict]:
        """Fetch a single row"""
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return result

        except Error as e:
            print(f"[v0] Fetch one error: {e}")
            return None

    async def fetch_all(self, sql: str, params: Tuple = None) -> List[Dict]:
        """Fetch all rows"""
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            results = cursor.fetchall()
            cursor.close()
            conn.close()

            return results if results else []

        except Error as e:
            print(f"[v0] Fetch all error: {e}")
            return []

    async def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a row and return last insert id"""
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, tuple(data.values()))
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()

            return last_id

        except Error as e:
            print(f"[v0] Insert error: {e}")
            return -1

    async def update(self, table: str, data: Dict[str, Any], where: str, where_params: Tuple) -> bool:
        """Update rows"""
        try:
            set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"

            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, tuple(data.values()) + where_params)
            cursor.close()
            conn.close()

            return True

        except Error as e:
            print(f"[v0] Update error: {e}")
            return False

    async def delete(self, table: str, where: str, params: Tuple) -> bool:
        """Delete rows"""
        try:
            sql = f"DELETE FROM {table} WHERE {where}"

            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            cursor.close()
            conn.close()

            return True

        except Error as e:
            print(f"[v0] Delete error: {e}")
            return False

    async def execute_script(self, script: str) -> bool:
        """Execute SQL script with multiple statements"""
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()

            # Split script by semicolons and execute each statement
            statements = [s.strip() for s in script.split(';') if s.strip()]

            for statement in statements:
                cursor.execute(statement)

            cursor.close()
            conn.close()

            print(f"[v0] Executed {len(statements)} SQL statements")
            return True

        except Error as e:
            print(f"[v0] Script execution error: {e}")
            return False

    async def log_event(self, event_type: str, severity: str, description: str, data: Optional[Dict] = None) -> int:
        """Log a system event"""
        import json
        event_data = {
            'event_type': event_type,
            'severity': severity,
            'description': description,
            'data': json.dumps(data) if data else None,
            'event_time': datetime.utcnow().isoformat()
        }
        return await self.insert('system_events', event_data)

    async def save_energy_record(self, record: Dict[str, Any]) -> int:
        """Save energy consumption record"""
        return await self.insert('energy_records', record)

    async def save_ai_decision(self, decision: Dict[str, Any]) -> int:
        """Save AI decision log"""
        return await self.insert('ai_decisions', decision)

    async def save_zone_stats(self, stats: Dict[str, Any]) -> int:
        """Save zone statistics"""
        return await self.insert('zone_statistics', stats)

    async def get_energy_trend(self, hours: int = 24) -> List[Dict]:
        """Get energy consumption trend for last N hours"""
        sql = """
        SELECT timestamp, total_power_watts, energy_savings_percent, active_lights
        FROM energy_records
        WHERE timestamp > UNIX_TIMESTAMP() - (%s * 3600)
        ORDER BY timestamp ASC
        """
        return await self.fetch_all(sql, (hours,))

    async def get_zone_summary(self) -> List[Dict]:
        """Get summary statistics for each zone"""
        sql = """
        SELECT zone_name, total_lights, active_lights, total_power_watts,
               avg_brightness, energy_savings_percent
        FROM zone_statistics
        WHERE recorded_at = (SELECT MAX(recorded_at) FROM zone_statistics)
        """
        return await self.fetch_all(sql)
      
