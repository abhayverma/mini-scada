import { ref, reactive } from 'vue'
import api from '../services/api'
import type { NetworkSnapshot, Alarm } from '../types'

export function useScada() {
  const token = ref<string | null>(localStorage.getItem('scada_token') || null)
  const userRole = ref<string | null>(null)
  const networkState = reactive<NetworkSnapshot>({})
  const alarms = ref<Alarm[]>([])
  let pollingInterval: number | null = null

  const updateRoleFromToken = () => {
    if (token.value) {
      try {
        // A JWT is 3 parts separated by dots. The middle part is the payload.
        const payload = JSON.parse(atob(token.value.split('.')[1]))
        userRole.value = payload.role
      } catch (e) {
        console.error("Failed to decode token", e)
        userRole.value = null
      }
    }
  }

  updateRoleFromToken()

  const logout = (): void => {
    token.value = null
    userRole.value = null
    localStorage.removeItem('scada_token')
    stopPolling()
    // Safely clear the reactive object
    for (const key in networkState) {
      delete networkState[key]
    }
  }

  const fetchSnapshot = async (): Promise<void> => {
    if (!token.value) return
    try {
      const response = await api.get<{ status: string; data: NetworkSnapshot }>('/api/network/snapshot')
      // Object.assign safely updates the proxy without losing reactive references
      Object.assign(networkState, response.data.data)
    } catch (error: any) {
      if (error.response?.status === 401) logout()
    }
  }

  const fetchAlarms = async (): Promise<void> => {
    if (!token.value) return
    try {
      const response = await api.get<Alarm[]>('/api/alarms')
      alarms.value = response.data
    } catch (error) {
      console.error("Failed to fetch alarms", error)
    }
  }

  const startPolling = (): void => {
    fetchSnapshot()
    fetchAlarms()
    // @ts-ignore
    pollingInterval = setInterval(() => {
      fetchSnapshot()
      fetchAlarms()
    }, 1000)
  }

  const stopPolling = (): void => {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }

  return {
    token,
    userRole,
    networkState,
    alarms,
    startPolling,
    stopPolling,
    logout
  }
}