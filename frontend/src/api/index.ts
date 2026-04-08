import client from './client'

export const authApi = {
  sendCode: (email: string, purpose: string) =>
    client.post('/auth/send-code', { email, purpose }),
  register: (email: string, password: string, code: string, nickname?: string) =>
    client.post('/auth/register', { email, password, code, nickname }),
  login: (email: string, password: string) =>
    client.post('/auth/login', { email, password }),
  refresh: (refreshToken: string) =>
    client.post('/auth/refresh', { refresh_token: refreshToken }),
  resetPassword: (email: string, code: string, newPassword: string) =>
    client.post('/auth/reset-password', { email, code, new_password: newPassword }),
  getMe: () => client.get('/auth/me'),
}

export const userApi = {
  getProfile: () => client.get('/users/profile'),
  updateProfile: (data: any) => client.put('/users/profile', data),
  changePassword: (oldPassword: string, newPassword: string) =>
    client.put('/users/password', { old_password: oldPassword, new_password: newPassword }),
}

export const keywordApi = {
  list: (quadrant?: number) =>
    client.get('/keywords/', { params: { quadrant } }),
  quadrants: () => client.get('/keywords/quadrants'),
  create: (data: any) => client.post('/keywords/', data),
  update: (id: number, data: any) => client.put(`/keywords/custom/${id}`, data),
  delete: (id: number) => client.delete(`/keywords/custom/${id}`),
}

export const mentorApi = {
  list: (category?: string) =>
    client.get('/mentors/', { params: { category } }),
  categories: () => client.get('/mentors/categories'),
  create: (data: any) => client.post('/mentors/', data),
  update: (id: number, data: any) => client.put(`/mentors/custom/${id}`, data),
  delete: (id: number) => client.delete(`/mentors/custom/${id}`),
}

export const preferencesApi = {
  get: () => client.get('/preferences/'),
  updatePush: (data: any) => client.put('/preferences/push', data),
  updateKeywordWeights: (weights: Record<number, number>) =>
    client.put('/preferences/keyword-weights', { weights }),
  updateMentorPrefs: (mentors: any[]) =>
    client.put('/preferences/mentor-prefs', { mentors }),
  updateCategoryWeights: (data: any) =>
    client.put('/preferences/category-weights', data),
}

export const quotesApi = {
  preview: (count: number = 3) => client.post('/quotes/preview', { count }),
  history: (page: number = 1, pageSize: number = 20, keyword?: string) =>
    client.get('/quotes/history', { params: { page, page_size: pageSize, keyword } }),
}
