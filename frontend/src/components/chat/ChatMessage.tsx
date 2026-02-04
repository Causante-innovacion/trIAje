import { Avatar } from '../ui/Avatar'
import { Message } from '../../types/chat'
import { OptionButtons } from './OptionButtons'
import { FileUpload } from './FileUpload'
import { ProgressBar } from '../ui/ProgressBar'

interface ChatMessageProps {
  message: Message
  onOptionSelect?: (value: string) => void
  onFileUpload?: (file: File) => void
}

export function ChatMessage({ message, onOptionSelect, onFileUpload }: ChatMessageProps) {
  const isJusto = message.sender === 'justo'

  // Render message content based on type
  const renderContent = () => {
    switch (message.contentType) {
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

      case 'file_upload':
        return (
          <>
            <div className="whitespace-pre-wrap mb-4">{message.content}</div>
            <FileUpload onFileSelect={onFileUpload} />
          </>
        )

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
