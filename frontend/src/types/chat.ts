// Types for GPT Legal Chat System

export type ToolType = 'evaluation' | 'compliance' | 'query' | 'advisor' | 'chat' | null

export type MessageSender = 'justo' | 'user'

export type MessageContentType =
  | 'text'
  | 'options'
  | 'file_upload'
  | 'file_uploaded'
  | 'progress'
  | 'semaphore_response'
  | 'error'

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

// =============================================================================
// INTELLIGENT CHAT TYPES (matching backend schemas)
// =============================================================================

export type SemaphoreLevel = 'verde' | 'amarillo' | 'rojo'

export type ActionType = 'upload_file' | 'derive_to_advisor' | 'provide_context' | 'none'

export interface ChatClassification {
  intention: string
  intention_name: string
  semaphore: SemaphoreLevel
  confidence: number
  gatillos_detected: string[]
  context_required: string[]
}

export interface LegalSource {
  title: string
  article?: string
  authority?: string
  url?: string
}

export interface SuggestedAction {
  type: ActionType
  label: string
  description: string
  endpoint?: string
  metadata?: Record<string, unknown>
}

export interface IntelligentChatResponse {
  message: string
  classification: ChatClassification
  sources: LegalSource[]
  actions: SuggestedAction[]
  disclaimers: string[]
  conversation_id?: string
  timestamp: string
}

// =============================================================================
// MESSAGE (extended for intelligent chat)
// =============================================================================

export interface Message {
  id: string
  sender: MessageSender
  content: string
  contentType: MessageContentType
  options?: MessageOption[]
  file?: UploadedFile
  timestamp: Date
  /** True mientras el mensaje se está recibiendo token a token (streaming) */
  isStreaming?: boolean
  /** True si el contenido llegó token a token (ya se vio construirse; no re-animar con typewriter) */
  wasStreamed?: boolean
  /** Texto de estado mostrado durante el streaming ("Buscando normativa...") */
  streamingStatus?: string
  metadata?: {
    step?: number
    toolContext?: ToolType
    requiresResponse?: boolean
    classification?: ChatClassification
    sources?: LegalSource[]
    actions?: SuggestedAction[]
    disclaimers?: string[]
    errorType?: 'network' | 'server' | 'validation' | 'timeout'
  }
}

// =============================================================================
// CHAT REQUEST / RESPONSE (legacy tool-based)
// =============================================================================

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

// Results types - aligned with backend EvaluationResponse
export interface GapDetail {
  id: string
  organization_id?: string
  organization_name?: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  intention: string
  description: string
  impact: string
  recommendation: string
  legal_basis?: string[]
}

export interface OrganizationEvaluation {
  organization_id: string
  organization_name: string
  role: string
  requirements_fulfilled: number
  requirements_partial: number
  requirements_not_fulfilled: number
  gaps: GapDetail[]
  detected_intentions: string[]
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
}

export interface RiskSummary {
  overall_level: 'LOW' | 'MEDIUM' | 'HIGH'
  derivation_color: 'green' | 'yellow' | 'red'
  requires_professional_advice: boolean
  professional_advice_reason?: string
  risk_factors: string[]
}

export interface EvaluationResult {
  viability: 'viable' | 'viable_with_conditions' | 'not_viable' | 'requires_review'
  viability_explanation: string
  traffic_light: 'green' | 'yellow' | 'red'
  organizations: OrganizationEvaluation[]
  shared_gaps: GapDetail[]
  risk_summary: RiskSummary
  total_requirements: number
  total_gaps: number
  critical_gaps: number
  project_intentions: string[]
  next_steps: string[]
  alternatives: string[]
  path_to_viability?: string
  evidence_sources: Array<{
    title: string
    authority_level: number
    url?: string
    relevance: string
  }>
  confidence_level: string
  assumptions: string[]
  limitations: string[]
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
    id: 'chat',
    name: 'Consulta libre',
    description: 'Escribe cualquier consulta legal y nuestro sistema clasificará tu intención y te dará la orientación adecuada.',
    icon: 'message-circle',
    initialMessage: '¡Hola! Soy **JUSTO**, tu asistente legal inteligente.\n\nPuedes preguntarme cualquier cosa sobre temas legales para organizaciones civiles en Perú: formalización, tributación, contratación, propiedad intelectual, y más.\n\n¿En qué puedo ayudarte hoy?'
  },
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

// Max message length (5000 matches backend ChatRequest max_length; allows document content in messages)
export const MAX_MESSAGE_LENGTH = 5000
