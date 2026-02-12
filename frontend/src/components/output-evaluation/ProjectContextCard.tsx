import { AlertTriangle, Archive, Users, Banknote, Lightbulb, Target } from 'lucide-react'
import { ProjectContextItem } from '../../types/evaluation.types'

interface ProjectContextCardProps {
    items: ProjectContextItem[]
}

const iconMap: Record<string, any> = {
    'alert': AlertTriangle,
    'archive': Archive,
    'users': Users,
    'banknote': Banknote,
    'lightbulb': Lightbulb,
    'target': Target,
}

export function ProjectContextCard({ items }: ProjectContextCardProps) {
    return (
        <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-card animate-fade-in">
            <h3 className="font-bold text-xl text-gray-900 mb-6">Contexto del Proyecto</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {items.map((item, index) => {
                    const Icon = iconMap[item.icon] || Target
                    return (
                        <div
                            key={index}
                            className="flex items-start gap-3 p-4 rounded-xl bg-gray-50 border border-gray-100 transition-all duration-200 hover:bg-cream-light hover:border-gold/20"
                        >
                            <div className="w-10 h-10 rounded-xl bg-gold/10 flex items-center justify-center flex-shrink-0">
                                <Icon className="w-5 h-5 text-gold" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">{item.label}</p>
                                <p className="text-sm font-semibold text-gray-900 break-words">
                                    {item.value}
                                </p>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
