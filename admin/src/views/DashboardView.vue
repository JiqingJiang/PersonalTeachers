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
    <h1 class="text-2xl font-bold text-gray-800 mb-6">数据看板</h1>

    <div v-if="loading" class="text-center text-gray-400 py-8">加载中...</div>

    <template v-else>
      <!-- 统计卡片 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-xl p-5 border border-gray-200">
          <div class="text-3xl font-bold text-gray-800">{{ stats.total_users }}</div>
          <div class="text-sm text-gray-500 mt-1">总用户数</div>
        </div>
        <div class="bg-white rounded-xl p-5 border border-gray-200">
          <div class="text-3xl font-bold text-indigo-600">{{ stats.active_today }}</div>
          <div class="text-sm text-gray-500 mt-1">今日活跃</div>
        </div>
        <div class="bg-white rounded-xl p-5 border border-gray-200">
          <div class="text-3xl font-bold text-green-600">{{ stats.sent_today }}</div>
          <div class="text-sm text-gray-500 mt-1">今日推送</div>
        </div>
        <div class="bg-white rounded-xl p-5 border border-gray-200">
          <div class="text-3xl font-bold" :class="stats.success_rate >= 90 ? 'text-green-600' : 'text-amber-600'">
            {{ stats.success_rate }}%
          </div>
          <div class="text-sm text-gray-500 mt-1">推送成功率</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div class="bg-white rounded-xl p-5 border border-gray-200">
          <div class="text-sm text-gray-500 mb-1">本周新增</div>
          <div class="text-2xl font-bold text-blue-600">{{ stats.new_this_week }}</div>
        </div>
        <div class="bg-white rounded-xl p-5 border border-gray-200">
          <div class="text-sm text-gray-500 mb-1">今日失败</div>
          <div class="text-2xl font-bold" :class="stats.failed_today > 0 ? 'text-red-600' : 'text-gray-400'">
            {{ stats.failed_today }}
          </div>
        </div>
      </div>

      <!-- 推送趋势 -->
      <div class="bg-white rounded-xl p-5 border border-gray-200">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">近7天推送趋势</h2>
        <div v-if="!pushData.length" class="text-gray-400 text-sm">暂无数据</div>
        <div v-else class="space-y-2">
          <div v-for="d in pushData" :key="d.date" class="flex items-center gap-3">
            <span class="text-xs text-gray-500 w-20">{{ d.date }}</span>
            <div class="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
              <div class="h-full bg-indigo-500 rounded-full" :style="{ width: Math.min(d.total / Math.max(...pushData.map(x => x.total), 1) * 100, 100) + '%' }"></div>
            </div>
            <span class="text-xs text-gray-600 w-24 text-right">{{ d.sent }}成功 / {{ d.failed }}失败</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
