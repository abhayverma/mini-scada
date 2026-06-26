from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, text
from app.db.database import Base

class AlarmEvent(Base):
    __tablename__ = "alarms"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=text('NOW()'))
    severity = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)

class Telemetry(Base):
    __tablename__ = "telemetry"
    time = Column(DateTime(timezone=True), primary_key=True, server_default=text('NOW()'))
    measurement_id = Column(String(50), nullable=False)
    voltage_v = Column(Float)
    current_a = Column(Float)
    active_power_kw = Column(Float)
    reactive_power_kvar = Column(Float)
    power_factor = Column(Float)
    frequency_hz = Column(Float)
    energized = Column(Boolean)
    fault_current = Column(Boolean)