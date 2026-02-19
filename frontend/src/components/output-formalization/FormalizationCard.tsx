import {
    Receipt,
    Globe,
    Building2,
    Store,
    Copyright,
    UserCheck,
    ArrowRight,
} from 'lucide-react'
import { FormalizationRoute } from './mockFormalizationData'

const ROUTE_ICONS = {
    receipt: Receipt,
    globe: Globe,
    building2: Building2,
    store: Store,
    copyright: Copyright,
    userCheck: UserCheck,
}

interface FormalizationCardProps {
    route: FormalizationRoute
    onViewDetail: (id: string) => void
}

export function FormalizationCard({ route, onViewDetail }: FormalizationCardProps) {
    const Icon = ROUTE_ICONS[route.iconType]

    return (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 flex flex-col gap-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-card-hover hover:border-gold/30 relative overflow-hidden">
            {/* Faded background number */}
            <span
                className="absolute top-3 left-5 text-7xl font-black text-gray-100 select-none leading-none pointer-events-none"
                aria-hidden="true"
            >
                {route.number}
            </span>

            {/* Icon badge top right */}
            <div className="self-end z-10">
                <div className="w-10 h-10 rounded-xl bg-gold/10 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-gold" />
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 z-10 mt-6">
                <h3 className="text-base font-bold text-gray-900 mb-2 leading-tight">{route.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{route.description}</p>
            </div>

            {/* CTA */}
            <button
                onClick={() => onViewDetail(route.id)}
                className="flex items-center gap-1.5 text-sm font-semibold text-gold hover:text-gold-dark transition-colors self-start group"
            >
                Ver guía detallada
                <ArrowRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-0.5" />
            </button>
        </div>
    )
}
