import {
    User,
    MapPin,
    Building2,
    Monitor,
    FileText,
    Globe,
    Briefcase,
    Shield,
    Award,
    Users,
    ArrowLeft,
    Receipt,
    Store,
    Copyright,
    UserCheck,
} from 'lucide-react'
import { FormalizationRoute } from './mockFormalizationData'

const STAGE_ICONS = {
    user: User,
    mapPin: MapPin,
    building: Building2,
    monitor: Monitor,
    fileText: FileText,
    globe: Globe,
    briefcase: Briefcase,
    shield: Shield,
    award: Award,
    users: Users,
}

const ROUTE_ICONS = {
    receipt: Receipt,
    globe: Globe,
    building2: Building2,
    store: Store,
    copyright: Copyright,
    userCheck: UserCheck,
}

interface FormalizationDetailViewProps {
    route: FormalizationRoute
    onBack: () => void
}

export function FormalizationDetailView({ route, onBack }: FormalizationDetailViewProps) {
    const RouteIcon = ROUTE_ICONS[route.iconType]

    return (
        <div className="min-h-screen bg-[#f5f4f0]">
            <div className="max-w-3xl mx-auto px-4 py-12">
                {/* Back button */}
                <button
                    onClick={onBack}
                    className="flex items-center gap-2 text-sm font-semibold text-gray-500 hover:text-gray-800 transition-colors mb-10 group"
                >
                    <ArrowLeft className="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-0.5" />
                    Volver a la ruta de formalización
                </button>

                {/* Header */}
                <div className="text-center mb-12 animate-slide-up">
                    {/* Icon */}
                    <div className="w-16 h-16 rounded-2xl bg-gold/15 flex items-center justify-center mx-auto mb-6">
                        <RouteIcon className="w-8 h-8 text-gold" />
                    </div>

                    <p className="text-xs font-black tracking-[0.2em] text-gold uppercase mb-2">
                        Guía Detallada de Requisitos
                    </p>
                    <h1 className="text-2xl font-bold text-gray-900 mb-4">{route.fullTitle}</h1>
                    <div className="w-12 h-0.5 bg-gold/40 mx-auto" />
                </div>

                {/* Timeline stages */}
                <div className="relative animate-slide-up stagger-1">
                    {route.stages.map((stage, index) => {
                        const StageIcon = STAGE_ICONS[stage.iconType]
                        const isLast = index === route.stages.length - 1

                        return (
                            <div key={stage.id} className="flex gap-6 mb-0">
                                {/* Left: icon + vertical line */}
                                <div className="flex flex-col items-center flex-shrink-0">
                                    <div className="w-10 h-10 rounded-full border-2 border-gold/40 bg-white flex items-center justify-center z-10 shadow-sm">
                                        <StageIcon className="w-4 h-4 text-gold" />
                                    </div>
                                    {!isLast && (
                                        <div className="w-px flex-1 bg-gold/20 my-1" style={{ minHeight: '2rem' }} />
                                    )}
                                </div>

                                {/* Right: card */}
                                <div className={`flex-1 ${isLast ? 'pb-0' : 'pb-6'}`}>
                                    <p className="text-[10px] font-black tracking-[0.15em] text-gold/70 uppercase mb-1 mt-2">
                                        Etapa {stage.number}
                                    </p>
                                    <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow duration-200">
                                        <h2 className="text-base font-bold text-gold mb-4">{stage.title}</h2>
                                        <ul className="space-y-3">
                                            {stage.items.map((item, i) => (
                                                <li key={i} className="flex gap-3">
                                                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-gold/60 flex-shrink-0" />
                                                    <p className="text-sm text-gray-700 leading-relaxed">
                                                        <span className="font-semibold text-gray-900">{item.title}:</span>{' '}
                                                        {item.detail}
                                                    </p>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </div>

                {/* Footer */}
                <div className="text-center mt-14 pt-8 border-t border-gray-200 animate-slide-up stagger-2">
                    <p className="text-xs text-gray-400">© 2024 GPT Legal - Guía Informativa de Cumplimiento.</p>
                    <p className="text-xs text-gray-400 mt-1">
                        Esta guía es de carácter informativo. Los requisitos pueden variar según las normativas vigentes.
                    </p>
                </div>
            </div>
        </div>
    )
}
