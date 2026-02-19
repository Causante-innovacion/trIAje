import { LucideIcon } from 'lucide-react'
import clsx from 'clsx'

interface FormBlockProps {
  title: string
  icon: LucideIcon
  iconColor: string
  completed: number
  total: number
  children: React.ReactNode
  width?: string
  height?: string
}

const iconColorStyles: Record<string, string> = {
  blue: 'bg-blue-100 text-blue-600',
  purple: 'bg-purple-100 text-purple-600',
  green: 'bg-green-100 text-green-600',
  orange: 'bg-orange-100 text-orange-600',
  teal: 'bg-teal-100 text-teal-600',
  indigo: 'bg-indigo-100 text-indigo-600',
  pink: 'bg-pink-100 text-pink-600',
}

const progressColorStyles: Record<string, string> = {
  blue: 'text-blue-600 bg-blue-50',
  purple: 'text-purple-600 bg-purple-50',
  green: 'text-green-600 bg-green-50',
  orange: 'text-orange-600 bg-orange-50',
  teal: 'text-teal-600 bg-teal-50',
  indigo: 'text-indigo-600 bg-indigo-50',
  pink: 'text-pink-600 bg-pink-50',
}

export function FormBlock({
  title,
  icon: Icon,
  iconColor,
  completed,
  total,
  children,
  width,
  height,
}: FormBlockProps) {
  const progressText = `${completed} / ${total}`

  return (
    <section
      className="bg-white border border-gray-100 rounded-2xl shadow-sm"
      style={{ width, height }}
    >
      {/* Header */}
      <div className="p-5 border-b border-gray-50 flex justify-between items-center bg-gray-50/30 rounded-t-2xl">
        <div className="flex items-center gap-3">
          <div className={clsx('p-2 rounded-lg', iconColorStyles[iconColor])}>
            <Icon className="w-5 h-5" />
          </div>
          <h3 className="font-heading font-semibold text-sm">{title}</h3>
        </div>
        <span
          className={clsx(
            'text-[10px] font-bold px-2 py-1 rounded',
            completed > 0 ? progressColorStyles[iconColor] : 'text-gray-400 bg-gray-100'
          )}
        >
          {progressText}
        </span>
      </div>

      {/* Content */}
      <div className="p-6">
        {children}
      </div>
    </section>
  )
}
