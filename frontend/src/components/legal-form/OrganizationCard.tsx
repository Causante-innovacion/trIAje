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
        'flex items-center gap-3 p-3.5 rounded-[1.25rem] border-2 transition-all duration-300 text-left w-full h-[82px]',
        isSelected
          ? 'border-causante-ocre bg-causante-crema/20 ring-4 ring-causante-ocre/5'
          : 'border-gray-50 bg-white hover:border-gray-200'
      )}
    >
      <div
        className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: organization.color + '10', color: organization.color }}
      >
        <Icon className="w-4.5 h-4.5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className={clsx(
          'font-heading font-bold text-[13px] leading-tight break-words',
          isSelected ? 'text-gray-900' : 'text-gray-700'
        )}>
          {organization.name}
        </p>
        <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wider mt-0.5 line-clamp-2 overflow-hidden leading-tight">
          {organization.role}
        </p>
      </div>
      <div className="text-right flex-shrink-0 pl-1">
        <div className={clsx(
          'px-2 py-1 rounded-lg text-[11px] font-black tracking-tight',
          organization.progress === 100
            ? 'bg-causante-ocre text-white'
            : 'bg-gray-50 text-gray-400 border border-gray-100'
        )}>
          {organization.progress}%
        </div>
      </div>
    </button>
  )
}
