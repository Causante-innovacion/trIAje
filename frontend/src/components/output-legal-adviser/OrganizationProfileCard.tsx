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
            <span className={clsx('px-3 py-1 rounded-full text-xs font-bold', c.bg, c.text)}>
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
            <span className="px-3 py-1 rounded-full bg-cream text-gray-700 text-xs font-semibold">
                {labels[stage as keyof typeof labels] || 'Unknown'}
            </span>
        )
    }

    return (
        <div className="bg-gold/5 rounded-2xl border-2 border-gold/30 p-8 animate-slide-up transition-all duration-300 hover:shadow-card-hover">
            <div className="flex items-center gap-3 mb-6">
                <div className="bg-gold w-5 h-5 transform rotate-45 rounded-sm" />
                <h3 className="text-lg font-bold text-gray-900">Perfil de la Organizacion</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Entidad</p>
                    <p className="font-bold text-sm text-gray-900">{profile.entityName}</p>
                </div>
                <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Estado Legal</p>
                    <div className="flex gap-2 flex-wrap">
                        {getStatusBadge('green')}
                        {getStatusBadge('yellow')}
                        {getStatusBadge('red')}
                    </div>
                </div>
                <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Etapa</p>
                    {getStageBadge(profile.stage)}
                </div>
            </div>

            <div className="bg-white rounded-xl p-5 border border-gold/20">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Financiamiento Critico</p>
                <p className="text-sm text-gray-700 mb-3 leading-relaxed">{fundingDescription}</p>
                <div className="flex items-center gap-2">
                    {profile.fundingTypes.includes('extranjero') && (
                        <span className="badge-info">USD Internacional</span>
                    )}
                    {profile.fundingTypes.includes('nacional') && (
                        <span className="badge bg-purple-100 text-purple-700">Nacional</span>
                    )}
                </div>
            </div>
        </div>
    )
}
