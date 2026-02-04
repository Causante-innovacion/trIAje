import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useChatStore } from '../../stores/chatStore'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { Avatar } from '../ui/Avatar'
import { ProjectInfoCard } from './ProjectInfoCard'
import { OrganizationsDetected } from './OrganizationsDetected'

// Mock data for project info
const MOCK_PROJECT_INFO = {
  projectName: 'Red de Narrativas Responsables',
  organization: 'Archivo de la Memoria Marica del Perú',
  description: 'Iniciativa dedicada a la preservación y difusión de memorias LGTBIQ+ a través de plataformas digitales y talleres comunitarios en diversas regiones del Perú, buscando combatir el estigma y fortalecer la identidad colectiva.',
  financing: {
    seed: { amount: '$15,000', source: 'Fondos concursables' },
    scaling: { amount: '$45,000', source: 'Cooperación Int.' },
  },
  team: {
    permanent: 4,
    external: 6,
  },
  interventionTypes: ['Derechos Humanos', 'Cultura y Memoria', 'Digitalización'],
}

const MOCK_ORGANIZATIONS = [
  { id: '1', name: 'AIESEC' },
  { id: '2', name: 'CENDES' },
  { id: '3', name: 'LANKI' },
]

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
  } = useChatStore()

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

  const handleFileUpload = (file: File) => {
    useChatStore.getState().addMessage({
      sender: 'user',
      content: `Archivo subido: ${file.name}`,
      contentType: 'file_uploaded',
      file: {
        id: Math.random().toString(36).substring(2),
        name: file.name,
        size: file.size,
        type: file.type,
        progress: 0,
        status: 'uploading',
      },
    })

    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 30
      if (progress >= 100) {
        progress = 100
        clearInterval(interval)

        setTimeout(() => {
          const msgs = useChatStore.getState().messages
          const lastMessage = msgs[msgs.length - 1]
          if (lastMessage?.file) {
            useChatStore.getState().updateFileStatus(lastMessage.file.id, 'analyzing', 100)
          }

          setTimeout(() => {
            if (lastMessage?.file) {
              useChatStore.getState().updateFileStatus(lastMessage.file.id, 'complete', 100)
            }
            // Show project info card (simulated with special message type)
            useChatStore.getState().addMessage({
              sender: 'justo',
              content: 'project_info_card',
              contentType: 'text',
              metadata: { step: currentStep, toolContext: currentTool },
            })
          }, 2000)
        }, 1500)
      }

      const msgs = useChatStore.getState().messages
      const lastMessage = msgs[msgs.length - 1]
      if (lastMessage?.file) {
        useChatStore.getState().updateFileStatus(lastMessage.file.id, 'uploading', progress)
      }
    }, 200)
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
      return (
        <div key={message.id} className="chat-message">
          <div className="flex items-start gap-4">
            <Avatar size="md" />
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                JUSTO
              </p>
              <ProjectInfoCard
                data={MOCK_PROJECT_INFO}
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
      return (
        <div key={message.id} className="chat-message">
          <div className="flex items-start gap-4">
            <Avatar size="md" />
            <div className="flex-1">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
                JUSTO
              </p>
              <OrganizationsDetected
                organizations={MOCK_ORGANIZATIONS}
                questionsPerOrg={12}
                timePerOrg="5-8 min"
                totalTime="15-25 minutos"
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
