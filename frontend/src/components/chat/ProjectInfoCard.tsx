import { Check, Pencil } from 'lucide-react'

interface ProjectInfo {
  projectName: string
  organization: string
  description: string
  financing: {
    seed: { amount: string; source: string }
    scaling: { amount: string; source: string }
  }
  team: {
    permanent: number
    external: number
  }
  interventionTypes: string[]
}

interface ProjectInfoCardProps {
  data: ProjectInfo
  onConfirm?: () => void
  onEdit?: () => void
}

export function ProjectInfoCard({ data, onConfirm, onEdit }: ProjectInfoCardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-green-600">
        <Check className="w-5 h-5" />
        <span className="font-medium">Documento procesado correctamente. He extraído la siguiente información:</span>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-card overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center gap-2">
          <div className="w-6 h-6 bg-cream rounded flex items-center justify-center">
            <svg className="w-4 h-4 text-gold" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-bold text-sm uppercase tracking-wide text-gray-600">
            Información del Proyecto
          </span>
        </div>

        <div className="p-5 space-y-5">
          {/* Project name and organization */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs font-bold text-gold uppercase tracking-wide mb-1">Proyecto</p>
              <p className="font-semibold text-gray-900">{data.projectName}</p>
            </div>
            <div>
              <p className="text-xs font-bold text-gold uppercase tracking-wide mb-1">Organización Líder</p>
              <p className="font-semibold text-gray-900">{data.organization}</p>
            </div>
          </div>

          {/* Description */}
          <div>
            <p className="text-xs font-bold text-gold uppercase tracking-wide mb-1">Descripción Breve</p>
            <p className="text-sm text-gray-600 leading-relaxed">{data.description}</p>
          </div>

          {/* Financing and Team */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs font-bold text-gold uppercase tracking-wide mb-3">Financiamiento Proyectado</p>
              <div className="space-y-2">
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-xs text-gray-500">Capital Semilla</span>
                  <span className="text-sm font-semibold">{data.financing.seed.amount} ({data.financing.seed.source})</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-xs text-gray-500">Escalamiento</span>
                  <span className="text-sm font-semibold">{data.financing.scaling.amount} ({data.financing.scaling.source})</span>
                </div>
              </div>
            </div>
            <div>
              <p className="text-xs font-bold text-gold uppercase tracking-wide mb-3">Equipo Operativo</p>
              <ul className="space-y-2">
                <li className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 bg-gold rounded-full" />
                  {data.team.permanent} Miembros permanentes
                </li>
                <li className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 bg-gold rounded-full" />
                  {data.team.external} Consultores externos (campaña)
                </li>
              </ul>
            </div>
          </div>

          {/* Intervention types */}
          <div>
            <p className="text-xs font-bold text-gold uppercase tracking-wide mb-2">Tipo de Intervención</p>
            <div className="flex flex-wrap gap-2">
              {data.interventionTypes.map((type, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full"
                >
                  {type}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation question */}
      <p className="font-medium text-gray-900">¿Esta información es correcta?</p>

      <div className="flex gap-3">
        <button
          onClick={onConfirm}
          className="btn-option-yes"
        >
          <Check className="w-4 h-4" />
          Sí, es correcta
        </button>
        <button
          onClick={onEdit}
          className="btn-option-no"
        >
          <Pencil className="w-4 h-4" />
          Necesito corregir algo
        </button>
      </div>
    </div>
  )
}
