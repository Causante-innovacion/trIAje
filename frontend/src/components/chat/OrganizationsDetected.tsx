import { ArrowRight, FileText, CheckCircle2, ExternalLink } from 'lucide-react'

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
  allOrgsCompleted?: boolean
  hasEvaluation?: boolean
  onViewEvaluation?: () => void
}

export function OrganizationsDetected({
  organizations,
  questionsPerOrg,
  timePerOrg,
  totalTime,
  onStartForms,
  allOrgsCompleted = false,
  hasEvaluation = false,
  onViewEvaluation,
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

      {allOrgsCompleted && hasEvaluation ? (
        /* ── Diagnóstico ya generado ── */
        <div className="bg-green-50 rounded-2xl border border-green-200 p-5">
          <div className="flex items-center gap-3 mb-3">
            <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0" />
            <div>
              <p className="font-bold text-green-900 text-sm">Fichas completadas • Diagnóstico generado</p>
              <p className="text-xs text-green-700">Todas las organizaciones han sido evaluadas.</p>
            </div>
          </div>
          <button
            onClick={onViewEvaluation}
            className="w-full flex items-center justify-center gap-2 bg-green-700 hover:bg-green-800 text-white text-sm font-bold py-3 px-4 rounded-xl transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            Ver diagnóstico legal
          </button>
          <button
            onClick={onStartForms}
            className="w-full mt-2 text-xs text-green-700 hover:text-green-900 underline underline-offset-2 transition-colors"
          >
            Editar fichas y regenerar
          </button>
        </div>
      ) : allOrgsCompleted ? (
        /* ── Fichas completas, sin diagnóstico aún ── */
        <div className="bg-amber-50 rounded-2xl border border-amber-200 p-5">
          <div className="flex items-center gap-3 mb-3">
            <CheckCircle2 className="w-6 h-6 text-amber-600 flex-shrink-0" />
            <div>
              <p className="font-bold text-amber-900 text-sm">Fichas completadas</p>
              <p className="text-xs text-amber-700">Genera el diagnóstico desde la ficha legal.</p>
            </div>
          </div>
          <button
            onClick={onStartForms}
            className="w-full flex items-center justify-center gap-2 bg-causante-ocre hover:opacity-90 text-white text-sm font-bold py-3 px-4 rounded-xl transition-colors"
          >
            <ArrowRight className="w-4 h-4" />
            Ir a Fichas Legales
          </button>
        </div>
      ) : (
        /* ── Estado inicial: completar fichas ── */
        <>
          <div className="chat-bubble">
            <p>
              Para evaluar viabilidad legal, necesito conocer el estado legal de cada una
              (peronía, RUC, fondos, etc).
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
        </>
      )}
    </div>
  )
}
