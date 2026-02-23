import { useState } from 'react'
import { ChevronDown, ChevronRight, Brain } from 'lucide-react'

interface ThinkingBlockProps {
  content: string
  /** Si true, el modelo todavía está razonando (no llegó </think>) */
  isThinking: boolean
}

export function ThinkingBlock({ content, isThinking }: ThinkingBlockProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="mb-3 rounded-xl border border-amber-200 bg-amber-50/60 text-xs overflow-hidden">
      {/* Header colapsable */}
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-2 px-3 py-2 text-amber-700 hover:bg-amber-100/60 transition-colors text-left"
      >
        <Brain className="w-3.5 h-3.5 flex-shrink-0" />
        <span className="font-medium flex-1">
          {isThinking ? 'Razonando…' : 'Ver razonamiento'}
        </span>
        {isThinking ? (
          <span className="flex gap-0.5">
            <span className="w-1 h-1 rounded-full bg-amber-500 animate-bounce [animation-delay:0ms]" />
            <span className="w-1 h-1 rounded-full bg-amber-500 animate-bounce [animation-delay:150ms]" />
            <span className="w-1 h-1 rounded-full bg-amber-500 animate-bounce [animation-delay:300ms]" />
          </span>
        ) : (
          open
            ? <ChevronDown className="w-3.5 h-3.5 flex-shrink-0" />
            : <ChevronRight className="w-3.5 h-3.5 flex-shrink-0" />
        )}
      </button>

      {/* Contenido colapsable */}
      {(open || isThinking) && content && (
        <div className="px-3 pb-3 pt-1 border-t border-amber-200">
          <pre className="whitespace-pre-wrap font-mono text-amber-800/80 leading-relaxed text-[11px] max-h-48 overflow-y-auto">
            {content}
            {isThinking && (
              <span className="inline-block w-1.5 h-3 bg-amber-500/60 ml-0.5 animate-pulse rounded-sm" />
            )}
          </pre>
        </div>
      )}
    </div>
  )
}

/**
 * Parsea el contenido del mensaje separando el bloque <think> del texto real.
 *
 * Casos:
 *   - Razonando:  "<think>texto parcial..."          → isThinking=true, thinkContent, answer=""
 *   - Completo:   "<think>texto</think>respuesta..."  → isThinking=false, thinkContent, answer
 *   - Sin think:  "respuesta directa"                 → isThinking=false, thinkContent="", answer
 */
export function parseThinkContent(raw: string): {
  thinkContent: string
  answer: string
  isThinking: boolean
} {
  if (!raw.includes('<think>')) {
    return { thinkContent: '', answer: raw, isThinking: false }
  }

  const thinkStart = raw.indexOf('<think>') + '<think>'.length
  const thinkEnd = raw.indexOf('</think>')

  if (thinkEnd === -1) {
    // Todavía dentro del bloque <think> (streaming)
    return {
      thinkContent: raw.slice(thinkStart).trimStart(),
      answer: '',
      isThinking: true,
    }
  }

  return {
    thinkContent: raw.slice(thinkStart, thinkEnd).trim(),
    answer: raw.slice(thinkEnd + '</think>'.length).trimStart(),
    isThinking: false,
  }
}
