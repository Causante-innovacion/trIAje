import { Check, LucideIcon } from 'lucide-react'
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
  onStepClick: (index: number) => void
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
  onStepClick,
  completedQuestions,
  totalQuestions,
  isFinished = false,
}: ProgressTrackerProps) {
  let pct = Math.round((completedQuestions / totalQuestions) * 100)
  if (pct === 100 && !isFinished) pct = 99

  return (
    <div className="bg-white rounded-3xl border border-gray-100 p-6 md:p-8 mb-8">
      {/* Top row: title + counter */}
      <div className="flex justify-between items-center mb-5">
        <div>
          <h2 className="font-heading text-lg font-bold text-gray-900">Progreso</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Paso {currentStep + 1} de {steps.length}
          </p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold" style={{ color: '#b3994c' }}>
            {completedQuestions}
            <span className="text-gray-300">/{totalQuestions}</span>
          </span>
          <p className="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Respuestas</p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-100 h-2 rounded-full mb-6">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: '#b3994c' }}
        />
      </div>

      {/* Step dots */}
      <div className="flex items-center justify-between gap-1 overflow-x-auto pb-1">
        {steps.map((step, i) => {
          const isComplete = step.completed === step.total
          const isCurrent = i === currentStep
          const hasProgress = step.completed > 0
          const StepIcon = step.icon

          return (
            <button
              key={step.id}
              type="button"
              onClick={() => onStepClick(i)}
              className={clsx(
                'flex flex-col items-center gap-1.5 flex-shrink-0 group transition-all duration-200',
                'min-w-[56px] py-1'
              )}
              aria-label={step.name}
            >
              {/* Circle */}
              <div
                className={clsx(
                  'w-9 h-9 rounded-full flex items-center justify-center border-2 transition-all duration-200',
                  isComplete
                    ? 'bg-causante-ocre border-causante-ocre text-white'
                    : isCurrent
                      ? 'bg-white border-causante-ocre text-causante-ocre'
                      : hasProgress
                        ? 'bg-gold-50 border-gold-light text-causante-ocre'
                        : 'bg-gray-50 border-gray-200 text-gray-400 group-hover:border-gray-300'
                )}
              >
                {isComplete ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <StepIcon className="w-4 h-4" />
                )}
              </div>

              {/* Label */}
              <span
                className={clsx(
                  'text-[10px] font-bold uppercase tracking-wider whitespace-nowrap',
                  isCurrent
                    ? 'text-causante-ocre'
                    : isComplete
                      ? 'text-causante-ocre'
                      : 'text-gray-400'
                )}
              >
                {step.name}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
