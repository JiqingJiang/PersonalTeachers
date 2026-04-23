<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../../api'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const nickname = ref('')
const code = ref('')
const step = ref<'email' | 'verify'>('email')
const loading = ref(false)
const error = ref('')
const countdown = ref(0)
let timer: any = null

async function sendCode() {
  error.value = ''
  loading.value = true
  try {
    await authApi.sendCode(email.value, 'register')
    step.value = 'verify'
    countdown.value = 60
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch (e: any) {
    // 调试模式下后端会返回 code
    const resp = e.response?.data
    if (resp?.code) {
      code.value = resp.code
      step.value = 'verify'
    } else {
      error.value = resp?.detail || '发送验证码失败'
    }
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(email.value, password.value, code.value, nickname.value || undefined)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex relative overflow-hidden bg-gradient-to-br from-sidebar via-[#111122] to-[#0a0a18]">
    <!-- 装饰性光晕 -->
    <div class="absolute top-[-15%] right-[10%] w-[450px] h-[450px] rounded-full bg-brand/5 blur-[120px] pointer-events-none" />
    <div class="absolute bottom-[-10%] left-[-8%] w-[350px] h-[350px] rounded-full bg-brand-dark/5 blur-[100px] pointer-events-none" />

    <!-- 左侧装饰文案 -->
    <div class="hidden lg:flex flex-1 flex-col justify-center items-start pl-16 xl:pl-24 pr-12 relative z-10">
      <div class="max-w-md">
        <div class="flex items-center gap-3 mb-10">
          <span class="text-3xl">📚</span>
          <h1 class="text-2xl font-bold font-display text-ink-on-dark tracking-wide">PersonalTeachers</h1>
        </div>
        <blockquote class="border-l-2 border-brand pl-6">
          <p class="text-xl xl:text-2xl font-display text-ink-on-dark/90 leading-relaxed italic">
            "求知若饥，虚心若愚。"
          </p>
          <footer class="mt-4 text-sm text-ink-on-dark-muted font-body">
            — 史蒂夫·乔布斯
          </footer>
        </blockquote>
        <p class="mt-8 text-sm text-ink-on-dark-muted/70 leading-relaxed max-w-sm">
          加入 PersonalTeachers，开始你的每日智慧之旅。<br />
          让历史上的伟大导师成为你的精神伴侣。
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
          <!-- 步骤指示器 -->
          <div class="flex items-center gap-2 mb-6">
            <div :class="step === 'email' ? 'bg-brand text-ink' : 'bg-brand/30 text-ink-on-dark-muted'" class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold transition-colors">1</div>
            <div :class="step === 'email' ? 'bg-white/10' : 'bg-brand/40'" class="flex-1 h-px transition-colors" />
            <div :class="step === 'verify' ? 'bg-brand text-ink' : 'bg-white/10 text-ink-on-dark-muted'" class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold transition-colors">2</div>
          </div>

          <h2 class="text-lg font-semibold text-ink-on-dark mb-6 font-display">
            {{ step === 'email' ? '创建你的账号' : '验证并完成注册' }}
          </h2>

          <!-- 错误提示 -->
          <div v-if="error" class="mb-5 px-4 py-3 bg-danger/10 border border-danger/20 text-danger text-sm rounded-lg backdrop-blur-sm">
            {{ error }}
          </div>

          <!-- Step 1: 输入邮箱 -->
          <template v-if="step === 'email'">
            <form @submit.prevent="sendCode" class="space-y-5">
              <div>
                <label class="block text-sm text-ink-on-dark-muted mb-2 font-body">邮箱</label>
                <input v-model="email" type="email" required placeholder="your@email.com"
                  class="auth-input w-full bg-white/[0.06] text-ink-on-dark placeholder-ink-on-dark-muted/50 px-4 py-3 rounded-lg text-sm border-b-2 border-white/10 focus:border-brand focus:bg-white/[0.09] transition-all duration-200 outline-none" />
              </div>
              <button type="submit" :disabled="loading"
                class="w-full py-3 bg-gradient-to-r from-brand to-brand-dark text-ink text-sm font-semibold rounded-lg shadow-amber hover:shadow-lg hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer">
                {{ loading ? '发送中...' : '发送验证码' }}
              </button>
            </form>
          </template>

          <!-- Step 2: 输入验证码 + 密码 -->
          <template v-else>
            <form @submit.prevent="handleRegister" class="space-y-5">
              <div>
                <label class="block text-sm text-ink-on-dark-muted mb-2 font-body">邮箱</label>
                <div class="text-sm text-ink-on-dark/70 bg-white/[0.04] px-4 py-2.5 rounded-lg border border-white/[0.06]">{{ email }}</div>
              </div>
              <div>
                <label class="block text-sm text-ink-on-dark-muted mb-2 font-body">验证码</label>
                <div class="flex gap-3">
                  <input v-model="code" type="text" required maxlength="6" placeholder="6位验证码"
                    class="auth-input flex-1 bg-white/[0.06] text-ink-on-dark placeholder-ink-on-dark-muted/50 px-4 py-3 rounded-lg text-sm border-b-2 border-white/10 focus:border-brand focus:bg-white/[0.09] transition-all duration-200 outline-none" />
                  <button type="button" @click="sendCode" :disabled="countdown > 0"
                    class="px-4 py-3 text-xs bg-white/[0.06] text-ink-on-dark-muted border border-white/[0.08] rounded-lg hover:bg-white/[0.1] hover:text-ink-on-dark disabled:opacity-40 disabled:cursor-not-allowed whitespace-nowrap transition-all duration-200 cursor-pointer">
                    {{ countdown > 0 ? `${countdown}s` : '重发' }}
                  </button>
                </div>
              </div>
              <div>
                <label class="block text-sm text-ink-on-dark-muted mb-2 font-body">昵称 <span class="text-ink-on-dark-muted/40">（选填）</span></label>
                <input v-model="nickname" type="text" placeholder="你的昵称"
                  class="auth-input w-full bg-white/[0.06] text-ink-on-dark placeholder-ink-on-dark-muted/50 px-4 py-3 rounded-lg text-sm border-b-2 border-white/10 focus:border-brand focus:bg-white/[0.09] transition-all duration-200 outline-none" />
              </div>
              <div>
                <label class="block text-sm text-ink-on-dark-muted mb-2 font-body">密码</label>
                <input v-model="password" type="password" required placeholder="至少6位"
                  class="auth-input w-full bg-white/[0.06] text-ink-on-dark placeholder-ink-on-dark-muted/50 px-4 py-3 rounded-lg text-sm border-b-2 border-white/10 focus:border-brand focus:bg-white/[0.09] transition-all duration-200 outline-none" />
              </div>
              <button type="submit" :disabled="loading"
                class="w-full py-3 bg-gradient-to-r from-brand to-brand-dark text-ink text-sm font-semibold rounded-lg shadow-amber hover:shadow-lg hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer">
                {{ loading ? '注册中...' : '注册' }}
              </button>
            </form>
          </template>

          <div class="mt-6 text-center text-sm">
            <span class="text-ink-on-dark-muted/60">已有账号？</span>
            <router-link to="/login" class="text-brand-light hover:text-brand transition-colors font-medium">立即登录</router-link>
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
