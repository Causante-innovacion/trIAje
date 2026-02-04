import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Paperclip, Send } from 'lucide-react'
import { ToolCard } from './ToolCard'
import { TOOLS, ToolType } from '../../types/chat'
import { useChatStore } from '../../stores/chatStore'

export function HomePage() {
  const navigate = useNavigate()
  const { startTool } = useChatStore()
  const [inputValue, setInputValue] = useState('')

  const handleToolSelect = (toolId: ToolType) => {
    startTool(toolId)
    navigate('/chat')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim()) return

    // For free text, we'll start with evaluation tool context but handle as general query
    startTool('evaluation')
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

        {/* Tool cards */}
        <div className="flex flex-col md:flex-row gap-6 mb-12 w-full justify-center">
          {TOOLS.map((tool) => (
            <ToolCard
              key={tool.id}
              id={tool.id}
              name={tool.name}
              description={tool.description}
              icon={tool.icon}
              onClick={handleToolSelect}
            />
          ))}
        </div>

        {/* Free text hint */}
        <p className="text-gray-600 mb-6 text-center">
          También puedes escribir libremente.{' '}
          <span className="text-gold">
            Nuestro asistente sugerirá la mejor herramienta
          </span>{' '}
          según tu consulta.
        </p>

        {/* Chat input */}
        <form onSubmit={handleSubmit} className="w-full max-w-3xl">
          <div className="chat-input-container">
            <button
              type="button"
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              title="Adjuntar archivo"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu consulta legal aquí o sube un documento..."
              className="chat-input"
            />
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400 uppercase tracking-wide hidden sm:block">
                Presiona<br />
                <strong>Enter</strong>
              </span>
              <button
                type="submit"
                className="send-button"
                disabled={!inputValue.trim()}
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
