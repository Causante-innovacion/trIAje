import { LucideIcon } from 'lucide-react'
import clsx from 'clsx'

interface StepDef {
  id: string
  name: string
  icon: LucideIcon
  completed: number
  total: number
}

interface ProgressTrackerProps {
  steps: StepDef[]
  currentStep: number
  onStepClick?: (index: number) => void
  completedQuestions: number
  totalQuestions: number
  isFinished?: boolean
}

/**
 * Step-based progress indicator for the legal form wizard.
 * Causante Design: clean, flat, gold accents.
 */
export function ProgressTracker({
  steps,
  currentStep,
  completedQuestions,
  totalQuestions,
  isFinished = false,
}: ProgressTrackerProps) {
  let pct = Math.round((completedQuestions / totalQuestions) * 100)
  if (pct === 100 && !isFinished) pct = 99

  const activeStep = steps[currentStep] || steps[0]
  const ActiveIcon = activeStep.icon

  return (
    <div className="bg-white rounded-[1.5rem] border border-gray-50 p-5 shadow-sm h-full flex flex-col justify-between">
      {/* Top row: title + counter */}
      <div className="flex justify-between items-end mb-4">
        <div>
          <h2 className="font-heading text-lg font-black text-gray-900 leading-none">Progreso</h2>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-2">
            Paso {currentStep + 1} de {steps.length}
          </p>
        </div>
        <div className="text-right">
          <span className="text-xl font-black text-causante-ocre">
            {completedQuestions}
            <span className="text-gray-200">/{totalQuestions}</span>
          </span>
          <p className="text-[9px] text-gray-400 uppercase font-black tracking-widest mt-0.5">Respuestas</p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-50 h-2.5 rounded-full mb-6 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(179,153,76,0.2)]"
          style={{ width: `${pct}%`, backgroundColor: '#b3994c' }}
        />
      </div>

      {/* Current Step Focus */}
      <div className="flex flex-col items-center py-0.5">
        <div className="relative">
          <div className="w-14 h-14 rounded-[1.25rem] bg-causante-crema/10 border-2 border-causante-ocre flex items-center justify-center text-causante-ocre shadow-lg shadow-causante-ocre/5">
            <ActiveIcon className="w-7 h-7" />
            <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-causante-ocre text-white flex items-center justify-center text-[9px] font-black border-[3px] border-white">
              {currentStep + 1}
            </div>
          </div>
        </div>
        <span className="mt-3 text-[10px] font-black uppercase tracking-[0.2em] text-causante-ocre">
          {activeStep.name}
        </span>
      </div>

      {/* Simplified dots for other steps */}
      <div className="flex items-center justify-center gap-2 mt-8">
        {steps.map((_, i) => (
          <div
            key={i}
            className={clsx(
              'h-1.5 rounded-full transition-all duration-500',
              i === currentStep ? 'w-8 bg-causante-ocre' : 'w-1.5 bg-gray-200'
            )}
          />
        ))}
      </div>
    </div>
  )
}
