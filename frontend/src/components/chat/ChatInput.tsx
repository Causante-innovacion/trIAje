import { useState, useRef, useEffect } from 'react'
import { Send, Square, Loader2 } from 'lucide-react'
import { useChatStore } from '../../stores/chatStore'
import { ActionMenu } from './ActionMenu'

interface ChatInputProps {
  onSend: (message: string) => void
  onFileUpload?: (file: File) => void
  onStopProcessing?: () => void
}

export function ChatInput({ onSend, onFileUpload, onStopProcessing }: ChatInputProps) {
  const [value, setValue] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const { isProcessing, isTyping } = useChatStore()

  // Auto-resize textarea height to fit content (max ~6 lines)
  useEffect(() => {
    const el = inputRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 168) + 'px'
  }, [value])

  const isDisabled = isProcessing || isTyping || isUploading

  const handleFileSelect = async (file: File) => {
    setUploadError(null)

    // Validate by extension (MIME type varies by browser/OS and is unreliable)
    const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
    if (!['pdf', 'docx', 'txt'].includes(ext)) {
      setUploadError('Solo se aceptan archivos PDF, DOCX o TXT.')
      return
    }
    const sizeMB = file.size / 1024 / 1024
    if (sizeMB > 10) {
      setUploadError('El archivo excede el tamaño máximo de 10 MB.')
      return
    }

    // Use the same extractPlan flow as the dedicated FileUpload component
    if (onFileUpload) {
      onFileUpload(file)
      return
    }

    // Fallback: if no onFileUpload handler, upload via chat/upload endpoint
    setIsUploading(true)
    try {
      const { api } = await import('../../shared/services/api')
      const formData = new FormData()
      formData.append('file', file)
      formData.append('tool', 'general')

      const { data } = await api.post('/chat/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000,
      })

      const filename = (data.filename as string) || file.name
      const preview = (data.content_preview as string) || ''

      const msg = preview
        ? `📎 He adjuntado el archivo "${filename}". Analiza su contenido y dame una orientación legal inicial dentro de tu ámbito.\n\nContenido extraído:\n${preview}`
        : `📎 He adjuntado el archivo "${filename}". Analiza su contenido y dame una orientación legal inicial dentro de tu ámbito.`

      onSend(msg)
    } catch {
      setUploadError('No se pudo subir el archivo. Verifica que el servidor esté activo.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!value.trim() || isDisabled) return
    onSend(value.trim())
    setValue('')
    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as unknown as React.FormEvent)
    }
  }

  const handleStop = () => {
    if (onStopProcessing) {
      onStopProcessing()
    }
  }

  return (
    <div className="border-t border-gray-100 bg-white/80 backdrop-blur-sm px-4 py-4">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
        <div className="chat-input-container">
          <ActionMenu onFileSelect={handleFileSelect} />

          <textarea
            ref={inputRef}
            rows={1}
            wrap="soft"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isUploading
                ? 'Subiendo archivo...'
                : isDisabled
                  ? 'Espere a que termine el procesamiento...'
                  : 'Escribe tu respuesta aquí... (Shift+Enter para nueva línea)'
            }
            className="chat-input resize-none overflow-y-auto"
            disabled={isDisabled}
          />

          <div className="flex items-center gap-2">
            {isUploading ? (
              <>
                <span className="text-xs text-gray-400 uppercase tracking-wide hidden sm:block">
                  Estado<br />
                  <strong className="text-blue-500">Subiendo</strong>
                </span>
                <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                  <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
                </div>
              </>
            ) : isDisabled ? (
              <>
                <span className="text-xs text-gray-400 uppercase tracking-wide hidden sm:block">
                  Estado<br />
                  <strong className="text-gold">Procesando</strong>
                </span>
                <button
                  type="button"
                  className="w-10 h-10 rounded-full bg-red-100 hover:bg-red-200 flex items-center justify-center transition-colors cursor-pointer"
                  onClick={handleStop}
                  title="Detener procesamiento"
                >
                  <Square className="w-4 h-4 text-red-500" />
                </button>
              </>
            ) : (
              <>
                <span className="text-xs text-gray-400 uppercase tracking-wide hidden sm:block">
                  Presiona<br />
                  <strong>Enter</strong>
                </span>
                <button
                  type="submit"
                  className="send-button"
                  disabled={!value.trim()}
                >
                  <Send className="w-5 h-5" />
                </button>
              </>
            )}
          </div>
        </div>

        {uploadError && (
          <p className="text-red-500 text-xs mt-2 pl-1">{uploadError}</p>
        )}
      </form>
    </div>
  )
}
