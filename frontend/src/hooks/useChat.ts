import { useCallback, useRef } from 'react'
import { useChatStore } from '../stores/chatStore'
import { chatApi } from '../shared/services/api'
import { ChatResponse, MAX_MESSAGE_LENGTH } from '../types/chat'
import axios from 'axios'

export function useChat() {
  const {
    messages,
    currentTool,
    currentStep,
    isProcessing,
    sessionId,
    conversationId,
    addUserMessage,
    addJustoMessage,
    addIntelligentResponse,
    addErrorMessage,
    setProcessing,
    setTyping,
    nextStep,
    setSessionId,
    setConversationId,
  } = useChatStore()

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Intelligent chat mode: uses /chat/message
  const sendIntelligentMessage = useCallback(async (content: string) => {
    if (!content.trim() || isProcessing) return

    // Validation: character limit
    if (content.length > MAX_MESSAGE_LENGTH) {
      addErrorMessage(
        `Tu mensaje excede el límite de ${MAX_MESSAGE_LENGTH} caracteres. Por favor, acórtalo e intenta de nuevo.`,
        'validation'
      )
      return
    }

    addUserMessage(content)
    setProcessing(true)
    setTyping(true)

    // Timeout warning after 10s
    timeoutRef.current = setTimeout(() => {
      // Only add the warning if still processing
      const state = useChatStore.getState()
      if (state.isProcessing) {
        // Don't add another message, just update the existing typing indicator logic
        // The UI will show the slow response message
      }
    }, 10000)

    try {
      const response = await chatApi.sendIntelligentMessage({
        message: content,
        conversation_id: conversationId || undefined,
      })

      if (timeoutRef.current) clearTimeout(timeoutRef.current)

      const data = response.data

      // Store conversation ID
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id)
      }

      setTyping(false)
      addIntelligentResponse(
        data.message,
        data.classification,
        data.sources,
        data.actions,
        data.disclaimers
      )
    } catch (error) {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      setTyping(false)

      if (axios.isAxiosError(error)) {
        if (!error.response) {
          // Network error
          addErrorMessage(
            'No se pudo conectar con el servidor. Verifica tu conexión a internet e intenta de nuevo.',
            'network'
          )
        } else if (error.response.status === 422) {
          // Validation error
          const detail = error.response.data?.detail || 'El mensaje no es válido.'
          addErrorMessage(
            `Error de validación: ${typeof detail === 'string' ? detail : JSON.stringify(detail)}`,
            'validation'
          )
        } else if (error.response.status >= 500) {
          // Server error
          addErrorMessage(
            'Error interno del servidor. Por favor, intenta de nuevo en unos segundos.',
            'server'
          )
        } else if (error.code === 'ECONNABORTED') {
          // Timeout
          addErrorMessage(
            'La solicitud tardó demasiado tiempo. El servidor puede estar ocupado. Intenta de nuevo.',
            'timeout'
          )
        } else {
          addErrorMessage(
            'Ocurrió un error inesperado. Por favor, intenta de nuevo.',
            'server'
          )
        }
      } else {
        addErrorMessage(
          'Ocurrió un error inesperado. Por favor, intenta de nuevo.',
          'server'
        )
      }
    } finally {
      setProcessing(false)
    }
  }, [
    isProcessing,
    conversationId,
    addUserMessage,
    addIntelligentResponse,
    addErrorMessage,
    setProcessing,
    setTyping,
    setConversationId,
  ])

  // Legacy tool-based chat
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isProcessing) return

    // If in intelligent chat mode, use the intelligent endpoint
    if (currentTool === 'chat') {
      return sendIntelligentMessage(content)
    }

    // Legacy flow for evaluation/compliance/advisor tools
    addUserMessage(content)
    setProcessing(true)
    setTyping(true)

    try {
      const response = await chatApi.sendMessage({
        sessionId: sessionId || undefined,
        tool: currentTool,
        message: content,
        step: currentStep,
      })

      const data: ChatResponse = response.data

      if (data.sessionId && !sessionId) {
        setSessionId(data.sessionId)
      }

      setTyping(false)
      addJustoMessage(
        data.message,
        data.options
      )

      if (data.nextStep) {
        nextStep()
      }
    } catch (error) {
      console.error('Chat error:', error)
      setTyping(false)
      addJustoMessage(
        'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.'
      )
    } finally {
      setProcessing(false)
    }
  }, [
    isProcessing,
    sessionId,
    currentTool,
    currentStep,
    sendIntelligentMessage,
    addUserMessage,
    addJustoMessage,
    setProcessing,
    setTyping,
    nextStep,
    setSessionId,
  ])

  const selectOption = useCallback(async (value: string, label: string) => {
    if (isProcessing) return

    addUserMessage(label)
    setProcessing(true)
    setTyping(true)

    try {
      const response = await chatApi.sendMessage({
        sessionId: sessionId || undefined,
        tool: currentTool,
        message: value,
        step: currentStep,
      })

      const data: ChatResponse = response.data

      setTyping(false)
      addJustoMessage(
        data.message,
        data.options
      )

      if (data.nextStep) {
        nextStep()
      }
    } catch (error) {
      console.error('Option selection error:', error)
      setTyping(false)
      addJustoMessage(
        'Lo siento, hubo un error. Por favor, intenta de nuevo.'
      )
    } finally {
      setProcessing(false)
    }
  }, [
    isProcessing,
    sessionId,
    currentTool,
    currentStep,
    addUserMessage,
    addJustoMessage,
    setProcessing,
    setTyping,
    nextStep,
  ])

  return {
    messages,
    currentTool,
    isProcessing,
    sendMessage,
    sendIntelligentMessage,
    selectOption,
  }
}
