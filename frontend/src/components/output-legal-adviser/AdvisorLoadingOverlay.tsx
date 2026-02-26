/**
 * AdvisorLoadingOverlay
 * Subtle fixed bottom banner shown while generating the adviser prep package.
 */

import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'

const STEPS = [
  'Analizando tu consulta legal...',
  'Revisando brechas del proyecto...',
  'Identificando temas críticos...',
  'Generando preguntas para el abogado...',
  'Preparando documentos y decisiones...',
  'Finalizando el paquete...',
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

  const progress = Math.round(((stepIndex + 1) / STEPS.length) * 100)

  return (
    <div className="fixed bottom-6 inset-x-0 flex justify-center z-50 animate-slide-up pointer-events-none">
      <div className="bg-gray-900 text-white rounded-2xl shadow-xl px-5 py-3.5 flex items-center gap-4 w-[320px] pointer-events-auto">
        {/* Spinner */}
        <Loader2 className="w-4 h-4 text-gold flex-shrink-0 animate-spin" />

        {/* Text */}
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-white/90 truncate">
            {STEPS[stepIndex]}
          </p>
          {/* Progress bar */}
          <div className="mt-1.5 w-full bg-white/10 rounded-full h-0.5 overflow-hidden">
            <div
              className="h-full bg-gold rounded-full transition-all duration-700 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

