import json
import time
import threading
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
import redis
from pydantic import ValidationError

from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session
from app.models.telemetry import Telemetry, AlarmEvent
from app.core.config import settings
from app.schemas.pydantic import TelemetryData

# --- Use Pydantic Settings ---
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

telemetry_buffer = []
alarm_buffer = []
buffer_lock = threading.Lock()

def check_for_alarms(data: TelemetryData):
    """Business logic for detecting threshold violations."""
    if data.energized and data.voltage_v < 7500:
        msg = f"Under-voltage detected on {data.measurement_id}: {data.voltage_v}V"
        alarm_buffer.append(("critical", msg))
        redis_client.publish("scada_alarms", json.dumps({"severity": "critical", "message": msg}))

def flush_to_db():
    """Background thread to bulk-insert telemetry and alarms using SQLAlchemy."""
    engine = create_engine(settings.DATABASE_URL)
    
    while True:
        time.sleep(5)
        with buffer_lock:
            current_telemetry = telemetry_buffer[:]
            current_alarms = alarm_buffer[:]
            telemetry_buffer.clear()
            alarm_buffer.clear()

        if current_telemetry or current_alarms:
            try:
                with Session(engine) as session:
                    if current_telemetry:
                        for t in current_telemetry:
                            new_tel = Telemetry(
                                time=t[0], measurement_id=t[1], voltage_v=t[2],
                                current_a=t[3], active_power_kw=t[4], reactive_power_kvar=t[5],
                                power_factor=t[6], frequency_hz=t[7], energized=t[8], fault_current=t[9]
                            )
                            session.add(new_tel)
                    if current_alarms:
                        for a in current_alarms:
                            new_alm = AlarmEvent(severity=a[0], message=a[1])
                            session.add(new_alm)
                    session.commit()
            except Exception as e:
                print(f"DB Flush Error: {e}", flush=True)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Worker connected to MQTT Broker")
        client.subscribe("scada/telemetry/#")
        client.subscribe("scada/alarm/fault")
    else:
        print(f"MQTT Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        raw_payload = json.loads(msg.payload.decode())
        
        # 1. Telemetry Data
        if msg.topic.startswith("scada/telemetry/"):
            valid_data = TelemetryData(**raw_payload)
            
            # Cache real-time state in Redis
            redis_mapping = {k: str(v) for k, v in valid_data.model_dump().items()}
            redis_client.hset(f"meter:{valid_data.measurement_id}", mapping=redis_mapping)
            
            with buffer_lock:
                check_for_alarms(valid_data)
                
                record = (
                    datetime.now(timezone.utc),
                    valid_data.measurement_id,
                    valid_data.voltage_v,
                    valid_data.current_a,
                    valid_data.active_power_kw,
                    valid_data.reactive_power_kvar,
                    valid_data.power_factor,
                    valid_data.frequency_hz,
                    valid_data.energized,
                    valid_data.fault_current
                )
                telemetry_buffer.append(record)
                
        # 2. Simulator Faults
        elif msg.topic == "scada/alarm/fault":
            if raw_payload.get("event") == "fault_injected":
                severity = raw_payload.get("severity", "critical").lower()
                description = raw_payload.get("description", "Unknown system fault detected")
                
                with buffer_lock:
                    alarm_buffer.append((severity, description))
                    redis_client.publish("scada_alarms", json.dumps({"severity": severity, "message": description}))

    except ValidationError as e:
        print(f"❌ Schema Mismatch for {msg.topic}", flush=True)
        # Extract the specific field errors and force them to print
        print(json.dumps(e.errors(), indent=2), flush=True)
    except json.JSONDecodeError:
        print("⚠️ Received malformed JSON.", flush=True)
    except Exception as e:
        print(f"⚠️ Worker Error: {str(e)}", flush=True)

# Start DB flush thread
threading.Thread(target=flush_to_db, daemon=True).start()

# Start MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        # Use settings.MQTT_BROKER
        client.connect(settings.MQTT_BROKER, 1883, 60)
        client.loop_forever()
    except Exception as e:
        print(f"MQTT connection failed, retrying in 5s... ({e})")
        time.sleep(5)