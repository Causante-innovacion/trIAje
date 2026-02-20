import { LucideIcon } from 'lucide-react'

interface FormBlockProps {
  title: string
  subtitle?: string
  icon: LucideIcon
  children: React.ReactNode
}

/**
 * FormBlock — clean card wrapper for each step of the wizard.
 * Causante Design: white bg, rounded-3xl, solid border, generous whitespace.
 */
export function FormBlock({ title, subtitle, icon: Icon, children }: FormBlockProps) {
  return (
    <section className="bg-white rounded-3xl border border-gray-100 overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="px-8 pt-8 pb-4">
        <div className="flex items-center gap-4 mb-2">
          <div className="w-12 h-12 rounded-2xl bg-cream flex items-center justify-center flex-shrink-0">
            <Icon className="w-6 h-6 text-causante-ocre" />
          </div>
          <div>
            <h2 className="font-heading text-xl md:text-2xl font-bold text-gray-900">{title}</h2>
            {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-8 pb-8">
        {children}
      </div>
    </section>
  )
}
