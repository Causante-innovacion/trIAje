import { useEffect, useRef, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useChatStore } from '../../stores/chatStore'
import { useChat } from '../../hooks/useChat'
import { chatApi, documentsApi } from '../../shared/services/api'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { Avatar } from '../ui/Avatar'
import { ChevronDown } from 'lucide-react'
import { ProjectInfoCard, ProjectInfo } from './ProjectInfoCard'
import { OrganizationsDetected } from './OrganizationsDetected'
import { FileUpload } from './FileUpload'
import type { PlanExtractionResponse } from '../../types/extraction.types'

// Builds ProjectInfoCard data from extracted plan
function buildProjectInfo(plan: PlanExtractionResponse) {
  const meta = plan.source_metadata
  const finance = plan.raw_extractions.financing_sources_raw
  const orgs = plan.raw_extractions.team_and_partners

  const phase1 = finance.phases_raw.find((p) => p.phase === 1)
  const phase2 = finance.phases_raw.find((p) => p.phase === 2)

  return {
    projectName: meta.project_name,
    organization: orgs.length > 0 ? orgs[0].name : 'Sin organización',
    description: meta.description || meta.problem_summary || '',
    financing: {
      seed: {
        amount: phase1 ? phase1.name : 'Por definir',
        source: finance.sources_suggested_raw.slice(0, 2).join(', ') || 'No especificado',
      },
      scaling: {
        amount: phase2 ? phase2.name : 'Por definir',
        source: finance.future_allies_raw.slice(0, 2).join(', ') || 'No especificado',
      },
    },
    team: {
      permanent: orgs.length,
      external: meta.external_dependency ?? 0,
    },
  }
}

// Builds organizations list from extracted plan
function buildOrganizations(plan: PlanExtractionResponse) {
  return plan.raw_extractions.team_and_partners.map((org, index) => ({
    id: String(index + 1),
    name: org.name,
  }))
}

