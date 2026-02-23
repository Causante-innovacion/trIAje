import { useState, useEffect } from 'react'
import { Check, Pencil } from 'lucide-react'

export interface ProjectInfo {
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
}

interface ProjectInfoCardProps {
  data: ProjectInfo
  onConfirm?: () => void
  onEdit?: () => void
}

export function ProjectInfoCard({ data, onConfirm, onEdit, isEditing, onSave, onCancel }: ProjectInfoCardProps & { isEditing?: boolean, onSave?: (data: ProjectInfo) => void, onCancel?: () => void }) {
  const [formData, setFormData] = useState<ProjectInfo>(data)

  // Reset form data when data prop changes or when entering edit mode
  useEffect(() => {
    setFormData(data)
  }, [data, isEditing])

  const handleChange = (field: keyof ProjectInfo, value: any) => {
    setFormData((prev: ProjectInfo) => ({ ...prev, [field]: value }))
  }

  const handleFinancingChange = (type: 'seed' | 'scaling', field: 'amount' | 'source', value: string) => {
    setFormData((prev: ProjectInfo) => ({
      ...prev,
      financing: {
        ...prev.financing,
        [type]: {
          ...prev.financing[type],
          [field]: value
        }
      }
    }))
  }

  const handleTeamChange = (type: 'permanent' | 'external', value: string) => {
    const numValue = parseInt(value) || 0
    setFormData((prev: ProjectInfo) => ({
      ...prev,
      team: {
        ...prev.team,
        [type]: numValue
      }
    }))
  }

  const handleSave = () => {
    onSave?.(formData)
  }

  if (isEditing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-yellow-600">
          <Pencil className="w-5 h-5" />
          <span className="font-medium">Editando información del proyecto:</span>
        </div>

        <div className="bg-white rounded-2xl border border-yellow-200 shadow-card overflow-hidden">
          <div className="p-4 border-b border-yellow-100 flex items-center gap-2 bg-yellow-50/50">
            <div className="w-6 h-6 bg-yellow-100 rounded flex items-center justify-center">
              <Pencil className="w-4 h-4 text-yellow-600" />
            </div>
            <span className="font-bold text-sm uppercase tracking-wide text-yellow-800">
              Edición de Información
            </span>
          </div>

          <div className="p-5 space-y-5">
            {/* Project name and organization */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-bold text-gold uppercase tracking-wide mb-1">Proyecto</label>
                <input
                  type="text"
                  value={formData.projectName}
                  onChange={(e) => handleChange('projectName', e.target.value)}
                  className="w-full text-sm border-gray-300 rounded-md shadow-sm focus:border-gold focus:ring focus:ring-gold/50"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gold uppercase tracking-wide mb-1">Organización Líder</label>
                <input
                  type="text"
                  value={formData.organization}
                  onChange={(e) => handleChange('organization', e.target.value)}
                  className="w-full text-sm border-gray-300 rounded-md shadow-sm focus:border-gold focus:ring focus:ring-gold/50"
                />
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-bold text-gold uppercase tracking-wide mb-1">Descripción Breve</label>
              <textarea
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
                className="w-full text-sm border-gray-300 rounded-md shadow-sm focus:border-gold focus:ring focus:ring-gold/50"
              />
            </div>

            {/* Financing and Team */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-xs font-bold text-gold uppercase tracking-wide mb-3">Financiamiento Proyectado</p>
                <div className="space-y-2">
                  <div className="py-2 border-b border-gray-100 space-y-2">
                    <span className="text-xs text-gray-500 block">Capital Semilla</span>
                    <input
                      placeholder="Monto"
                      value={formData.financing.seed.amount}
                      onChange={(e) => handleFinancingChange('seed', 'amount', e.target.value)}
                      className="w-full text-sm border-gray-300 rounded-md shadow-sm mb-1"
                    />
                    <input
                      placeholder="Fuente"
                      value={formData.financing.seed.source}
                      onChange={(e) => handleFinancingChange('seed', 'source', e.target.value)}
                      className="w-full text-sm border-gray-300 rounded-md shadow-sm"
                    />
                  </div>
                  <div className="py-2 space-y-2">
                    <span className="text-xs text-gray-500 block">Escalamiento</span>
                    <input
                      placeholder="Monto"
                      value={formData.financing.scaling.amount}
                      onChange={(e) => handleFinancingChange('scaling', 'amount', e.target.value)}
                      className="w-full text-sm border-gray-300 rounded-md shadow-sm mb-1"
                    />
                    <input
                      placeholder="Fuente"
                      value={formData.financing.scaling.source}
                      onChange={(e) => handleFinancingChange('scaling', 'source', e.target.value)}
                      className="w-full text-sm border-gray-300 rounded-md shadow-sm"
                    />
                  </div>
                </div>
              </div>
              <div>
                <p className="text-xs font-bold text-gold uppercase tracking-wide mb-3">Equipo Operativo</p>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Miembros permanentes</label>
                    <input
                      type="number"
                      value={formData.team.permanent}
                      onChange={(e) => handleTeamChange('permanent', e.target.value)}
                      className="w-full text-sm border-gray-300 rounded-md shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Consultores externos</label>
                    <input
                      type="number"
                      value={formData.team.external}
                      onChange={(e) => handleTeamChange('external', e.target.value)}
                      className="w-full text-sm border-gray-300 rounded-md shadow-sm"
                    />
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium text-white bg-gold rounded-lg hover:bg-yellow-600"
          >
            Guardar cambios
          </button>
        </div>
      </div>
    )
  }

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
              <div className="space-y-3">
                <div className="py-2 border-b border-gray-100">
                  <span className="text-xs text-gray-500 block mb-1">Capital Semilla</span>
                  <span className="text-sm font-semibold text-gray-900">{data.financing.seed.amount}</span>
                  <span className="text-xs text-gray-400 ml-1">({data.financing.seed.source})</span>
                </div>
                <div className="py-2">
                  <span className="text-xs text-gray-500 block mb-1">Escalamiento</span>
                  <span className="text-sm font-semibold text-gray-900">{data.financing.scaling.amount}</span>
                  <span className="text-xs text-gray-400 ml-1">({data.financing.scaling.source})</span>
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
