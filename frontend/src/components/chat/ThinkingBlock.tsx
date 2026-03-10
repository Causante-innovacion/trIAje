import { useState } from 'react'
import { ChevronDown, ChevronRight, Brain, Globe } from 'lucide-react'

interface ThinkingBlockProps {
  content: string
  /** Si true, el modelo todavía está razonando (no llegó </think>) */
  isThinking: boolean
}

/**
 * Heurística rápida para detectar si el texto del razonamiento está
 * mayoritariamente en inglés. Busca palabras de alta frecuencia en inglés
 * que raramente aparecen en español formal.
 */
function isLikelyEnglish(text: string): boolean {
  if (!text || text.length < 40) return false
  const sample = text.slice(0, 600).toLowerCase()
  // Palabras comunes de inglés que NO son palabras españolas
  const englishIndicators = [
    ' the ', ' is ', ' are ', ' this ', ' that ', ' for ',
    ' with ', ' have ', ' will ', ' need ', ' not ', ' can ',
    ' let ', ' also ', ' when ', ' there ', ' then ',
    'i need to', 'let me', 'the user', 'we need', 'i will',
    'the question', 'the system', 'first,', 'second,', 'third,',
    'however,', 'therefore,', 'note that',
  ]
  const hits = englishIndicators.filter(w => sample.includes(w)).length
  // Si hay 3 o más indicadores, probable inglés
  return hits >= 3
}

export function ThinkingBlock({ content, isThinking }: ThinkingBlockProps) {
  const [open, setOpen] = useState(false)

  const inEnglish = !isThinking && isLikelyEnglish(content)

  return (
    <div className="mb-3 rounded-xl border border-amber-200 bg-amber-50/60 text-xs overflow-hidden">
      {/* Header colapsable */}
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-2 px-3 py-2 text-amber-700 hover:bg-amber-100/60 transition-colors text-left"
      >
        <Brain className="w-3.5 h-3.5 flex-shrink-0" />
        <span className="font-medium flex-1">
          {isThinking ? 'Analizando…' : 'Ver razonamiento completo'}
        </span>

        {/* Badge de idioma — solo cuando el razonamiento quedó en inglés */}
        {inEnglish && !isThinking && (
          <span
            title="El razonamiento interno del modelo quedó en inglés. La respuesta final está en español."
            className="
              inline-flex items-center gap-1
              px-1.5 py-0.5 rounded-full
              bg-amber-200/80 text-amber-800
              text-[10px] font-medium
              border border-amber-300/60
              cursor-help
            "
          >
            <Globe className="w-2.5 h-2.5" />
            EN
          </span>
        )}

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
          {inEnglish && (
            <p className="text-[10px] text-amber-600/80 italic mb-1.5">
              * Razonamiento interno en inglés — la respuesta a continuación está en español.
            </p>
          )}
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
