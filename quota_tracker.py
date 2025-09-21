"""Production quota tracking with database backend.
Replaces in-memory counters with persistent database storage.
"""
from datetime import datetime
from typing import Dict, Tuple, Optional
from sqlalchemy import create_engine, text
import os

class DatabaseQuotaTracker:
    """Database-backed quota tracking system."""
    
    def __init__(self, database_url=None):
        if not database_url:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///investor_terminal.db')
        
        self.engine = create_engine(database_url)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure quota tracking tables exist."""
        quota_tables_sql = """
        CREATE TABLE IF NOT EXISTS hourly_usage (
            investor_id VARCHAR(50) NOT NULL,
            hour_key VARCHAR(20) NOT NULL,
            usage_count INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (investor_id, hour_key)
        );
        
        CREATE TABLE IF NOT EXISTS daily_feature_usage (
            investor_id VARCHAR(50) NOT NULL,
            date_key VARCHAR(12) NOT NULL,
            feature_name VARCHAR(100) NOT NULL,
            usage_count INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (investor_id, date_key, feature_name)
        );
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(quota_tables_sql))
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not create quota tables: {e}")
    
    def get_hourly_usage(self, investor_id: str, hour_key: str) -> int:
        """Get hourly usage count for investor."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT usage_count FROM hourly_usage WHERE investor_id = :investor_id AND hour_key = :hour_key"),
                    {"investor_id": investor_id, "hour_key": hour_key}
                ).fetchone()
                return result[0] if result else 0
        except:
            return 0
    
    def get_daily_feature_usage(self, investor_id: str, date_key: str, feature: str) -> int:
        """Get daily feature usage count for investor."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT usage_count FROM daily_feature_usage WHERE investor_id = :investor_id AND date_key = :date_key AND feature_name = :feature"),
                    {"investor_id": investor_id, "date_key": date_key, "feature": feature}
                ).fetchone()
                return result[0] if result else 0
        except:
            return 0
    
    def get_daily_total_usage(self, investor_id: str, date_key: str) -> int:
        """Get total daily usage across all features."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COALESCE(SUM(usage_count), 0) FROM daily_feature_usage WHERE investor_id = :investor_id AND date_key = :date_key"),
                    {"investor_id": investor_id, "date_key": date_key}
                ).fetchone()
                return result[0] if result else 0
        except:
            return 0
    
    def increment_hourly_usage(self, investor_id: str, hour_key: str, cost: int = 1) -> int:
        """Increment hourly usage counter."""
        try:
            with self.engine.connect() as conn:
                # Upsert (insert or update)
                conn.execute(
                    text("""
                    INSERT INTO hourly_usage (investor_id, hour_key, usage_count, updated_at)
                    VALUES (:investor_id, :hour_key, :cost, CURRENT_TIMESTAMP)
                    ON CONFLICT (investor_id, hour_key)
                    DO UPDATE SET usage_count = usage_count + :cost, updated_at = CURRENT_TIMESTAMP
                    """),
                    {"investor_id": investor_id, "hour_key": hour_key, "cost": cost}
                )
                conn.commit()
                return self.get_hourly_usage(investor_id, hour_key)
        except Exception as e:
            print(f"Error incrementing hourly usage: {e}")
            return 0
    
    def increment_feature_usage(self, investor_id: str, date_key: str, feature: str, cost: int = 1) -> int:
        """Increment daily feature usage counter."""
        try:
            with self.engine.connect() as conn:
                # Upsert (insert or update)
                conn.execute(
                    text("""
                    INSERT INTO daily_feature_usage (investor_id, date_key, feature_name, usage_count, updated_at)
                    VALUES (:investor_id, :date_key, :feature, :cost, CURRENT_TIMESTAMP)
                    ON CONFLICT (investor_id, date_key, feature_name)
                    DO UPDATE SET usage_count = usage_count + :cost, updated_at = CURRENT_TIMESTAMP
                    """),
                    {"investor_id": investor_id, "date_key": date_key, "feature": feature, "cost": cost}
                )
                conn.commit()
                return self.get_daily_feature_usage(investor_id, date_key, feature)
        except Exception as e:
            print(f"Error incrementing feature usage: {e}")
            return 0

# Global tracker instance (fallback to in-memory if DB fails)
_db_tracker = None

try:
    _db_tracker = DatabaseQuotaTracker()
except Exception as e:
    print(f"Warning: Database quota tracker failed, using fallback: {e}")
    _db_tracker = None

# Fallback to in-memory tracking
from collections import defaultdict
_hourly_counters = defaultdict(lambda: defaultdict(int))
_daily_counters = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

def get_quota_usage_db(investor_id: str, plan: str) -> Dict:
    """Get current usage with database backend."""
    from plan_access import HOURLY_QUOTAS, DAILY_CAPS
    
    now = datetime.now()
    hour_key = now.strftime('%Y-%m-%d %H')
    date_key = now.strftime('%Y-%m-%d')
    
    if _db_tracker:
        # Database backend
        hourly_usage = _db_tracker.get_hourly_usage(investor_id, hour_key)
        daily_usage = _db_tracker.get_daily_total_usage(investor_id, date_key)
    else:
        # Fallback to in-memory
        hourly_usage = _hourly_counters[hour_key][investor_id]
        daily_usage = sum(_daily_counters[date_key][investor_id].values())
    
    hourly_quota = HOURLY_QUOTAS.get(plan, 0)
    daily_cap = DAILY_CAPS.get(plan, 0)
    
    return {
        "hourly_usage": hourly_usage,
        "hourly_quota": hourly_quota,
        "hourly_remaining": max(0, hourly_quota - hourly_usage),
        "daily_usage": daily_usage,
        "daily_cap": daily_cap,
        "daily_remaining": max(0, daily_cap - daily_usage),
        "hour_key": hour_key,
        "date_key": date_key,
        "backend": "database" if _db_tracker else "memory"
    }

def increment_usage_db(investor_id: str, feature: str, cost: int = 1) -> int:
    """Increment usage with database backend."""
    now = datetime.now()
    hour_key = now.strftime('%Y-%m-%d %H')
    date_key = now.strftime('%Y-%m-%d')
    
    if _db_tracker:
        # Database backend
        _db_tracker.increment_hourly_usage(investor_id, hour_key, cost)
        return _db_tracker.increment_feature_usage(investor_id, date_key, feature, cost)
    else:
        # Fallback to in-memory
        _hourly_counters[hour_key][investor_id] += cost
        _daily_counters[date_key][investor_id][feature] += cost
        return _daily_counters[date_key][investor_id][feature]

def get_feature_usage_db(investor_id: str, feature: str) -> int:
    """Get current feature usage with database backend."""
    date_key = datetime.now().strftime('%Y-%m-%d')
    
    if _db_tracker:
        return _db_tracker.get_daily_feature_usage(investor_id, date_key, feature)
    else:
        return _daily_counters[date_key][investor_id][feature]
