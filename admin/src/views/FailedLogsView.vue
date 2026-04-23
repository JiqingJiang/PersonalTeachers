<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminFailedLogs } from '../api'

const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)

async function loadLogs() {
  loading.value = true
  try {
    const { data } = await adminFailedLogs.list(page.value, 20)
    logs.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

onMounted(loadLogs)

async function resolveLog(id: number) {
  try {
    await adminFailedLogs.resolve(id)
    await loadLogs()
  } catch {
    alert('操作失败')
  }
}

const totalPages = () => Math.ceil(total.value / 20)
</script>

<template>
  <div class="space-y-6">
    <!-- Title & count badge -->
    <div class="flex items-center gap-3">
      <h1 class="text-ink text-2xl font-bold font-body">推送失败记录</h1>
      <span v-if="total > 0" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-danger/10 text-danger">
        {{ total }}
      </span>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center text-ink-muted py-16 text-sm">加载中...</div>

    <!-- Empty state -->
    <div v-else-if="logs.length === 0" class="text-center text-ink-muted py-20">
      <svg class="mx-auto w-12 h-12 text-ink-light mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm">暂无失败记录，一切正常</p>
    </div>

    <!-- Failed logs table -->
    <div v-else class="bg-surface-card rounded-[var(--radius-lg)] shadow-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface border-b border-ink-light/10">
            <tr>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">用户邮箱</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">收件邮箱</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">发件邮箱</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">语录数</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">错误信息</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">重试次数</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">时间</th>
              <th class="text-left px-4 py-3 text-ink-muted font-medium text-xs uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in logs" :key="l.id" class="border-b border-ink-light/5 hover:bg-brand-50 transition-colors">
              <td class="px-4 py-3 text-ink font-medium">{{ l.user_email || '-' }}</td>
              <td class="px-4 py-3 text-ink-secondary">{{ l.to_email }}</td>
              <td class="px-4 py-3 text-ink-muted text-xs">{{ l.sender_email }}</td>
              <td class="px-4 py-3 text-ink-secondary">{{ l.quote_count }}</td>
              <td class="px-4 py-3 text-danger text-xs max-w-xs truncate" :title="l.error_message">
                {{ l.error_message || '-' }}
              </td>
              <td class="px-4 py-3">
                <span :class="(l.retry_count || 0) > 0 ? 'text-danger font-semibold' : 'text-ink-secondary'">
                  {{ l.retry_count || 0 }}
                </span>
              </td>
              <td class="px-4 py-3 text-ink-muted text-xs">{{ l.created_at?.replace('T', ' ').substring(0, 16) }}</td>
              <td class="px-4 py-3">
                <button @click="resolveLog(l.id)" class="text-brand hover:text-brand-dark text-xs font-medium transition-colors">
                  标记已处理
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages() > 1" class="flex justify-center gap-1.5 pt-2">
      <button v-for="p in totalPages()" :key="p" @click="page = p; loadLogs()"
        class="px-3 py-1.5 text-sm font-medium rounded-[var(--radius-sm)] transition-colors"
        :class="page === p
          ? 'bg-brand text-ink-on-dark'
          : 'bg-surface-card text-ink-secondary hover:bg-brand-50 hover:text-ink'">
        {{ p }}
      </button>
    </div>
  </div>
</template>
