import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, UserCheck, HelpCircle, ArrowRight, Loader2 } from 'lucide-react'
import type { SuggestedAction, ActionType } from '../../types/chat'
import { useChatStore } from '../../stores/chatStore'
import { advisorPrepApi } from '../../shared/services/api'

interface ActionCardProps {
    action: SuggestedAction
    onFileUploadRequest?: () => void
}

const ACTION_CONFIG: Record<ActionType, {
    icon: typeof Upload
    colorClass: string
    bgClass: string
    borderClass: string
}> = {
    upload_file: {
        icon: Upload,
        colorClass: 'text-blue-700',
        bgClass: 'bg-blue-50',
        borderClass: 'border-blue-200 hover:border-blue-300',
    },
    derive_to_advisor: {
        icon: UserCheck,
        colorClass: 'text-red-700',
        bgClass: 'bg-red-50',
        borderClass: 'border-red-200 hover:border-red-300',
    },
    provide_context: {
        icon: HelpCircle,
        colorClass: 'text-amber-700',
        bgClass: 'bg-amber-50',
        borderClass: 'border-amber-200 hover:border-amber-300',
    },
    none: {
        icon: HelpCircle,
        colorClass: 'text-gray-500',
        bgClass: 'bg-gray-50',
        borderClass: 'border-gray-200',
    },
}

export function ActionCard({ action, onFileUploadRequest }: ActionCardProps) {
    const navigate = useNavigate()
    const [isLoading, setIsLoading] = useState(false)
    const config = ACTION_CONFIG[action.type] || ACTION_CONFIG.none
    const Icon = isLoading ? Loader2 : config.icon

    if (action.type === 'none') return null

    const handleClick = async () => {
        switch (action.type) {
            case 'upload_file':
                onFileUploadRequest?.()
                break

            case 'derive_to_advisor': {
                setIsLoading(true)
                try {
                    // Recopilar historial de conversación del store
                    const { messages, conversationId } = useChatStore.getState()
                    const conversation = messages
                        .filter(m =>
                            (m.sender === 'user' && m.contentType === 'text' && m.content?.trim()) ||
                            (m.sender === 'justo' &&
                                (m.contentType === 'semaphore_response' || m.contentType === 'text') &&
                                m.content?.trim() && !m.isStreaming)
                        )
                        .map(m => ({
                            role: m.sender === 'user' ? 'user' : 'assistant',
                            content: m.content,
                        }))

                    const response = await advisorPrepApi.prepareFromChat(
                        conversation,
                        conversationId ?? undefined
                    )
                    useChatStore.getState().setLastAdviserData(response.data)
                    navigate('/legal-adviser', { state: { adviserData: response.data } })
                } catch {
                    // Si el API falla, navegar igual (usará mockData como fallback)
                    navigate('/legal-adviser')
                } finally {
                    setIsLoading(false)
                }
                break
            }

            case 'provide_context':
                // Informativo: las preguntas aparecen en el mensaje
                break
        }
    }

    return (
        <button
            onClick={handleClick}
            disabled={isLoading}
            className={`w-full mt-3 p-4 rounded-xl border ${config.borderClass} ${config.bgClass} text-left transition-all duration-200 hover:shadow-sm group animate-fade-in disabled:opacity-70 disabled:cursor-wait`}
        >
            <div className="flex items-start gap-3">
                <div className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center ${config.bgClass}`}>
                    <Icon className={`w-5 h-5 ${config.colorClass} ${isLoading ? 'animate-spin' : ''}`} />
                </div>
                <div className="flex-1 min-w-0">
                    <p className={`font-semibold text-sm ${config.colorClass}`}>
                        {isLoading ? 'Preparando paquete para tu asesor…' : action.label}
                    </p>
                    <p className="text-xs text-gray-600 mt-0.5 leading-relaxed">
                        {isLoading
                            ? 'Analizando la conversación y generando contenido personalizado.'
                            : action.description}
                    </p>
                </div>
                {action.type !== 'provide_context' && !isLoading && (
                    <ArrowRight className={`w-4 h-4 flex-shrink-0 mt-1 ${config.colorClass} opacity-50 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all`} />
                )}
            </div>
        </button>
    )
}
