<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userApi, preferencesApi, quotesApi } from '../api'
const profile = ref<any>({})
const prefs = ref<any>({})
const pushTime = ref('08:00')
const pushEnabled = ref(true)
const pushCount = ref(10)
const maxWords = ref(100)
const personalBio = ref('')
const personalizationWeight = ref(0.5)
const categoryWeights = ref<Record<string, number>>({ historical: 0.3, modern: 0.4, common: 0.1, future_self: 0.2 })
const saving = ref(false)

// 修改密码
const oldPassword = ref('')
const newPassword = ref('')
const changingPassword = ref(false)

// 测试邮件
const sendingTestEmail = ref(false)
const testEmailCount = ref(3)

async function sendTestEmail() {
  sendingTestEmail.value = true
  try {
    const { data } = await quotesApi.testEmail(testEmailCount.value)
    alert(data.message || '测试邮件已发送')
  } catch (e: any) {
    alert('发送失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    sendingTestEmail.value = false
  }
}

// 时间选择：小时和分钟
const pushHour = ref(8)
const pushMinute = ref(0)

onMounted(async () => {
  const [profileRes, prefRes] = await Promise.all([
    userApi.getProfile(),
    preferencesApi.get(),
  ])
  profile.value = profileRes.data
  prefs.value = prefRes.data
  pushTime.value = prefRes.data.push_time || '08:00'
  pushEnabled.value = prefRes.data.push_enabled ?? true
  pushCount.value = prefRes.data.push_count ?? 10
  maxWords.value = prefRes.data.max_words ?? 100
  personalizationWeight.value = prefRes.data.personalization_weight ?? 0.5
  if (prefRes.data.mentor_category_prefs) {
    categoryWeights.value = prefRes.data.mentor_category_prefs
  }
  // 解析时间
  if (profileRes.data.personal_bio) {
    personalBio.value = profileRes.data.personal_bio
  }
  if (profileRes.data.personalization_weight !== undefined) {
    personalizationWeight.value = profileRes.data.personalization_weight
  }
  const parts = pushTime.value.split(':')
  pushHour.value = parseInt(parts[0])
  pushMinute.value = parseInt(parts[1])
})

const hourOptions = Array.from({ length: 24 }, (_, i) => i)
const minuteOptions = Array.from({ length: 60 }, (_, i) => i)
const pushCountOptions = Array.from({ length: 10 }, (_, i) => i + 1)

async function savePushSettings() {
  saving.value = true
  try {
    const timeStr = `${String(pushHour.value).padStart(2, '0')}:${String(pushMinute.value).padStart(2, '0')}`
    await preferencesApi.updatePush({
      push_time: timeStr,
      push_enabled: pushEnabled.value,
      push_count: pushCount.value,
      max_words: maxWords.value,
    })
    pushTime.value = timeStr
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
      personal_bio: personalBio.value,
      personalization_weight: personalizationWeight.value,
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

function getPersonalizationLabel(w: number): string {
  if (w <= 0.2) return '低 - 普适性内容为主'
  if (w <= 0.5) return '中 - 适度结合背景'
  if (w <= 0.8) return '高 - 大部分内容贴合背景'
  return '极高 - 完全针对个人背景'
}
</script>

<template>
  <div class="max-w-2xl">
    <h1 class="text-3xl font-display font-bold text-ink tracking-tight mb-8">设置</h1>

    <!-- 个人信息 -->
    <div class="bg-surface-card rounded-lg p-6 shadow-card border border-ink-light/10 mb-6">
      <h2 class="text-lg font-semibold text-ink mb-1">个人信息</h2>
      <p class="text-sm text-ink-muted mb-5">完善个人信息，让系统更好地了解你</p>
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-ink-secondary mb-1.5 font-medium">昵称</label>
          <input v-model="profile.nickname"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-ink-secondary mb-1.5 font-medium">年龄</label>
            <input v-model.number="profile.age" type="number"
              class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          </div>
          <div>
            <label class="block text-sm text-ink-secondary mb-1.5 font-medium">职业</label>
            <input v-model="profile.profession"
              class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
          </div>
        </div>
        <div>
          <label class="block text-sm text-ink-secondary mb-1.5 font-medium">个人背景简介</label>
          <textarea v-model="personalBio" rows="3"
            class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all resize-none"
            placeholder="简要描述你的身份背景，如：程序员、创业者、大学生、宝妈等，系统会根据你的背景生成更贴合你的内容"></textarea>
        </div>
        <div>
          <label class="block text-sm text-ink-secondary mb-1.5 font-medium">
            个性化权重
            <span class="ml-2 text-xs text-brand-600 font-medium">{{ getPersonalizationLabel(personalizationWeight) }}</span>
          </label>
          <input type="range" min="0" max="1" step="0.1" v-model.number="personalizationWeight"
            class="w-full accent-brand" />
          <div class="flex justify-between text-xs text-ink-muted mt-1.5">
            <span>普适性</span>
            <span>个性化</span>
          </div>
        </div>
        <button @click="updateProfile"
          class="px-6 py-2.5 bg-gradient-to-r from-brand to-brand-dark text-white text-sm font-medium rounded-lg shadow-amber hover:shadow-elevated transition-all duration-200">
          保存个人信息
        </button>
      </div>
    </div>

    <!-- 推送设置 -->
    <div class="bg-surface-card rounded-lg p-6 shadow-card border border-ink-light/10 mb-6">
      <h2 class="text-lg font-semibold text-ink mb-1">推送设置</h2>
      <p class="text-sm text-ink-muted mb-5">管理每日语录推送的时间和频率</p>
      <div class="space-y-5">
        <div class="flex items-center justify-between">
          <span class="text-sm text-ink-secondary font-medium">启用推送</span>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="pushEnabled" class="sr-only peer" />
            <div class="w-10 h-5.5 bg-ink-light/30 peer-checked:bg-brand rounded-full peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4.5 after:w-4.5 after:transition-all after:shadow-sm"></div>
          </label>
        </div>
        <div>
          <label class="block text-sm text-ink-secondary mb-1.5 font-medium">推送时间</label>
          <div class="flex gap-2 items-center">
            <select v-model.number="pushHour"
              class="px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all">
              <option v-for="h in hourOptions" :key="h" :value="h">{{ String(h).padStart(2, '0') }}</option>
            </select>
            <span class="text-ink-muted font-medium">:</span>
            <select v-model.number="pushMinute"
              class="px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all">
              <option v-for="m in minuteOptions" :key="m" :value="m">{{ String(m).padStart(2, '0') }}</option>
            </select>
          </div>
        </div>
        <div>
          <label class="block text-sm text-ink-secondary mb-1.5 font-medium">
            每次推送语录数量
            <span class="ml-2 text-brand-600 font-medium">{{ pushCount }} 条</span>
          </label>
          <select v-model.number="pushCount"
            class="px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all">
            <option v-for="c in pushCountOptions" :key="c" :value="c">{{ c }} 条</option>
          </select>
          <p class="text-xs text-ink-muted mt-1.5">每封邮件中的语录条数（1~10条）</p>
        </div>
        <div>
          <label class="block text-sm text-ink-secondary mb-1.5 font-medium">
            每条语录最大字数
            <span class="ml-2 text-brand-600 font-medium">{{ maxWords }} 字</span>
          </label>
          <input type="range" min="30" max="200" step="10" v-model.number="maxWords"
            class="w-full accent-brand" />
          <div class="flex justify-between text-xs text-ink-muted mt-1.5">
            <span>30字</span>
            <span>200字</span>
          </div>
        </div>
        <button @click="savePushSettings" :disabled="saving"
          class="px-6 py-2.5 bg-gradient-to-r from-brand to-brand-dark text-white text-sm font-medium rounded-lg shadow-amber hover:shadow-elevated transition-all duration-200 disabled:opacity-50 disabled:shadow-none">
          {{ saving ? '保存中...' : '保存推送设置' }}
        </button>
      </div>
    </div>

    <!-- 测试邮件 -->
    <div class="bg-surface-card rounded-lg p-6 shadow-card border border-ink-light/10 mb-6">
      <h2 class="text-lg font-semibold text-ink mb-1">测试邮件</h2>
      <p class="text-sm text-ink-muted mb-5">发送测试邮件到你的注册邮箱，验证推送效果</p>
      <div class="flex items-center gap-3">
        <select v-model.number="testEmailCount"
          class="px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all">
          <option v-for="c in [1,2,3,4,5]" :key="c" :value="c">{{ c }} 条语录</option>
        </select>
        <button @click="sendTestEmail" :disabled="sendingTestEmail"
          class="px-6 py-2.5 bg-info text-white text-sm font-medium rounded-lg hover:brightness-110 disabled:opacity-50 transition-all duration-200">
          {{ sendingTestEmail ? '发送中...' : '发送测试邮件' }}
        </button>
      </div>
    </div>

    <!-- 导师类别权重 -->
    <div class="bg-surface-card rounded-lg p-6 shadow-card border border-ink-light/10 mb-6">
      <h2 class="text-lg font-semibold text-ink mb-1">导师类别权重</h2>
      <p class="text-sm text-ink-muted mb-5">调整各类别导师的出现频率</p>
      <div class="space-y-4">
        <div v-for="cat in categories" :key="cat.key" class="flex items-center gap-4">
          <span class="text-sm text-ink-secondary w-28 shrink-0">{{ cat.emoji }} {{ cat.name }}</span>
          <input
            type="range" min="0" max="1" step="0.05"
            v-model.number="categoryWeights[cat.key]"
            class="flex-1 accent-brand"
          />
          <span class="text-xs text-ink-secondary w-12 text-right font-medium tabular-nums">{{ (categoryWeights[cat.key] * 100).toFixed(0) }}%</span>
        </div>
      </div>
      <button @click="saveCategoryWeights" :disabled="saving"
        class="mt-6 px-6 py-2.5 bg-gradient-to-r from-brand to-brand-dark text-white text-sm font-medium rounded-lg shadow-amber hover:shadow-elevated transition-all duration-200 disabled:opacity-50 disabled:shadow-none">
        {{ saving ? '保存中...' : '保存类别权重' }}
      </button>
    </div>

    <!-- 修改密码 -->
    <div class="bg-surface-card rounded-lg p-6 shadow-card border border-ink-light/10">
      <h2 class="text-lg font-semibold text-ink mb-1">修改密码</h2>
      <p class="text-sm text-ink-muted mb-5">定期更新密码以保护账户安全</p>
      <div class="space-y-4">
        <input v-model="oldPassword" type="password" placeholder="当前密码"
          class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
        <input v-model="newPassword" type="password" placeholder="新密码"
          class="w-full px-4 py-2.5 bg-surface border border-ink-light/30 rounded-lg text-sm text-ink placeholder-ink-muted focus:ring-2 focus:ring-brand focus:border-brand outline-none transition-all" />
        <button @click="changePassword" :disabled="changingPassword"
          class="px-6 py-2.5 bg-danger text-white text-sm font-medium rounded-lg hover:brightness-110 disabled:opacity-50 transition-all duration-200">
          {{ changingPassword ? '修改中...' : '修改密码' }}
        </button>
      </div>
    </div>
  </div>
</template>
