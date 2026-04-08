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
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-800">📚 PersonalTeachers</h1>
        <p class="text-gray-500 text-sm mt-2">创建账号</p>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div v-if="error" class="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg">{{ error }}</div>

        <!-- Step 1: 输入邮箱 -->
        <template v-if="step === 'email'">
          <form @submit.prevent="sendCode" class="space-y-4">
            <div>
              <label class="block text-sm text-gray-600 mb-1">邮箱</label>
              <input v-model="email" type="email" required placeholder="your@email.com"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <button type="submit" :disabled="loading"
              class="w-full py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50">
              {{ loading ? '发送中...' : '发送验证码' }}
            </button>
          </form>
        </template>

        <!-- Step 2: 输入验证码 + 密码 -->
        <template v-else>
          <form @submit.prevent="handleRegister" class="space-y-4">
            <div>
              <label class="block text-sm text-gray-600 mb-1">邮箱</label>
              <div class="text-sm text-gray-800">{{ email }}</div>
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">验证码</label>
              <div class="flex gap-2">
                <input v-model="code" type="text" required maxlength="6" placeholder="6位验证码"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <button type="button" @click="sendCode" :disabled="countdown > 0"
                  class="px-3 py-2 text-xs bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 whitespace-nowrap">
                  {{ countdown > 0 ? `${countdown}s` : '重发' }}
                </button>
              </div>
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">昵称（选填）</label>
              <input v-model="nickname" type="text" placeholder="你的昵称"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">密码</label>
              <input v-model="password" type="password" required placeholder="至少6位"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <button type="submit" :disabled="loading"
              class="w-full py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50">
              {{ loading ? '注册中...' : '注册' }}
            </button>
          </form>
        </template>

        <div class="mt-4 text-center text-sm">
          <router-link to="/login" class="text-indigo-600 hover:underline">已有账号？登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>
