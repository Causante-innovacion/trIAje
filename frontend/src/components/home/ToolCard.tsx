import { BarChart3, ListChecks, Users } from 'lucide-react'
import { ToolType } from '../../types/chat'

interface ToolCardProps {
  id: ToolType
  name: string
  description: string
  icon: string
  onClick: (id: ToolType) => void
}

const iconMap = {
  chart: BarChart3,
  checklist: ListChecks,
  users: Users,
}

export function ToolCard({ id, name, description, icon, onClick }: ToolCardProps) {
  const IconComponent = iconMap[icon as keyof typeof iconMap] || BarChart3

  return (
    <button
      onClick={() => onClick(id)}
      className="tool-card flex flex-col items-center text-center p-8 min-w-[280px] flex-1"
    >
      <div className="icon-container mb-4">
        <IconComponent className="w-6 h-6 text-gold" />
      </div>
      <h3 className="font-semibold text-gray-900 text-lg mb-2">{name}</h3>
      <p className="text-sm text-gray-500 leading-relaxed">{description}</p>
    </button>
  )
}
