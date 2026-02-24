import { useEffect } from 'react'
import { Avatar } from '../ui/Avatar'
import { Message } from '../../types/chat'
import { OptionButtons } from './OptionButtons'
import { FileUpload } from './FileUpload'
import { ProgressBar } from '../ui/ProgressBar'
import { SourcesCitation } from './SourcesCitation'
import { ActionCard } from './ActionCard'
import { MarkdownRenderer } from '../ui/MarkdownRenderer'
import { AlertCircle, WifiOff, ServerCrash, Clock, Paperclip, ExternalLink } from 'lucide-react'
import { useTypewriter } from '../../hooks/useTypewriter'
import { ThinkingBlock, parseThinkContent } from './ThinkingBlock'
import { useNavigate } from 'react-router-dom'
import { useChatStore } from '../../stores/chatStore'

/** Detect file-attachment messages and extract just the filename */
function parseFileAttachment(content: string): string | null {
  // Matches: Analiza mi proyecto. 📎 He adjuntado el archivo "filename.ext":
  const match = content.match(/📎 He adjuntado el archivo "([^"]+)"/)
  return match ? match[1] : null
}

interface ChatMessageProps {
  message: Message
  onOptionSelect?: (value: string) => void
  onFileUpload?: (file: File) => void
  onFileUploadRequest?: () => void
  /** If true, animate the text with a typewriter effect */
  animate?: boolean
}

function ErrorIcon({ type }: { type?: string }) {
  switch (type) {
    case 'network': return <WifiOff className="w-5 h-5 text-red-500" />
    case 'timeout': return <Clock className="w-5 h-5 text-amber-500" />
    case 'server': return <ServerCrash className="w-5 h-5 text-red-500" />
    default: return <AlertCircle className="w-5 h-5 text-red-500" />
  }
}

/** Renders text with optional typewriter animation + Markdown */
function AnimatedText({ text, animate, messageId }: { text: string; animate: boolean; messageId?: string }) {
  const { visibleText, isAnimating } = useTypewriter(text, {
    enabled: animate,
    wordsPerTick: 3,
    speed: 25,
  })

  // Once the typewriter finishes, mark this message so it never re-animates
  // when the user navigates away and comes back.
  useEffect(() => {
    if (!isAnimating && animate && messageId) {
      useChatStore.getState().markMessageAnimated(messageId)
    }
  }, [isAnimating, animate, messageId])

  return (
    <div className="leading-relaxed">
      <MarkdownRenderer content={visibleText} />
      {isAnimating && (
        <span className="inline-block w-1.5 h-4 bg-gold/60 ml-0.5 animate-pulse rounded-sm" />
      )}
    </div>
  )
}

/** Status pill shown while a streaming message is in progress */
function StreamingStatusPill({ status }: { status: string }) {
  return (
    <div className="flex items-center gap-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-3 py-1 w-fit animate-pulse">
      <span className="flex gap-0.5">
        <span className="w-1 h-1 rounded-full bg-amber-500 animate-bounce [animation-delay:0ms]" />
        <span className="w-1 h-1 rounded-full bg-amber-500 animate-bounce [animation-delay:150ms]" />
        <span className="w-1 h-1 rounded-full bg-amber-500 animate-bounce [animation-delay:300ms]" />
      </span>
      {status}
    </div>
  )
}

