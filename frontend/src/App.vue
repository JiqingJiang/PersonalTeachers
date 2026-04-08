<script setup lang="ts">
import { useAuthStore } from './stores/auth'
import { useRoute } from 'vue-router'

const auth = useAuthStore()
const route = useRoute()

// 尝试恢复登录状态
if (auth.isLoggedIn && !auth.user) {
  auth.fetchMe()
}

const navItems = [
  { path: '/', label: '仪表盘', icon: '📊' },
  { path: '/keywords', label: '关键词', icon: '🔑' },
  { path: '/mentors', label: '导师', icon: '🧑‍🏫' },
  { path: '/settings', label: '设置', icon: '⚙️' },
  { path: '/history', label: '历史', icon: '📖' },
]

const isAuthPage = () => ['login', 'register', 'reset-password'].includes(route.name as string)
</script>

<template>
  <!-- 认证页面（无侧边栏） -->
  <template v-if="isAuthPage()">
    <router-view />
  </template>

  <!-- 主布局（侧边栏 + 内容） -->
  <template v-else>
    <div class="flex min-h-screen bg-gray-50">
      <!-- 侧边栏 -->
      <aside class="hidden md:flex w-60 flex-col border-r border-gray-200 bg-white">
        <div class="p-6 border-b border-gray-200">
          <h1 class="text-lg font-bold text-gray-800">📚 PersonalTeachers</h1>
          <p class="text-xs text-gray-400 mt-1">每日人生智慧</p>
        </div>
        <nav class="flex-1 p-4 space-y-1">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors"
            :class="route.path === item.path
              ? 'bg-indigo-50 text-indigo-700 font-medium'
              : 'text-gray-600 hover:bg-gray-50'"
          >
            <span>{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
        <div class="p-4 border-t border-gray-200">
          <div class="text-sm text-gray-600 truncate">{{ auth.user?.email }}</div>
          <button
            @click="auth.logout(); $router.push('/login')"
            class="text-xs text-red-500 hover:text-red-700 mt-1"
          >
            退出登录
          </button>
        </div>
      </aside>

      <!-- 主内容 -->
      <main class="flex-1 overflow-auto">
        <!-- 移动端顶栏 -->
        <header class="md:hidden flex items-center justify-between p-4 bg-white border-b border-gray-200">
          <h1 class="text-sm font-bold text-gray-800">📚 PersonalTeachers</h1>
          <div class="flex gap-2">
            <router-link
              v-for="item in navItems.slice(0, 4)"
              :key="item.path"
              :to="item.path"
              class="px-2 py-1 text-xs rounded"
              :class="route.path === item.path ? 'bg-indigo-100 text-indigo-700' : 'text-gray-500'"
            >
              {{ item.icon }}
            </router-link>
          </div>
        </header>
        <div class="p-4 md:p-8 max-w-5xl">
          <router-view />
        </div>
      </main>
    </div>
  </template>
</template>
