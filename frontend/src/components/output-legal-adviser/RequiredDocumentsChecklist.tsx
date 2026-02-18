import { useState } from 'react'
import { RequiredDocument } from '../../types/adviser.types'
import { FileText, Check } from 'lucide-react'
import clsx from 'clsx'

interface RequiredDocumentsChecklistProps {
    documents: RequiredDocument[]
}

export function RequiredDocumentsChecklist({ documents }: RequiredDocumentsChecklistProps) {
    const [checked, setChecked] = useState<Set<string>>(
        () => new Set(documents.filter(d => d.completed).map(d => d.id))
    )

    const toggle = (id: string) => {
        setChecked(prev => {
            const next = new Set(prev)
            if (next.has(id)) next.delete(id)
            else next.add(id)
            return next
        })
    }

    return (
        <section className="bg-green-50 rounded-2xl border-2 border-green-200 p-6 animate-slide-up">
            <div className="flex items-center gap-3 mb-5">
                <div className="w-8 h-8 rounded-xl bg-green-100 flex items-center justify-center">
                    <FileText className="w-4 h-4 text-green-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-900">Requerimientos de Documentos</h3>
            </div>

            <div className="space-y-2.5">
                {documents.map((doc) => {
                    const isChecked = checked.has(doc.id)
                    return (
                        <button
                            key={doc.id}
                            type="button"
                            onClick={() => toggle(doc.id)}
                            className={clsx(
                                'w-full flex items-center gap-3 p-4 rounded-xl border-2 transition-all duration-200 text-left cursor-pointer',
                                isChecked
                                    ? 'bg-green-100/70 border-green-300'
                                    : 'bg-white border-gray-200 hover:border-green-300 hover:bg-green-50/50'
                            )}
                        >
                            <div
                                className={clsx(
                                    'flex-shrink-0 w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all duration-200',
                                    isChecked
                                        ? 'bg-green-500 border-green-500'
                                        : 'bg-white border-gray-300'
                                )}
                            >
                                {isChecked && <Check className="w-3.5 h-3.5 text-white" strokeWidth={3} />}
                            </div>
                            <div className="flex items-center gap-2 flex-1">
                                <FileText className={clsx(
                                    'w-4 h-4 flex-shrink-0',
                                    isChecked ? 'text-green-600' : 'text-gray-400'
                                )} />
                                <span
                                    className={clsx(
                                        'text-sm font-medium',
                                        isChecked ? 'text-green-900 line-through decoration-green-400' : 'text-gray-800'
                                    )}
                                >
                                    {doc.title}
                                </span>
                            </div>
                        </button>
                    )
                })}
            </div>

            <p className="text-xs text-gray-400 mt-4 text-right">
                {checked.size}/{documents.length} completados
            </p>
        </section>
    )
}
