<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { quotesApi, keywordApi, mentorApi, preferencesApi } from '../api'
const todayQuotes = ref<any[]>([])
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

async function generatePreview() {
  loading.value = true
  try {
    const { data } = await quotesApi.preview(3)
    todayQuotes.value = data
  } catch (e: any) {
    alert(e.response?.data?.detail || '生成失败，请检查 AI 模型配置')
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
  <div>
    <h1 class="text-2xl font-bold text-gray-800 mb-6">仪表盘</h1>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white rounded-xl p-4 border border-gray-200">
        <div class="text-2xl font-bold text-indigo-600">{{ keywords.length }}</div>
        <div class="text-sm text-gray-500">关键词</div>
      </div>
      <div class="bg-white rounded-xl p-4 border border-gray-200">
        <div class="text-2xl font-bold text-indigo-600">{{ mentors.length }}</div>
        <div class="text-sm text-gray-500">导师</div>
      </div>
      <div class="bg-white rounded-xl p-4 border border-gray-200">
        <div class="text-2xl font-indigo-600">{{ prefs.push_time || '08:00' }}</div>
        <div class="text-sm text-gray-500">推送时间</div>
      </div>
      <div class="bg-white rounded-xl p-4 border border-gray-200">
        <div class="text-2xl" :class="prefs.push_enabled ? 'text-green-600' : 'text-gray-400'">
          {{ prefs.push_enabled ? '已开启' : '已关闭' }}
        </div>
        <div class="text-sm text-gray-500">推送状态</div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="bg-white rounded-xl p-6 border border-gray-200 mb-8">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">快捷操作</h2>
      <button
        @click="generatePreview"
        :disabled="loading"
        class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50"
      >
        {{ loading ? '生成中...' : '预览语录（生成3条）' }}
      </button>
    </div>

    <!-- 预览语录 -->
    <div v-if="todayQuotes.length" class="mb-8">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">预览语录</h2>
      <div class="space-y-3">
        <div
          v-for="(q, i) in todayQuotes"
          :key="i"
          class="bg-white rounded-xl p-4 border border-gray-200 border-l-4 border-l-indigo-500"
        >
          <div class="text-xs text-gray-400 mb-2">#{{ i + 1 }} · {{ q.keyword }} — {{ q.mentor_name }}</div>
          <div class="text-sm text-gray-700 leading-relaxed">{{ q.content }}</div>
        </div>
      </div>
    </div>

    <!-- 关键词象限概览 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div
        v-for="q in [1, 2, 3, 4]"
        :key="q"
        class="bg-white rounded-xl p-4 border border-gray-200"
      >
        <div class="text-sm font-medium text-gray-600 mb-1">{{ quadrantNames[q] }}</div>
        <div class="text-xl font-bold text-gray-800">
          {{ keywords.filter(k => k.quadrant === q).length }}
        </div>
      </div>
    </div>
  </div>
</template>
