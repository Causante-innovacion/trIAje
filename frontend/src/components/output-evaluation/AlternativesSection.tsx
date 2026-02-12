import { Lightbulb } from 'lucide-react'
import { Alternative } from '../../types/evaluation.types'

interface AlternativesSectionProps {
    alternatives: Alternative[]
}

export function AlternativesSection({ alternatives }: AlternativesSectionProps) {
    if (alternatives.length === 0) return null

    return (
        <div className="animate-fade-in">
            <h3 className="font-bold text-xl text-gray-900 mb-4">Alternativas</h3>
            <div className="space-y-4">
                {alternatives.map((alternative, index) => (
                    <div
                        key={index}
                        className="bg-white rounded-2xl p-6 border border-gray-200 shadow-card transition-all duration-300 hover:-translate-y-0.5 hover:shadow-card-hover"
                    >
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-xl bg-cream flex items-center justify-center flex-shrink-0">
                                <Lightbulb className="w-5 h-5 text-gold" />
                            </div>
                            <div>
                                <h4 className="font-bold text-gray-900 mb-2">{alternative.title}</h4>
                                <p className="text-sm text-gray-600 leading-relaxed">{alternative.description}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
