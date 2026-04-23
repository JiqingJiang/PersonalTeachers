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
  { path: '/dashboard', label: '仪表盘', icon: 'chart' },
  { path: '/keywords', label: '关键词', icon: 'key' },
  { path: '/mentors', label: '导师', icon: 'mentor' },
  { path: '/settings', label: '设置', icon: 'settings' },
  { path: '/history', label: '历史', icon: 'history' },
]

const isFullPage = () => ['landing', 'login', 'register', 'reset-password'].includes(route.name as string)
</script>

<template>
  <!-- 全屏页面（Landing / 认证页面，无侧边栏） -->
  <template v-if="isFullPage()">
    <router-view />
  </template>

  <!-- 主布局（侧边栏 + 内容） -->
  <template v-else>
    <div class="flex min-h-screen bg-surface">
      <!-- 侧边栏 -->
      <aside class="hidden md:flex w-[260px] flex-col bg-sidebar text-ink-on-dark relative">
        <!-- 顶部装饰线 -->
        <div class="h-[2px] bg-gradient-to-r from-brand via-brand-dark to-transparent"></div>

        <!-- Logo 区域 -->
        <div class="px-6 py-6">
          <h1 class="text-lg font-bold text-ink-on-dark" style="font-family: var(--font-display)">
            PersonalTeachers
          </h1>
          <p class="text-xs text-ink-on-dark-muted mt-1 tracking-wide">每日人生智慧推送</p>
        </div>

        <!-- 导航 -->
        <nav class="flex-1 px-3 space-y-0.5">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-3 py-2.5 rounded-[var(--radius-md)] text-sm transition-all duration-200 relative group"
            :class="route.path === item.path
              ? 'bg-sidebar-light text-brand font-medium'
              : 'text-ink-on-dark-muted hover:bg-sidebar-hover hover:text-ink-on-dark'"
          >
            <!-- 活跃指示条 -->
            <div
              v-if="route.path === item.path"
              class="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-4 bg-brand rounded-r-full"
            ></div>
            <!-- 图标 -->
            <svg v-if="item.icon === 'chart'" class="w-[18px] h-[18px] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="7" width="4" height="14" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/></svg>
            <svg v-else-if="item.icon === 'key'" class="w-[18px] h-[18px] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.778-7.778zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
            <svg v-else-if="item.icon === 'mentor'" class="w-[18px] h-[18px] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
            <svg v-else-if="item.icon === 'settings'" class="w-[18px] h-[18px] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
            <svg v-else-if="item.icon === 'history'" class="w-[18px] h-[18px] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
            <span>{{ item.label }}</span>
          </router-link>
        </nav>

        <!-- 用户信息 -->
        <div class="px-4 py-4 border-t border-white/[0.06]">
          <div class="text-sm text-ink-on-dark truncate">{{ auth.user?.email || auth.user?.nickname || '未登录' }}</div>
          <button
            @click="auth.logout(); $router.push('/login')"
            class="text-xs text-ink-on-dark-muted hover:text-brand transition-colors mt-1"
          >
            退出登录
          </button>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="flex-1 overflow-auto min-w-0">
        <!-- 移动端顶栏 -->
        <header class="md:hidden sticky top-0 z-30 flex items-center justify-between px-4 py-3 bg-sidebar text-ink-on-dark">
          <h1 class="text-sm font-bold" style="font-family: var(--font-display)">PersonalTeachers</h1>
          <div class="flex gap-1">
            <router-link
              v-for="item in navItems.slice(0, 4)"
              :key="item.path"
              :to="item.path"
              class="px-2.5 py-1.5 text-xs rounded-[var(--radius-sm)] transition-colors"
              :class="route.path === item.path ? 'bg-brand text-sidebar' : 'text-ink-on-dark-muted hover:text-ink-on-dark'"
            >
              {{ item.label }}
            </router-link>
          </div>
        </header>

        <!-- 页面内容 -->
        <div class="p-5 md:p-8 max-w-5xl">
          <router-view />
        </div>
      </main>
    </div>
  </template>
</template>
