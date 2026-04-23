<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { quotesApi } from '../api'

const quotes = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

async function loadHistory() {
  loading.value = true
  try {
    const { data } = await quotesApi.history(page.value, pageSize)
    quotes.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

onMounted(loadHistory)

const totalPages = () => Math.ceil(total.value / pageSize)
</script>

<template>
  <div class="space-y-8">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-3xl font-display font-bold text-ink tracking-tight">历史语录</h1>
      <p class="mt-1 text-sm text-ink-muted font-body">每日 AI 生成的智慧语录存档</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-ink-muted">
      <svg class="w-8 h-8 animate-spin text-brand mb-3" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
      <span class="text-sm font-body">加载中...</span>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!quotes.length" class="flex flex-col items-center justify-center py-20">
      <div class="w-16 h-16 rounded-full bg-brand-50 flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-brand-200" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" />
        </svg>
      </div>
      <p class="text-ink-secondary font-body text-base">暂无历史语录</p>
      <p class="text-sm text-ink-muted font-body mt-1">开启推送后，每天生成的语录会在这里展示</p>
    </div>

    <!-- 语录列表 -->
    <div v-else>
      <div class="text-sm text-ink-muted font-body mb-5">共 {{ total }} 条语录</div>

      <div class="space-y-4">
        <div
          v-for="q in quotes"
          :key="q.id"
          class="bg-surface-card rounded-lg p-5 shadow-card border-l-4 border-l-brand transition-shadow duration-200 hover:shadow-card-hover"
        >
          <!-- 头部：标签 + 元信息 -->
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2 flex-wrap">
              <span
                class="inline-flex items-center text-xs font-body px-2.5 py-0.5 rounded-full"
                :class="{
                  'bg-quadrant-1-bg text-quadrant-1': q.quadrant === 1,
                  'bg-quadrant-2-bg text-quadrant-2': q.quadrant === 2,
                  'bg-quadrant-3-bg text-quadrant-3': q.quadrant === 3,
                  'bg-quadrant-4-bg text-quadrant-4': q.quadrant === 4,
                  'bg-brand-50 text-brand': !q.quadrant || q.quadrant < 1 || q.quadrant > 4,
                }"
              >{{ q.keyword }}</span>
              <span class="text-xs font-body text-ink-muted">{{ q.mentor_name }}</span>
            </div>
            <span class="text-xs font-body text-ink-light whitespace-nowrap ml-3">{{ q.created_at?.split('T')[0] }}</span>
          </div>

          <!-- 语录内容 -->
          <p class="text-sm font-body text-ink-secondary leading-relaxed">{{ q.content }}</p>

          <!-- AI 模型信息 -->
          <div class="mt-3 text-xs font-body text-ink-light">via {{ q.ai_model }}</div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages() > 1" class="flex justify-center gap-2 mt-8">
        <button
          v-for="p in totalPages()"
          :key="p"
          @click="page = p; loadHistory()"
          class="w-9 h-9 text-sm font-body rounded-lg transition-all duration-200"
          :class="page === p
            ? 'bg-brand text-white shadow-amber font-medium'
            : 'bg-surface text-ink-secondary hover:bg-brand-50 hover:text-brand'"
        >{{ p }}</button>
      </div>
    </div>
  </div>
</template>
