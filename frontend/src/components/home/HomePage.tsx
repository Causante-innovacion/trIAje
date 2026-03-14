import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send, Loader2, X } from 'lucide-react'
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
  const [showTerms, setShowTerms] = useState(false)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const isOverLimit = inputValue.length > MAX_MESSAGE_LENGTH

  // Auto-resize textarea height to fit content (max ~6 lines)
  useEffect(() => {
    const el = inputRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 168) + 'px'
  }, [inputValue])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isOverLimit) return

    startIntelligentChat(inputValue.trim())
    navigate('/chat')
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
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
      let errorMessage = 'Error procesando el archivo'
      if (error instanceof Error) {
        if (error.message.includes('413')) {
          errorMessage = 'El archivo es demasiado grande para ser procesado.'
        } else {
          errorMessage = error.message
        }
      }
      setUploadError(`No se pudo procesar el archivo. ${errorMessage}`)
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
            <textarea
              ref={inputRef}
              rows={1}
              wrap="soft"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isUploading ? 'Procesando archivo...' : 'Escribe tu consulta legal aquí...'}
              className="chat-input resize-none overflow-y-auto"
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
            Presiona <strong className="text-gray-500">Enter</strong> para enviar · <strong className="text-gray-500">Shift+Enter</strong> para nueva línea
          </p>
        </form>

        {/* T&C notice */}
        <p className="text-center text-xs text-gray-400 mt-6">
          Al usar esta herramienta aceptas nuestros{' '}
          <button
            type="button"
            onClick={() => setShowTerms(true)}
            className="underline underline-offset-2 text-causante-ocre hover:opacity-70 transition-opacity"
          >
            Términos y Condiciones
          </button>
        </p>
      </main>

      {/* T&C Modal */}
      {showTerms && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setShowTerms(false)}
          />
          <div className="relative bg-white rounded-3xl shadow-2xl max-w-lg w-full max-h-[80vh] flex flex-col overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h2 className="text-base font-black text-gray-900 tracking-tight">Términos y Condiciones</h2>
              <button
                onClick={() => setShowTerms(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="overflow-y-auto px-6 py-5 text-sm text-gray-600 leading-relaxed space-y-4">
              <p>
                <strong className="text-gray-900">1. Naturaleza del servicio.</strong>{' '}
                JUSTO es una herramienta de orientación legal de carácter informativo. Las respuestas generadas no constituyen asesoría legal formal ni reemplazan la consulta con un abogado habilitado.
              </p>
              <p>
                <strong className="text-gray-900">2. Limitación de responsabilidad.</strong>{' '}
                El uso de esta plataforma es bajo tu propia responsabilidad. Causante no garantiza la exactitud, completitud o actualización de la información proporcionada.
              </p>
              <p>
                <strong className="text-gray-900">3. Datos personales.</strong>{' '}
                La información que ingreses en la plataforma será utilizada únicamente para generar las respuestas de orientación legal. No será compartida con terceros sin tu consentimiento.
              </p>
              <p>
                <strong className="text-gray-900">4. Confidencialidad.</strong>{' '}
                Aunque tratamos los datos con la debida diligencia, no se garantiza confidencialidad absoluta en entornos digitales. Evita ingresar información altamente sensible.
              </p>
              <p>
                <strong className="text-gray-900">5. Modificaciones.</strong>{' '}
                Causante se reserva el derecho de modificar estos términos en cualquier momento. El uso continuado de la plataforma implica la aceptación de los términos vigentes.
              </p>
            </div>
            <div className="px-6 py-4 border-t border-gray-100">
              <button
                onClick={() => setShowTerms(false)}
                className="w-full py-3 rounded-2xl bg-causante-ocre text-white text-xs font-black tracking-widest uppercase hover:bg-opacity-90 transition-all"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
