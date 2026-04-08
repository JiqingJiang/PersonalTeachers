import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const isLoggedIn = ref(!!localStorage.getItem('access_token'))

  async function login(email: string, password: string) {
    const { data } = await authApi.login(email, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    isLoggedIn.value = true
    await fetchMe()
  }

  async function register(email: string, password: string, code: string, nickname?: string) {
    const { data } = await authApi.register(email, password, code, nickname)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    isLoggedIn.value = true
    await fetchMe()
  }

  async function fetchMe() {
    try {
      const { data } = await authApi.getMe()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    isLoggedIn.value = false
  }

  return { user, isLoggedIn, login, register, fetchMe, logout }
})
