import { create } from 'zustand'
import { Message, ToolType, UploadedFile, TOOLS } from '../types/chat'

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

  // Actions
  startTool: (tool: ToolType) => void
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  addJustoMessage: (content: string, options?: Message['options']) => void
  addUserMessage: (content: string) => void
  setProcessing: (status: boolean) => void
  setTyping: (status: boolean) => void
  setUploadProgress: (progress: number) => void
  setPendingFile: (file: UploadedFile | null) => void
  updateFileStatus: (fileId: string, status: UploadedFile['status'], progress?: number) => void
  setSessionId: (id: string) => void
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

  // Actions
  startTool: (tool) => {
    const toolConfig = TOOLS.find(t => t.id === tool)
    if (!toolConfig) return

    set({
      currentTool: tool,
      currentStep: 1,
      messages: [],
      sessionId: generateId(),
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

  setProcessing: (status) => set({ isProcessing: status }),

  setTyping: (status) => set({ isTyping: status }),

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

  nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),

  clearChat: () => set({
    messages: [],
    currentStep: 0,
    isProcessing: false,
    isTyping: false,
    uploadProgress: 0,
    pendingFile: null,
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
  }),
}))
