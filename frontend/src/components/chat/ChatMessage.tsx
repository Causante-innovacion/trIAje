import { Avatar } from '../ui/Avatar'
import { Message } from '../../types/chat'
import { OptionButtons } from './OptionButtons'
import { FileUpload } from './FileUpload'
import { ProgressBar } from '../ui/ProgressBar'
import { SourcesCitation } from './SourcesCitation'
import { ActionCard } from './ActionCard'
import { MarkdownRenderer } from '../ui/MarkdownRenderer'
import { AlertCircle, WifiOff, ServerCrash, Clock } from 'lucide-react'
import { useTypewriter } from '../../hooks/useTypewriter'

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
function AnimatedText({ text, animate }: { text: string; animate: boolean }) {
  const { visibleText, isAnimating } = useTypewriter(text, {
    enabled: animate,
    wordsPerTick: 3,
    speed: 25,
  })

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

  // Render message content based on type
  const renderContent = () => {
    switch (message.contentType) {

      // ── Intelligent chat response ──
      case 'semaphore_response':
        return (
          <div className="space-y-3">
            {/* Streaming status pill — shown while tokens haven't started yet */}
            {message.isStreaming && message.streamingStatus && !message.content && (
              <StreamingStatusPill status={message.streamingStatus} />
            )}



            {/* Main message text — typewriter for completed, raw for streaming */}
            {message.isStreaming ? (
              <div className="leading-relaxed">
                <MarkdownRenderer content={message.content} />
                {message.content && (
                  <span className="inline-block w-1.5 h-4 bg-gold/60 ml-0.5 animate-pulse rounded-sm" />
                )}
              </div>
            ) : (
              <AnimatedText text={message.content} animate={animate} />
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
                onFileUploadRequest={onFileUploadRequest}
              />
            ))}

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
            <AnimatedText text={message.content} animate={animate} />
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
        return <AnimatedText text={message.content} animate={animate} />
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
          <div className="whitespace-pre-wrap text-sm">{message.content}</div>
        </div>
      </div>
    </div>
  )
}
