import { ArrowRight, FileText } from 'lucide-react'

interface Organization {
  id: string
  name: string
}

interface OrganizationsDetectedProps {
  organizations: Organization[]
  questionsPerOrg: number
  timePerOrg: string
  totalTime: string
  onStartForms: () => void
}

export function OrganizationsDetected({
  organizations,
  questionsPerOrg,
  timePerOrg,
  totalTime,
  onStartForms,
}: OrganizationsDetectedProps) {
  return (
    <div className="space-y-4">
      <div className="chat-bubble">
        <p className="mb-3">
          Perfecto. Ya tengo la información del proyecto. He detectado{' '}
          <strong className="text-gray-900">{organizations.length} organizaciones</strong> involucradas:
        </p>

        <div className="flex flex-wrap gap-2 mb-4">
          {organizations.map((org) => (
            <span
              key={org.id}
              className="px-3 py-1.5 bg-teal-50 text-teal-700 text-sm font-medium rounded-full border border-teal-200"
            >
              {org.name}
            </span>
          ))}
        </div>
      </div>

      <div className="chat-bubble">
        <p>
          Para evaluar viabilidad legal, necesito conocer el estado legal de cada una
          (personería, RUC, fondos, etc).
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-card p-5">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-cream rounded-xl flex items-center justify-center">
            <FileText className="w-5 h-5 text-gold" />
          </div>
          <div>
            <h4 className="font-bold text-gray-900">Ficha Legal Mínima</h4>
            <p className="text-xs text-gray-500">
              {questionsPerOrg} preguntas por organización · {timePerOrg} c/u
            </p>
          </div>
        </div>

        <div className="mb-4">
          <span className="inline-block px-3 py-1 bg-gold/10 text-gold text-xs font-bold rounded-full">
            TOTAL: ~{totalTime}
          </span>
        </div>

        <button
          onClick={onStartForms}
          className="w-full btn-primary flex items-center justify-center gap-2"
        >
          <ArrowRight className="w-4 h-4" />
          Completar Fichas Legales Mínimas
        </button>
      </div>
    </div>
  )
}
