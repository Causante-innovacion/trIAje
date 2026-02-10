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
    const borderColor = isCritical ? 'border-red-400' : 'border-orange-400'
    const iconBgColor = isCritical ? 'bg-red-100' : 'bg-orange-100'
    const iconColor = isCritical ? 'text-red-600' : 'text-orange-600'
    const badgeColor = isCritical ? 'bg-red-600' : 'bg-orange-600'

    return (
        <div className={clsx(
            'bg-white rounded-xl border-2 p-6',
            borderColor
        )}>
            <div className="flex items-start gap-4 mb-4">
                <div className={clsx('w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0', iconBgColor)}>
                    <Icon className={clsx('w-6 h-6', iconColor)} />
                </div>
                <div className="flex-1">
                    <div className="flex items-start justify-between gap-2 mb-2">
                        <h4 className="font-bold text-gray-900">{condition.title}</h4>
                        <span className={clsx('px-2 py-1 rounded text-xs font-bold text-white', badgeColor)}>
                            {condition.severity}
                        </span>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600">
                        <div>
                            <span className="font-semibold">TIEMPO:</span> {condition.time}
                        </div>
                        <div>
                            <span className="font-semibold">COSTO:</span> {condition.cost}
                        </div>
                    </div>
                </div>
            </div>

            <div className="space-y-3">
                <div>
                    <p className="text-sm font-semibold text-gray-900 mb-1">¿POR QUÉ ES NECESARIO?</p>
                    <p className="text-sm text-gray-700">{condition.reason}</p>
                </div>

                <div>
                    <p className="text-sm font-semibold text-gray-900 mb-2">REQUISITOS</p>
                    <ul className="space-y-1">
                        {condition.requirements.map((req, index) => (
                            <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                                <span className="text-gray-400 mt-1">•</span>
                                <span>{req}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    )
}
