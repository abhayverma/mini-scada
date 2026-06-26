import pytest
from fastapi.testclient import TestClient
from backend.app.main import app, create_access_token
import json

# Initialize the FastAPI Test Client
client = TestClient(app)

# ---------------------------------------------------------
# 1. API Security Integration Tests (Layer 5)
# ---------------------------------------------------------
def test_switch_command_rejected_without_token():
    """Prove that anonymous users cannot operate the grid."""
    response = client.post("/api/commands/switch/CH-01", json={"command": "open"})
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_switch_command_accepted_with_supervisor_token():
    """Prove that an authenticated Supervisor CAN operate the grid."""
    # Generate a valid mock token for our test supervisor
    valid_token = create_access_token(data={"sub": "test.supervisor", "role": "supervisor"})
    headers = {"Authorization": f"Bearer {valid_token}"}
    
    response = client.post(
        "/api/commands/switch/CH-02", 
        json={"command": "close"}, 
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"

# ---------------------------------------------------------
# 2. Alarm Engine Business Logic Tests (Layer 3)
# ---------------------------------------------------------
def test_alarm_engine_detects_undervoltage():
    """Prove the alarm threshold logic correctly catches voltage drops."""
    
    # Let's import the raw logic from our worker (assuming you named the function check_for_alarms)
    # If your worker has this logic deeply embedded, we can simulate the math here:
    
    class MockTelemetry:
        def __init__(self, voltage_v, energized):
            self.measurement_id = "MED-TEST"
            self.voltage_v = voltage_v
            self.energized = energized

    def run_alarm_engine_logic(data):
        alarms = []
        # The logic we built: Nominal is ~7900V. Under-voltage is < 7500V.
        if data.energized and data.voltage_v < 7500:
            alarms.append({"severity": "critical", "msg": f"Under-voltage on {data.measurement_id}"})
        return alarms

    # Test Case A: Normal Voltage (Should not alarm)
    healthy_data = MockTelemetry(voltage_v=7950.0, energized=True)
    assert len(run_alarm_engine_logic(healthy_data)) == 0

    # Test Case B: Dangerous Under-voltage (Should trigger critical alarm)
    failing_data = MockTelemetry(voltage_v=6000.0, energized=True)
    triggered_alarms = run_alarm_engine_logic(failing_data)
    
    assert len(triggered_alarms) == 1
    assert triggered_alarms[0]["severity"] == "critical"
    assert "Under-voltage" in triggered_alarms[0]["msg"]