import { OrganizationProfile } from '../../types/adviser.types'
import clsx from 'clsx'

interface OrganizationProfileCardProps {
    profile: OrganizationProfile
    fundingDescription: string
}

export function OrganizationProfileCard({ profile, fundingDescription }: OrganizationProfileCardProps) {
    const getStatusBadge = (status: string) => {
        const config = {
            green: { bg: 'bg-green-100', text: 'text-green-800', label: 'SUNARP' },
            yellow: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'RUC' },
            red: { bg: 'bg-red-100', text: 'text-red-800', label: 'APCI' }
        }
        const c = config[status as keyof typeof config]
        return (
            <span className={clsx('px-3 py-1 rounded text-xs font-bold', c.bg, c.text)}>
                {c.label}
            </span>
        )
    }

    const getStageBadge = (stage: string) => {
        const labels = {
            prototipo: 'Prototipo',
            piloto: 'Piloto',
            escalamiento: 'Escalamiento',
            unknown: 'Unknown'
        }
        return (
            <span className="px-3 py-1 rounded bg-gray-100 text-gray-700 text-xs font-semibold">
                {labels[stage as keyof typeof labels] || 'Unknown'}
            </span>
        )
    }

    return (
        <div className="bg-yellow-50 rounded-xl border-2 border-yellow-400 p-6">
            <div className="flex items-center gap-2 mb-4">
                <div className="bg-yellow-400 w-5 h-5 transform rotate-45 rounded-sm" />
                <h3 className="text-lg font-bold text-gray-900">Perfil de la Organización</h3>
            </div>

            <div className="grid grid-cols-3 gap-6 mb-6">
                <div>
                    <p className="text-xs text-gray-600 mb-1">ENTIDAD</p>
                    <p className="font-bold text-sm text-gray-900">{profile.entityName}</p>
                </div>
                <div>
                    <p className="text-xs text-gray-600 mb-2">ESTADO LEGAL</p>
                    <div className="flex gap-2">
                        {getStatusBadge('green')}
                        {getStatusBadge('yellow')}
                        {getStatusBadge('red')}
                    </div>
                </div>
                <div>
                    <p className="text-xs text-gray-600 mb-2">ETAPA</p>
                    {getStageBadge(profile.stage)}
                </div>
            </div>

            <div className="bg-white rounded-lg p-4 border border-yellow-200">
                <p className="text-xs text-gray-600 mb-2">FINANCIAMIENTO CRÍTICO</p>
                <p className="text-sm text-gray-700 mb-2">{fundingDescription}</p>
                <div className="flex items-center gap-2">
                    {profile.fundingTypes.includes('extranjero') && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded">
                            USD Internacional
                        </span>
                    )}
                    {profile.fundingTypes.includes('nacional') && (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-bold rounded">
                            Nacional
                        </span>
                    )}
                </div>
            </div>
        </div>
    )
}
