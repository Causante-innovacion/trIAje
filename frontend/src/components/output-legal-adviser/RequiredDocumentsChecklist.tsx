import { RequiredDocument } from '../../types/adviser.types'
import { FileText, CheckCircle2 } from 'lucide-react'
import clsx from 'clsx'

interface RequiredDocumentsChecklistProps {
    documents: RequiredDocument[]
}

export function RequiredDocumentsChecklist({ documents }: RequiredDocumentsChecklistProps) {
    return (
        <section className="bg-green-50 rounded-xl border-2 border-green-300 p-6">
            <div className="flex items-center gap-2 mb-4">
                <FileText className="w-5 h-5 text-green-600" />
                <h3 className="text-xl font-bold text-gray-900">Requerimientos de Documentos</h3>
            </div>

            <div className="space-y-3">
                {documents.map((doc) => (
                    <div
                        key={doc.id}
                        className={clsx(
                            'flex items-center gap-3 p-4 rounded-lg border-2 transition-all',
                            doc.completed
                                ? 'bg-green-100 border-green-400'
                                : 'bg-white border-gray-200 hover:border-green-300'
                        )}
                    >
                        <div
                            className={clsx(
                                'flex-shrink-0 w-6 h-6 rounded border-2 flex items-center justify-center',
                                doc.completed
                                    ? 'bg-green-500 border-green-500'
                                    : 'bg-white border-gray-300'
                            )}
                        >
                            {doc.completed && <CheckCircle2 className="w-4 h-4 text-white" />}
                        </div>
                        <div className="flex items-center gap-2 flex-1">
                            <FileText className="w-4 h-4 text-gray-500" />
                            <span
                                className={clsx(
                                    'text-sm font-medium',
                                    doc.completed ? 'text-green-900' : 'text-gray-900'
                                )}
                            >
                                {doc.title}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    )
}
