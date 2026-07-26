import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
})

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On 401, attempt a single token refresh, then retry the original request
let isRefreshing = false
let pendingQueue = []

function processQueue(error, token = null) {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  pendingQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true
      const refreshToken = localStorage.getItem('refresh_token')

      try {
        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        processQueue(null, data.access_token)
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

// ---- Endpoint helpers ----

export const authApi = {
  register: (payload) => api.post('/auth/register', payload),
  login: (payload) => api.post('/auth/login', payload),
  me: () => api.get('/auth/me'),
}

export const xrayApi = {
  upload: (file, onUploadProgress) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/xray/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    })
  },
  status: (xrayId) => api.get(`/xray/${xrayId}/status`),
  history: (patientId) => api.get(`/patients/${patientId}/history`),
}

export const predictionApi = {
  get: (predictionId) => api.get(`/predictions/${predictionId}`),
}

export const doctorApi = {
  patients: (doctorId) => api.get(`/doctors/${doctorId}/patients`),
  review: (predictionId, payload) => api.post(`/doctors/predictions/${predictionId}/review`, payload),
}

export const reportApi = {
  generate: (predictionId, params) => api.post(`/reports/${predictionId}/generate`, null, { params }),
  download: (reportId) => api.get(`/reports/${reportId}`, { responseType: 'blob' }),
}

export const chatApi = {
  send: (question) => api.post('/chat', { question }),
  history: (userId) => api.get(`/chat/${userId}/history`),
}
