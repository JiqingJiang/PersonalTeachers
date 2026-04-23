import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes: [
    { path: '/', name: 'login', component: () => import('../views/LoginView.vue') },
    { path: '/dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue'), meta: { auth: true } },
    { path: '/users', name: 'users', component: () => import('../views/UsersView.vue'), meta: { auth: true } },
    { path: '/ai-models', name: 'ai-models', component: () => import('../views/AIModelsView.vue'), meta: { auth: true } },
    { path: '/email-pool', name: 'email-pool', component: () => import('../views/EmailPoolView.vue'), meta: { auth: true } },
    { path: '/failed-logs', name: 'failed-logs', component: () => import('../views/FailedLogsView.vue'), meta: { auth: true } },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('admin_token')
  if (to.meta.auth && !token) return { name: 'login' }
})

export default router
