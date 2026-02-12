import { CriticalTopic } from '../../types/adviser.types'
import { AlertCircle } from 'lucide-react'

interface CriticalTopicsSectionProps {
    topics: CriticalTopic[]
    fundingRange: { min: string; max: string; description: string }
}

export function CriticalTopicsSection({ topics, fundingRange }: CriticalTopicsSectionProps) {
    return (
        <section className="animate-slide-up">
            <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-xl bg-red-100 flex items-center justify-center">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">Topicos Criticos (Alta Prioridad)</h3>
            </div>

            {/* Funding Critical Card */}
            <div className="bg-orange-50 rounded-2xl border-2 border-orange-300 p-8 mb-6 transition-all duration-300 hover:shadow-card-hover">
                <p className="text-xs font-bold text-orange-600 uppercase tracking-wide mb-2">Financiamiento Critico</p>
                <p className="text-3xl font-bold text-orange-900 mb-3">
                    {fundingRange.min} - {fundingRange.max}
                </p>
                <p className="text-sm text-gray-700 leading-relaxed">{fundingRange.description}</p>
                <div className="flex gap-2 mt-5">
                    <span className="badge-info">USD Internacional</span>
                    <span className="badge bg-purple-100 text-purple-700">Grants & VC</span>
                </div>
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
