// src/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

// Automatically attach the JWT token to every request
api.interceptors.request.use((config: any) => {
  const token = localStorage.getItem('scada_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api