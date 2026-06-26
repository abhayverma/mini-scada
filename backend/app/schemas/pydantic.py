from pydantic import BaseModel, Field
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    DISPATCHER = "dispatcher"
    OPERATOR = "operator"

class Token(BaseModel):
    access_token: str
    token_type: str

class SwitchCommand(BaseModel):
    command: str  # "open" or "close"

class TelemetryData(BaseModel):
    measurement_id: str
    voltage_v: float = Field(..., ge=0)  # Voltage cannot be negative
    current_a: float = Field(..., ge=0)
    active_power_kw: float
    reactive_power_kvar: float
    power_factor: float = Field(..., ge=-1.0, le=1.0)
    frequency_hz: float = Field(..., ge=0)
    energized: bool = True
    fault_current: bool = False

class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: UserRole = Field(..., description="The designated access role for the user")
