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
    <section className="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="px-6 pt-6 pb-2">
        <div className="flex items-center gap-4 mb-2">
          <div className="w-10 h-10 rounded-xl bg-causante-crema/10 flex items-center justify-center flex-shrink-0">
            <Icon className="w-5 h-5 text-causante-ocre" />
          </div>
          <div>
            <h2 className="font-heading text-lg md:text-xl font-bold text-gray-900">{title}</h2>
            {subtitle && <p className="text-[11px] text-gray-400 mt-0.5">{subtitle}</p>}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-6 pb-6">
        {children}
      </div>
    </section>
  )
}
