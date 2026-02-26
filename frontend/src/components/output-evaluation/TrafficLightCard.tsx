import { CheckCircle2, AlertCircle, XCircle } from 'lucide-react'
import { OrganizationStatus } from '../../types/evaluation.types'
import clsx from 'clsx'

interface TrafficLightCardProps {
    organization: OrganizationStatus
}

export function TrafficLightCard({ organization }: TrafficLightCardProps) {
    const getStatusConfig = () => {
        switch (organization.status) {
            case 'green':
                return {
                    icon: CheckCircle2,
                    bgColor: 'bg-green-50',
                    borderColor: 'border-green-400',
                    iconColor: 'text-green-600',
                    textColor: 'text-green-800',
                    label: 'VIABLE',
                    glowClass: 'hover:shadow-[0_0_20px_rgba(34,197,94,0.15)]'
                }
            case 'yellow':
                return {
                    icon: AlertCircle,
                    bgColor: 'bg-yellow-50',
                    borderColor: 'border-yellow-400',
                    iconColor: 'text-yellow-600',
                    textColor: 'text-yellow-800',
                    label: 'VIABLE CON AJUSTES NECESARIOS',
                    glowClass: 'hover:shadow-[0_0_20px_rgba(234,179,8,0.15)]'
                }
            case 'red':
                return {
                    icon: XCircle,
                    bgColor: 'bg-red-50',
                    borderColor: 'border-red-400',
                    iconColor: 'text-red-600',
                    textColor: 'text-red-800',
                    label: 'REQUIERE ATENCIÓN URGENTE',
                    glowClass: 'hover:shadow-[0_0_20px_rgba(239,68,68,0.15)]'
                }
        }
    }

    const config = getStatusConfig()
    const Icon = config.icon

    return (
        <div className={clsx(
            'rounded-2xl border-2 p-6 animate-fade-in transition-all duration-300 hover:-translate-y-0.5',
            config.bgColor,
            config.borderColor,
            config.glowClass
        )}>
            <div className="flex items-start gap-4">
                <div className={clsx(
                    'w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0',
                    config.bgColor
                )}>
                    <Icon className={clsx('w-7 h-7', config.iconColor)} />
                </div>
                <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-3">
                        <h3 className="font-bold text-lg text-gray-900">
                            {organization.name}
                        </h3>
                        <span className={clsx(
                            'inline-block px-3 py-1 rounded-full text-xs font-bold',
                            config.textColor,
                            config.bgColor
                        )}>
                            {config.label}
                        </span>
                    </div>
                    <p className="text-sm text-gray-700 leading-relaxed">
                        {organization.message}
                    </p>
                </div>
            </div>
        </div>
    )
}
