<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminEmailPool } from '../api'

const senders = ref<any[]>([])
const loading = ref(false)
const showForm = ref(false)
const testing = ref<number | null>(null)

const form = ref({
  email: '', smtp_host: 'smtp.qq.com', smtp_port: 587,
  smtp_password: '', display_name: 'PersonalTeachers', daily_limit: 200,
})

async function loadSenders() {
  loading.value = true
  try {
    const { data } = await adminEmailPool.list()
    senders.value = data
  } finally {
    loading.value = false
  }
}

onMounted(loadSenders)

async function addSender() {
  try {
    await adminEmailPool.create(form.value)
    showForm.value = false
    form.value = { email: '', smtp_host: 'smtp.qq.com', smtp_port: 587, smtp_password: '', display_name: 'PersonalTeachers', daily_limit: 200 }
    await loadSenders()
  } catch (e: any) {
    alert('添加失败: ' + (e.response?.data?.detail || e.message))
  }
}

async function toggleActive(s: any) {
  try {
    await adminEmailPool.update(s.id, { is_active: !s.is_active })
    await loadSenders()
  } catch { alert('操作失败') }
}

async function deleteSender(id: number) {
  if (!confirm('确定删除该邮箱？')) return
  try {
    await adminEmailPool.delete(id)
    await loadSenders()
  } catch { alert('删除失败') }
}

async function testSender(id: number) {
  testing.value = id
  try {
    await adminEmailPool.test(id)
    alert('测试邮件发送成功')
  } catch (e: any) {
    alert('测试失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    testing.value = null
  }
}

function capacityColor(s: any) {
  const ratio = s.remaining / s.daily_limit
  if (ratio > 0.5) return 'bg-green-500'
  if (ratio > 0.2) return 'bg-amber-500'
  return 'bg-red-500'
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">邮箱池管理</h1>
      <button @click="showForm = true"
        class="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700">
        + 添加邮箱
      </button>
    </div>

    <div v-if="loading" class="text-center text-gray-400 py-8">加载中...</div>

    <div v-else class="space-y-4">
      <div v-for="s in senders" :key="s.id"
        class="bg-white rounded-xl p-5 border border-gray-200"
        :class="s.is_active ? '' : 'opacity-50'">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="font-semibold text-gray-800">{{ s.email }}</h3>
            <div class="text-xs text-gray-500 mt-1">
              {{ s.smtp_host }}:{{ s.smtp_port }} · {{ s.display_name }}
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span :class="s.is_active ? 'text-green-500' : 'text-gray-400'" class="text-xs">
              {{ s.is_active ? '活跃' : '停用' }}
            </span>
          </div>
        </div>

        <!-- 容量条 -->
        <div class="mb-3">
          <div class="flex justify-between text-xs text-gray-500 mb-1">
            <span>今日已发 {{ s.sent_today }} / {{ s.daily_limit }}</span>
            <span>剩余 {{ s.remaining }}</span>
          </div>
          <div class="w-full bg-gray-100 rounded-full h-2">
            <div :class="capacityColor(s)" class="h-full rounded-full transition-all"
              :style="{ width: (s.sent_today / s.daily_limit * 100) + '%' }"></div>
          </div>
        </div>

        <div class="flex gap-3">
          <button @click="toggleActive(s)" class="text-xs text-indigo-600 hover:underline">
            {{ s.is_active ? '停用' : '启用' }}
          </button>
          <button @click="testSender(s.id)" :disabled="testing === s.id"
            class="text-xs text-blue-600 hover:underline disabled:opacity-50">
            {{ testing === s.id ? '发送中...' : '测试发送' }}
          </button>
          <button @click="deleteSender(s.id)" class="text-xs text-red-500 hover:underline">删除</button>
        </div>
      </div>

      <div v-if="!senders.length" class="text-center text-gray-400 py-8">
        暂无发件邮箱，请添加
      </div>
    </div>

    <!-- 添加邮箱弹窗 -->
    <div v-if="showForm" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl p-6 w-full max-w-sm">
        <h3 class="text-lg font-semibold mb-4">添加发件邮箱</h3>
        <div class="space-y-3">
          <input v-model="form.email" placeholder="邮箱地址" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <input v-model="form.smtp_host" placeholder="SMTP 主机（如 smtp.qq.com）" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <div class="grid grid-cols-2 gap-2">
            <input v-model.number="form.smtp_port" type="number" placeholder="端口" class="px-3 py-2 border rounded-lg text-sm" />
            <input v-model.number="form.daily_limit" type="number" placeholder="每日限额" class="px-3 py-2 border rounded-lg text-sm" />
          </div>
          <input v-model="form.smtp_password" type="password" placeholder="SMTP 密码/授权码" class="w-full px-3 py-2 border rounded-lg text-sm" />
          <input v-model="form.display_name" placeholder="发件人名称" class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>
        <div class="flex gap-2 mt-4">
          <button @click="showForm = false" class="flex-1 py-2 text-sm bg-gray-100 rounded-lg hover:bg-gray-200">取消</button>
          <button @click="addSender" class="flex-1 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>
