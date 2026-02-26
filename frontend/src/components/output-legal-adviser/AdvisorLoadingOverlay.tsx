/**
 * AdvisorLoadingOverlay
 * Full-screen overlay shown while generating the adviser prep package.
 * Cycles through descriptive messages so the user knows what the system is doing.
 */

import { useEffect, useState } from 'react'
import { Loader2, Search, FileText, MessageSquare, ClipboardList, Scale } from 'lucide-react'

const STEPS = [
  { icon: Search, text: 'Analizando tu consulta legal...' },
  { icon: FileText, text: 'Revisando el análisis de brechas del proyecto...' },
  { icon: Scale, text: 'Identificando temas críticos y riesgos legales...' },
  { icon: MessageSquare, text: 'Generando preguntas específicas para el abogado...' },
  { icon: ClipboardList, text: 'Preparando lista de documentos y decisiones previas...' },
  { icon: Loader2, text: 'Finalizando el paquete de preparación...' },
]

const STEP_DURATION_MS = 2200

interface Props {
  visible: boolean
}

export function AdvisorLoadingOverlay({ visible }: Props) {
  const [stepIndex, setStepIndex] = useState(0)

  useEffect(() => {
    if (!visible) {
      setStepIndex(0)
      return
    }
    const interval = setInterval(() => {
      setStepIndex(prev => (prev + 1 < STEPS.length ? prev + 1 : prev))
    }, STEP_DURATION_MS)
    return () => clearInterval(interval)
  }, [visible])

  if (!visible) return null

  const current = STEPS[stepIndex]
  const Icon = current.icon
  const progress = Math.round(((stepIndex + 1) / STEPS.length) * 100)

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-sm w-full mx-4 text-center animate-slide-up">
        {/* Icon */}
        <div className="w-16 h-16 rounded-2xl bg-cream flex items-center justify-center mx-auto mb-5">
          <Icon className={`w-8 h-8 text-gold ${Icon === Loader2 ? 'animate-spin' : 'animate-pulse'}`} />
        </div>

        {/* Title */}
        <h3 className="font-bold text-gray-900 text-lg mb-1">
          Preparando reunión con asesor
        </h3>
        <p className="text-sm text-gray-500 mb-6">
          Esto puede tomar unos segundos
        </p>

        {/* Current step message */}
        <div className="bg-gray-50 rounded-xl px-4 py-3 mb-5 min-h-[48px] flex items-center justify-center">
          <p className="text-sm font-medium text-gray-700 transition-all duration-300">
            {current.text}
          </p>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
          <div
            className="h-full bg-gold rounded-full transition-all duration-700 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Steps dots */}
        <div className="flex justify-center gap-1.5 mt-3">
          {STEPS.map((_, i) => (
            <div
              key={i}
              className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
                i <= stepIndex ? 'bg-gold' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
