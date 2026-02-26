import { OrganizationProfile, LegalStatusCard } from '../../types/adviser.types'
import clsx from 'clsx'

interface OrganizationProfileCardProps {
    profile: OrganizationProfile
    fundingDescription: string
    legalStatusCards: LegalStatusCard[]
}

export function OrganizationProfileCard({ profile, legalStatusCards }: OrganizationProfileCardProps) {
    const statusConfig = {
        green: { bg: 'bg-green-100', text: 'text-green-800' },
        yellow: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
        red: { bg: 'bg-red-100', text: 'text-red-800' },
    }

    const getStageBadge = (stage: string) => {
        const labels = {
            prototipo: 'Prototipo',
            piloto: 'Piloto',
            escalamiento: 'Escalamiento',
            unknown: 'Desconocido',
        }
        return (
            <span className="px-3 py-1 rounded-full bg-cream text-gray-700 text-xs font-semibold">
                {labels[stage as keyof typeof labels] || stage}
            </span>
        )
    }

    return (
        <div className="bg-gold/5 rounded-2xl border-2 border-gold/30 p-5 md:p-8 animate-slide-up transition-all duration-300 hover:shadow-card-hover">
            <div className="flex items-center gap-3 mb-6">
                <h3 className="text-lg font-bold text-gray-900">Perfil de la Organización</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Entidad</p>
                    <p className="font-bold text-sm text-gray-900">{profile.entityName}</p>
                </div>
                <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Estado Legal</p>
                    <div className="flex gap-2 flex-wrap">
                        {legalStatusCards.map(card => {
                            const c = statusConfig[card.status]
                            return (
                                <span key={card.id} className={clsx('px-3 py-1 rounded-full text-xs font-bold', c.bg, c.text)}>
                                    {card.label}
                                </span>
                            )
                        })}
                    </div>
                </div>
                <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Etapa</p>
                    {getStageBadge(profile.stage)}
                </div>
            </div>

            <div className="bg-white rounded-xl p-5 border border-gold/20">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Tipo de Financiamiento</p>
                <div className="flex items-center gap-2 flex-wrap">
                    {profile.fundingTypes?.includes('extranjero') && (
                        <span className="badge-info">USD Internacional</span>
                    )}
                    {profile.fundingTypes?.includes('nacional') && (
                        <span className="badge bg-purple-100 text-purple-700">Nacional</span>
                    )}
                    {(!profile.fundingTypes || profile.fundingTypes.length === 0) && (
                        <span className="text-sm text-gray-400 italic">No especificado</span>
                    )}
                </div>
            </div>
        </div>
    )
}
