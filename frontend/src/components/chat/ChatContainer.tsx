import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useChatStore } from '../../stores/chatStore'
import { documentsApi } from '../../shared/services/api'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { Avatar } from '../ui/Avatar'
import { ProjectInfoCard } from './ProjectInfoCard'
import { OrganizationsDetected } from './OrganizationsDetected'
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
    interventionTypes: [] as string[],
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
  } = useChatStore()

  const [projectInfo, setProjectInfo] = useState<ReturnType<typeof buildProjectInfo> | null>(null)
  const [organizations, setOrganizations] = useState<{ id: string; name: string }[]>([])

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  // If extractedPlan already in store (e.g. navigating back), rebuild local state
  useEffect(() => {
    if (extractedPlan && !projectInfo) {
      setProjectInfo(buildProjectInfo(extractedPlan))
      setOrganizations(buildOrganizations(extractedPlan))
    }
  }, [extractedPlan, projectInfo])

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

      const errorMessage =
        error instanceof Error ? error.message : 'Error procesando el archivo'
      addJustoMessage(
        `No pude procesar el archivo. ${errorMessage}\n\nPor favor intenta con otro archivo .docx o empecemos desde cero.`
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
    addUserMessage('Necesito corregir algo')
    setTyping(true)
    setTimeout(() => {
      setTyping(false)
      addJustoMessage('Entendido. ¿Qué información necesitas corregir?')
    }, 1000)
  }

  const handleStartLegalForms = () => {
    navigate('/legal-form')
  }

  const handleSendMessage = (message: string) => {
    addUserMessage(message)
    setTyping(true)
    setTimeout(() => {
      setTyping(false)
      addJustoMessage(
        'Gracias por tu mensaje. Estoy analizando tu consulta para darte la mejor orientación posible.\n\n' +
        'Basándome en la normativa peruana vigente, te puedo ayudar con información general. ' +
        'Sin embargo, para un análisis más detallado, te recomiendo seleccionar una de las herramientas específicas.'
      )
    }, 1500)
  }

  const renderMessage = (message: typeof messages[0]) => {
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
        interventionTypes: [],
      }

      return (
        <div key={message.id} className="chat-message">
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

      return (
        <div key={message.id} className="chat-message">
          <div className="flex items-start gap-4">
            <Avatar size="md" />
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                JUSTO
              </p>
              <OrganizationsDetected
                organizations={orgs}
                questionsPerOrg={12}
                timePerOrg="5-8 min"
                totalTime={`${orgs.length * 5}-${orgs.length * 8} minutos`}
                onStartForms={handleStartLegalForms}
              />
            </div>
          </div>
        </div>
      )
    }

    return (
      <ChatMessage
        key={message.id}
        message={message}
        onOptionSelect={handleOptionSelect}
        onFileUpload={handleFileUpload}
      />
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-64px)]">
      {/* Messages area - scrollable */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto px-4 py-6"
      >
        <div className="max-w-3xl mx-auto">
          {messages.map(renderMessage)}

          {/* Typing indicator */}
          {isTyping && (
            <div className="chat-message">
              <div className="flex items-start gap-4">
                <Avatar size="md" />
                <div className="flex-1">
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                    JUSTO
                  </p>
                  <div className="chat-bubble inline-flex items-center gap-1 py-3 px-4">
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

      {/* Input area - fixed at bottom */}
      <div className="flex-shrink-0">
        <ChatInput onSend={handleSendMessage} />
      </div>
    </div>
  )
}
