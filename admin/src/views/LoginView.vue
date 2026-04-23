<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { adminAuth } from '../api'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await adminAuth.login(email.value, password.value)
    localStorage.setItem('admin_token', data.access_token)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4 relative overflow-hidden"
       style="background: linear-gradient(160deg, var(--color-sidebar) 0%, #0F0F1E 50%, #12121F 100%);">
    <!-- Decorative gradient orb -->
    <div class="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full opacity-15"
         style="background: radial-gradient(circle, var(--color-brand) 0%, transparent 70%);"></div>
    <div class="absolute -bottom-32 -left-32 w-[400px] h-[400px] rounded-full opacity-10"
         style="background: radial-gradient(circle, var(--color-brand-dark) 0%, transparent 70%);"></div>
    <!-- Subtle noise texture overlay -->
    <div class="absolute inset-0 opacity-[0.03]"
         style="background-image: radial-gradient(circle at 1px 1px, white 1px, transparent 0); background-size: 24px 24px;"></div>

    <div class="w-full max-w-sm relative z-10">
      <!-- Title -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-[var(--radius-lg)] bg-white/5 border border-white/10 mb-4">
          <svg viewBox="0 0 24 24" fill="none" stroke="var(--color-brand)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
        </div>
        <h1 class="font-display text-2xl text-ink-on-dark tracking-wide">PersonalTeachers</h1>
        <p class="text-sm text-ink-on-dark-muted mt-1">管理后台</p>
      </div>

      <!-- Glassmorphism card -->
      <div class="bg-white/[0.07] backdrop-blur-xl rounded-[var(--radius-xl)] border border-white/[0.08] p-6 shadow-elevated">
        <!-- Error message -->
        <div v-if="error" class="mb-4 p-3 bg-danger/20 text-white/90 text-sm rounded-[var(--radius-md)] flex items-center gap-2">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 shrink-0">
            <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <span>{{ error }}</span>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Email -->
          <div>
            <label class="block text-sm text-ink-on-dark-muted mb-1.5">管理员邮箱</label>
            <div class="relative">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-on-dark-muted">
                <rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 7L2 7"/>
              </svg>
              <input v-model="email" type="email" required placeholder="admin@example.com"
                class="w-full pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-[var(--radius-md)] text-sm text-ink-on-dark placeholder:text-ink-on-dark-muted focus:outline-none focus:border-brand/50 focus:ring-1 focus:ring-brand/30 transition-all duration-200" />
            </div>
          </div>
          <!-- Password -->
          <div>
            <label class="block text-sm text-ink-on-dark-muted mb-1.5">密码</label>
            <div class="relative">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-on-dark-muted">
                <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input v-model="password" type="password" required placeholder="输入密码"
                class="w-full pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-[var(--radius-md)] text-sm text-ink-on-dark placeholder:text-ink-on-dark-muted focus:outline-none focus:border-brand/50 focus:ring-1 focus:ring-brand/30 transition-all duration-200" />
            </div>
          </div>
          <!-- Submit -->
          <button type="submit" :disabled="loading"
            class="w-full py-2.5 bg-gradient-to-r from-brand to-brand-dark text-white text-sm font-semibold rounded-[var(--radius-md)] hover:shadow-amber disabled:opacity-50 disabled:hover:shadow-none transition-all duration-200 cursor-pointer">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="text-center text-xs text-ink-on-dark-muted/50 mt-6">PersonalTeachers Admin Panel</p>
    </div>
  </div>
</template>
