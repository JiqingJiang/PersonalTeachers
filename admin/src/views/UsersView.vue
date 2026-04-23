<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminUsers } from '../api'

const users = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const search = ref('')
const loading = ref(false)

async function loadUsers() {
  loading.value = true
  try {
    const { data } = await adminUsers.list(page.value, 20, search.value || undefined)
    users.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)

async function toggleActive(id: number) {
  try {
    await adminUsers.toggleActive(id)
    await loadUsers()
  } catch { alert('操作失败') }
}

const totalPages = () => Math.ceil(total.value / 20)
</script>

<template>
  <div class="space-y-6">
    <!-- Title & subtitle -->
    <div class="flex items-baseline gap-3">
      <h1 class="text-ink text-2xl font-bold font-body">用户管理</h1>
      <span class="text-ink-muted text-sm">共 {{ total }} 个用户</span>
    </div>

    <!-- Search bar -->
    <div class="flex gap-2">
      <div class="relative flex-1">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input v-model="search" @keyup.enter="page = 1; loadUsers()" placeholder="搜索邮箱/昵称"
          class="w-full pl-10 pr-4 py-2.5 bg-surface-card border border-ink-light/20 rounded-[var(--radius-md)] text-sm text-ink placeholder:text-ink-muted focus:outline-none focus:border-brand focus:ring-1 focus:ring-brand" />
      </div>
      <button @click="page = 1; loadUsers()"
        class="px-5 py-2.5 bg-brand text-ink-on-dark text-sm font-medium rounded-[var(--radius-md)] hover:bg-brand-dark transition-colors">
        搜索
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center text-ink-muted py-16 text-sm">加载中...</div>

    <!-- User table -->
    <div v-else class="bg-surface-card rounded-[var(--radius-lg)] shadow-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface border-b border-ink-light/10">
            <tr>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">邮箱</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">昵称</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">推送时间</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">语录数</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">字数</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">个性化</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">状态</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">注册时间</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id" class="border-b border-ink-light/5 hover:bg-brand-50 transition-colors">
              <td class="px-4 py-3 text-ink font-medium">{{ u.email }}</td>
              <td class="px-4 py-3 text-ink-secondary">{{ u.nickname || '-' }}</td>
              <td class="px-4 py-3 text-ink-secondary">{{ u.push_time }}</td>
              <td class="px-4 py-3 text-ink-secondary">{{ u.push_count }} 条</td>
              <td class="px-4 py-3 text-ink-secondary">{{ u.max_words }} 字</td>
              <td class="px-4 py-3 text-ink-secondary">{{ (u.personalization_weight * 100).toFixed(0) }}%</td>
              <td class="px-4 py-3">
                <span v-if="u.is_active" class="inline-flex items-center text-success text-sm">
                  <span class="w-1.5 h-1.5 rounded-full bg-success inline-block mr-1"></span>
                  活跃
                </span>
                <span v-else class="text-ink-muted text-sm">停用</span>
                <span v-if="u.push_enabled" class="ml-2 text-brand text-xs font-medium">推送中</span>
              </td>
              <td class="px-4 py-3 text-ink-muted text-xs">{{ u.created_at?.split('T')[0] }}</td>
              <td class="px-4 py-3">
                <button @click="toggleActive(u.id)" class="text-brand hover:text-brand-dark text-xs font-medium transition-colors">
                  {{ u.is_active ? '停用' : '启用' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages() > 1" class="flex justify-center gap-1.5 pt-2">
      <button v-for="p in totalPages()" :key="p" @click="page = p; loadUsers()"
        class="px-3 py-1.5 text-sm font-medium rounded-[var(--radius-sm)] transition-colors"
        :class="page === p
          ? 'bg-brand text-ink-on-dark'
          : 'bg-surface-card text-ink-secondary hover:bg-brand-50 hover:text-ink'">
        {{ p }}
      </button>
    </div>
  </div>
</template>
