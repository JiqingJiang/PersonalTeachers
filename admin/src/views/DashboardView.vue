<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminStats } from '../api'

const stats = ref<any>({})
const pushData = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [dashRes, pushRes] = await Promise.all([
      adminStats.dashboard(),
      adminStats.push(7),
    ])
    stats.value = dashRes.data
    pushData.value = pushRes.data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <!-- 页面标题 -->
    <div class="mb-8">
      <h1 class="text-3xl font-display text-ink">数据看板</h1>
      <p class="text-ink-muted text-sm mt-1">平台运营数据概览与推送趋势</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-16 text-ink-muted">
      <div class="w-8 h-8 border-2 border-brand/30 border-t-brand rounded-full animate-spin mb-4"></div>
      <span class="text-sm">数据加载中...</span>
    </div>

    <template v-else>
      <!-- 主统计卡片 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="bg-surface-card rounded-[var(--radius-lg)] shadow-card overflow-hidden">
          <div class="h-1 bg-ink"></div>
          <div class="p-5">
            <div class="text-3xl font-bold text-ink">{{ stats.total_users }}</div>
            <div class="text-sm text-ink-muted mt-1">总用户数</div>
          </div>
        </div>
        <div class="bg-surface-card rounded-[var(--radius-lg)] shadow-card overflow-hidden">
          <div class="h-1 bg-brand"></div>
          <div class="p-5">
            <div class="text-3xl font-bold text-ink">{{ stats.active_today }}</div>
            <div class="text-sm text-ink-muted mt-1">今日活跃</div>
          </div>
        </div>
        <div class="bg-surface-card rounded-[var(--radius-lg)] shadow-card overflow-hidden">
          <div class="h-1 bg-success"></div>
          <div class="p-5">
            <div class="text-3xl font-bold text-ink">{{ stats.sent_today }}</div>
            <div class="text-sm text-ink-muted mt-1">今日推送</div>
          </div>
        </div>
        <div class="bg-surface-card rounded-[var(--radius-lg)] shadow-card overflow-hidden">
          <div class="h-1" :class="stats.success_rate >= 90 ? 'bg-success' : 'bg-danger'"></div>
          <div class="p-5">
            <div class="text-3xl font-bold text-ink">{{ stats.success_rate }}%</div>
            <div class="text-sm text-ink-muted mt-1">推送成功率</div>
          </div>
        </div>
      </div>

      <!-- 次要统计卡片 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div class="bg-surface-card rounded-[var(--radius-lg)] shadow-card overflow-hidden">
          <div class="h-1 bg-info"></div>
          <div class="p-5">
            <div class="text-sm text-ink-muted mb-1">本周新增</div>
            <div class="text-2xl font-bold text-ink">{{ stats.new_this_week }}</div>
          </div>
        </div>
        <div class="bg-surface-card rounded-[var(--radius-lg)] shadow-card overflow-hidden">
          <div class="h-1" :class="stats.failed_today > 0 ? 'bg-danger' : 'bg-ink-light'"></div>
          <div class="p-5">
            <div class="text-sm text-ink-muted mb-1">今日失败</div>
            <div class="text-2xl font-bold text-ink">{{ stats.failed_today }}</div>
          </div>
        </div>
      </div>

      <!-- 推送趋势 -->
      <div class="bg-surface-card rounded-[var(--radius-lg)] shadow-card p-6">
        <h2 class="text-lg font-semibold text-ink mb-5">近7天推送趋势</h2>
        <div v-if="!pushData.length" class="text-ink-muted text-sm py-4">暂无数据</div>
        <div v-else class="space-y-3">
          <div v-for="d in pushData" :key="d.date" class="flex items-center gap-3">
            <span class="text-xs text-ink-muted w-20 shrink-0">{{ d.date }}</span>
            <div class="flex-1 bg-brand/20 rounded-full h-4 overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-brand to-brand-dark rounded-full transition-all duration-500"
                :style="{ width: Math.min(d.total / Math.max(...pushData.map(x => x.total), 1) * 100, 100) + '%' }"
              ></div>
            </div>
            <span class="text-xs text-ink-secondary w-24 text-right shrink-0">{{ d.sent }}成功 / {{ d.failed }}失败</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
