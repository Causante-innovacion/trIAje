import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, UserCheck, HelpCircle, ArrowRight, Loader2, ChevronRight } from 'lucide-react'
import type { SuggestedAction, ActionType } from '../../types/chat'
import { useChatStore } from '../../stores/chatStore'
import { advisorPrepApi } from '../../shared/services/api'

interface ActionCardProps {
    action: SuggestedAction
    messageId?: string
    onFileUploadRequest?: () => void
    /** If true, the adviser package for this message was already generated — hide the derive card */
    alreadyGenerated?: boolean
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

export function ActionCard({ action, messageId, onFileUploadRequest, alreadyGenerated }: ActionCardProps) {
    const navigate = useNavigate()
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Inline context-collection form (shown when conversation is too thin)
    const [showForm, setShowForm] = useState(false)
    const [form, setForm] = useState({ orgName: '', situation: '', need: '' })

    const config = ACTION_CONFIG[action.type] || ACTION_CONFIG.none
    const Icon = isLoading ? Loader2 : config.icon

    if (action.type === 'none') return null
    // Once the adviser package for this message is generated, hide the derive button
    if (action.type === 'derive_to_advisor' && alreadyGenerated) return null
    // "provide_context" is informational only — user continues the conversation naturally
    if (action.type === 'provide_context') return null

    const generatePackage = async (extraContext?: { orgName: string; situation: string; need: string }) => {
        setIsLoading(true)
        setError(null)
        try {
            const { messages, conversationId } = useChatStore.getState()
            let conversation = messages
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

            // Prepend collected context so the LLM has enough info to produce a useful package
            if (extraContext) {
                const parts: string[] = []
                if (extraContext.orgName.trim())
                    parts.push(`Nombre de la organización: ${extraContext.orgName.trim()}`)
                if (extraContext.situation.trim())
                    parts.push(`Situación concreta: ${extraContext.situation.trim()}`)
                if (extraContext.need.trim())
                    parts.push(`Qué necesito resolver con el asesor: ${extraContext.need.trim()}`)
                if (parts.length > 0) {
                    conversation = [
                        { role: 'user', content: parts.join('\n') },
                        ...conversation,
                    ]
                }
            }

            const response = await advisorPrepApi.prepareFromChat(
                conversation,
                conversationId ?? undefined
            )
            useChatStore.getState().setLastAdviserData(response.data)
            if (messageId) {
                useChatStore.getState().markMessageWithReport(messageId, 'adviser')
            }
            navigate('/legal-adviser', { state: { adviserData: response.data, skipAnimation: true } })
        } catch (err) {
            console.error('[ActionCard] derive_to_advisor error:', err)
            setError('No se pudo preparar el paquete. Intenta de nuevo.')
        } finally {
            setIsLoading(false)
        }
    }

    // ── Standard action button ──────────────────────────────────────────────────
    const handleClick = async () => {
        switch (action.type) {
            case 'upload_file':
                onFileUploadRequest?.()
                break

            case 'derive_to_advisor': {
                // Count meaningful user messages in conversation
                const userMsgCount = useChatStore.getState().messages.filter(
                    m => m.sender === 'user' && m.contentType === 'text' && m.content?.trim()
                ).length

                if (userMsgCount < 3) {
                    // Not enough context — ask for it inline first
                    setShowForm(true)
                } else {
                    await generatePackage()
                }
                break
            }

            case 'provide_context':
                break
        }
    }

    const handleFormSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setShowForm(false)
        await generatePackage(form)
    }

    // ── Inline context form ────────────────────────────────────────────────────────
    if (showForm && action.type === 'derive_to_advisor') {
        return (
            <div className="mt-3 rounded-xl border border-red-200 bg-red-50 p-4 animate-fade-in">
                <p className="text-sm font-semibold text-red-700 mb-1">
                    Necesito algunos datos para armar tu paquete
                </p>
                <p className="text-xs text-gray-600 mb-3 leading-relaxed">
                    Con esta información podré generar preguntas, documentos y temas concretos para tu reunión.
                </p>
                <form onSubmit={handleFormSubmit} className="flex flex-col gap-2.5">
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            Nombre de la organización
                        </label>
                        <input
                            type="text"
                            value={form.orgName}
                            onChange={e => setForm(f => ({ ...f, orgName: e.target.value }))}
                            placeholder="Ej: Asociación Civil Mi Organización"
                            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-300 bg-white"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            Describe brevemente la situación <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            required
                            rows={2}
                            value={form.situation}
                            onChange={e => setForm(f => ({ ...f, situation: e.target.value }))}
                            placeholder="Ej: Recibimos una denuncia en SUNAFIL por un ex-trabajador..."
                            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-300 bg-white resize-none"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                            ¿Qué necesitas resolver con el asesor?
                        </label>
                        <input
                            type="text"
                            value={form.need}
                            onChange={e => setForm(f => ({ ...f, need: e.target.value }))}
                            placeholder="Ej: Saber cómo responder y qué documentos presentar"
                            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-300 bg-white"
                        />
                    </div>
                    {error && <p className="text-xs text-red-600 font-medium">{error}</p>}
                    <div className="flex gap-2 pt-1">
                        <button
                            type="button"
                            onClick={() => setShowForm(false)}
                            className="flex-1 text-xs font-medium text-gray-500 border border-gray-200 rounded-lg py-2 hover:bg-gray-100 bg-white transition-colors"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading || !form.situation.trim()}
                            className="flex-1 flex items-center justify-center gap-1.5 text-xs font-semibold text-white bg-red-600 rounded-lg py-2 hover:bg-red-700 transition-colors disabled:opacity-60 disabled:cursor-wait"
                        >
                            {isLoading
                                ? <><Loader2 className="w-3.5 h-3.5 animate-spin" />Generando...</>
                                : <><ChevronRight className="w-3.5 h-3.5" />Generar paquete</>
                            }
                        </button>
                    </div>
                </form>
            </div>
        )
    }

    // ── Standard action button ─────────────────────────────────────────────────
    return (
        <button
            onClick={handleClick}
            disabled={isLoading}
            className={`mt-3 flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left transition-all ${config.bgClass} ${config.borderClass} disabled:opacity-60 disabled:cursor-wait`}
        >
            <Icon className={`w-5 h-5 flex-shrink-0 ${config.colorClass} ${isLoading ? 'animate-spin' : ''}`} />
            <div className="flex-1 min-w-0">
                <p className={`text-sm font-semibold ${config.colorClass}`}>{action.label}</p>
                {action.description && (
                    <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{action.description}</p>
                )}
            </div>
            <ArrowRight className={`w-4 h-4 flex-shrink-0 ${config.colorClass} opacity-60`} />
        </button>
    )
}