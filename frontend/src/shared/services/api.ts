import axios, { AxiosProgressEvent } from 'axios'
import { ChatRequest } from '../../types/chat'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Chat API - Principal endpoint conversacional
export const chatApi = {
  sendMessage: (data: ChatRequest) => api.post('/chat', data),

  uploadDocument: (
    file: File,
    tool: string,
    onProgress?: (progressEvent: AxiosProgressEvent) => void
  ) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('tool', tool)

    return api.post('/chat/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    })
  },

  getSession: (sessionId: string) => api.get(`/chat/session/${sessionId}`),
}

// API endpoints por feature (legacy - para compatibilidad)
export const evaluationApi = {
  getQuestions: () => api.get('/evaluation/questions'),
  evaluate: (data: Record<string, unknown>) => api.post('/evaluation', data),
}

export const queryApi = {
  getQuestions: () => api.get('/query/questions'),
  query: (data: Record<string, unknown>) => api.post('/query', data),
}

export const advisorPrepApi = {
  getQuestions: () => api.get('/advisor-prep/questions'),
  prepare: (data: Record<string, unknown>) => api.post('/advisor-prep', data),
}

export const complianceApi = {
  getQuestions: () => api.get('/compliance/questions'),
  generateRoute: (data: Record<string, unknown>) => api.post('/compliance', data),
}
