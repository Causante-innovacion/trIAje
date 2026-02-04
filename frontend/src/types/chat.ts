// Types for GPT Legal Chat System

export type ToolType = 'evaluation' | 'compliance' | 'advisor' | null

export type MessageSender = 'justo' | 'user'

export type MessageContentType = 'text' | 'options' | 'file_upload' | 'file_uploaded' | 'progress'

export interface MessageOption {
  id: string
  label: string
  value: string
  icon?: 'check' | 'x'
}

export interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  progress: number
  status: 'uploading' | 'analyzing' | 'complete' | 'error'
  extractedData?: Record<string, unknown>
}

export interface Message {
  id: string
  sender: MessageSender
  content: string
  contentType: MessageContentType
  options?: MessageOption[]
  file?: UploadedFile
  timestamp: Date
  metadata?: {
    step?: number
    toolContext?: ToolType
    requiresResponse?: boolean
  }
}

export interface ChatState {
  messages: Message[]
  currentTool: ToolType
  currentStep: number
  isProcessing: boolean
  isTyping: boolean
  uploadProgress: number
  sessionId: string | null
}

export interface ChatRequest {
  sessionId?: string
  tool: ToolType
  message: string
  step?: number
  fileData?: Record<string, unknown>
}

export interface ChatResponse {
  sessionId: string
  message: string
  contentType: MessageContentType
  options?: MessageOption[]
  requiresFileUpload?: boolean
  nextStep?: number
  isComplete?: boolean
  result?: EvaluationResult | ComplianceResult | AdvisorPackage
}

// Results types
export interface EvaluationResult {
  viability: 'viable' | 'inviable_with_alternatives'
  viability_explanation: string
  traffic_light: 'green' | 'yellow'
  risk_assessment: {
    level: string
    factors: string[]
  }
  gaps_found: Array<{
    requirement: string
    status: string
    priority: string
  }>
  alternatives: string[]
  next_steps: string[]
  escalation_recommended: boolean
  confidence_level: string
  disclaimers: string[]
}

export interface ComplianceResult {
  total_milestones: number
  completed_milestones: number
  progress_percentage: number
  milestones: Milestone[]
  estimated_total_duration?: string
}

export interface Milestone {
  id: string
  name: string
  description: string
  phase: string
  status: 'pending' | 'in_progress' | 'completed'
  prerequisites: string[]
  documents_required: string[]
  steps: string[]
  authority?: string
}

export interface AdvisorPackage {
  recommended_advisor_type: string
  executive_summary: string
  meeting_objectives: string[]
  legal_issues: Array<{
    id: string
    title: string
    severity: 'low' | 'medium' | 'high'
  }>
  questions_for_advisor: string[]
  documents_to_bring: string[]
}

// Tool definitions
export interface Tool {
  id: ToolType
  name: string
  description: string
  icon: string
  initialMessage: string
}

export const TOOLS: Tool[] = [
  {
    id: 'evaluation',
    name: 'Evaluar proyecto',
    description: 'Analizamos riesgos legales y la viabilidad técnica de tus iniciativas sociales con rigor jurídico.',
    icon: 'chart',
    initialMessage: 'Perfecto, voy a evaluar la viabilidad legal de tu proyecto. ¿Vienes del Generador Cívico con un plan ya desarrollado?\n\nSi tienes un plan estratégico del Generador Cívico, puedo extraer información clave (descripción del proyecto, financiamiento, equipo) y solo preguntarte lo que falta. Si no, no hay problema. Podemos empezar desde cero.'
  },
  {
    id: 'compliance',
    name: 'Ruta de cumplimiento',
    description: 'Hoja de ruta personalizada para asegurar que tu organización cumpla con todas las normativas vigentes.',
    icon: 'checklist',
    initialMessage: '¡Vamos a crear tu ruta de cumplimiento! Para comenzar, necesito conocer algunos detalles sobre tu organización.\n\n¿Qué tipo de organización tienes actualmente?'
  },
  {
    id: 'advisor',
    name: 'Preparar reunión',
    description: 'Sintetiza tus consultas y genera la documentación clave para una sesión eficiente con asesores legales.',
    icon: 'users',
    initialMessage: '¡Excelente! Te ayudaré a preparar todo para tu reunión con el asesor legal.\n\n¿Cuál es el tema principal que quieres tratar en la reunión?'
  }
]
