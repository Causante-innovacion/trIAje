import { Building2, LucideIcon } from 'lucide-react'
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
  const Icon = organization.icon || Building2

  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        'flex items-center gap-4 p-4 rounded-2xl border-2 transition-all duration-200 text-left w-full',
        isSelected
          ? 'border-causante-ocre bg-gold-50'
          : 'border-gray-100 bg-white hover:border-gray-300'
      )}
    >
      <div
        className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: organization.color + '15', color: organization.color }}
      >
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className={clsx(
          'font-heading font-semibold text-sm truncate',
          isSelected ? 'text-gray-900' : 'text-gray-700'
        )}>{organization.name}</p>
        <p className="text-xs text-gray-400 truncate">{organization.role}</p>
      </div>
      <div className="text-right flex-shrink-0">
        <span className={clsx(
          'text-lg font-bold',
          organization.progress === 100 ? 'text-causante-ocre' : 'text-gray-300'
        )}>
          {organization.progress}%
        </span>
      </div>
    </button>
  )
}
