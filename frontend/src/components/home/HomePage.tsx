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
            <ActionMenu />
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu consulta legal aquí..."
              className="chat-input"
            />
            <div className="flex items-center gap-2">
              {/* Character counter */}
              {inputValue.length > MAX_MESSAGE_LENGTH * 0.8 && (
                <span className={`text-xs tabular-nums ${isOverLimit ? 'text-red-500 font-semibold' : 'text-gray-400'}`}>
                  {inputValue.length}/{MAX_MESSAGE_LENGTH}
                </span>
              )}
              <button
                type="submit"
                className="send-button"
                disabled={!inputValue.trim() || isOverLimit}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Subtle hint */}
          <p className="text-center text-xs text-gray-400 mt-4">
            Presiona <strong className="text-gray-500">Enter</strong> para enviar
          </p>
        </form>
      </main>
    </div>
  )
}
