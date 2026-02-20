import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send, Loader2 } from 'lucide-react'
import { ActionMenu } from '../chat/ActionMenu'
import { MAX_MESSAGE_LENGTH } from '../../types/chat'
import { useChatStore } from '../../stores/chatStore'
import { documentsApi } from '../../shared/services/api'

export function HomePage() {
  const navigate = useNavigate()
  const { startIntelligentChat, setExtractedPlan } = useChatStore()
  const [inputValue, setInputValue] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)

  const isOverLimit = inputValue.length > MAX_MESSAGE_LENGTH

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isOverLimit) return

    startIntelligentChat(inputValue.trim())
    navigate('/chat')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e)
    }
  }

  const handleFileSelect = async (file: File) => {
    setUploadError(null)

    // Validate extension
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
      // Use the same extractPlan flow as ChatContainer.handleFileUpload
      const fileId = Math.random().toString(36).substring(2)

      // Initialize chat state (sets currentTool='chat', sessionId, etc.)
      // Skip greeting since the ProjectInfoCard will be the first response.
      startIntelligentChat(undefined, true)

      // Show upload message in chat store (will appear when navigated)
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

      // Call extractPlan (same as ChatContainer)
      const response = await documentsApi.extractPlan(file)
      const plan = response.data

      // Update file status to complete
      useChatStore.getState().updateFileStatus(fileId, 'complete', 100)

      // Store extracted data in the global store
      setExtractedPlan(plan)

      // Add the project info card message
      useChatStore.getState().addMessage({
        sender: 'justo',
        content: 'project_info_card',
        contentType: 'text',
      })

      // Navigate to chat — ChatContainer will reconstruct projectInfo from extractedPlan
      navigate('/chat')
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Error procesando el archivo'
      setUploadError(
        `No se pudo procesar el archivo. ${errorMessage}\nVerifica que el servidor esté activo.`
      )
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Main content — centered vertically */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 max-w-3xl mx-auto w-full">

        {/* Title */}
        <div className="text-center mb-14">
          <h1 className="font-heading text-4xl md:text-5xl font-bold text-black mb-5 tracking-tight">
            ¿Cómo puedo ayudarte?
          </h1>
          <p className="subtitle">
            Somos un potenciador legal inteligente especializado en proyectos y emprendimientos sociales.
          </p>
        </div>

        {/* Chat input — single pill input */}
        <form onSubmit={handleSubmit} className="w-full">
          <div className="chat-input-container">
            <ActionMenu onFileSelect={handleFileSelect} />
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isUploading ? 'Procesando archivo...' : 'Escribe tu consulta legal aquí...'}
              className="chat-input"
              disabled={isUploading}
            />
            <div className="flex items-center gap-2">
              {/* Character counter */}
              {inputValue.length > MAX_MESSAGE_LENGTH * 0.8 && (
                <span className={`text-xs tabular-nums ${isOverLimit ? 'text-red-500 font-semibold' : 'text-gray-400'}`}>
                  {inputValue.length}/{MAX_MESSAGE_LENGTH}
                </span>
              )}
              {isUploading ? (
                <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                </div>
              ) : (
                <button
                  type="submit"
                  className="send-button"
                  disabled={!inputValue.trim() || isOverLimit}
                >
                  <Send className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>
          {uploadError && (
            <p className="text-red-500 text-xs mt-2 pl-1">{uploadError}</p>
          )}

          {/* Subtle hint */}
          <p className="text-center text-xs text-gray-400 mt-4">
            Presiona <strong className="text-gray-500">Enter</strong> para enviar
          </p>
        </form>
      </main>
    </div>
  )
}
