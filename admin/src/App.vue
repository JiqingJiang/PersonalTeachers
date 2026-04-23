<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isLoginPage = () => route.name === 'login'

const navItems = [
  { path: '/dashboard', label: '数据看板', icon: '📊' },
  { path: '/users', label: '用户管理', icon: '👥' },
  { path: '/failed-logs', label: '失败记录', icon: '⚠️' },
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
    <div class="flex min-h-screen bg-surface font-body">
      <!-- Sidebar -->
      <aside class="hidden md:flex w-56 flex-col bg-sidebar">
        <!-- Brand decoration line -->
        <div class="h-1 bg-gradient-to-r from-brand to-brand-dark"></div>
        <!-- Logo -->
        <div class="px-5 py-5 border-b border-white/5">
          <h1 class="font-display text-lg text-ink-on-dark tracking-wide">PersonalTeachers</h1>
          <p class="mt-0.5 text-xs text-ink-on-dark-muted">管理后台</p>
        </div>
        <!-- Navigation -->
        <nav class="flex-1 px-3 py-4 space-y-1">
          <router-link
            v-for="item in navItems" :key="item.path" :to="item.path"
            class="relative flex items-center gap-3 px-3 py-2.5 rounded-[var(--radius-md)] text-sm transition-all duration-200"
            :class="route.path === item.path
              ? 'bg-sidebar-light text-brand font-medium'
              : 'text-ink-on-dark-muted hover:bg-sidebar-hover hover:text-ink-on-dark'"
          >
            <!-- Active indicator bar -->
            <span v-if="route.path === item.path" class="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-brand rounded-full"></span>
            <!-- Dashboard icon -->
            <svg v-if="item.path === '/dashboard'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-[18px] h-[18px] shrink-0">
              <rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>
            </svg>
            <!-- Users icon -->
            <svg v-else-if="item.path === '/users'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-[18px] h-[18px] shrink-0">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            <!-- Failed logs icon -->
            <svg v-else-if="item.path === '/failed-logs'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-[18px] h-[18px] shrink-0">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <!-- AI models icon -->
            <svg v-else-if="item.path === '/ai-models'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-[18px] h-[18px] shrink-0">
              <rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6"/><path d="M9 13h4"/><circle cx="9" cy="9" r="0.5" fill="currentColor"/><circle cx="9" cy="13" r="0.5" fill="currentColor"/>
            </svg>
            <!-- Email pool icon -->
            <svg v-else-if="item.path === '/email-pool'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-[18px] h-[18px] shrink-0">
              <rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 7L2 7"/>
            </svg>
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
        <!-- Logout -->
        <div class="px-5 py-4 border-t border-white/5">
          <button @click="logout" class="flex items-center gap-2 text-sm text-ink-on-dark-muted hover:text-brand transition-colors duration-200">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-[18px] h-[18px]">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            退出登录
          </button>
        </div>
      </aside>

      <!-- Main content -->
      <main class="flex-1 overflow-auto">
        <!-- Mobile header -->
        <header class="md:hidden flex items-center gap-2 px-4 py-3 bg-sidebar border-b border-white/5">
          <h1 class="font-display text-sm text-ink-on-dark mr-2">PersonalTeachers</h1>
          <div class="flex-1 flex items-center justify-end gap-1">
            <router-link v-for="item in navItems" :key="item.path" :to="item.path"
              class="p-2 rounded-[var(--radius-sm)] transition-colors duration-200"
              :class="route.path === item.path ? 'bg-sidebar-light text-brand' : 'text-ink-on-dark-muted hover:text-ink-on-dark'"
              :title="item.label"
            >
              <!-- Mobile SVG icons (same as sidebar) -->
              <svg v-if="item.path === '/dashboard'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                <rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>
              </svg>
              <svg v-else-if="item.path === '/users'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
              </svg>
              <svg v-else-if="item.path === '/failed-logs'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <svg v-else-if="item.path === '/ai-models'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                <rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h6"/><path d="M9 13h4"/>
              </svg>
              <svg v-else-if="item.path === '/email-pool'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4">
                <rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 7L2 7"/>
              </svg>
            </router-link>
          </div>
        </header>
        <!-- Page content -->
        <div class="p-5 md:p-8 max-w-5xl">
          <router-view />
        </div>
      </main>
    </div>
  </template>
</template>
