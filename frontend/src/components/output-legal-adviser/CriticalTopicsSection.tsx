import { CriticalTopic } from '../../types/adviser.types'
import { AlertCircle } from 'lucide-react'

const INCOME_SOURCE_STYLES: Record<string, string> = {
    'Donaciones': 'bg-blue-100 text-blue-700',
    'Venta de servicios o productos': 'bg-green-100 text-green-700',
    'Fondos públicos': 'bg-indigo-100 text-indigo-700',
    'Fondos privados': 'bg-purple-100 text-purple-700',
    'Cooperación internacional': 'bg-cyan-100 text-cyan-700',
    'Aún no recibe ingresos': 'bg-gray-100 text-gray-600',
}

interface CriticalTopicsSectionProps {
    topics: CriticalTopic[]
    fundingRange: { min: string; max: string; description: string }
    incomeSources?: string[]
}

export function CriticalTopicsSection({ topics, fundingRange, incomeSources }: CriticalTopicsSectionProps) {
    return (
        <section className="animate-slide-up">
            <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-xl bg-red-100 flex items-center justify-center">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">Tópicos Críticos (Alta Prioridad)</h3>
            </div>

            {/* Funding Critical Card */}
            <div className="bg-orange-50 rounded-2xl border-2 border-orange-300 p-8 mb-6 transition-all duration-300 hover:shadow-card-hover">
                <p className="text-xs font-bold text-orange-600 uppercase tracking-wide mb-2">Financiamiento Crítico</p>
                <p className="text-3xl font-bold text-orange-900 mb-3">
                    {fundingRange.min} - {fundingRange.max}
                </p>
                <p className="text-sm text-gray-700 leading-relaxed">{fundingRange.description}</p>
                {incomeSources && incomeSources.length > 0 && (
                    <div className="flex gap-2 mt-5 flex-wrap">
                        {incomeSources.map(source => (
                            <span
                                key={source}
                                className={`px-2.5 py-1 rounded-full text-xs font-semibold ${INCOME_SOURCE_STYLES[source] ?? 'bg-gray-100 text-gray-600'}`}
                            >
                                {source}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            {/* Critical Topics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {topics.map((topic) => (
                    <div
                        key={topic.id}
                        className="bg-white rounded-2xl border-2 border-red-200 p-6 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-card-hover hover:border-red-300"
                    >
                        <div className="flex items-start justify-between mb-3">
                            <h4 className="font-bold text-gray-900">{topic.title}</h4>
                            <span className="badge-critical">{topic.priority}</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-4 leading-relaxed">{topic.description}</p>
                        {topic.actionLink && (
                            <a
                                href={topic.actionLink}
                                className="text-sm text-gold font-semibold hover:text-gold-dark flex items-center gap-1 transition-colors"
                            >
                                {topic.actionLabel}
                                <span className="transition-transform group-hover:translate-x-1">→</span>
                            </a>
                        )}
                    </div>
                ))}
            </div>
        </section>
    )
}