export function ChatContainer() {
  const navigate = useNavigate()
  const {
    messages,
    isTyping,
    addUserMessage,
    addJustoMessage,
    setTyping,
    nextStep,
    currentStep,
    currentTool,
    extractedPlan,
    setExtractedPlan,
    lastEvaluationData,
    consumePendingMessage,
  } = useChatStore()

  const { sendMessage, stopProcessing } = useChat()

  const [projectInfo, setProjectInfo] = useState<ReturnType<typeof buildProjectInfo> | null>(null)
  const [organizations, setOrganizations] = useState<{ id: string; name: string }[]>([])
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [isEditingProjectInfo, setIsEditingProjectInfo] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const hasSentPending = useRef(false)
  const userHasScrolledUp = useRef(false)
  const lastJustoMessageRef = useRef<HTMLDivElement>(null)
  // ID del último mensaje del asistente al que ya scrolleamos el inicio
  const scrolledToStartForId = useRef<string | null>(null)
  const [showScrollToBottom, setShowScrollToBottom] = useState(false)

  const scrollToBottom = useCallback(() => {
    const el = scrollContainerRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [])

  const scrollToLastJustoMessageStart = useCallback(() => {
    const container = scrollContainerRef.current
    const msgEl = lastJustoMessageRef.current
    if (!container || !msgEl) return
    const msgTop = msgEl.offsetTop - container.offsetTop
    container.scrollTo({ top: Math.max(0, msgTop - 16), behavior: 'smooth' })
    // Mostrar la flecha inmediatamente para que el usuario pueda ir al final
    setShowScrollToBottom(true)
  }, [])

  const handleScroll = useCallback(() => {
    const el = scrollContainerRef.current
    if (!el) return
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    userHasScrolledUp.current = distanceFromBottom > 80
    setShowScrollToBottom(distanceFromBottom > 150)
  }, [])

  useEffect(() => {
    const lastMsg = messages[messages.length - 1]
    if (!lastMsg) return

    if (lastMsg.sender === 'user') {
      // Usuario envió un mensaje: ir al fondo para ver el indicador de carga
      userHasScrolledUp.current = false
      scrolledToStartForId.current = null
      scrollToBottom()
      return
    }

    if (
      lastMsg.sender === 'justo' &&
      lastMsg.id !== scrolledToStartForId.current
    ) {
      // Nuevo mensaje del asistente: scrollear al inicio UNA Única vez
      scrolledToStartForId.current = lastMsg.id
      userHasScrolledUp.current = true

      // Ejecutar el scroll después de que el DOM haya pintado el nuevo mensaje.
      // doble rAF = espera al menos dos frames de render (el navegador pintó el nodo).
      const doScroll = () => {
        if (lastJustoMessageRef.current) {
          scrollToLastJustoMessageStart()
        } else {
          // El elemento aún no existe en el DOM: esperar con ResizeObserver
          const container = scrollContainerRef.current
          if (!container) return
          let fired = false
          const obs = new ResizeObserver(() => {
            if (fired || !lastJustoMessageRef.current) return
            fired = true
            obs.disconnect()
            scrollToLastJustoMessageStart()
          })
          obs.observe(container)
          setTimeout(() => { if (!fired) obs.disconnect() }, 1000)
        }
      }

      requestAnimationFrame(() => requestAnimationFrame(doScroll))
      return
    }

    // Durante el streaming (mismo id) → NO hacer nada.
    // El usuario permanece donde está sin que la vista lo arrastre.
  }, [messages, scrollToBottom, scrollToLastJustoMessageStart])

  // If extractedPlan already in store (e.g. navigating back), rebuild local state
  useEffect(() => {
    if (extractedPlan && !projectInfo) {
      setProjectInfo(buildProjectInfo(extractedPlan))
      setOrganizations(buildOrganizations(extractedPlan))
    }
  }, [extractedPlan, projectInfo])

  // Send pending message from home page (intelligent chat)
  useEffect(() => {
    if (currentTool === 'chat' && !hasSentPending.current) {
      hasSentPending.current = true
      const pending = consumePendingMessage()
      if (pending) {
        // Small delay so the UI renders first
        setTimeout(() => {
          sendMessage(pending)
        }, 400)
      }
    }
  }, [currentTool, consumePendingMessage, sendMessage])

  const handleOptionSelect = (value: string) => {
    const selectedOption = messages
      .flatMap((m) => m.options || [])
      .find((opt) => opt.value === value)

    if (selectedOption) {
      addUserMessage(selectedOption.label)
    }

    setTyping(true)
    setTimeout(() => {
      setTyping(false)

      if (currentTool === 'evaluation' && currentStep === 1) {
        if (value === 'yes') {
          addJustoMessage(
            'Excelente. Sube tu plan estratégico aquí y extraeré información como:\n\n✓ Descripción del proyecto\n✓ Modelo de financiamiento\n✓ Organizaciones involucradas\n✓ Recursos operativos\n\nDespués solo te preguntaré lo que necesite para completar la evaluación legal.'
          )
          setTimeout(() => {
            useChatStore.getState().addMessage({
              sender: 'justo',
              content: '',
              contentType: 'file_upload',
            })
          }, 500)
        } else {
          addJustoMessage(
            'Sin problema, empecemos desde cero.\n\n¿Cuál es el nombre de tu proyecto o iniciativa?'
          )
        }
        nextStep()
      }
    }, 1000)
  }

  const handleFileUpload = async (file: File) => {
    const fileId = Math.random().toString(36).substring(2)

    // Hide inline upload UI
    setShowFileUpload(false)

    // Show upload message
    useChatStore.getState().addMessage({
      sender: 'user',
      content: `Archivo subido: ${file.name}`,
      contentType: 'file_uploaded',
      file: {
        id: fileId,
        name: file.name,
        size: file.size,
        type: file.type,
        progress: 0,
        status: 'uploading',
      },
    })

    // Simulate initial upload progress
    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 25
      if (progress >= 90) {
        progress = 90
        clearInterval(interval)
      }
      useChatStore.getState().updateFileStatus(fileId, 'uploading', Math.min(progress, 90))
    }, 200)

    try {
      // Real API call
      useChatStore.getState().updateFileStatus(fileId, 'uploading', 95)

      if (currentTool === 'chat') {
        const response = await chatApi.uploadDocument(file, 'general')
        clearInterval(interval)

        useChatStore.getState().updateFileStatus(fileId, 'analyzing', 100)

        const data = response.data as Record<string, unknown>
        const filename = (data.filename as string) || file.name
        const preview = (data.content_preview as string) || ''

        useChatStore.getState().updateFileStatus(fileId, 'complete', 100)

        const chatMessage = preview
          ? `📎 He adjuntado el archivo "${filename}". Analiza su contenido y dame una orientación legal inicial dentro de tu ámbito.\n\nContenido extraído:\n${preview}`
          : `📎 He adjuntado el archivo "${filename}". Analiza su contenido y dame una orientación legal inicial dentro de tu ámbito.`

        sendMessage(chatMessage)
        return
      }

      const response = await documentsApi.extractPlan(file)
      clearInterval(interval)

      // Mark analyzing
      useChatStore.getState().updateFileStatus(fileId, 'analyzing', 100)

      // Store extracted data
      const plan = response.data
      setExtractedPlan(plan)
      setProjectInfo(buildProjectInfo(plan))
      setOrganizations(buildOrganizations(plan))

      // Brief pause then show complete
      setTimeout(() => {
        useChatStore.getState().updateFileStatus(fileId, 'complete', 100)

        // Show project info card
        useChatStore.getState().addMessage({
          sender: 'justo',
          content: 'project_info_card',
          contentType: 'text',
          metadata: { step: currentStep, toolContext: currentTool },
        })
      }, 1500)
    } catch (error) {
      clearInterval(interval)
      useChatStore.getState().updateFileStatus(fileId, 'error', 0)

      const axiosDetail = (error as any)?.response?.data?.detail
      let errorMessage = axiosDetail || (error instanceof Error ? error.message : 'Error procesando el archivo')
      
      if (errorMessage.includes('413')) {
        errorMessage = 'El archivo es demasiado grande y supera el límite permitido.'
      }

      addJustoMessage(
        `No pude procesar el archivo. ${errorMessage}\n\nPor favor intenta con otro archivo .docx, .pdf o .txt, o empecemos desde cero.`
      )
    }
  }

  const handleProjectInfoConfirm = () => {
    addUserMessage('Sí, la información es correcta')
    setTyping(true)
    setTimeout(() => {
      setTyping(false)
      useChatStore.getState().addMessage({
        sender: 'justo',
        content: 'organizations_detected',
        contentType: 'text',
      })
    }, 1000)
  }

  const handleProjectInfoEdit = () => {
    setIsEditingProjectInfo(true)
    // Removed old logic: addUserMessage('Necesito corregir algo') ...
  }

  const handleProjectInfoSave = (newData: ProjectInfo) => {
    setProjectInfo(newData)
    setIsEditingProjectInfo(false)
    // Optional: Add a system message confirming update?
    // For now, just update the view.
  }

  const handleProjectInfoCancel = () => {
    setIsEditingProjectInfo(false)
  }

  const handleStartLegalForms = () => {
    navigate('/legal-form')
  }

  const handleFileUploadRequest = useCallback(() => {
    setShowFileUpload(true)
    setTimeout(scrollToBottom, 100)
  }, [])

  const handleSendMessage = (content: string, options?: { hidden?: boolean; isExplanation?: boolean }) => {
    // Use the unified sendMessage from useChat
    sendMessage(content, options)
  }

  // Find the last justo message ID for animation
  const lastJustoMessageId = [...messages].reverse().find(m => m.sender === 'justo')?.id

  const renderMessage = (message: typeof messages[0]) => {
    // Should this message animate?
    // Streamed messages (wasStreamed=true) already showed content building up
    // token by token, so we skip the typewriter re-play after streaming ends.
    const shouldAnimate = message.id === lastJustoMessageId &&
      message.sender === 'justo' &&
      !message.wasStreamed &&
      !message.hasBeenAnimated

    // Whether this is the last justo message (for scroll anchor)
    const isLastJusto = message.id === lastJustoMessageId && message.sender === 'justo'

    // Special rendering for project info card
    if (message.content === 'project_info_card' && message.sender === 'justo') {
      const data = projectInfo ?? {
        projectName: 'Cargando...',
        organization: '',
        description: '',
        financing: {
          seed: { amount: '', source: '' },
          scaling: { amount: '', source: '' },
        },
        team: { permanent: 0, external: 0 },
      }

      return (
        <div key={message.id} ref={isLastJusto ? lastJustoMessageRef : undefined} className="chat-message">
          <div className="flex items-start gap-4">
            <Avatar size="md" />
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                JUSTO
              </p>
              <ProjectInfoCard
                data={data}
                onConfirm={handleProjectInfoConfirm}
                onEdit={handleProjectInfoEdit}
                isEditing={isEditingProjectInfo}
                onSave={handleProjectInfoSave}
                onCancel={handleProjectInfoCancel}
                organizations={organizations}
              />
            </div>
          </div>
        </div>
      )
    }

    // Special rendering for organizations detected
    if (message.content === 'organizations_detected' && message.sender === 'justo') {
      const orgs = organizations.length > 0
        ? organizations
        : [{ id: '1', name: 'Organización principal' }]

      // Check if all org forms are completed in localStorage
      const STORAGE_KEY = (id: string) => `gpt_legal_form_progress_${id}`
      const allOrgsCompleted = orgs.every(org => {
        try {
          const raw = localStorage.getItem(STORAGE_KEY(org.id))
          if (!raw) return false
          const parsed = JSON.parse(raw)
          const data = parsed.data ?? parsed
          return data.isCompleted === true
        } catch { return false }
      })

      return (
        <div key={message.id} ref={isLastJusto ? lastJustoMessageRef : undefined} className="chat-message">
          <div className="flex items-start gap-4">
            <Avatar size="md" />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                JUSTO
              </p>
              <OrganizationsDetected
                organizations={orgs}
                questionsPerOrg={12}
                timePerOrg="5-8 min"
                totalTime={`${orgs.length * 5}-${orgs.length * 8} minutos`}
                onStartForms={handleStartLegalForms}
                allOrgsCompleted={allOrgsCompleted}
                hasEvaluation={!!lastEvaluationData}
                onViewEvaluation={() => navigate('/evaluation', { state: { evaluationData: lastEvaluationData, skipAnimation: true } })}
              />
            </div>
          </div>
        </div>
      )
    }

    return (
      <div key={message.id} ref={isLastJusto ? lastJustoMessageRef : undefined}>
        <ChatMessage
          message={message}
          onOptionSelect={handleOptionSelect}
          onFileUpload={handleFileUpload}
          onFileUploadRequest={handleFileUploadRequest}
          onSendMessage={handleSendMessage}
          animate={shouldAnimate}
        />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full relative">
      {/* Messages area - scrollable */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 py-6"
      >
        <div className="max-w-3xl mx-auto">
          {messages.map(renderMessage)}

          {/* Inline file upload (triggered by action card) */}
          {showFileUpload && (
            <div className="chat-message animate-fade-in">
              <div className="flex items-start gap-4">
                <Avatar size="md" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                    JUSTO
                  </p>
                  <div className="chat-bubble overflow-hidden">
                    <p className="mb-3 text-sm text-gray-600">
                      Sube tu archivo aquí para que pueda analizarlo:
                    </p>
                    <FileUpload onFileSelect={handleFileUpload} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Typing indicator */}
          {isTyping && (
            <div className="chat-message">
              <div className="flex items-start gap-4">
                <Avatar size="md" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                    JUSTO
                  </p>
                  <div className="chat-bubble inline-flex items-center gap-1 py-3 px-4 overflow-hidden">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Floating scroll-to-bottom button */}
      {showScrollToBottom && (
        <button
          onClick={scrollToBottom}
          aria-label="Ir al final de la respuesta"
          className="
            absolute right-1/2 translate-x-1/2 bottom-[100px] z-20 /* Mover al centro y un poco más arriba de la caja de texto */
            w-10 h-10 rounded-full shadow-lg
            bg-gray-900 border border-black
            flex items-center justify-center
            text-white hover:bg-black
            hover:shadow-xl hover:scale-110
            transition-all duration-200
            animate-fade-in
          "
        >
          <ChevronDown className="w-6 h-6" />
        </button>
      )}

      {/* Input area - fixed at bottom */}
      <div className="flex-shrink-0 z-10 bg-white relative">
        <ChatInput
          onSend={handleSendMessage}
          onFileUpload={handleFileUpload}
          onStopProcessing={stopProcessing}
        />
      </div>
    </div>
  )
}
