import { create } from 'zustand'
import { Message, ToolType, UploadedFile, TOOLS, ChatClassification, LegalSource, SuggestedAction } from '../types/chat'
import type { PlanExtractionResponse } from '../types/extraction.types'

interface ChatStore {
  // State
  messages: Message[]
  currentTool: ToolType
  currentStep: number
  isProcessing: boolean
  isTyping: boolean
  uploadProgress: number
  sessionId: string | null
  pendingFile: UploadedFile | null
  extractedPlan: PlanExtractionResponse | null
  conversationId: string | null

  // Intelligent chat state
  lastClassification: ChatClassification | null
  lastSources: LegalSource[]
  lastActions: SuggestedAction[]
  error: string | null

  // Initial message to send on mount (for home page → chat transition)
  pendingInitialMessage: string | null

  // Actions
  startTool: (tool: ToolType) => void
  startIntelligentChat: (initialMessage?: string) => void
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  addJustoMessage: (content: string, options?: Message['options']) => void
  addUserMessage: (content: string) => void
  addIntelligentResponse: (
    content: string,
    classification: ChatClassification,
    sources: LegalSource[],
    actions: SuggestedAction[],
    disclaimers: string[]
  ) => void
  addErrorMessage: (content: string, errorType: Message['metadata'] extends infer M ? M extends { errorType?: infer E } ? E : never : never) => void
  setProcessing: (status: boolean) => void
  setTyping: (status: boolean) => void
  // Streaming actions
  startStreamingMessage: () => string
  setStreamingStatus: (id: string, status: string | null) => void
  setStreamingClassification: (id: string, classification: ChatClassification) => void
  setStreamingSources: (id: string, sources: LegalSource[]) => void
  appendToStreamingMessage: (id: string, text: string) => void
  finalizeStreamingMessage: (id: string, options: { actions?: SuggestedAction[]; disclaimers?: string[]; conversation_id?: string }) => void
  setUploadProgress: (progress: number) => void
  setPendingFile: (file: UploadedFile | null) => void
  updateFileStatus: (fileId: string, status: UploadedFile['status'], progress?: number) => void
  setSessionId: (id: string) => void
  setConversationId: (id: string) => void
  setExtractedPlan: (data: PlanExtractionResponse | null) => void
  setError: (error: string | null) => void
  clearError: () => void
  consumePendingMessage: () => string | null
  nextStep: () => void
  clearChat: () => void
  resetToHome: () => void
}

const generateId = () => Math.random().toString(36).substring(2, 15)

