import axios, { AxiosProgressEvent } from 'axios'
import { ChatRequest, IntelligentChatResponse } from '../../types/chat'
import type { PlanExtractionResponse } from '../../types/extraction.types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 90000, // 90s — chat chains multiple LLM calls
})

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Chat API - Intelligent chat endpoint
export const chatApi = {
  /** Send a message to the intelligent chat (classification + semaphore) */
  sendIntelligentMessage: (data: { message: string; conversation_id?: string; context?: Record<string, string> }) =>
    api.post<IntelligentChatResponse>('/chat/message', data),

  /** Legacy tool-based chat */
  sendMessage: (data: ChatRequest) => api.post('/chat', data),

  /** List all intentions (reference) */
  getIntentions: () => api.get('/chat/intentions'),

  /** List all gatillos (reference) */
  getGatillos: () => api.get('/chat/gatillos'),

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

// Documents API - Extracción y gestión de documentos
export const documentsApi = {
  extractPlan: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<PlanExtractionResponse>('/documents/extract-plan', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// API endpoints por feature (legacy - para compatibilidad)
export const evaluationApi = {
  getQuestions: () => api.get('/evaluation/questions'),
  evaluate: (data: Record<string, unknown>) => api.post('/evaluation', data),
  /** Evalúa un NormalizedProjectIntake directamente */
  evaluateIntake: (intake: Record<string, unknown>) =>
    api.post('/evaluation/intake', intake, { params: { include_rag: false } }),
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

// Intake Interfaces
export interface IntakeRequest {
  tool: 'evaluation' | 'compliance' | 'query'
  legalProfile: {
    // Identity
    orgType: string
    orgTypeOther?: string
    orgPurpose: string
    orgPurposeOther?: string
    seeksProfits: boolean | null

    // Formalization
    hasLegalStatus: string | null
    rucStatus: string | null
    specialRegistries: string[]

    // Income
    handlesMoney: boolean | null
    receivesForeignFunds: boolean | null
    incomeSources: string[]

    // International Cooperation
    receivesInternationalCooperation: boolean | null
    apciStatus: string | null

    // HR
    hiringModalities: string[]
    contractsValid: string | null

    // Accounting
    accountingRecords: string | null
    accountingRecordsDetail: string | null
    availableDocuments: string[]

    // Governance
    hasGovernanceBodies: boolean | null
    hasLegalRepresentative: string | null

    // Intangibles
    intangibleAssets: string[]
  }
  toolSpecific: {
    // Evaluation
    evaluationGoals?: string[]
    legalAreas?: string[]
    urgency?: string

    // Compliance  
    complianceGoal?: string
    timeline?: string

    // Query
    queryArea?: string
    specificQuestion?: string
  }
}

export interface IntakeValidationResponse {
  valid: boolean
  errors?: {
    field: string
    message: string
  }[]
  warnings?: {
    field: string
    message: string
    severity: 'low' | 'medium'
  }[]
  riskSignals: {
    derivationRequired: boolean
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH'
    reasons: string[]
  }
}

export const intakeApi = {
  getQuestions: (tool?: string) => api.get(tool ? `/intake/questions/${tool}` : '/intake/questions'),
  getOptions: () => api.get('/intake/options'),
  validate: (data: IntakeRequest) => api.post<IntakeValidationResponse>('/intake/validate', data),
  submit: (data: IntakeRequest) => api.post<IntakeValidationResponse>('/intake/submit', data),
  getSummary: (tool: string) => api.get(`/intake/summary/${tool}`),
}
