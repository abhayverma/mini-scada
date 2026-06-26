<template>
  <div class="dashboard-wrapper">
    <header class="header">
      <h1>⚡ Distribution Network Mini-SCADA</h1>
      <div class="user-info">
        System Active ({{ userRole }}) | 
        
        <button v-if="userRole === 'admin'" @click="showAuditModal = true" class="admin-btn">
          🛡️ View Audit Logs
        </button>
        
        <button @click="handleLogout" class="logout-btn">Logout</button>
      </div>
    </header>

    <AuditModal v-if="showAuditModal" @close="showAuditModal = false" />

    <main class="dashboard-grid">
      <div class="panel sld-panel">
        <h2>Network Overview</h2>
        <SLD :networkState="networkState" />
      </div>
      
      <div class="sidebar">
        <div class="panel alarms-panel">
          <h2>🔔 Active Alarms</h2>
          <AlarmsPanel :alarms="alarms" />
        </div>
        
        <div class="panel charts-panel">
          <h2>📈 Load Curves</h2>
          <LoadCurves />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useScada } from '../composables/useScada'
import SLD from '../components/SLD.vue'
import AlarmsPanel from '../components/AlarmsPanel.vue'
import LoadCurves from '../components/LoadCurves.vue'
import AuditModal from '../components/AuditModal.vue'

const emit = defineEmits(['logout'])

// Pull in the global state and engine
const { networkState, alarms, startPolling, stopPolling, logout, userRole } = useScada()

const showAuditModal = ref(false)

const handleLogout = () => {
  logout()
  emit('logout') // Tell parent to show login screen
}

onMounted(() => {
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
    .dashboard-wrapper { display: flex; flex-direction: column; height: 100vh; background: #f3f4f6; }
    .header { background: #1f2937; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
    .header h1 { margin: 0; font-size: 1.5rem; }
    .logout-btn { background: transparent; border: 1px solid white; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; cursor: pointer; margin-left: 1rem; }
    .logout-btn:hover { background: rgba(255,255,255,0.1); }
    .dashboard-grid { display: flex; flex: 1; padding: 1.5rem; gap: 1.5rem; overflow: hidden; }
    .panel { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; }
    .panel h2 { margin-top: 0; margin-bottom: 1rem; font-size: 1.25rem; color: #111827; }
    .sld-panel { flex: 2; overflow-y: auto; }
    .sidebar { flex: 1; display: flex; flex-direction: column; gap: 1.5rem; overflow: hidden; }
    .alarms-panel { flex: 1; overflow-y: hidden; }
    .charts-panel { height: 350px; }
    .admin-btn { background: #374151; border: 1px solid #4b5563; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; cursor: pointer; margin-left: 1rem; font-weight: bold; }
    .admin-btn:hover { background: #4b5563; }
</style>