import { Avatar } from '../ui/Avatar'
import { Message } from '../../types/chat'
import { OptionButtons } from './OptionButtons'
import { FileUpload } from './FileUpload'
import { ProgressBar } from '../ui/ProgressBar'
import { SemaphoreBadge } from './SemaphoreBadge'
import { SourcesCitation } from './SourcesCitation'
import { ActionCard } from './ActionCard'
import { AlertCircle, WifiOff, ServerCrash, Clock } from 'lucide-react'

interface ChatMessageProps {
  message: Message
  onOptionSelect?: (value: string) => void
  onFileUpload?: (file: File) => void
  onFileUploadRequest?: () => void
}

function ErrorIcon({ type }: { type?: string }) {
  switch (type) {
    case 'network': return <WifiOff className="w-5 h-5 text-red-500" />
    case 'timeout': return <Clock className="w-5 h-5 text-amber-500" />
    case 'server': return <ServerCrash className="w-5 h-5 text-red-500" />
    default: return <AlertCircle className="w-5 h-5 text-red-500" />
  }
}

export function ChatMessage({ message, onOptionSelect, onFileUpload, onFileUploadRequest }: ChatMessageProps) {
  const isJusto = message.sender === 'justo'

  // Render message content based on type
  const renderContent = () => {
    switch (message.contentType) {

      // ── Intelligent chat response ──
      case 'semaphore_response':
        return (
          <div className="space-y-3">
            {/* Semaphore badge */}
            {message.metadata?.classification && (
              <SemaphoreBadge classification={message.metadata.classification} />
            )}

            {/* Gatillos alert for ROJO */}
            {message.metadata?.classification?.semaphore === 'rojo' &&
              (message.metadata.classification.gatillos_detected?.length ?? 0) > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm">
                  <p className="font-semibold text-red-800 flex items-center gap-2 mb-1">
                    <AlertCircle className="w-4 h-4" />
                    ⚠️ Indicadores de riesgo detectados
                  </p>
                  <ul className="list-disc list-inside text-red-700 text-xs space-y-0.5 ml-1">
                    {(message.metadata.classification.gatillos_detected ?? []).map((g, i) => (
                      <li key={i}>{g}</li>
                    ))}
                  </ul>
                </div>
              )}

            {/* Context required for AMARILLO */}
            {message.metadata?.classification?.semaphore === 'amarillo' &&
              (message.metadata.classification.context_required?.length ?? 0) > 0 && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm">
                  <p className="font-semibold text-amber-800 mb-1">
                    📋 Para darte una mejor respuesta, necesito saber:
                  </p>
                  <ul className="list-disc list-inside text-amber-700 text-xs space-y-0.5 ml-1">
                    {(message.metadata.classification.context_required ?? []).map((ctx, i) => (
                      <li key={i}>{ctx}</li>
                    ))}
                  </ul>
                </div>
              )}

            {/* Main message text */}
            <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>

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
            <div className="whitespace-pre-wrap">{message.content}</div>
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
        return <div className="whitespace-pre-wrap">{message.content}</div>
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
        <div className="bg-gold text-white rounded-2xl px-5 py-3 max-w-lg">
          <div className="whitespace-pre-wrap">{message.content}</div>
        </div>
      </div>
    </div>
  )
}
