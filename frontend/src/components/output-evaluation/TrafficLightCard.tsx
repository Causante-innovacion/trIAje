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
                    label: 'VIABLE'
                }
            case 'yellow':
                return {
                    icon: AlertCircle,
                    bgColor: 'bg-yellow-50',
                    borderColor: 'border-yellow-400',
                    iconColor: 'text-yellow-600',
                    textColor: 'text-yellow-800',
                    label: 'VIABLE CON AJUSTES NECESARIOS'
                }
            case 'red':
                return {
                    icon: XCircle,
                    bgColor: 'bg-red-50',
                    borderColor: 'border-red-400',
                    iconColor: 'text-red-600',
                    textColor: 'text-red-800',
                    label: 'REQUIERE ATENCIÓN URGENTE'
                }
        }
    }

    const config = getStatusConfig()
    const Icon = config.icon

    return (
        <div className={clsx(
            'rounded-xl border-2 p-6',
            config.bgColor,
            config.borderColor
        )}>
            <div className="flex items-start gap-4">
                <Icon className={clsx('w-8 h-8 flex-shrink-0', config.iconColor)} />
                <div className="flex-1">
                    <h3 className="font-bold text-lg text-gray-900 mb-1">
                        {organization.name}
                    </h3>
                    <p className={clsx('text-sm font-semibold mb-2', config.textColor)}>
                        {config.label}
                    </p>
                    <p className="text-sm text-gray-700">
                        {organization.message}
                    </p>
                </div>
            </div>
        </div>
    )
}
