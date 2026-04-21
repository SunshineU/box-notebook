import axios from 'axios'

const API_BASE = '/api'

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000
})

// 请求拦截器 - 添加 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 处理 401
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login', { username, password }),
  register: (username, email, password) =>
    api.post('/auth/register', { username, email, password }),
  getMe: () => api.get('/auth/me')
}

export const itemAPI = {
  getAll: (keyword) => api.get('/items', { params: { keyword } }),
  getById: (id) => api.get(`/items/${id}`),
  create: (data) => api.post('/items', data),
  update: (id, data) => api.put(`/items/${id}`, data),
  delete: (id) => api.delete(`/items/${id}`),
  exportCSV: () => api.get('/items/export/csv', { responseType: 'blob' }),
  importCSV: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/items/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export default api
