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
        'flex items-center gap-4 p-4 rounded-[1.5rem] border-2 transition-all duration-300 text-left w-full shadow-sm',
        isSelected
          ? 'border-causante-ocre bg-causante-crema/20 ring-4 ring-causante-ocre/5'
          : 'border-gray-50 bg-white hover:border-gray-200'
      )}
    >
      <div
        className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: organization.color + '10', color: organization.color }}
      >
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex-1 min-w-0 py-1">
        <p className={clsx(
          'font-heading font-bold text-sm leading-tight break-words',
          isSelected ? 'text-gray-900' : 'text-gray-700'
        )}>
          {organization.name}
        </p>
        <p className="text-[11px] text-gray-400 font-medium uppercase tracking-wider mt-1 break-words">
          {organization.role}
        </p>
      </div>
      <div className="text-right flex-shrink-0 pl-2">
        <span className={clsx(
          'text-lg font-black',
          organization.progress === 100 ? 'text-causante-ocre' : 'text-gray-200'
        )}>
          {organization.progress}%
        </span>
      </div>
    </button>
  )
}
