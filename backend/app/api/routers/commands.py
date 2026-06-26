import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import paho.mqtt.publish as mqtt_publish
from app.db.database import get_db
from app.core.security import require_dispatcher
from app.core.config import settings
from app.schemas.pydantic import SwitchCommand
from app.models.audit import AuditLog

router = APIRouter(prefix="/api/commands", tags=["Commands"])

@router.post("/switch/{switch_id}")
def operate_switch(switch_id: str, payload: SwitchCommand, current_user: dict = Depends(require_dispatcher), db: Session = Depends(get_db)):
    if payload.command not in ["open", "close"]:
        raise HTTPException(status_code=400, detail="Command must be 'open' or 'close'")

    username = current_user["username"]

    # 1. Write to Audit Log using SQLAlchemy
    try:
        new_log = AuditLog(
            username=username,
            action=f"Operated Switch {switch_id}",
            details=json.dumps({"command": payload.command})
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database audit failed: {e}")

    # 2. Publish Command to MQTT
    topic = f"scada/commands/switch/{switch_id}"
    message = json.dumps({"command": payload.command, "operator": username})
    
    try:
        mqtt_publish.single(topic, payload=message, hostname=settings.MQTT_BROKER, port=1883)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MQTT publish failed: {e}")

    return {"status": "success", "message": f"Command '{payload.command}' sent to {switch_id}"}