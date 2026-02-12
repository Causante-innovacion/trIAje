import { InternalDecision } from '../../types/adviser.types'
import { Vote } from 'lucide-react'

interface InternalDecisionsChecklistProps {
    decisions: InternalDecision[]
}

export function InternalDecisionsChecklist({ decisions }: InternalDecisionsChecklistProps) {
    return (
        <section className="bg-gold/5 rounded-2xl border-2 border-gold/30 p-6 animate-slide-up">
            <div className="flex items-center gap-3 mb-5">
                <div className="w-8 h-8 rounded-xl bg-gold/10 flex items-center justify-center">
                    <Vote className="w-4 h-4 text-gold" />
                </div>
                <h3 className="text-lg font-bold text-gray-900">Decisiones Internas (Pre-Votacion)</h3>
            </div>

            <div className="space-y-4">
                {decisions.map((decision) => (
                    <div key={decision.id} className="bg-white rounded-xl p-5 border border-gold/20 transition-all duration-200 hover:shadow-sm">
                        <p className="font-bold text-sm text-gray-900 mb-4">{decision.scenario}</p>
                        <div className="space-y-2">
                            {decision.options.map((option) => (
                                <label
                                    key={option.id}
                                    className="flex items-center gap-3 p-3 rounded-xl hover:bg-cream-light cursor-pointer transition-all duration-200 border border-transparent hover:border-gold/20"
                                >
                                    <input
                                        type="radio"
                                        name={decision.id}
                                        value={option.id}
                                        className="w-4 h-4 text-gold focus:ring-gold accent-gold"
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
