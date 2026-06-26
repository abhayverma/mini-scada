export interface MeterData {
  measurement_id: string;
  voltage_v: string;
  current_a: string;
  active_power_kw: string;
  reactive_power_kvar: string;
  power_factor: string;
  frequency_hz: string;
  energized: string;
  fault_current: string;
}

export interface NetworkSnapshot {
  [key: string]: MeterData;
}

export interface Alarm {
  id?: number;
  timestamp: string;
  severity: string;
  message: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}