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
        const classMap: Record<string, string> = {
            'BAJA': 'badge-success',
            'ALTA': 'badge-warning',
            'CRÍTICA': 'badge-critical',
        }
        return (
            <span className={classMap[priority] || 'badge-info'}>
                {priority}
            </span>
        )
    }

    const getRowBgColor = (priority: string) => {
        switch (priority) {
            case 'CRÍTICA':
                return 'bg-red-50/50'
            case 'ALTA':
                return 'bg-orange-50/50'
            default:
                return 'bg-white'
        }
    }

    return (
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-card animate-fade-in">
            <div className="overflow-x-auto">
                <table className="w-full min-w-[520px]">
                    <thead className="bg-cream border-b border-gray-200">
                        <tr>
                            <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wide">
                                Entidad / Objeto
                            </th>
                            <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wide">
                                Estado
                            </th>
                            <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wide">
                                Prioridad
                            </th>
                            <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wide">
                                Accion
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {entities.map((entity, index) => (
                            <tr
                                key={index}
                                className={clsx(
                                    'border-b border-gray-100 last:border-b-0 transition-colors duration-200 hover:bg-cream-light',
                                    getRowBgColor(entity.priority)
                                )}
                            >
                                <td className="px-6 py-4">
                                    <div>
                                        <p className="font-semibold text-sm text-gray-900">{entity.entity}</p>
                                        <p className="text-xs text-gray-500 mt-1">{entity.description}</p>
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-2">
                                        {getStatusIcon(entity.status)}
                                        <span className="text-sm font-medium text-gray-900">
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
