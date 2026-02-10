import { Alternative } from '../../types/evaluation.types'

interface AlternativesSectionProps {
    alternatives: Alternative[]
}

export function AlternativesSection({ alternatives }: AlternativesSectionProps) {
    if (alternatives.length === 0) return null

    return (
        <div>
            <h3 className="font-bold text-gray-900 mb-4">Alternativas</h3>
            <div className="space-y-4">
                {alternatives.map((alternative, index) => (
                    <div key={index} className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                        <h4 className="font-bold text-gray-900 mb-2">{alternative.title}</h4>
                        <p className="text-sm text-gray-700">{alternative.description}</p>
                    </div>
                ))}
            </div>
        </div>
    )
}
