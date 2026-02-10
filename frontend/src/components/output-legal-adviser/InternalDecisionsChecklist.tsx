import { InternalDecision } from '../../types/adviser.types'
import { Vote } from 'lucide-react'

interface InternalDecisionsChecklistProps {
    decisions: InternalDecision[]
}

export function InternalDecisionsChecklist({ decisions }: InternalDecisionsChecklistProps) {
    return (
        <section className="bg-yellow-50 rounded-xl border-2 border-yellow-300 p-6">
            <div className="flex items-center gap-2 mb-4">
                <Vote className="w-5 h-5 text-yellow-600" />
                <h3 className="text-xl font-bold text-gray-900">Decisiones Internas (Pre-Votación)</h3>
            </div>

            <div className="space-y-6">
                {decisions.map((decision) => (
                    <div key={decision.id} className="bg-white rounded-lg p-5 border border-yellow-200">
                        <p className="font-bold text-sm text-gray-900 mb-3">{decision.scenario}</p>
                        <div className="space-y-2">
                            {decision.options.map((option) => (
                                <label
                                    key={option.id}
                                    className="flex items-center gap-3 p-3 rounded-lg hover:bg-yellow-50 cursor-pointer transition-colors"
                                >
                                    <input
                                        type="radio"
                                        name={decision.id}
                                        value={option.id}
                                        className="w-4 h-4 text-yellow-500 focus:ring-yellow-400"
                                    />
                                    <span className="text-sm text-gray-700">{option.label}</span>
                                </label>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </section>
    )
}
