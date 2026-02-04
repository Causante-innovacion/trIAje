import { useCallback } from 'react'
import { useChatStore } from '../stores/chatStore'
import { chatApi } from '../shared/services/api'
import { ChatResponse } from '../types/chat'

export function useChat() {
  const {
    messages,
    currentTool,
    currentStep,
    isProcessing,
    sessionId,
    addUserMessage,
    addJustoMessage,
    setProcessing,
    setTyping,
    nextStep,
    setSessionId,
  } = useChatStore()

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isProcessing) return

    // Add user message
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

      // Update session ID if new
      if (data.sessionId && !sessionId) {
        setSessionId(data.sessionId)
      }

      // Add JUSTO's response
      setTyping(false)
      addJustoMessage(
        data.message,
        data.options
      )

      // Move to next step if indicated
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
    addUserMessage,
    addJustoMessage,
    setProcessing,
    setTyping,
    nextStep,
    setSessionId,
  ])

  const selectOption = useCallback(async (value: string, label: string) => {
    if (isProcessing) return

    // Add user's selection as message
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
    selectOption,
  }
}
