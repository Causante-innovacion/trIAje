import { LawyerQuestion } from '../../types/adviser.types'
import { MessageSquare } from 'lucide-react'

interface LawyerQuestionsSectionProps {
    questions: LawyerQuestion[]
}

export function LawyerQuestionsSection({ questions }: LawyerQuestionsSectionProps) {
    if (questions.length === 0) {
        return null
    }

    return (
        <section className="bg-blue-50 rounded-xl border-2 border-blue-300 p-6">
            <div className="flex items-center gap-2 mb-4">
                <MessageSquare className="w-5 h-5 text-blue-600" />
                <h3 className="text-xl font-bold text-gray-900">Guía de Preguntas para el Abogado</h3>
            </div>
            <p className="text-sm text-gray-600 mb-6">
                Preguntas clave para maximizar el tiempo de consulta
            </p>

            <div className="space-y-4">
                {questions.map((q) => (
                    <div
                        key={q.id}
                        className="bg-white rounded-lg p-4 border border-blue-200 hover:border-blue-400 transition-colors"
                    >
                        <div className="flex gap-3">
                            <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-bold">
                                {String(q.number).padStart(2, '0')}
                            </span>
                            <p className="text-sm text-gray-900 font-medium pt-1">{q.question}</p>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    )
}