export function ChatMessage({ message, onOptionSelect, onFileUpload, onFileUploadRequest, animate = false }: ChatMessageProps) {
  const isJusto = message.sender === 'justo'
  const navigate = useNavigate()

  // Render message content based on type
  const renderContent = () => {
    switch (message.contentType) {

      // ── Intelligent chat response ──
      case 'semaphore_response': {
        const { thinkContent, answer, isThinking } = parseThinkContent(message.content ?? '')
        const scanningDocs = message.metadata?.scanningDocs ?? []
        const isScanning = message.isStreaming && !message.content && scanningDocs.length > 0

        return (
          <div className="space-y-3">
            {/* Streaming status pill — shown while tokens haven't started yet */}
            {message.isStreaming && message.streamingStatus && !message.content && !isScanning && (
              <StreamingStatusPill status={message.streamingStatus} />
            )}

            {/* Lista de documentos encontrando durante RAG */}
            {isScanning && (
              <div className="rounded-xl border border-blue-100 bg-blue-50/60 px-3 py-2 space-y-1">
                <p className="text-[11px] font-semibold text-blue-600 uppercase tracking-wide flex items-center gap-1.5">
                  <span className="flex gap-0.5">
                    <span className="w-1 h-1 rounded-full bg-blue-400 animate-bounce [animation-delay:0ms]" />
                    <span className="w-1 h-1 rounded-full bg-blue-400 animate-bounce [animation-delay:150ms]" />
                    <span className="w-1 h-1 rounded-full bg-blue-400 animate-bounce [animation-delay:300ms]" />
                  </span>
                  Revisando normativa
                </p>
                <ul className="space-y-0.5">
                  {scanningDocs.map((doc, i) => (
                    <li key={i} className="text-[11px] text-blue-700 flex items-center gap-1.5 animate-fade-in">
                      <span className="text-blue-400">‣</span>
                      <span className="truncate">{doc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Bloque de razonamiento <think> (colapsable) */}
            {(thinkContent || isThinking) && (
              <ThinkingBlock content={thinkContent} isThinking={isThinking} />
            )}

            {/* Main message text — typewriter for completed, raw for streaming */}
            {message.isStreaming ? (
              <div className="leading-relaxed">
                <MarkdownRenderer content={answer} />
                {answer && (
                  <span className="inline-block w-1.5 h-4 bg-gold/60 ml-0.5 animate-pulse rounded-sm" />
                )}
              </div>
            ) : (
              <AnimatedText text={answer || message.content} animate={animate} messageId={message.id} />
            )}

            {/* Sources */}
            {message.metadata?.sources && message.metadata.sources.length > 0 && (
              <SourcesCitation sources={message.metadata.sources} />
            )}

            {/* Actions */}
            {message.metadata?.actions?.map((action, i) => (
              <ActionCard
                key={i}
                action={action}
                messageId={message.id}
                onFileUploadRequest={onFileUploadRequest}
                alreadyGenerated={message.metadata?.generatedReport === 'adviser'}
              />
            ))}

            {/* Inline report link — shown after adviser prep completes */}
            {message.metadata?.generatedReport === 'adviser' && (
              <button
                onClick={() => {
                  const adviserData = useChatStore.getState().lastAdviserData
                  navigate('/legal-adviser', { state: { adviserData: adviserData ?? undefined, skipAnimation: true } })
                }}
                className="mt-3 flex items-center gap-2 text-xs font-semibold text-red-700 bg-red-50 border border-red-200 rounded-xl px-4 py-2.5 hover:bg-red-100 hover:border-red-300 transition-all w-full"
              >
                <ExternalLink className="w-3.5 h-3.5 flex-shrink-0" />
                Ver paquete para asesor
              </button>
            )}
            {message.metadata?.generatedReport === 'evaluation' && (
              <button
                onClick={() => navigate('/evaluation', { state: { skipAnimation: true } })}
                className="mt-3 flex items-center gap-2 text-xs font-semibold text-causante-ocre bg-amber-50 border border-amber-200 rounded-xl px-4 py-2.5 hover:bg-amber-100 hover:border-amber-300 transition-all w-full"
              >
                <ExternalLink className="w-3.5 h-3.5 flex-shrink-0" />
                Ver diagnóstico legal
              </button>
            )}

            {/* Disclaimers */}
            {message.metadata?.disclaimers && message.metadata.disclaimers.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                {message.metadata.disclaimers.map((d, i) => (
                  <p key={i} className="text-[11px] text-gray-400 leading-relaxed">
                    ⚖️ {d}
                  </p>
                ))}
              </div>
            )}
          </div>
        )
      }

      // ── Error message ──
      case 'error':
        return (
          <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4 animate-fade-in">
            <ErrorIcon type={message.metadata?.errorType} />
            <div>
              <p className="text-sm text-red-800 font-medium">
                {message.content}
              </p>
              {message.metadata?.errorType === 'network' && (
                <p className="text-xs text-red-600 mt-1">
                  Verifica que el servidor backend esté corriendo en el puerto correcto.
                </p>
              )}
            </div>
          </div>
        )

      // ── Options (buttons) ──
      case 'options':
        return (
          <>
            <AnimatedText text={message.content} animate={animate} messageId={message.id} />
            {message.options && (
              <OptionButtons
                options={message.options}
                onSelect={onOptionSelect}
              />
            )}
          </>
        )

      // ── File upload prompt ──
      case 'file_upload':
        return (
          <>
            <div className="whitespace-pre-wrap mb-4">{message.content}</div>
            <FileUpload onFileSelect={onFileUpload} />
          </>
        )

      // ── File uploaded status ──
      case 'file_uploaded':
        return (
          <div className="space-y-3">
            <div className="whitespace-pre-wrap">{message.content}</div>
            {message.file && (
              <div className="bg-gray-50 rounded-xl p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-cream rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-gold" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 text-sm">{message.file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(message.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  {message.file.status === 'complete' && (
                    <span className="text-sm text-gray-500">{message.file.progress}%</span>
                  )}
                </div>
                {message.file.status !== 'complete' && (
                  <>
                    <ProgressBar progress={message.file.progress} size="sm" />
                    <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                      <span className="inline-block w-1.5 h-1.5 bg-gold rounded-full animate-pulse" />
                      {message.file.status === 'uploading' ? 'Subiendo archivo...' : 'Analizando documento...'}
                    </p>
                  </>
                )}
              </div>
            )}
          </div>
        )

      // ── Progress ──
      case 'progress':
        return (
          <div className="space-y-3">
            <div className="whitespace-pre-wrap">{message.content}</div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span className="inline-block w-2 h-2 bg-gold rounded-full animate-pulse" />
              Procesando...
            </div>
          </div>
        )

      // ── Default text ──
      default:
        return <AnimatedText text={message.content} animate={animate} messageId={message.id} />
    }
  }

  if (isJusto) {
    return (
      <div className="chat-message">
        <div className="flex items-start gap-4">
          <Avatar size="md" />
          <div className="flex-1">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              JUSTO
            </p>
            <div className="chat-bubble">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
    )
  }

  // User message
  return (
    <div className="chat-message">
      <div className="flex justify-end">
        <div className="bg-black text-white rounded-3xl px-5 py-3 max-w-lg">
          {parseFileAttachment(message.content) ? (
            // Render a compact file card instead of the raw document dump
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center">
                <Paperclip className="w-4 h-4 text-white/80" />
              </div>
              <div className="min-w-0">
                <p className="text-xs text-white/50 uppercase tracking-wide mb-0.5">Documento adjunto</p>
                <p className="text-sm font-medium truncate leading-tight">
                  {parseFileAttachment(message.content)}
                </p>
                <p className="text-xs text-white/50 mt-0.5">Solicitando análisis de proyecto…</p>
              </div>
            </div>
          ) : (
            <div className="whitespace-pre-wrap text-sm">{message.content}</div>
          )}
        </div>
      </div>
    </div>
  )
}
