<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
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

async function loadMentors() {
  loading.value = true
  try {
    const [mRes, cRes] = await Promise.all([mentorApi.list(), mentorApi.categories()])
    mentors.value = mRes.data
    categories.value = cRes.data
  } finally {
    loading.value = false
  }
}

onMounted(loadMentors)

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
    await loadMentors()
  } catch (e: any) {
    alert('新增失败: ' + (e.response?.data?.detail || e.message))
  }
}

// 编辑导师
const showEdit = ref(false)
const editingMentor = ref<any>(null)

function openEdit(m: any) {
  editingMentor.value = {
    ...m,
    keywords: Array.isArray(m.keywords) ? m.keywords.join(', ') : (m.keywords || ''),
  }
  showEdit.value = true
}

async function saveEdit() {
  try {
    const payload = {
      name: editingMentor.value.name,
      category: editingMentor.value.category,
      field: editingMentor.value.field,
      personality: editingMentor.value.personality,
      tone: editingMentor.value.tone,
      background: editingMentor.value.background,
      keywords: editingMentor.value.keywords
        ? editingMentor.value.keywords.split(',').map((s: string) => s.trim())
        : [],
    }
    await mentorApi.update(editingMentor.value.id, payload)
    showEdit.value = false
    editingMentor.value = null
    await loadMentors()
  } catch (e: any) {
    alert('编辑失败: ' + (e.response?.data?.detail || e.message))
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
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-display font-bold text-ink tracking-tight">导师管理</h1>
      <button @click="showAdd = true"
        class="px-5 py-2.5 bg-gradient-to-r from-brand to-brand-dark text-white text-sm font-medium rounded-lg shadow-amber hover:shadow-elevated transition-all duration-200">
        + 新增导师
      </button>
    </div>

    <!-- 类别切换 -->
    <div class="flex gap-2 mb-8 flex-wrap">
      <button @click="filterByCategory('')"
        class="px-4 py-2 text-sm rounded-lg transition-all duration-200 font-medium"
        :class="!activeCategory
          ? 'bg-ink text-white shadow-card'
          : 'bg-surface-card text-ink-muted hover:bg-brand-50 hover:text-ink-secondary border border-ink-light/30'"
      >全部 ({{ mentors.length }})</button>
      <button
        v-for="cat in categories" :key="cat.id"
        @click="filterByCategory(cat.id)"
        class="px-4 py-2 text-sm rounded-lg transition-all duration-200 font-medium"
        :class="activeCategory === cat.id
          ? 'bg-ink text-white shadow-card'
          : 'bg-surface-card text-ink-muted hover:bg-brand-50 hover:text-ink-secondary border border-ink-light/30'"
      >{{ cat.emoji }} {{ cat.name }} ({{ cat.count }})</button>
    </div>

    <!-- 导师卡片 -->
    <div v-if="loading" class="text-center text-ink-muted py-12 font-body">加载中...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="m in filteredMentors"
        :key="m.id"
        class="bg-surface-card rounded-lg p-5 shadow-card hover:shadow-card-hover transition-shadow duration-200 border border-transparent relative overflow-hidden"
        :class="m.is_enabled === false ? 'opacity-50' : ''"
      >
        <!-- 左侧分类色竖线 -->
        <div class="absolute left-0 top-0 bottom-0 w-1"
          :class="[
            m.category === 'historical' ? 'bg-cat-historical' : '',
            m.category === 'modern' ? 'bg-cat-modern' : '',
            m.category === 'common' ? 'bg-cat-common' : '',
            m.category === 'future_self' ? 'bg-cat-future' : '',
          ]"
        ></div>

        <div class="flex items-start justify-between mb-3 pl-3">
          <div>
            <div class="flex items-center gap-2">
              <span class="font-display font-bold text-ink text-lg">{{ m.name }}</span>
              <span v-if="!m.is_system" class="text-xs bg-brand-100 text-brand-600 px-2 py-0.5 rounded-full font-medium">自定义</span>
            </div>
            <div class="text-xs text-ink-secondary mt-0.5">{{ m.field || m.category }}</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer shrink-0">
            <input type="checkbox" :checked="m.is_enabled !== false" @change="toggleMentor(m.id, m.is_enabled !== false)"
              class="sr-only peer" />
            <div class="w-10 h-5.5 bg-ink-light/30 peer-checked:bg-brand rounded-full peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4.5 after:w-4.5 after:transition-all after:shadow-sm"></div>
          </label>
        </div>

        <p v-if="m.background" class="text-xs text-ink-secondary line-clamp-2 mb-3 pl-3 leading-relaxed">{{ m.background }}</p>

        <div v-if="m.keywords?.length" class="flex flex-wrap gap-1.5 pl-3">
          <span v-for="kw in (m.keywords || []).slice(0, 4)" :key="kw"
            class="text-xs bg-brand-50 text-brand-700 px-2 py-0.5 rounded-full border border-brand-100">{{ kw }}</span>
        </div>

        <div v-if="!m.is_system" class="flex gap-4 mt-3 pl-3 pt-3 border-t border-ink-light/15">
          <button @click="openEdit(m)" class="text-xs text-brand-600 hover:text-brand-700 font-medium transition-colors">编辑</button>
          <button @click="deleteMentor(m.id)" class="text-xs text-danger hover:text-red-700 font-medium transition-colors">删除</button>
        </div>
      </div>
    </div>

    <!-- 新增导师弹窗 -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-surface-card rounded-xl p-6 w-full max-w-sm max-h-[90vh] overflow-auto shadow-elevated">
        <h3 class="text-xl font-display font-bold text-ink mb-5">新增导师</h3>
        <div class="space-y-4">
          <input v-model="newMentor.name" placeholder="导师名称"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <select v-model="newMentor.category"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all">
            <option v-for="(info, key) in categoryInfo" :key="key" :value="key">{{ info.emoji }} {{ info.name }}</option>
          </select>
          <input v-model="newMentor.field" placeholder="领域（选填）"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <input v-model="newMentor.personality" placeholder="性格特质（选填）"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <input v-model="newMentor.tone" placeholder="说话风格（选填）"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <textarea v-model="newMentor.background" placeholder="背景介绍（选填）" rows="2"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all resize-none"></textarea>
          <input v-model="newMentor.keywords" placeholder="关联关键词（逗号分隔，选填）"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showAdd = false" class="flex-1 py-2.5 text-sm text-ink-secondary bg-surface rounded-lg hover:bg-ink/5 font-medium transition-colors">取消</button>
          <button @click="addMentor" class="flex-1 py-2.5 text-sm text-white bg-gradient-to-r from-brand to-brand-dark rounded-lg shadow-amber hover:shadow-elevated font-medium transition-all">添加</button>
        </div>
      </div>
    </div>

    <!-- 编辑导师弹窗 -->
    <div v-if="showEdit && editingMentor" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-surface-card rounded-xl p-6 w-full max-w-sm max-h-[90vh] overflow-auto shadow-elevated">
        <h3 class="text-xl font-display font-bold text-ink mb-5">编辑导师</h3>
        <div class="space-y-4">
          <input v-model="editingMentor.name" placeholder="导师名称"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <select v-model="editingMentor.category"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all">
            <option v-for="(info, key) in categoryInfo" :key="key" :value="key">{{ info.emoji }} {{ info.name }}</option>
          </select>
          <input v-model="editingMentor.field" placeholder="领域（选填）"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <input v-model="editingMentor.personality" placeholder="性格特质（选填）"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <input v-model="editingMentor.tone" placeholder="说话风格（选填）"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          <textarea v-model="editingMentor.background" placeholder="背景介绍（选填）" rows="2"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all resize-none"></textarea>
          <input v-model="editingMentor.keywords" placeholder="关联关键词（逗号分隔，选填）"
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
