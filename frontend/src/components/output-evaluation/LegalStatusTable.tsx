import { CheckCircle2, AlertCircle, XCircle } from 'lucide-react'
import { LegalEntity } from '../../types/evaluation.types'
import clsx from 'clsx'

interface LegalStatusTableProps {
    entities: LegalEntity[]
}

export function LegalStatusTable({ entities }: LegalStatusTableProps) {
    const getStatusIcon = (status: 'green' | 'yellow' | 'red') => {
        switch (status) {
            case 'green':
                return <CheckCircle2 className="w-5 h-5 text-green-600" />
            case 'yellow':
                return <AlertCircle className="w-5 h-5 text-yellow-600" />
            case 'red':
                return <XCircle className="w-5 h-5 text-red-600" />
        }
    }

    const getPriorityBadge = (priority: string) => {
        const config = {
            'BAJA': 'bg-green-100 text-green-800 border-green-200',
            'ALTA': 'bg-orange-100 text-orange-800 border-orange-200',
            'CRÍTICA': 'bg-red-100 text-red-800 border-red-200',
        }
        return (
            <span className={clsx(
                'px-3 py-1 rounded-full text-xs font-bold border',
                config[priority as keyof typeof config]
            )}>
                {priority}
            </span>
        )
    }

    const getRowBgColor = (priority: string) => {
        switch (priority) {
            case 'CRÍTICA':
                return 'bg-red-50'
            case 'ALTA':
                return 'bg-orange-50'
            default:
                return 'bg-white'
        }
    }

    return (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-pink-50 border-b border-gray-200">
                        <tr>
                            <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">
                                Entidad / Objeto
                            </th>
                            <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">
                                Estado
                            </th>
                            <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">
                                Prioridad
                            </th>
                            <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">
                                Acción
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {entities.map((entity, index) => (
                            <tr
                                key={index}
                                className={clsx(
                                    'border-b border-gray-100 last:border-b-0',
                                    getRowBgColor(entity.priority)
                                )}
                            >
                                <td className="px-6 py-4">
                                    <div>
                                        <p className="font-bold text-sm text-gray-900">{entity.entity}</p>
                                        <p className="text-xs text-gray-500 mt-1">{entity.description}</p>
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-2">
                                        {getStatusIcon(entity.status)}
                                        <span className="text-sm font-semibold text-gray-900">
                                            {entity.statusText}
                                        </span>
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    {getPriorityBadge(entity.priority)}
                                </td>
                                <td className="px-6 py-4">
                                    <p className="text-sm text-gray-700">{entity.action}</p>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
