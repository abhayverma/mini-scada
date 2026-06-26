<template>
  <div class="sld-wrapper">
    
    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>

    <div v-if="modal.show" class="modal-overlay">
      <div class="modal-content">
        <h3>⚠️ Confirm Operation</h3>
        <p>Are you sure you want to <strong>{{ modal.command.toUpperCase() }}</strong> switch <strong>{{ modal.switchId }}</strong>?</p>
        <div class="modal-actions">
          <button class="btn btn-cancel" @click="closeModal">Cancel</button>
          <button class="btn" :class="modal.command === 'open' ? 'btn-open' : 'btn-close'" @click="executeCommand">
            Confirm {{ modal.command.toUpperCase() }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="['dispatcher', 'admin'].includes(userRole)" class="switch-panel">
      <h3>⚡ Switch Operations</h3>
      <p class="subtitle">Dispatcher and admin only. Requires confirmation.</p>
      <div class="switch-grid">
        <div v-for="id in ['CH-01', 'CH-02', 'CH-03', 'CH-04', 'CH-05']" :key="id" class="switch-card">
          <span class="switch-id">{{ id }}</span>
          <div class="btn-group">
            <button class="btn btn-open" @click="requestOperation(id, 'open')">OPEN</button>
            <button class="btn btn-close" @click="requestOperation(id, 'close')">CLOSE</button>
          </div>
        </div>
      </div>
    </div>

    <hr class="divider" />

    <div class="meters-panel">
      <h3>📊 Live Telemetry</h3>
      <div class="meters-grid">
        <div 
          v-for="(meter, id) in networkState" 
          :key="id" 
          class="meter-card"
          :class="{
            'state-fault': meter.fault_current === 'True',
            'state-offline': meter.energized === 'False' || Number(meter.voltage_v) < 10,
            'state-active': meter.energized === 'True' && meter.fault_current === 'False' && Number(meter.voltage_v) >= 10
          }"
        >
          <div class="meter-header">
            <strong>{{ id }}</strong>
            <span class="badge">{{ getStatusLabel(meter) }}</span>
          </div>
          <div class="meter-body">
            <div class="data-row"><span>Voltage:</span> <strong>{{ formatNumber(meter.voltage_v) }} V</strong></div>
            <div class="data-row"><span>Current:</span> <strong>{{ formatNumber(meter.current_a) }} A</strong></div>
            <div class="data-row"><span>Active Pwr:</span> <strong>{{ formatNumber(meter.active_power_kw) }} kW</strong></div>
            <div class="data-row"><span>Power Factor:</span> <strong>{{ formatNumber(meter.power_factor) }}</strong></div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import api from '../services/api'
import type { NetworkSnapshot } from '../types'
import { useScada } from '../composables/useScada'

const { userRole } = useScada()

const props = defineProps<{
  networkState: NetworkSnapshot;
}>()

const toast = reactive({ show: false, message: '', type: 'success' })
const modal = reactive({ show: false, switchId: '', command: '' })

const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
  toast.message = msg
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

const formatNumber = (val: string) => {
  const num = Number.parseFloat(val);
  return Number.isNaN(num) ? '0.00' : num.toFixed(2);
}

const getStatusLabel = (meter: any) => {
  if (meter.fault_current === 'True') return '⚠️ FAULT'
  if (meter.energized === 'False' || Number(meter.voltage_v) < 10) return 'OFFLINE'
  return 'ENERGIZED'
}

const requestOperation = (switchId: string, cmd: string) => {
  modal.switchId = switchId
  modal.command = cmd
  modal.show = true
}

const closeModal = () => {
  modal.show = false
}

const executeCommand = async () => {
  const { switchId, command } = modal
  closeModal() 

  try {
    await api.post(`/api/commands/switch/${switchId}`, { command })
    showToast(`✅ Command sent to ${switchId}`, 'success')
  } catch (error: any) {
    showToast(`❌ Failed: ${error.response?.data?.detail || error.message}`, 'error')
  }
}
</script>

<style scoped>
    .sld-wrapper { display: flex; flex-direction: column; gap: 1.5rem; position: relative; }
    h3 { margin: 0 0 0.5rem 0; color: #1f2937; }
    .subtitle { margin: 0 0 1rem 0; font-size: 0.85rem; color: #6b7280; }
    .divider { border: 0; border-top: 1px solid #e5e7eb; margin: 1rem 0; }

    /* Custom Toast */
    .toast { position: fixed; top: 1rem; right: 1rem; padding: 1rem 1.5rem; border-radius: 8px; color: white; font-weight: bold; z-index: 1000; animation: slideIn 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .toast.success { background: #10b981; }
    .toast.error { background: #ef4444; }
    @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }

    /* Custom Modal */
    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 999; backdrop-filter: blur(2px); }
    .modal-content { background: white; padding: 2rem; border-radius: 8px; width: 350px; box-shadow: 0 10px 15px rgba(0,0,0,0.1); text-align: center; }
    .modal-actions { display: flex; gap: 1rem; margin-top: 1.5rem; }
    .btn-cancel { background: #6b7280; color: white; }

    /* Switch Panel */
    .switch-grid { display: flex; flex-wrap: wrap; gap: 1rem; }
    .switch-card { background: #f9fafb; border: 1px solid #d1d5db; border-radius: 6px; padding: 0.75rem; display: flex; flex-direction: column; align-items: center; gap: 0.5rem; min-width: 120px; }
    .switch-id { font-weight: bold; font-family: monospace; font-size: 1.1rem; }
    .btn-group { display: flex; gap: 0.25rem; width: 100%; }
    .btn { flex: 1; border: none; padding: 0.5rem; font-size: 0.8rem; font-weight: bold; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; color: white; }
    .btn:hover { opacity: 0.8; }
    .btn-open { background: #ef4444; }
    .btn-close { background: #10b981; }

    /* Meters Grid */
    .meters-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
    .meter-card { border-radius: 8px; padding: 1rem; color: white; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .meter-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 0.5rem; }
    .badge { font-size: 0.7rem; font-weight: bold; padding: 0.2rem 0.4rem; border-radius: 4px; background: rgba(0,0,0,0.2); }
    .data-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.25rem; font-family: monospace; }

    /* Dynamic States */
    .state-active { background: #059669; }     /* Green */
    .state-offline { background: #6b7280; }    /* Gray */
    .state-fault { background: #dc2626; animation: pulse 1.5s infinite; } /* Red Pulse */

    @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
    }
</style>