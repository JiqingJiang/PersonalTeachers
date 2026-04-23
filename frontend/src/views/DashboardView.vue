<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { quotesApi, keywordApi, mentorApi, preferencesApi } from '../api'
const keywords = ref<any[]>([])
const mentors = ref<any[]>([])
const prefs = ref<any>({})
const loading = ref(false)

onMounted(async () => {
  try {
    const [kwRes, mRes, prefRes] = await Promise.all([
      keywordApi.list(),
      mentorApi.list(),
      preferencesApi.get(),
    ])
    keywords.value = kwRes.data
    mentors.value = mRes.data
    prefs.value = prefRes.data
  } catch (e) {
    console.error('加载数据失败', e)
  }
})

async function sendTestEmail() {
  loading.value = true
  try {
    const { data } = await quotesApi.testEmail(10)
    alert(data.message || '测试邮件发送成功')
  } catch (e: any) {
    alert(e.response?.data?.detail || '发送失败，请检查 AI 模型或邮箱配置')
  } finally {
    loading.value = false
  }
}

const quadrantNames: Record<number, string> = {
  1: '🏠 生存与根基',
  2: '❤️ 关系与情感',
  3: '🌱 成长与认知',
  4: '🌌 终极与哲思',
}
</script>

<template>
  <div class="space-y-8">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-3xl font-display font-bold text-ink tracking-tight">仪表盘</h1>
      <p class="mt-1 text-sm text-ink-muted font-body">系统概览与快捷操作</p>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-5">
      <!-- 关键词 -->
      <div class="bg-surface-card rounded-lg p-5 shadow-card relative overflow-hidden">
        <div class="absolute top-0 left-0 right-0 h-1 bg-brand rounded-t-lg"></div>
        <div class="pt-1">
          <div class="text-xs font-body text-ink-muted uppercase tracking-wider mb-2">关键词</div>
          <div class="text-3xl font-display font-bold text-brand">{{ keywords.length }}</div>
        </div>
      </div>
      <!-- 导师 -->
      <div class="bg-surface-card rounded-lg p-5 shadow-card relative overflow-hidden">
        <div class="absolute top-0 left-0 right-0 h-1 bg-brand-dark rounded-t-lg"></div>
        <div class="pt-1">
          <div class="text-xs font-body text-ink-muted uppercase tracking-wider mb-2">导师</div>
          <div class="text-3xl font-display font-bold text-brand-dark">{{ mentors.length }}</div>
        </div>
      </div>
      <!-- 推送时间 -->
      <div class="bg-surface-card rounded-lg p-5 shadow-card relative overflow-hidden">
        <div class="absolute top-0 left-0 right-0 h-1 bg-brand-light rounded-t-lg"></div>
        <div class="pt-1">
          <div class="text-xs font-body text-ink-muted uppercase tracking-wider mb-2">推送时间</div>
          <div class="text-3xl font-display font-bold text-brand-light">{{ prefs.push_time || '08:00' }}</div>
        </div>
      </div>
      <!-- 推送状态 -->
      <div class="bg-surface-card rounded-lg p-5 shadow-card relative overflow-hidden">
        <div class="absolute top-0 left-0 right-0 h-1 rounded-t-lg"
          :class="prefs.push_enabled ? 'bg-success' : 'bg-ink-light/40'"></div>
        <div class="pt-1">
          <div class="text-xs font-body text-ink-muted uppercase tracking-wider mb-2">推送状态</div>
          <div class="text-2xl font-display font-bold"
            :class="prefs.push_enabled ? 'text-success' : 'text-ink-light'">
            {{ prefs.push_enabled ? '已开启' : '已关闭' }}
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="bg-surface-card rounded-lg p-6 shadow-card">
      <h2 class="text-lg font-display font-semibold text-ink mb-5">快捷操作</h2>
      <button
        @click="sendTestEmail"
        :disabled="loading"
        class="inline-flex items-center gap-2 px-6 py-2.5 text-sm font-body font-medium text-white rounded-lg
               bg-gradient-to-r from-brand to-brand-dark
               shadow-amber
               hover:shadow-card-hover hover:brightness-105
               active:scale-[0.98]
               disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none
               transition-all duration-200"
      >
        <svg v-if="!loading" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0-8.953 8.953a2.25 2.25 0 0 1-3.182 0L2.25 6.75" />
        </svg>
        <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        {{ loading ? '发送中...' : '发送测试邮件（10条语录）' }}
      </button>
    </div>

    <!-- 四象限概览 -->
    <div>
      <h2 class="text-lg font-display font-semibold text-ink mb-4">四象限概览</h2>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <!-- 象限 1: 生存与根基 -->
        <div
          v-for="q in [1, 2, 3, 4]"
          :key="q"
          class="rounded-lg p-5 shadow-card transition-shadow duration-200 hover:shadow-card-hover"
          :class="{
            'bg-quadrant-1-bg border border-quadrant-1-border': q === 1,
            'bg-quadrant-2-bg border border-quadrant-2-border': q === 2,
            'bg-quadrant-3-bg border border-quadrant-3-border': q === 3,
            'bg-quadrant-4-bg border border-quadrant-4-border': q === 4,
          }"
        >
          <div class="text-sm font-body mb-3"
            :class="{
              'text-quadrant-1': q === 1,
              'text-quadrant-2': q === 2,
              'text-quadrant-3': q === 3,
              'text-quadrant-4': q === 4,
            }"
          >{{ quadrantNames[q] }}</div>
          <div class="text-3xl font-display font-bold text-ink">
            {{ keywords.filter(k => k.quadrant === q).length }}
          </div>
          <div class="text-xs font-body text-ink-muted mt-1">个关键词</div>
        </div>
      </div>
    </div>
  </div>
</template>
