import { LucideIcon } from 'lucide-react'
import clsx from 'clsx'

interface Organization {
  id: string
  name: string
  role: string
  progress: number
  color: string
  icon: LucideIcon
}

interface OrganizationCardProps {
  organization: Organization
  isSelected: boolean
  onClick: () => void
}

export function OrganizationCard({ organization, isSelected, onClick }: OrganizationCardProps) {
  const { name, role, progress, color, icon: Icon } = organization

  return (
    <button
      onClick={onClick}
      className={clsx(
        'text-left bg-white p-4 rounded-xl border-2 shadow-sm transition-all hover:shadow-md',
        !isSelected && 'border-gray-100 hover:border-gray-300'
      )}
      style={isSelected ? {
        borderColor: color,
        boxShadow: `0 0 0 4px ${color}1A`
      } : undefined}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className="p-2 rounded-lg"
            style={{ backgroundColor: `${color}1A`, color: color }}
          >
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-sm">{name}</h3>
            <p className="text-[10px] text-gray-400 uppercase font-bold tracking-wider">{role}</p>
          </div>
        </div>
      </div>

      <div className="space-y-1">
        <div className="flex justify-between text-[10px] font-bold text-gray-400 uppercase">
          <span>Progreso</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-100 h-1 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all"
            style={{ width: `${progress}%`, backgroundColor: color }}
          />
        </div>
      </div>
    </button>
  )
}
