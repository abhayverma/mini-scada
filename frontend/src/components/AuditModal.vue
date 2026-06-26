<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>🛡️ System Audit Logs</h2>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      
      <div class="table-container">
        <table v-if="logs.length > 0">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Operator</th>
              <th>Action</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td class="mono">{{ formatTime(log.timestamp) }}</td>
              <td class="bold">{{ log.username }}</td>
              <td>{{ log.action }}</td>
              <td class="mono detail-cell">{{ log.details }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state">No audit logs found.</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'

defineEmits(['close'])

const logs = ref<any[]>([])

const fetchLogs = async () => {
  try {
    const response = await api.get('/api/admin/audit-logs')
    logs.value = response.data.data
  } catch (error) {
    console.error("Failed to fetch audit logs", error)
  }
}

const formatTime = (isoString: string) => {
  return new Date(isoString).toLocaleString()
}

onMounted(() => fetchLogs())
</script>

<style scoped>
    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(3px); }
    .modal-content { background: white; border-radius: 8px; width: 90%; max-width: 800px; max-height: 80vh; display: flex; flex-direction: column; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
    .modal-header { padding: 1.5rem; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
    .modal-header h2 { margin: 0; color: #1f2937; }
    .close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #6b7280; }
    .table-container { padding: 1.5rem; overflow-y: auto; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th { background: #f9fafb; padding: 0.75rem; border-bottom: 2px solid #e5e7eb; color: #374151; }
    td { padding: 0.75rem; border-bottom: 1px solid #e5e7eb; font-size: 0.9rem; }
    .mono { font-family: monospace; color: #4b5563; }
    .bold { font-weight: bold; color: #111827; }
    .detail-cell { font-size: 0.8rem; background: #f3f4f6; border-radius: 4px; padding: 0.25rem; display: inline-block; margin-top: 0.25rem;}
    .empty-state { text-align: center; color: #6b7280; padding: 2rem; font-style: italic; }
</style>