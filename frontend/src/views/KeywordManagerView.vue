<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { keywordApi, preferencesApi } from '../api'

const keywords = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const activeQuadrant = ref(0) // 0 = 全部

const quadrantInfo: Record<number, { name: string; color: string; bg: string }> = {
  1: { name: '🏠 生存与根基', color: 'text-green-700', bg: 'bg-green-50' },
  2: { name: '❤️ 关系与情感', color: 'text-red-700', bg: 'bg-red-50' },
  3: { name: '🌱 成长与认知', color: 'text-blue-700', bg: 'bg-blue-50' },
  4: { name: '🌌 终极与哲思', color: 'text-purple-700', bg: 'bg-purple-50' },
}

const filteredKeywords = computed(() => {
  if (activeQuadrant.value === 0) return keywords.value
  return keywords.value.filter(k => k.quadrant === activeQuadrant.value)
})

// 本地权重状态
const localWeights = ref<Record<number, number>>({})

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await keywordApi.list()
    keywords.value = data
    // 初始化本地权重
    const weights: Record<number, number> = {}
    data.forEach((k: any) => {
      weights[k.id] = k.weight ?? k.default_weight
    })
    localWeights.value = weights
  } finally {
    loading.value = false
  }
})

function updateWeight(id: number, weight: number) {
  localWeights.value[id] = Math.round(weight * 10) / 10
}

async function saveWeights() {
  saving.value = true
  try {
    const weights: Record<number, number> = {}
    keywords.value.forEach((k: any) => {
      if (localWeights.value[k.id] !== undefined) {
        weights[k.id] = localWeights.value[k.id]
      }
    })
    await preferencesApi.updateKeywordWeights(weights)
    alert('权重已保存')
  } catch (e: any) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

// 新增自定义关键词
const showAdd = ref(false)
const newKeyword = ref({ name: '', quadrant: 1, description: '' })

async function addKeyword() {
  try {
    await keywordApi.create(newKeyword.value)
    showAdd.value = false
    newKeyword.value = { name: '', quadrant: 1, description: '' }
    // 刷新
    const { data } = await keywordApi.list()
    keywords.value = data
  } catch (e: any) {
    alert('新增失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteKeyword(id: number) {
  if (!confirm('确定删除该关键词？')) return
  try {
    await keywordApi.delete(id)
    keywords.value = keywords.value.filter(k => k.id !== id)
  } catch (e: any) {
    alert('删除失败')
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">关键词管理</h1>
      <button @click="showAdd = true"
        class="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700">
        + 新增关键词
      </button>
    </div>

    <!-- 象限切换 -->
    <div class="flex gap-2 mb-6 flex-wrap">
      <button
        @click="activeQuadrant = 0"
        class="px-3 py-1.5 text-sm rounded-lg transition-colors"
        :class="activeQuadrant === 0 ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
      >全部 ({{ keywords.length }})</button>
      <button
        v-for="q in [1, 2, 3, 4]"
        :key="q"
        @click="activeQuadrant = q"
        class="px-3 py-1.5 text-sm rounded-lg transition-colors"
        :class="activeQuadrant === q ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
      >{{ quadrantInfo[q].name }} ({{ keywords.filter(k => k.quadrant === q).length }})</button>
    </div>

    <!-- 关键词列表 -->
    <div v-if="loading" class="text-center text-gray-400 py-8">加载中...</div>
    <div v-else class="space-y-2">
      <div
        v-for="kw in filteredKeywords"
        :key="kw.id"
        class="bg-white rounded-lg p-3 border border-gray-200 flex items-center gap-4"
      >
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="font-medium text-sm text-gray-800">{{ kw.name }}</span>
            <span v-if="kw.english" class="text-xs text-gray-400">{{ kw.english }}</span>
            <span v-if="!kw.is_system" class="text-xs bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded">自定义</span>
          </div>
          <p v-if="kw.description" class="text-xs text-gray-500 mt-0.5 truncate">{{ kw.description }}</p>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <input
            type="range"
            :min="0" :max="5" :step="0.1"
            :value="localWeights[kw.id] ?? kw.default_weight"
            @input="updateWeight(kw.id, parseFloat(($event.target as HTMLInputElement).value))"
            class="w-20 accent-indigo-600"
          />
          <span class="text-xs text-gray-600 w-8 text-right">{{ (localWeights[kw.id] ?? kw.default_weight).toFixed(1) }}</span>
        </div>
        <button
          v-if="!kw.is_system"
          @click="deleteKeyword(kw.id)"
          class="text-xs text-red-400 hover:text-red-600"
        >删除</button>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="mt-6">
      <button
        @click="saveWeights"
        :disabled="saving"
        class="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50"
      >{{ saving ? '保存中...' : '保存权重' }}</button>
    </div>

    <!-- 新增关键词弹窗 -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl p-6 w-full max-w-sm">
        <h3 class="text-lg font-semibold mb-4">新增关键词</h3>
        <div class="space-y-3">
          <input v-model="newKeyword.name" placeholder="关键词名称" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <select v-model="newKeyword.quadrant" class="w-full px-3 py-2 border rounded-lg text-sm">
            <option v-for="q in [1,2,3,4]" :key="q" :value="q">{{ quadrantInfo[q].name }}</option>
          </select>
          <input v-model="newKeyword.description" placeholder="描述（选填）" class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>
        <div class="flex gap-2 mt-4">
          <button @click="showAdd = false" class="flex-1 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200">取消</button>
          <button @click="addKeyword" class="flex-1 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>
