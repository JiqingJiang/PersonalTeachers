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
  <div>
    <h1 class="text-2xl font-bold text-gray-800 mb-6">历史语录</h1>

    <div v-if="loading" class="text-center text-gray-400 py-8">加载中...</div>

    <div v-else-if="!quotes.length" class="text-center text-gray-400 py-8">
      <p>暂无历史语录</p>
      <p class="text-sm mt-1">开启推送后，每天生成的语录会在这里展示</p>
    </div>

    <div v-else>
      <div class="text-sm text-gray-500 mb-4">共 {{ total }} 条</div>

      <!-- 按日期分组 -->
      <div class="space-y-6">
        <div v-for="q in quotes" :key="q.id"
          class="bg-white rounded-xl p-4 border border-gray-200 border-l-4 border-l-indigo-500">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded">{{ q.keyword }}</span>
              <span class="text-xs text-gray-400">— {{ q.mentor_name }}</span>
            </div>
            <span class="text-xs text-gray-400">{{ q.created_at?.split('T')[0] }}</span>
          </div>
          <p class="text-sm text-gray-700 leading-relaxed">{{ q.content }}</p>
          <div class="mt-2 text-xs text-gray-300">via {{ q.ai_model }}</div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages() > 1" class="flex justify-center gap-2 mt-6">
        <button
          v-for="p in totalPages()" :key="p"
          @click="page = p; loadHistory()"
          class="px-3 py-1 text-sm rounded-lg"
          :class="page === p ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
        >{{ p }}</button>
      </div>
    </div>
  </div>
</template>
