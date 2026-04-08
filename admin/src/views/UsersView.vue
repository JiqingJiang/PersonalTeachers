<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminUsers } from '../api'

const users = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const search = ref('')
const loading = ref(false)

async function loadUsers() {
  loading.value = true
  try {
    const { data } = await adminUsers.list(page.value, 20, search.value || undefined)
    users.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)

async function toggleActive(id: number) {
  try {
    await adminUsers.toggleActive(id)
    await loadUsers()
  } catch { alert('操作失败') }
}

const totalPages = () => Math.ceil(total.value / 20)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-800 mb-6">用户管理</h1>

    <!-- 搜索 -->
    <div class="flex gap-2 mb-4">
      <input v-model="search" @keyup.enter="page = 1; loadUsers()" placeholder="搜索邮箱/昵称"
        class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <button @click="page = 1; loadUsers()"
        class="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700">搜索</button>
    </div>

    <div class="text-sm text-gray-500 mb-4">共 {{ total }} 个用户</div>

    <!-- 用户表格 -->
    <div v-if="loading" class="text-center text-gray-400 py-8">加载中...</div>
    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 text-gray-600 font-medium">邮箱</th>
              <th class="text-left px-4 py-3 text-gray-600 font-medium">昵称</th>
              <th class="text-left px-4 py-3 text-gray-600 font-medium">推送时间</th>
              <th class="text-left px-4 py-3 text-gray-600 font-medium">状态</th>
              <th class="text-left px-4 py-3 text-gray-600 font-medium">注册时间</th>
              <th class="text-left px-4 py-3 text-gray-600 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id" class="border-b border-gray-100 hover:bg-gray-50">
              <td class="px-4 py-3 text-gray-800">{{ u.email }}</td>
              <td class="px-4 py-3 text-gray-600">{{ u.nickname || '-' }}</td>
              <td class="px-4 py-3 text-gray-600">{{ u.push_time }}</td>
              <td class="px-4 py-3">
                <span :class="u.is_active ? 'text-green-600' : 'text-red-500'">
                  {{ u.is_active ? '活跃' : '停用' }}
                </span>
                <span v-if="u.push_enabled" class="ml-1 text-indigo-500">🔔</span>
              </td>
              <td class="px-4 py-3 text-gray-400">{{ u.created_at?.split('T')[0] }}</td>
              <td class="px-4 py-3">
                <button @click="toggleActive(u.id)"
                  :class="u.is_active ? 'text-red-500 hover:text-red-700' : 'text-green-500 hover:text-green-700'"
                  class="text-xs">
                  {{ u.is_active ? '停用' : '启用' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages() > 1" class="flex justify-center gap-2 mt-4">
      <button v-for="p in totalPages()" :key="p" @click="page = p; loadUsers()"
        class="px-3 py-1 text-sm rounded-lg"
        :class="page === p ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
        {{ p }}
      </button>
    </div>
  </div>
</template>
