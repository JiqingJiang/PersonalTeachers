<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userApi, preferencesApi } from '../api'
const profile = ref<any>({})
const prefs = ref<any>({})
const pushTime = ref('08:00')
const pushEnabled = ref(true)
const categoryWeights = ref<Record<string, number>>({ historical: 0.3, modern: 0.4, common: 0.1, future_self: 0.2 })
const saving = ref(false)

// 修改密码
const oldPassword = ref('')
const newPassword = ref('')
const changingPassword = ref(false)

onMounted(async () => {
  const [profileRes, prefRes] = await Promise.all([
    userApi.getProfile(),
    preferencesApi.get(),
  ])
  profile.value = profileRes.data
  prefs.value = prefRes.data
  pushTime.value = prefRes.data.push_time || '08:00'
  pushEnabled.value = prefRes.data.push_enabled ?? true
  if (prefRes.data.mentor_category_prefs) {
    categoryWeights.value = prefRes.data.mentor_category_prefs
  }
})

const timeOptions = Array.from({ length: 17 }, (_, i) => {
  const h = i + 6 // 06:00 ~ 22:00
  return `${String(h).padStart(2, '0')}:00`
})

async function savePushSettings() {
  saving.value = true
  try {
    await preferencesApi.updatePush({
      push_time: pushTime.value,
      push_enabled: pushEnabled.value,
    })
    alert('推送设置已保存')
  } catch { alert('保存失败') }
  finally { saving.value = false }
}

async function saveCategoryWeights() {
  saving.value = true
  try {
    await preferencesApi.updateCategoryWeights(categoryWeights.value)
    alert('类别权重已保存')
  } catch { alert('保存失败') }
  finally { saving.value = false }
}

async function changePassword() {
  changingPassword.value = true
  try {
    await userApi.changePassword(oldPassword.value, newPassword.value)
    oldPassword.value = ''
    newPassword.value = ''
    alert('密码已修改')
  } catch (e: any) {
    alert(e.response?.data?.detail || '修改失败')
  } finally {
    changingPassword.value = false
  }
}

async function updateProfile() {
  try {
    await userApi.updateProfile({
      nickname: profile.value.nickname,
      age: profile.value.age,
      profession: profile.value.profession,
    })
    alert('个人信息已更新')
  } catch { alert('更新失败') }
}

const categories = [
  { key: 'historical', name: '历史人物', emoji: '📜' },
  { key: 'modern', name: '现代人物', emoji: '💼' },
  { key: 'common', name: '普通百姓', emoji: '👥' },
  { key: 'future_self', name: '未来自己', emoji: '🔮' },
]
</script>

<template>
  <div class="max-w-2xl">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">设置</h1>

    <!-- 个人信息 -->
    <div class="bg-white rounded-xl p-6 border border-gray-200 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">个人信息</h2>
      <div class="space-y-3">
        <div>
          <label class="block text-sm text-gray-600 mb-1">昵称</label>
          <input v-model="profile.nickname" class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm text-gray-600 mb-1">年龄</label>
            <input v-model.number="profile.age" type="number" class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">职业</label>
            <input v-model="profile.profession" class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>
        </div>
        <button @click="updateProfile"
          class="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700">保存</button>
      </div>
    </div>

    <!-- 推送设置 -->
    <div class="bg-white rounded-xl p-6 border border-gray-200 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">推送设置</h2>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">启用推送</span>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="pushEnabled" class="sr-only peer" />
            <div class="w-9 h-5 bg-gray-200 peer-checked:bg-indigo-600 rounded-full peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all"></div>
          </label>
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">推送时间</label>
          <select v-model="pushTime" class="px-3 py-2 border rounded-lg text-sm">
            <option v-for="t in timeOptions" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
        <button @click="savePushSettings" :disabled="saving"
          class="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50">
          {{ saving ? '保存中...' : '保存推送设置' }}
        </button>
      </div>
    </div>

    <!-- 导师类别权重 -->
    <div class="bg-white rounded-xl p-6 border border-gray-200 mb-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">导师类别权重</h2>
      <div class="space-y-3">
        <div v-for="cat in categories" :key="cat.key" class="flex items-center gap-3">
          <span class="text-sm w-24">{{ cat.emoji }} {{ cat.name }}</span>
          <input
            type="range" min="0" max="1" step="0.05"
            v-model.number="categoryWeights[cat.key]"
            class="flex-1 accent-indigo-600"
          />
          <span class="text-xs text-gray-600 w-10 text-right">{{ (categoryWeights[cat.key] * 100).toFixed(0) }}%</span>
        </div>
      </div>
      <button @click="saveCategoryWeights" :disabled="saving"
        class="mt-4 px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50">
        {{ saving ? '保存中...' : '保存类别权重' }}
      </button>
    </div>

    <!-- 修改密码 -->
    <div class="bg-white rounded-xl p-6 border border-gray-200">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">修改密码</h2>
      <div class="space-y-3">
        <input v-model="oldPassword" type="password" placeholder="当前密码"
          class="w-full px-3 py-2 border rounded-lg text-sm" />
        <input v-model="newPassword" type="password" placeholder="新密码"
          class="w-full px-3 py-2 border rounded-lg text-sm" />
        <button @click="changePassword" :disabled="changingPassword"
          class="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 disabled:opacity-50">
          {{ changingPassword ? '修改中...' : '修改密码' }}
        </button>
      </div>
    </div>
  </div>
</template>
