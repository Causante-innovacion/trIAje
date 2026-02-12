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
        <section className="bg-blue-50 rounded-2xl border-2 border-blue-200 p-8 animate-slide-up">
            <div className="flex items-center gap-3 mb-2">
                <div className="w-8 h-8 rounded-xl bg-blue-100 flex items-center justify-center">
                    <MessageSquare className="w-4 h-4 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">Guia de Preguntas para el Abogado</h3>
            </div>
            <p className="text-sm text-gray-500 mb-6 ml-11">
                Preguntas clave para maximizar el tiempo de consulta
            </p>

            <div className="space-y-3">
                {questions.map((q) => (
                    <div
                        key={q.id}
                        className="bg-white rounded-xl p-5 border border-blue-100 transition-all duration-200 hover:border-blue-300 hover:shadow-sm"
                    >
                        <div className="flex gap-4">
                            <span className="flex-shrink-0 w-9 h-9 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                {String(q.number).padStart(2, '0')}
                            </span>
                            <p className="text-sm text-gray-800 font-medium pt-1.5 leading-relaxed">{q.question}</p>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    )
}
