<template>
  <div class="login-wrapper">
    <div class="login-card">
      <h2>SCADA Authentication</h2>
      <p class="subtitle">Authorized personnel only</p>
      
      <div class="form-group">
        <input v-model="credentials.username" placeholder="Username" class="input-field" />
      </div>
      <div class="form-group">
        <input v-model="credentials.password" type="password" placeholder="Password" class="input-field" @keyup.enter="handleLogin" />
      </div>
      
      <button @click="handleLogin" class="login-btn" :disabled="isLoading">
        {{ isLoading ? 'Authenticating...' : 'Secure Login' }}
      </button>
      <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import api from '../services/api'
import type { AuthResponse } from '../types'

const emit = defineEmits(['authenticated'])

const isLoading = ref(false)
const errorMsg = ref('')

const credentials = reactive({
  username: 'test.supervisor',
  password: 'admin123'
})

const handleLogin = async () => {
  isLoading.value = true
  errorMsg.value = ''
  
  try {
    const params = new URLSearchParams()
    params.append('username', credentials.username)
    params.append('password', credentials.password)
    
    const response = await api.post<AuthResponse>('/token', params)
    localStorage.setItem('scada_token', response.data.access_token)
    emit('authenticated') // Tell the parent to swap views
  } catch (error) {
    errorMsg.value = 'Invalid credentials. Access denied.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
    .login-wrapper { display: flex; align-items: center; justify-content: center; height: 100vh; background: #f3f4f6; }
    .login-card { background: white; padding: 2.5rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
    .subtitle { color: #6b7280; margin-bottom: 2rem; font-size: 0.9rem; }
    .form-group { margin-bottom: 1rem; }
    .input-field { width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 4px; box-sizing: border-box; }
    .login-btn { width: 100%; padding: 0.75rem; background: #1f2937; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
    .login-btn:hover:not(:disabled) { background: #374151; }
    .login-btn:disabled { opacity: 0.7; cursor: not-allowed; }
    .error-text { color: #ef4444; margin-top: 1rem; font-size: 0.85rem; }
</style>