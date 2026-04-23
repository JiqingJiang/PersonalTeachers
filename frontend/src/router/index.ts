import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 首页（Landing Page）
    { path: '/', name: 'landing', component: () => import('../views/LandingView.vue') },
    // 认证页面（无侧边栏）
    { path: '/login', name: 'login', component: () => import('../views/auth/LoginView.vue') },
    { path: '/register', name: 'register', component: () => import('../views/auth/RegisterView.vue') },
    { path: '/reset-password', name: 'reset-password', component: () => import('../views/auth/ResetPasswordView.vue') },
    // 业务页面（有侧边栏）
    { path: '/dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue'), meta: { auth: true } },
    { path: '/keywords', name: 'keywords', component: () => import('../views/KeywordManagerView.vue'), meta: { auth: true } },
    { path: '/mentors', name: 'mentors', component: () => import('../views/MentorManagerView.vue'), meta: { auth: true } },
    { path: '/settings', name: 'settings', component: () => import('../views/SettingsView.vue'), meta: { auth: true } },
    { path: '/history', name: 'history', component: () => import('../views/HistoryView.vue'), meta: { auth: true } },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.auth && !token) {
    return { name: 'login' }
  }
})

export default router
