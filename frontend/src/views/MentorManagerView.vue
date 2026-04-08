<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { mentorApi, preferencesApi } from '../api'

const mentors = ref<any[]>([])
const categories = ref<any[]>([])
const activeCategory = ref('')
const loading = ref(false)

const categoryInfo: Record<string, { name: string; emoji: string; color: string }> = {
  historical: { name: '历史人物', emoji: '📜', color: 'bg-amber-50 border-amber-200' },
  modern: { name: '现代人物', emoji: '💼', color: 'bg-blue-50 border-blue-200' },
  common: { name: '普通百姓', emoji: '👥', color: 'bg-green-50 border-green-200' },
  future_self: { name: '未来自己', emoji: '🔮', color: 'bg-purple-50 border-purple-200' },
}

onMounted(async () => {
  loading.value = true
  try {
    const [mRes, cRes] = await Promise.all([mentorApi.list(), mentorApi.categories()])
    mentors.value = mRes.data
    categories.value = cRes.data
  } finally {
    loading.value = false
  }
})

const filteredMentors = ref<any[]>([])
function filterByCategory(cat: string) {
  activeCategory.value = cat
  if (!cat) {
    filteredMentors.value = mentors.value
  } else {
    filteredMentors.value = mentors.value.filter(m => m.category === cat)
  }
}

// 初始化显示全部
import { watch } from 'vue'
watch(mentors, () => filterByCategory(activeCategory.value), { immediate: true })

async function toggleMentor(mentorId: number, enabled: boolean) {
  try {
    await preferencesApi.updateMentorPrefs([{ mentor_id: mentorId, is_enabled: !enabled }])
    mentors.value = mentors.value.map(m =>
      m.id === mentorId ? { ...m, is_enabled: !enabled } : m
    )
  } catch {
    alert('操作失败')
  }
}

// 新增自定义导师
const showAdd = ref(false)
const newMentor = ref({ name: '', category: 'modern', field: '', personality: '', tone: '', background: '', keywords: '' })

async function addMentor() {
  try {
    const payload = {
      ...newMentor.value,
      keywords: newMentor.value.keywords ? newMentor.value.keywords.split(',').map(s => s.trim()) : [],
    }
    await mentorApi.create(payload)
    showAdd.value = false
    newMentor.value = { name: '', category: 'modern', field: '', personality: '', tone: '', background: '', keywords: '' }
    const { data } = await mentorApi.list()
    mentors.value = data
  } catch (e: any) {
    alert('新增失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteMentor(id: number) {
  if (!confirm('确定删除该导师？')) return
  try {
    await mentorApi.delete(id)
    mentors.value = mentors.value.filter(m => m.id !== id)
  } catch { alert('删除失败') }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">导师管理</h1>
      <button @click="showAdd = true"
        class="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700">
        + 新增导师
      </button>
    </div>

    <!-- 类别切换 -->
    <div class="flex gap-2 mb-6 flex-wrap">
      <button @click="filterByCategory('')"
        class="px-3 py-1.5 text-sm rounded-lg"
        :class="!activeCategory ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
      >全部 ({{ mentors.length }})</button>
      <button
        v-for="cat in categories" :key="cat.id"
        @click="filterByCategory(cat.id)"
        class="px-3 py-1.5 text-sm rounded-lg"
        :class="activeCategory === cat.id ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
      >{{ cat.emoji }} {{ cat.name }} ({{ cat.count }})</button>
    </div>

    <!-- 导师卡片 -->
    <div v-if="loading" class="text-center text-gray-400 py-8">加载中...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="m in filteredMentors"
        :key="m.id"
        class="bg-white rounded-xl p-4 border"
        :class="[(categoryInfo[m.category]?.color || 'border-gray-200'), m.is_enabled === false ? 'opacity-50' : '']"
      >
        <div class="flex items-start justify-between mb-2">
          <div>
            <div class="flex items-center gap-2">
              <span class="font-semibold text-gray-800">{{ m.name }}</span>
              <span v-if="!m.is_system" class="text-xs bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded">自定义</span>
            </div>
            <div class="text-xs text-gray-500">{{ m.field || m.category }}</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" :checked="m.is_enabled !== false" @change="toggleMentor(m.id, m.is_enabled !== false)"
              class="sr-only peer" />
            <div class="w-9 h-5 bg-gray-200 peer-checked:bg-indigo-600 rounded-full peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all"></div>
          </label>
        </div>
        <p v-if="m.background" class="text-xs text-gray-600 line-clamp-2 mb-2">{{ m.background }}</p>
        <div v-if="m.keywords?.length" class="flex flex-wrap gap-1">
          <span v-for="kw in (m.keywords || []).slice(0, 4)" :key="kw"
            class="text-xs bg-white/60 text-gray-600 px-1.5 py-0.5 rounded">{{ kw }}</span>
        </div>
        <button v-if="!m.is_system" @click="deleteMentor(m.id)"
          class="mt-2 text-xs text-red-400 hover:text-red-600">删除</button>
      </div>
    </div>

    <!-- 新增导师弹窗 -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl p-6 w-full max-w-sm max-h-[90vh] overflow-auto">
        <h3 class="text-lg font-semibold mb-4">新增导师</h3>
        <div class="space-y-3">
          <input v-model="newMentor.name" placeholder="导师名称" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <select v-model="newMentor.category" class="w-full px-3 py-2 border rounded-lg text-sm">
            <option v-for="(info, key) in categoryInfo" :key="key" :value="key">{{ info.emoji }} {{ info.name }}</option>
          </select>
          <input v-model="newMentor.field" placeholder="领域（选填）" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <input v-model="newMentor.personality" placeholder="性格特质（选填）" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <input v-model="newMentor.tone" placeholder="说话风格（选填）" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <textarea v-model="newMentor.background" placeholder="背景介绍（选填）" rows="2"
            class="w-full px-3 py-2 border rounded-lg text-sm"></textarea>
          <input v-model="newMentor.keywords" placeholder="关联关键词（逗号分隔，选填）"
            class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>
        <div class="flex gap-2 mt-4">
          <button @click="showAdd = false" class="flex-1 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200">取消</button>
          <button @click="addMentor" class="flex-1 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>
