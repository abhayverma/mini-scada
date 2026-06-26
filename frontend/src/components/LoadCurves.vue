<template>
  <div class="charts-container">
    <div class="controls">
      <label for="meter-select">Select Meter:</label>
      <select id="meter-select" v-model="selectedMeter" @change="fetchHistory">
        <option v-for="i in 10" :key="i" :value="`MED-${String(i).padStart(2, '0')}`">
          MED-{{ String(i).padStart(2, '0') }}
        </option>
      </select>
      <button @click="fetchHistory" class="refresh-btn">🔄 Refresh</button>
    </div>

    <div class="chart-wrapper">
      <Line v-if="!isLoading && chartData.labels.length > 0" :data="chartData" :options="chartOptions" />
      <div v-else-if="isLoading" class="loading">Loading historical data...</div>
      <div v-else class="no-data">Not enough data to draw curve yet.</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '../services/api'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Line } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const selectedMeter = ref('MED-01')
const isLoading = ref(false)

const chartData = ref({
  labels: [] as string[],
  datasets: [
    {
      label: 'Active Power (kW)',
      backgroundColor: 'rgba(16, 185, 129, 0.2)',
      borderColor: '#10b981',
      borderWidth: 2,
      pointRadius: 0,
      fill: true,
      data: [] as number[],
      tension: 0.4 // Smooth curves
    }
  ]
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 0 }, // Disable animation for snappy updates
  scales: {
    y: { title: { display: true, text: 'Kilowatts (kW)' } },
    x: { 
      ticks: { maxTicksLimit: 10 },
      grid: { display: false }
    }
  },
  plugins: { legend: { display: false } }
}

const fetchHistory = async () => {
  isLoading.value = true
  try {
    // Clean, relative API call. Interceptor handles the auth.
    const response = await api.get(`/api/telemetry/history/${selectedMeter.value}?minutes=10`)
    const rawData = response.data
    
    chartData.value.labels = rawData.map((row: any) => {
      const d = new Date(row.time)
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    })
    chartData.value.datasets[0].data = rawData.map((row: any) => Number.parseFloat(row.active_power_kw))
  } catch (error) {
    console.error("Failed to fetch history", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchHistory()
})

// Auto-refresh the chart every 10 seconds
setInterval(fetchHistory, 10000)
</script>

<style scoped>
    .charts-container { 
    display: flex; 
    flex-direction: column; 
    gap: 1rem; 
    }

    .controls { 
    display: flex; 
    align-items: center; 
    gap: 0.5rem; 
    }

    select { 
    padding: 0.25rem 0.5rem; 
    border-radius: 4px; 
    border: 1px solid #d1d5db; 
    }

    .refresh-btn { 
    background: #f3f4f6; 
    border: 1px solid #d1d5db; 
    padding: 0.25rem 0.5rem; 
    border-radius: 4px; 
    cursor: pointer; 
    }

    .refresh-btn:hover { 
    background: #e5e7eb; 
    }

    .chart-wrapper { 
    position: relative; 
    width: 100%; 
    height: 250px;
    }

    .loading, .no-data { 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    height: 250px; 
    color: #6b7280; 
    font-style: italic; 
    }
</style>