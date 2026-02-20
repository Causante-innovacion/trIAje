import { useState, useRef } from 'react'
import { Send, Square, Loader2 } from 'lucide-react'
import { useChatStore } from '../../stores/chatStore'
import { ActionMenu } from './ActionMenu'
import { api } from '../../shared/services/api'

interface ChatInputProps {
  onSend: (message: string) => void
}

export function ChatInput({ onSend }: ChatInputProps) {
  const [value, setValue] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const { isProcessing, isTyping } = useChatStore()

  const isDisabled = isProcessing || isTyping || isUploading

  const handleFileSelect = async (file: File) => {
    setUploadError(null)

    // Validate by extension (MIME type varies by browser/OS and is unreliable)
    const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
    if (!['pdf', 'docx'].includes(ext)) {
      setUploadError('Solo se aceptan archivos PDF o DOCX.')
      return
    }
    const sizeMB = file.size / 1024 / 1024
    if (sizeMB > 10) {
      setUploadError('El archivo excede el tamaño máximo de 10 MB.')
      return
    }

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('tool', 'general')

      const { data } = await api.post('/chat/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000,
      })

      const filename = (data.filename as string) || file.name
      const preview = (data.content_preview as string) || ''

      // Start with a recognised project-analysis trigger so the classifier
      // routes this directly into the project analysis pipeline.
      const msg = preview
        ? `Analiza mi proyecto. 📎 He adjuntado el archivo "${filename}":\n\n${preview}`
        : `Analiza mi proyecto. 📎 He adjuntado el archivo "${filename}".`

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
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e)
    }
  }

  return (
    <div className="border-t border-gray-100 bg-white/80 backdrop-blur-sm px-4 py-4">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
        <div className="chat-input-container">
          <ActionMenu onFileSelect={handleFileSelect} />

          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isUploading
                ? 'Subiendo archivo...'
                : isDisabled
                ? 'Espere a que termine el procesamiento...'
                : 'Escribe tu respuesta aquí...'
            }
            className="chat-input"
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
                  className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center"
                  disabled
                >
                  <Square className="w-4 h-4 text-gray-400" />
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
