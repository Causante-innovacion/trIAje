import { useCallback, useRef } from 'react'
import { useChatStore } from '../stores/chatStore'
import { chatApi } from '../shared/services/api'
import { ChatResponse, MAX_MESSAGE_LENGTH } from '../types/chat'

// Base URL for the streaming endpoint (same origin as the REST API)
const STREAM_URL = `${import.meta.env.VITE_API_URL ?? ''}/api/v1/chat/message/stream`

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
    addErrorMessage,
    setProcessing,
    setTyping,
    nextStep,
    setSessionId,
    startStreamingMessage,
    setStreamingStatus,
    setStreamingClassification,
    setStreamingSources,
    appendToStreamingMessage,
    appendScanningDoc,
    finalizeStreamingMessage,
    consumePendingAmberContext,
  } = useChatStore()

  // Ref to hold the active AbortController for the streaming fetch
  const abortControllerRef = useRef<AbortController | null>(null)

  // Intelligent chat mode: uses /chat/message/stream (SSE)
  const sendIntelligentMessage = useCallback(async (content: string, options?: { hidden?: boolean; isExplanation?: boolean }) => {
    if (!content.trim() || isProcessing) return

    if (content.length > MAX_MESSAGE_LENGTH) {
      addErrorMessage(
        `Tu mensaje excede el límite de ${MAX_MESSAGE_LENGTH} caracteres. Por favor, acórtalo e intenta de nuevo.`,
        'validation'
      )
      return
    }

    // Recopilar historial antes de agregar el mensaje actual (excluye el mensaje presente)
    const history = messages
      .filter(m =>
        (m.sender === 'user' && m.contentType === 'text' && m.content?.trim()) ||
        (m.sender === 'justo' &&
          (m.contentType === 'semaphore_response' || m.contentType === 'text') &&
          m.content?.trim() && !m.isStreaming)
      )
      .slice(-8)  // últimas 4 conversaciones (8 mensajes)
      .map(m => ({ role: m.sender === 'user' ? 'user' : 'assistant' as const, content: m.content }))

    if (!options?.hidden) {
      addUserMessage(content)
    }
    setProcessing(true)

    // Consume pending AMARILLO context before we overwrite lastUserMessage
    const pendingAmber = consumePendingAmberContext()

    // Create placeholder streaming message bubble immediately
    const streamId = startStreamingMessage({ isExplanation: options?.isExplanation })

    try {
      // Create an AbortController so we can cancel the request
      const abortController = new AbortController()
      abortControllerRef.current = abortController

      const response = await fetch(STREAM_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: abortController.signal,
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId || undefined,
          history,
          ...(pendingAmber ? {
            context: {
              pending_amber: {
                intention: pendingAmber.intention,
                original_query: pendingAmber.originalMessage,
              },
            },
          } : {}),
        }),
      })

      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // SSE lines are separated by \n\n; process all complete events
        const parts = buffer.split('\n\n')
        buffer = parts.pop() ?? ''  // last incomplete chunk stays in buffer

        for (const part of parts) {
          const line = part.trim()
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))
            switch (event.type) {
              case 'status':
                setStreamingStatus(streamId, event.message)
                break
              case 'classification':
                setStreamingClassification(streamId, event.data)
                break
              case 'sources':
                setStreamingSources(streamId, event.data)
                break
              case 'doc_scanning':
                appendScanningDoc(streamId, event.title)
                break
              case 'token':
                appendToStreamingMessage(streamId, event.text)
                break
              case 'done':
                if (event.classification) {
                  setStreamingClassification(streamId, event.classification)
                }
                finalizeStreamingMessage(streamId, {
                  actions: event.actions,
                  disclaimers: event.disclaimers,
                  conversation_id: event.conversation_id,
                  // Pass one-shot content (greeting/out-of-scope) directly into
                  // finalize so it never appears in the streaming render.  This
                  // lets AnimatedText show it with the typewriter from the start
                  // instead of flashing the raw text first.
                  ...(event.message ? { content: event.message } : {}),
                  // Pre-clarify responses (semaphore VERDE) also need pending context
                  // so the user's answer is treated as a follow-up, not a new query.
                  ...(event.metadata?.pre_clarify && event.metadata?.intention
                    ? { preClarifyIntention: event.metadata.intention }
                    : {}),
                })
                break
            }
          } catch {
            // Malformed JSON line — skip silently
          }
        }
      }
    } catch (error) {
      // If the request was aborted by the user, just clean up silently
      if (error instanceof DOMException && error.name === 'AbortError') {
        finalizeStreamingMessage(streamId, {})
      } else if (error instanceof TypeError && (error.message.includes('fetch') || error.message.includes('network'))) {
        // Remove the empty streaming bubble on error and show error message
        finalizeStreamingMessage(streamId, {})
        addErrorMessage(
          'No se pudo conectar con el servidor. Verifica tu conexión a internet e intenta de nuevo.',
          'network'
        )
      } else {
        finalizeStreamingMessage(streamId, {})
        addErrorMessage(
          'Ocurrió un error inesperado. Por favor, intenta de nuevo.',
          'server'
        )
      }
    } finally {
      abortControllerRef.current = null
      setProcessing(false)
    }
  }, [
    messages,
    isProcessing,
    conversationId,
    addUserMessage,
    addErrorMessage,
    setProcessing,
    startStreamingMessage,
    setStreamingStatus,
    setStreamingClassification,
    setStreamingSources,
    appendToStreamingMessage,
    appendScanningDoc,
    finalizeStreamingMessage,
    consumePendingAmberContext,
  ])

  // Legacy tool-based chat
  const sendMessage = useCallback(async (content: string, options?: { hidden?: boolean; isExplanation?: boolean }) => {
    if (!content.trim() || isProcessing) return

    // If in intelligent chat mode, use the intelligent endpoint
    if (currentTool === 'chat') {
      return sendIntelligentMessage(content, options)
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

  // Stop any in-progress streaming request
  const stopProcessing = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setProcessing(false)
  }, [setProcessing])

  return {
    messages,
    currentTool,
    isProcessing,
    sendMessage,
    sendIntelligentMessage,
    selectOption,
    stopProcessing,
  }
}
