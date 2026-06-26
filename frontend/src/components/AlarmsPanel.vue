<template>
  <div class="alarms-container">
    <div v-if="alarms.length === 0" class="no-alarms">
      <span class="status-icon">✅</span> System Stable. No active alarms.
    </div>
    
    <div class="alarms-list" v-else>
      <div 
        v-for="(alarm, index) in alarms" 
        :key="index" 
        class="alarm-card"
        :class="'severity-' + alarm.severity.toLowerCase()"
      >
        <div class="alarm-header">
          <span class="alarm-badge">{{ alarm.severity.toUpperCase() }}</span>
          <span class="alarm-time">{{ formatTime(alarm.timestamp) }}</span>
        </div>
        <div class="alarm-body">
          {{ alarm.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Alarm } from '../types'

defineProps<{
  alarms: Alarm[]
}>()

const formatTime = (isoString: string) => {
  if (!isoString) return 'Unknown Time';
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
</script>

<style scoped>
    .alarms-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    }

    .no-alarms {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    height: 100px;
    background: #f0fdf4;
    color: #166534;
    border-radius: 6px;
    font-weight: bold;
    }

    .alarms-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    max-height: 400px;
    overflow-y: auto;
    padding-right: 0.5rem;
    }

    /* Custom Scrollbar for the feed */
    .alarms-list::-webkit-scrollbar { width: 6px; }
    .alarms-list::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
    .alarms-list::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }

    .alarm-card {
    padding: 0.75rem;
    border-radius: 6px;
    border-left: 4px solid transparent;
    background: #f8fafc;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
    }

    .alarm-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
    }

    .alarm-time {
    font-size: 0.75rem;
    color: #64748b;
    font-family: monospace;
    }

    .alarm-badge {
    font-size: 0.7rem;
    font-weight: bold;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    color: white;
    }

    .alarm-body {
    font-size: 0.85rem;
    color: #334155;
    line-height: 1.4;
    }

    /* Severity Color Coding */
    .severity-critical { border-left-color: #ef4444; background: #fef2f2; }
    .severity-critical .alarm-badge { background: #ef4444; }

    .severity-major { border-left-color: #f97316; background: #fff7ed; }
    .severity-major .alarm-badge { background: #f97316; }

    .severity-warning { border-left-color: #f59e0b; background: #fffbeb; }
    .severity-warning .alarm-badge { background: #f59e0b; }

    .severity-info { border-left-color: #3b82f6; background: #eff6ff; }
    .severity-info .alarm-badge { background: #3b82f6; }
</style>