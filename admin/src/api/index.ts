import client from './client'

export const adminAuth = {
  login: (email: string, password: string) =>
    client.post('/auth/login', { email, password }),
}

export const adminUsers = {
  list: (page = 1, pageSize = 20, search?: string) =>
    client.get('/admin/users/', { params: { page, page_size: pageSize, search } }),
  get: (id: number) => client.get(`/admin/users/${id}`),
  toggleActive: (id: number) => client.put(`/admin/users/${id}/toggle-active`),
}

export const adminAIModels = {
  list: () => client.get('/admin/ai-models/'),
  create: (data: any) => client.post('/admin/ai-models/', data),
  update: (id: number, data: any) => client.put(`/admin/ai-models/${id}`, data),
  delete: (id: number) => client.delete(`/admin/ai-models/${id}`),
}

export const adminEmailPool = {
  list: () => client.get('/admin/email-pool/'),
  create: (data: any) => client.post('/admin/email-pool/', data),
  update: (id: number, data: any) => client.put(`/admin/email-pool/${id}`, data),
  delete: (id: number) => client.delete(`/admin/email-pool/${id}`),
  test: (id: number) => client.post(`/admin/email-pool/${id}/test`),
}

export const adminStats = {
  dashboard: () => client.get('/admin/stats/dashboard'),
  push: (days = 7) => client.get('/admin/stats/push', { params: { days } }),
  email: () => client.get('/admin/stats/email'),
}
