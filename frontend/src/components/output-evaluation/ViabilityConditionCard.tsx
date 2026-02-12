import { AlertCircle, FileText, Users, Scale, Lightbulb } from 'lucide-react'
import { ViabilityCondition } from '../../types/evaluation.types'
import clsx from 'clsx'

interface ViabilityConditionCardProps {
    condition: ViabilityCondition
}

const iconMap: Record<string, any> = {
    'alert': AlertCircle,
    'file': FileText,
    'users': Users,
    'scale': Scale,
    'lightbulb': Lightbulb,
}

export function ViabilityConditionCard({ condition }: ViabilityConditionCardProps) {
    const Icon = iconMap[condition.icon] || AlertCircle

    const isCritical = condition.severity === 'CRÍTICA'
    const borderColor = isCritical ? 'border-red-300' : 'border-orange-300'
    const iconBgColor = isCritical ? 'bg-red-100' : 'bg-orange-100'
    const iconColor = isCritical ? 'text-red-600' : 'text-orange-600'
    const badgeClass = isCritical ? 'badge-critical' : 'badge-warning'

    return (
        <div className={clsx(
            'bg-white rounded-2xl border-2 p-6 animate-slide-up transition-all duration-300 hover:-translate-y-0.5 hover:shadow-card-hover',
            borderColor
        )}>
            <div className="flex items-start gap-4 mb-5">
                <div className={clsx('w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0', iconBgColor)}>
                    <Icon className={clsx('w-6 h-6', iconColor)} />
                </div>
                <div className="flex-1">
                    <div className="flex items-start justify-between gap-2 mb-2">
                        <h4 className="font-bold text-gray-900">{condition.title}</h4>
                        <span className={badgeClass}>
                            {condition.severity}
                        </span>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                            <span className="font-semibold text-gray-700">Tiempo:</span> {condition.time}
                        </div>
                        <div className="flex items-center gap-1">
                            <span className="font-semibold text-gray-700">Costo:</span> {condition.cost}
                        </div>
                    </div>
                </div>
            </div>

            <div className="space-y-4">
                <div className="bg-gray-50 rounded-xl p-4">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Por que es necesario</p>
                    <p className="text-sm text-gray-700 leading-relaxed">{condition.reason}</p>
                </div>

                <div>
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Requisitos</p>
                    <ul className="space-y-2">
                        {condition.requirements.map((req, index) => (
                            <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                                <span className={clsx(
                                    'w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0 mt-0.5',
                                    isCritical ? 'bg-red-100 text-red-600' : 'bg-orange-100 text-orange-600'
                                )}>
                                    {index + 1}
                                </span>
                                <span>{req}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    )
}
