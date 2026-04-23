<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex relative overflow-hidden bg-gradient-to-br from-sidebar via-[#111122] to-[#0a0a18]">
    <!-- 装饰性光晕 -->
    <div class="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-brand/5 blur-[120px] pointer-events-none" />
    <div class="absolute bottom-[-15%] right-[-5%] w-[400px] h-[400px] rounded-full bg-brand-dark/5 blur-[100px] pointer-events-none" />

    <!-- 左侧装饰文案 -->
    <div class="hidden lg:flex flex-1 flex-col justify-center items-start pl-16 xl:pl-24 pr-12 relative z-10">
      <div class="max-w-md">
        <div class="flex items-center gap-3 mb-10">
          <span class="text-3xl">📚</span>
          <h1 class="text-2xl font-bold font-display text-ink-on-dark tracking-wide">PersonalTeachers</h1>
        </div>
        <blockquote class="border-l-2 border-brand pl-6">
          <p class="text-xl xl:text-2xl font-display text-ink-on-dark/90 leading-relaxed italic">
            "那些改变人生轨迹的智慧，<br />往往来自你意想不到的人。"
          </p>
        </blockquote>
        <p class="mt-8 text-sm text-ink-on-dark-muted/70 leading-relaxed max-w-sm">
          50 多位跨越时空的 AI 导师——老子、巴菲特、<br />一个工人、未来的你自己等——<br />
          围绕人生许多的主题，每日推送一句专属感悟。
        </p>
      </div>
    </div>

    <!-- 右侧表单区域 -->
    <div class="flex-1 lg:max-w-[520px] flex items-center justify-center px-6 py-12 relative z-10">
      <div class="w-full max-w-sm">
        <!-- 移动端 Logo -->
        <div class="flex items-center gap-2.5 mb-10 lg:hidden">
          <span class="text-2xl">📚</span>
          <h1 class="text-xl font-bold font-display text-ink-on-dark">PersonalTeachers</h1>
        </div>

        <!-- 毛玻璃卡片 -->
        <div class="bg-white/[0.07] backdrop-blur-2xl rounded-xl border border-white/[0.08] p-8 shadow-elevated">
          <h2 class="text-lg font-semibold text-ink-on-dark mb-6 font-display">登录你的账号</h2>

          <!-- 错误提示 -->
          <div v-if="error" class="mb-5 px-4 py-3 bg-danger/10 border border-danger/20 text-danger text-sm rounded-lg backdrop-blur-sm">
            {{ error }}
          </div>

          <form @submit.prevent="handleLogin" class="space-y-5">
            <div>
              <label class="block text-sm text-ink-on-dark-muted mb-2 font-body">邮箱</label>
              <input
                v-model="email"
                type="email"
                required
                placeholder="your@email.com"
                class="auth-input w-full bg-white/[0.06] text-ink-on-dark placeholder-ink-on-dark-muted/50 px-4 py-3 rounded-lg text-sm border-b-2 border-white/10 focus:border-brand focus:bg-white/[0.09] transition-all duration-200 outline-none"
              />
            </div>
            <div>
              <label class="block text-sm text-ink-on-dark-muted mb-2 font-body">密码</label>
              <input
                v-model="password"
                type="password"
                required
                placeholder="输入密码"
                class="auth-input w-full bg-white/[0.06] text-ink-on-dark placeholder-ink-on-dark-muted/50 px-4 py-3 rounded-lg text-sm border-b-2 border-white/10 focus:border-brand focus:bg-white/[0.09] transition-all duration-200 outline-none"
              />
            </div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full py-3 bg-gradient-to-r from-brand to-brand-dark text-ink text-sm font-semibold rounded-lg shadow-amber hover:shadow-lg hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
            >
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </form>

          <div class="mt-6 text-center text-sm space-y-2">
            <router-link to="/reset-password" class="text-brand-light hover:text-brand transition-colors">忘记密码？</router-link>
            <p class="text-ink-on-dark-muted/60">
              还没有账号？
              <router-link to="/register" class="text-brand-light hover:text-brand transition-colors font-medium">立即注册</router-link>
            </p>
          </div>
        </div>

        <!-- 底部版权 -->
        <p class="mt-8 text-center text-xs text-ink-on-dark-muted/40">
          PersonalTeachers &middot; 每日人生智慧推送
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-input {
  border-radius: var(--radius-md);
}

.auth-input:-webkit-autofill,
.auth-input:-webkit-autofill:hover,
.auth-input:-webkit-autofill:focus {
  -webkit-text-fill-color: var(--color-ink-on-dark);
  -webkit-box-shadow: 0 0 0 1000px rgba(255, 255, 255, 0.06) inset;
  transition: background-color 5000s ease-in-out 0s;
}
</style>
