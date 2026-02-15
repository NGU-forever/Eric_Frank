import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import type { User, LoginRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.isSuperuser || false)

  async function login(credentials: LoginRequest) {
    const response = await api.post('/api/v1/auth/login/json', credentials)
    const data = response.data

    token.value = data.access_token
    refreshToken.value = data.refresh_token

    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)

    await fetchUser()
  }

  async function logout() {
    try {
      await api.post('/api/v1/auth/logout')
    } catch {
      // Ignore logout errors
    } finally {
      token.value = null
      refreshToken.value = null
      user.value = null

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  async function fetchUser() {
    if (!token.value) return

    const response = await api.get('/api/v1/auth/me')
    user.value = response.data
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    const response = await api.post('/api/v1/auth/refresh', {
      token: refreshToken.value,
    })

    token.value = response.data.access_token
    refreshToken.value = response.data.refresh_token

    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token)
  }

  function initialize() {
    if (token.value) {
      fetchUser()
    }
  }

  return {
    token,
    refreshToken,
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchUser,
    refreshAccessToken,
    initialize,
  }
})
