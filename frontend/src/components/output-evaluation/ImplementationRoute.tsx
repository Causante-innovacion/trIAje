import { ChevronRight } from 'lucide-react'
import { ImplementationPhase, ActionItem } from '../../types/evaluation.types'
import clsx from 'clsx'

interface ImplementationRouteProps {
    phases: ImplementationPhase[]
    actions: ActionItem[]
    disclaimer: string
}

export function ImplementationRoute({ phases, actions, disclaimer }: ImplementationRouteProps) {
    return (
        <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
            <h3 className="font-bold text-gray-900 mb-6">Ruta de Implementación</h3>

            {/* Timeline */}
            <div className="flex items-center justify-between mb-8 relative">
                {/* Connection line */}
                <div className="absolute top-6 left-0 right-0 h-0.5 bg-gray-300 -z-10" />

                {phases.map((phase) => (
                    <div key={phase.id} className="flex flex-col items-center flex-1">
                        <div className={clsx(
                            'w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg mb-2',
                            phase.status === 'current' ? 'bg-yellow-400 text-white' : 'bg-gray-200 text-gray-600'
                        )}>
                            {phase.id}
                        </div>
                        <p className={clsx(
                            'text-sm font-semibold text-center',
                            phase.status === 'current' ? 'text-gray-900' : 'text-gray-600'
                        )}>
                            Fase {phase.id}:
                        </p>
                        <p className={clsx(
                            'text-sm text-center',
                            phase.status === 'current' ? 'text-gray-900 font-semibold' : 'text-gray-600'
                        )}>
                            {phase.name}
                        </p>
                    </div>
                ))}
            </div>

            {/* Action Items */}
            <div className="space-y-3 mb-6">
                {actions.map((action, index) => (
                    <div key={index} className="flex items-start gap-3 bg-white rounded-lg p-4 border border-gray-200">
                        <ChevronRight className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                        <p className="text-sm text-gray-700">{action.text}</p>
                    </div>
                ))}
            </div>

            {/* Disclaimer */}
            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                <p className="text-xs text-gray-600 text-center italic">
                    {disclaimer}
                </p>
            </div>
        </div>
    )
}
