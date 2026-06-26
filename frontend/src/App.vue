<template>
  <LoginView v-if="!isAuthenticated" @authenticated="isAuthenticated = true" />
  <DashboardView v-else @logout="isAuthenticated = false" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'

// Determine initial state based on token existence
const isAuthenticated = ref(!!localStorage.getItem('scada_token'))
</script>

<style>
/* Global reset */
body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}
</style>