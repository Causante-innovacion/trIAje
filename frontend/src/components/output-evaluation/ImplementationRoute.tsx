import { ChevronRight, Shield } from 'lucide-react'
import { ImplementationPhase, ActionItem } from '../../types/evaluation.types'
import clsx from 'clsx'

interface ImplementationRouteProps {
    phases: ImplementationPhase[]
    actions: ActionItem[]
    disclaimer: string
}

export function ImplementationRoute({ phases, actions, disclaimer }: ImplementationRouteProps) {
    return (
        <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-card animate-fade-in">
            <h3 className="font-bold text-xl text-gray-900 mb-8">Ruta de Implementacion</h3>

            {/* Timeline */}
            <div className="flex items-start justify-between mb-10 relative px-4">
                {/* Connection line */}
                <div className="absolute top-6 left-12 right-12 h-0.5 bg-gray-200" />
                {/* Animated progress line */}
                <div
                    className="absolute top-6 left-12 h-0.5 bg-gold transition-all duration-1000"
                    style={{
                        width: `${((phases.findIndex(p => p.status === 'current') + 1) / phases.length) * 100}%`,
                        maxWidth: 'calc(100% - 6rem)'
                    }}
                />

                {phases.map((phase) => (
                    <div key={phase.id} className="flex flex-col items-center flex-1 relative z-10">
                        <div className={clsx(
                            'w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg mb-3 transition-all duration-300',
                            phase.status === 'current'
                                ? 'bg-gold text-white shadow-glow-gold scale-110'
                                : 'bg-gray-100 text-gray-400 border-2 border-gray-200'
                        )}>
                            {phase.id}
                        </div>
                        <p className={clsx(
                            'text-xs font-bold uppercase tracking-wide mb-1',
                            phase.status === 'current' ? 'text-gold' : 'text-gray-400'
                        )}>
                            Fase {phase.id}
                        </p>
                        <p className={clsx(
                            'text-sm text-center font-medium',
                            phase.status === 'current' ? 'text-gray-900' : 'text-gray-500'
                        )}>
                            {phase.name}
                        </p>
                    </div>
                ))}
            </div>

            {/* Action Items */}
            <div className="space-y-3 mb-8">
                {actions.map((action, index) => (
                    <div
                        key={index}
                        className="flex items-start gap-3 bg-gray-50 rounded-xl p-4 border border-gray-100 transition-all duration-200 hover:bg-cream-light hover:border-gold/20"
                    >
                        <div className="w-6 h-6 rounded-full bg-gold/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <ChevronRight className="w-4 h-4 text-gold" />
                        </div>
                        <p className="text-sm text-gray-700 leading-relaxed">{action.text}</p>
                    </div>
                ))}
            </div>

            {/* Disclaimer */}
            <div className="bg-amber-50 rounded-xl p-5 border border-amber-200 flex items-start gap-3">
                <Shield className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-amber-800 leading-relaxed">
                    {disclaimer}
                </p>
            </div>
        </div>
    )
}
