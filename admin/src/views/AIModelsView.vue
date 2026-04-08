<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminAIModels } from '../api'

const models = ref<any[]>([])
const loading = ref(false)
const showForm = ref(false)
const editingId = ref<number | null>(null)

const form = ref({
  name: '', provider: 'deepseek', base_url: '', api_key: '', model_id: '',
  priority: 1, is_active: true, max_tokens: 300, temperature: 0.7,
})

const providerPresets: Record<string, { base_url: string; model_id: string }> = {
  deepseek: { base_url: 'https://api.deepseek.com', model_id: 'deepseek-chat' },
  zhipu: { base_url: 'https://open.bigmodel.cn/api/paas/v4', model_id: 'glm-4-flash' },
  custom: { base_url: '', model_id: '' },
}

function onProviderChange() {
  const preset = providerPresets[form.value.provider]
  if (preset) {
    form.value.base_url = preset.base_url
    form.value.model_id = preset.model_id
  }
}

async function loadModels() {
  loading.value = true
  try {
    const { data } = await adminAIModels.list()
    models.value = data
  } finally {
    loading.value = false
  }
}

onMounted(loadModels)

function openAdd() {
  editingId.value = null
  form.value = {
    name: '', provider: 'deepseek', base_url: 'https://api.deepseek.com',
    api_key: '', model_id: 'deepseek-chat', priority: models.value.length + 1,
    is_active: true, max_tokens: 300, temperature: 0.7,
  }
  showForm.value = true
}

function openEdit(m: any) {
  editingId.value = m.id
  form.value = {
    name: m.name, provider: m.provider, base_url: m.base_url,
    api_key: '', model_id: m.model_id, priority: m.priority,
    is_active: m.is_active, max_tokens: m.max_tokens, temperature: m.temperature,
  }
  showForm.value = true
}

async function saveModel() {
  try {
    if (editingId.value) {
      await adminAIModels.update(editingId.value, form.value)
    } else {
      await adminAIModels.create(form.value)
    }
    showForm.value = false
    await loadModels()
  } catch (e: any) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function deleteModel(id: number) {
  if (!confirm('确定删除该模型？')) return
  try {
    await adminAIModels.delete(id)
    await loadModels()
  } catch { alert('删除失败') }
}

const providerLabels: Record<string, string> = {
  deepseek: 'DeepSeek', zhipu: '智谱GLM', custom: '自定义',
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">AI 模型配置</h1>
      <button @click="openAdd"
        class="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700">
        + 添加模型
      </button>
    </div>

    <div v-if="loading" class="text-center text-gray-400 py-8">加载中...</div>

    <!-- 模型卡片 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="m in models" :key="m.id"
        class="bg-white rounded-xl p-5 border border-gray-200"
        :class="m.is_active ? '' : 'opacity-50'">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-semibold text-gray-800">{{ m.name }}</h3>
            <span class="text-xs text-gray-500">{{ providerLabels[m.provider] || m.provider }}</span>
          </div>
          <span :class="m.is_active ? 'text-green-500' : 'text-gray-400'" class="text-xs">
            {{ m.is_active ? '活跃' : '停用' }}
          </span>
        </div>
        <div class="text-xs text-gray-500 space-y-1 mb-3">
          <div>模型: <span class="text-gray-700">{{ m.model_id }}</span></div>
          <div>Base URL: <span class="text-gray-700 font-mono text-[10px]">{{ m.base_url }}</span></div>
          <div>API Key: <span class="text-gray-700 font-mono">{{ m.has_api_key ? m.api_key : '未配置' }}</span></div>
          <div>优先级: {{ m.priority }} · max_tokens: {{ m.max_tokens }} · temperature: {{ m.temperature }}</div>
        </div>
        <div class="flex gap-2">
          <button @click="openEdit(m)" class="text-xs text-indigo-600 hover:underline">编辑</button>
          <button @click="deleteModel(m.id)" class="text-xs text-red-500 hover:underline">删除</button>
        </div>
      </div>
    </div>

    <!-- 表单弹窗 -->
    <div v-if="showForm" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl p-6 w-full max-w-md max-h-[90vh] overflow-auto">
        <h3 class="text-lg font-semibold mb-4">{{ editingId ? '编辑模型' : '添加模型' }}</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm text-gray-600 mb-1">厂商</label>
            <select v-model="form.provider" @change="onProviderChange"
              class="w-full px-3 py-2 border rounded-lg text-sm">
              <option value="deepseek">DeepSeek</option>
              <option value="zhipu">智谱GLM</option>
              <option value="custom">自定义</option>
            </select>
          </div>
          <input v-model="form.name" placeholder="显示名称（如 DeepSeek）" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <input v-model="form.base_url" placeholder="Base URL" class="w-full px-3 py-2 border rounded-lg text-sm font-mono text-xs" />
          <input v-model="form.api_key" type="password" placeholder="API Key" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <input v-model="form.model_id" placeholder="模型 ID（如 deepseek-chat）" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <div class="grid grid-cols-3 gap-2">
            <div>
              <label class="block text-xs text-gray-500 mb-1">优先级</label>
              <input v-model.number="form.priority" type="number" min="1" class="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Max Tokens</label>
              <input v-model.number="form.max_tokens" type="number" class="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Temperature</label>
              <input v-model.number="form.temperature" type="number" step="0.1" min="0" max="2" class="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
          </div>
          <label class="flex items-center gap-2 text-sm text-gray-600">
            <input type="checkbox" v-model="form.is_active" class="rounded" /> 启用
          </label>
        </div>
        <div class="flex gap-2 mt-4">
          <button @click="showForm = false" class="flex-1 py-2 text-sm bg-gray-100 rounded-lg hover:bg-gray-200">取消</button>
          <button @click="saveModel" class="flex-1 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>
