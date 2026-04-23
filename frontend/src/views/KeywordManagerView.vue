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

async function loadKeywords() {
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
}

onMounted(loadKeywords)

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
    await loadKeywords()
  } catch (e: any) {
    alert('新增失败: ' + (e.response?.data?.detail || e.message))
  }
}

// 编辑关键词
const showEdit = ref(false)
const editingKeyword = ref<any>(null)

function openEdit(kw: any) {
  editingKeyword.value = { ...kw }
  showEdit.value = true
}

async function saveEdit() {
  try {
    await keywordApi.update(editingKeyword.value.id, {
      name: editingKeyword.value.name,
      quadrant: editingKeyword.value.quadrant,
      description: editingKeyword.value.description,
    })
    showEdit.value = false
    editingKeyword.value = null
    await loadKeywords()
  } catch (e: any) {
    alert('编辑失败: ' + (e.response?.data?.detail || e.message))
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
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-display font-bold text-ink tracking-tight">关键词管理</h1>
      <button @click="showAdd = true"
        class="px-5 py-2.5 bg-gradient-to-r from-brand to-brand-dark text-white text-sm font-medium rounded-lg shadow-amber hover:shadow-elevated transition-all duration-200">
        + 新增关键词
      </button>
    </div>

    <!-- 象限切换 -->
    <div class="flex gap-2 mb-8 flex-wrap">
      <button
        @click="activeQuadrant = 0"
        class="px-4 py-2 text-sm rounded-lg transition-all duration-200 font-medium"
        :class="activeQuadrant === 0
          ? 'bg-ink text-white shadow-card'
          : 'bg-surface-card text-ink-muted hover:bg-brand-50 hover:text-ink-secondary border border-ink-light/30'"
      >全部 ({{ keywords.length }})</button>
      <button
        v-for="q in [1, 2, 3, 4]"
        :key="q"
        @click="activeQuadrant = q"
        class="px-4 py-2 text-sm rounded-lg transition-all duration-200 font-medium"
        :class="activeQuadrant === q
          ? [
              q === 1 ? 'bg-quadrant-1 text-white' : '',
              q === 2 ? 'bg-quadrant-2 text-white' : '',
              q === 3 ? 'bg-quadrant-3 text-white' : '',
              q === 4 ? 'bg-quadrant-4 text-white' : '',
              'shadow-card'
            ]
          : [
              q === 1 ? 'bg-quadrant-1-bg text-quadrant-1 border border-quadrant-1-border' : '',
              q === 2 ? 'bg-quadrant-2-bg text-quadrant-2 border border-quadrant-2-border' : '',
              q === 3 ? 'bg-quadrant-3-bg text-quadrant-3 border border-quadrant-3-border' : '',
              q === 4 ? 'bg-quadrant-4-bg text-quadrant-4 border border-quadrant-4-border' : '',
              'hover:shadow-card'
            ]"
      >{{ quadrantInfo[q].name }} ({{ keywords.filter(k => k.quadrant === q).length }})</button>
    </div>

    <!-- 关键词列表 -->
    <div v-if="loading" class="text-center text-ink-muted py-12 font-body">加载中...</div>
    <div v-else class="space-y-3">
      <div
        v-for="kw in filteredKeywords"
        :key="kw.id"
        class="bg-surface-card rounded-lg p-4 flex items-center gap-4 shadow-card hover:shadow-card-hover transition-shadow duration-200 border border-transparent"
      >
        <!-- 象限圆点 -->
        <div class="w-2.5 h-2.5 rounded-full shrink-0"
          :class="[
            kw.quadrant === 1 ? 'bg-quadrant-1' : '',
            kw.quadrant === 2 ? 'bg-quadrant-2' : '',
            kw.quadrant === 3 ? 'bg-quadrant-3' : '',
            kw.quadrant === 4 ? 'bg-quadrant-4' : '',
          ]"
        ></div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="font-medium text-sm text-ink">{{ kw.name }}</span>
            <span v-if="kw.english" class="text-xs text-ink-light italic">{{ kw.english }}</span>
            <span v-if="!kw.is_system" class="text-xs bg-brand-100 text-brand-600 px-2 py-0.5 rounded-full font-medium">自定义</span>
          </div>
          <p v-if="kw.description" class="text-xs text-ink-muted mt-0.5 truncate">{{ kw.description }}</p>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <input
            type="range"
            :min="0" :max="5" :step="0.1"
            :value="localWeights[kw.id] ?? kw.default_weight"
            @input="updateWeight(kw.id, parseFloat(($event.target as HTMLInputElement).value))"
            class="w-20 accent-brand"
          />
          <span class="text-xs text-ink-secondary w-8 text-right font-medium tabular-nums">{{ (localWeights[kw.id] ?? kw.default_weight).toFixed(1) }}</span>
        </div>
        <button v-if="!kw.is_system" @click="openEdit(kw)"
          class="text-xs text-brand-600 hover:text-brand-700 font-medium transition-colors">编辑</button>
        <button
          v-if="!kw.is_system"
          @click="deleteKeyword(kw.id)"
          class="text-xs text-danger hover:text-red-700 font-medium transition-colors"
        >删除</button>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="mt-8">
      <button
        @click="saveWeights"
        :disabled="saving"
        class="px-6 py-2.5 bg-gradient-to-r from-brand to-brand-dark text-white text-sm font-medium rounded-lg shadow-amber hover:shadow-elevated transition-all duration-200 disabled:opacity-50 disabled:shadow-none"
      >{{ saving ? '保存中...' : '保存权重' }}</button>
    </div>

    <!-- 新增关键词弹窗 -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-surface-card rounded-xl p-6 w-full max-w-sm shadow-elevated">
        <h3 class="text-xl font-display font-bold text-ink mb-5">新增关键词</h3>
        <div class="space-y-4">
          <input v-model="newKeyword.name" placeholder="关键词名称"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <select v-model="newKeyword.quadrant"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all">
            <option v-for="q in [1,2,3,4]" :key="q" :value="q">{{ quadrantInfo[q].name }}</option>
          </select>
          <input v-model="newKeyword.description" placeholder="描述（选填）"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showAdd = false" class="flex-1 py-2.5 text-sm text-ink-secondary bg-surface rounded-lg hover:bg-ink/5 font-medium transition-colors">取消</button>
          <button @click="addKeyword" class="flex-1 py-2.5 text-sm text-white bg-gradient-to-r from-brand to-brand-dark rounded-lg shadow-amber hover:shadow-elevated font-medium transition-all">添加</button>
        </div>
      </div>
    </div>

    <!-- 编辑关键词弹窗 -->
    <div v-if="showEdit && editingKeyword" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-surface-card rounded-xl p-6 w-full max-w-sm shadow-elevated">
        <h3 class="text-xl font-display font-bold text-ink mb-5">编辑关键词</h3>
        <div class="space-y-4">
          <input v-model="editingKeyword.name" placeholder="关键词名称"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <select v-model="editingKeyword.quadrant"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all">
            <option v-for="q in [1,2,3,4]" :key="q" :value="q">{{ quadrantInfo[q].name }}</option>
          </select>
          <input v-model="editingKeyword.description" placeholder="描述（选填）"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showEdit = false" class="flex-1 py-2.5 text-sm text-ink-secondary bg-surface rounded-lg hover:bg-ink/5 font-medium transition-colors">取消</button>
          <button @click="saveEdit" class="flex-1 py-2.5 text-sm text-white bg-gradient-to-r from-brand to-brand-dark rounded-lg shadow-amber hover:shadow-elevated font-medium transition-all">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>
