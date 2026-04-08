<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isLoginPage = () => route.name === 'login'

const navItems = [
  { path: '/dashboard', label: '数据看板', icon: '📊' },
  { path: '/users', label: '用户管理', icon: '👥' },
  { path: '/ai-models', label: 'AI 模型', icon: '🤖' },
  { path: '/email-pool', label: '邮箱池', icon: '📧' },
]

function logout() {
  localStorage.removeItem('admin_token')
  router.push('/')
}
</script>

<template>
  <!-- 登录页 -->
  <template v-if="isLoginPage()">
    <router-view />
  </template>

  <!-- 管理后台布局 -->
  <template v-else>
    <div class="flex min-h-screen bg-gray-50">
      <aside class="hidden md:flex w-56 flex-col border-r border-gray-200 bg-white">
        <div class="p-5 border-b border-gray-200">
          <h1 class="text-sm font-bold text-gray-800">📚 PT 管理后台</h1>
        </div>
        <nav class="flex-1 p-3 space-y-1">
          <router-link
            v-for="item in navItems" :key="item.path" :to="item.path"
            class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors"
            :class="route.path === item.path ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-gray-600 hover:bg-gray-50'"
          >
            <span>{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
        <div class="p-4 border-t border-gray-200">
          <button @click="logout" class="text-xs text-red-500 hover:text-red-700">退出登录</button>
        </div>
      </aside>

      <main class="flex-1 overflow-auto">
        <header class="md:hidden flex items-center gap-2 p-3 bg-white border-b border-gray-200">
          <router-link v-for="item in navItems" :key="item.path" :to="item.path"
            class="px-2 py-1 text-xs rounded"
            :class="route.path === item.path ? 'bg-indigo-100 text-indigo-700' : 'text-gray-500'"
          >{{ item.icon }}</router-link>
        </header>
        <div class="p-4 md:p-8 max-w-5xl">
          <router-view />
        </div>
      </main>
    </div>
  </template>
</template>
