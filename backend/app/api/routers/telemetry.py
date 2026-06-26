from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
import redis

from app.db.database import get_db
from app.core.security import require_operator
from app.core.config import settings
from app.models.telemetry import Telemetry, AlarmEvent

router = APIRouter(prefix="/api", tags=["Telemetry"])
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.get("/network/snapshot", dependencies=[Depends(require_operator)])
def get_network_snapshot():
    """Fetches the current state of all meters from Redis cache."""
    keys = redis_client.keys("meter:*")
    snapshot = {key.split(":")[1]: redis_client.hgetall(key) for key in keys}
    return {"status": "success", "data": snapshot}

@router.get("/telemetry/history/{meter_id}", dependencies=[Depends(require_operator)])
def get_telemetry_history(meter_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """Fetches the latest historical data, bypassing timezone math for debugging."""
    
    stmt = (
        select(Telemetry.time, Telemetry.voltage_v, Telemetry.current_a, Telemetry.active_power_kw)
        .where(Telemetry.measurement_id == meter_id)
        .order_by(Telemetry.time.desc())
        .limit(limit)
    )
    
    # Execute, convert to dicts, and reverse the list so the chart draws left-to-right (oldest to newest)
    result = db.execute(stmt).mappings().all()
    data = [dict(row) for row in result]
    return list(reversed(data))

@router.get("/alarms", dependencies=[Depends(require_operator)])
def get_recent_alarms(limit: int = 50, db: Session = Depends(get_db)):
    """Fetches recent alarms for the frontend alarm panel."""
    alarms = db.query(AlarmEvent).order_by(AlarmEvent.timestamp.desc()).limit(limit).all()
    return alarms