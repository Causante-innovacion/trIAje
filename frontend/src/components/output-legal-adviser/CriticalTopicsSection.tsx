import { CriticalTopic } from '../../types/adviser.types'
import { AlertCircle } from 'lucide-react'

interface CriticalTopicsSectionProps {
    topics: CriticalTopic[]
    fundingRange: { min: string; max: string; description: string }
}

export function CriticalTopicsSection({ topics, fundingRange }: CriticalTopicsSectionProps) {
    return (
        <section>
            <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <h3 className="text-xl font-bold text-gray-900">Tópicos Críticos (Alta Prioridad)</h3>
            </div>

            {/* Funding Critical Card */}
            <div className="bg-orange-50 rounded-xl border-2 border-orange-300 p-6 mb-4">
                <p className="text-xs text-orange-700 font-semibold mb-2">FINANCIAMIENTO CRÍTICO</p>
                <p className="text-3xl font-bold text-orange-900 mb-2">
                    {fundingRange.min} - {fundingRange.max}
                </p>
                <p className="text-sm text-gray-700">{fundingRange.description}</p>
                <div className="flex gap-2 mt-4">
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded">
                        USD Internacional
                    </span>
                    <span className="px-3 py-1 bg-purple-100 text-purple-800 text-xs font-bold rounded">
                        Grants & VC
                    </span>
                </div>
            </div>

            {/* Critical Topics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {topics.map((topic) => (
                    <div
                        key={topic.id}
                        className="bg-white rounded-xl border-2 border-red-300 p-6 hover:shadow-lg transition-shadow"
                    >
                        <div className="flex items-start justify-between mb-3">
                            <h4 className="font-bold text-gray-900">{topic.title}</h4>
                            <span className="px-3 py-1 bg-red-100 text-red-800 text-xs font-bold rounded-full">
                                {topic.priority}
                            </span>
                        </div>
                        <p className="text-sm text-gray-700 mb-4">{topic.description}</p>
                        {topic.actionLink && (
                            <a
                                href={topic.actionLink}
                                className="text-sm text-yellow-600 font-semibold hover:text-yellow-700 flex items-center gap-1"
                            >
                                {topic.actionLabel} →
                            </a>
                        )}
                    </div>
                ))}
            </div>
        </section>
    )
}
