import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send } from 'lucide-react'
import { ActionMenu } from '../chat/ActionMenu'
import { MAX_MESSAGE_LENGTH } from '../../types/chat'
import { useChatStore } from '../../stores/chatStore'

export function HomePage() {
  const navigate = useNavigate()
  const { startIntelligentChat } = useChatStore()
  const [inputValue, setInputValue] = useState('')

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

  return (
    <div className="min-h-screen flex flex-col pt-20 pb-16">
      {/* Main content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 max-w-6xl mx-auto w-full">
        {/* Title section */}
        <div className="text-center mb-12">
          <h1 className="font-heading text-4xl md:text-5xl font-semibold text-gray-900 mb-4">
            ¿Cómo puedo ayudarte hoy?
          </h1>
          <p className="subtitle">
            Tu asistente legal inteligente para análisis de riesgos y cumplimiento
            normativo diseñado para organizaciones civiles.
          </p>
        </div>

        {/* Chat input */}
        <form onSubmit={handleSubmit} className="w-full max-w-3xl">
          <div className="chat-input-container">
            <ActionMenu />
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu consulta legal aquí o sube un documento..."
              className="chat-input"
            />
            <div className="flex items-center gap-2">
              {/* Character counter */}
              {inputValue.length > MAX_MESSAGE_LENGTH * 0.8 && (
                <span className={`text-xs tabular-nums ${isOverLimit ? 'text-red-500 font-semibold' : 'text-gray-400'}`}>
                  {inputValue.length}/{MAX_MESSAGE_LENGTH}
                </span>
              )}
              <span className="text-xs text-gray-400 uppercase tracking-wide hidden sm:block">
                Presiona<br />
                <strong>Enter</strong>
              </span>
              <button
                type="submit"
                className="send-button"
                disabled={!inputValue.trim() || isOverLimit}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </form>
      </main>
    </div>
  )
}