export const useChatStore = create<ChatStore>((set, get) => ({
  // Initial state
  messages: [],
  currentTool: null,
  currentStep: 0,
  isProcessing: false,
  isTyping: false,
  uploadProgress: 0,
  sessionId: null,
  pendingFile: null,
  extractedPlan: null,
  conversationId: null,

  // Intelligent chat state
  lastClassification: null,
  lastSources: [],
  lastActions: [],
  error: null,
  pendingInitialMessage: null,

  // Actions
  startTool: (tool) => {
    const toolConfig = TOOLS.find(t => t.id === tool)
    if (!toolConfig) return

    set({
      currentTool: tool,
      currentStep: 1,
      messages: [],
      sessionId: generateId(),
      error: null,
      lastClassification: null,
      lastSources: [],
      lastActions: [],
    })

    // Add initial message from JUSTO after a small delay for natural feel
    setTimeout(() => {
      get().addJustoMessage(toolConfig.initialMessage,
        tool === 'evaluation' ? [
          { id: '1', label: 'Sí, tengo un plan del Generador Cívico', value: 'yes', icon: 'check' },
          { id: '2', label: 'No, empiezo desde cero', value: 'no', icon: 'x' }
        ] : undefined
      )
    }, 300)
  },

  startIntelligentChat: (initialMessage?: string) => {
    set({
      currentTool: 'chat',
      currentStep: 1,
      messages: [],
      sessionId: generateId(),
      error: null,
      lastClassification: null,
      lastSources: [],
      lastActions: [],
      pendingInitialMessage: initialMessage || null,
    })

    const toolConfig = TOOLS.find(t => t.id === 'chat')
    if (toolConfig && !initialMessage) {
      setTimeout(() => {
        get().addJustoMessage(toolConfig.initialMessage)
      }, 300)
    }
  },

  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: generateId(),
      timestamp: new Date(),
    }
    set((state) => ({
      messages: [...state.messages, newMessage],
    }))
  },

  addJustoMessage: (content, options) => {
    get().addMessage({
      sender: 'justo',
      content,
      contentType: options ? 'options' : 'text',
      options,
      metadata: {
        step: get().currentStep,
        toolContext: get().currentTool,
        requiresResponse: !!options,
      },
    })
  },

  addUserMessage: (content) => {
    get().addMessage({
      sender: 'user',
      content,
      contentType: 'text',
    })
  },

  addIntelligentResponse: (content, classification, sources, actions, disclaimers) => {
    set({ lastClassification: classification, lastSources: sources, lastActions: actions })
    get().addMessage({
      sender: 'justo',
      content,
      contentType: 'semaphore_response',
      metadata: {
        classification,
        sources,
        actions,
        disclaimers,
        toolContext: 'chat',
      },
    })
  },

  addErrorMessage: (content, errorType) => {
    get().addMessage({
      sender: 'justo',
      content,
      contentType: 'error',
      metadata: { errorType: errorType as 'network' | 'server' | 'validation' | 'timeout' },
    })
  },

  setProcessing: (status) => set({ isProcessing: status }),

  setTyping: (status) => set({ isTyping: status }),

  // ── Streaming ──────────────────────────────────────────────────────────

  startStreamingMessage: () => {
    const id = generateId()
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id,
          sender: 'justo' as const,
          content: '',
          contentType: 'semaphore_response' as const,
          timestamp: new Date(),
          isStreaming: true,
          streamingStatus: 'Clasificando tu consulta\u2026',
          metadata: { toolContext: 'chat' as const },
        },
      ],
    }))
    return id
  },

  setStreamingStatus: (id, status) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, streamingStatus: status ?? undefined } : m
      ),
    }))
  },

  setStreamingClassification: (id, classification) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id
          ? { ...m, metadata: { ...m.metadata, classification } }
          : m
      ),
    }))
  },

  setStreamingSources: (id, sources) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id
          ? { ...m, metadata: { ...m.metadata, sources } }
          : m
      ),
    }))
  },

  appendToStreamingMessage: (id, text) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id
          ? { ...m, content: m.content + text, streamingStatus: undefined }
          : m
      ),
    }))
  },

  finalizeStreamingMessage: (id, { actions, disclaimers, conversation_id }) => {
    if (conversation_id) {
      set({ conversationId: conversation_id })
    }
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id
          ? {
              ...m,
              isStreaming: false,
              streamingStatus: undefined,
              metadata: {
                ...m.metadata,
                actions: actions ?? [],
                disclaimers: disclaimers ?? [],
              },
            }
          : m
      ),
    }))
  },

  setUploadProgress: (progress) => set({ uploadProgress: progress }),

  setPendingFile: (file) => set({ pendingFile: file }),

  updateFileStatus: (fileId, status, progress) => {
    set((state) => ({
      messages: state.messages.map((msg) => {
        if (msg.file?.id === fileId) {
          return {
            ...msg,
            file: {
              ...msg.file,
              status,
              progress: progress ?? msg.file.progress,
            },
          }
        }
        return msg
      }),
    }))
  },

  setSessionId: (id) => set({ sessionId: id }),

  setConversationId: (id) => set({ conversationId: id }),

  setExtractedPlan: (data) => set({ extractedPlan: data }),

  setError: (error) => set({ error }),

  clearError: () => set({ error: null }),

  consumePendingMessage: () => {
    const msg = get().pendingInitialMessage
    set({ pendingInitialMessage: null })
    return msg
  },

  nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),

  clearChat: () => set({
    messages: [],
    currentStep: 0,
    isProcessing: false,
    isTyping: false,
    uploadProgress: 0,
    pendingFile: null,
    error: null,
    lastClassification: null,
    lastSources: [],
    lastActions: [],
  }),

  resetToHome: () => set({
    messages: [],
    currentTool: null,
    currentStep: 0,
    isProcessing: false,
    isTyping: false,
    uploadProgress: 0,
    sessionId: null,
    pendingFile: null,
    extractedPlan: null,
    conversationId: null,
    lastClassification: null,
    lastSources: [],
    lastActions: [],
    error: null,
    pendingInitialMessage: null,
  }),
}))
