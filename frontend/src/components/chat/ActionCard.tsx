import { useNavigate } from 'react-router-dom'
import { Upload, UserCheck, HelpCircle, ArrowRight } from 'lucide-react'
import type { SuggestedAction, ActionType } from '../../types/chat'

interface ActionCardProps {
    action: SuggestedAction
    onFileUploadRequest?: () => void
}

const ACTION_CONFIG: Record<ActionType, {
    icon: typeof Upload
    colorClass: string
    bgClass: string
    borderClass: string
}> = {
    upload_file: {
        icon: Upload,
        colorClass: 'text-blue-700',
        bgClass: 'bg-blue-50',
        borderClass: 'border-blue-200 hover:border-blue-300',
    },
    derive_to_advisor: {
        icon: UserCheck,
        colorClass: 'text-red-700',
        bgClass: 'bg-red-50',
        borderClass: 'border-red-200 hover:border-red-300',
    },
    provide_context: {
        icon: HelpCircle,
        colorClass: 'text-amber-700',
        bgClass: 'bg-amber-50',
        borderClass: 'border-amber-200 hover:border-amber-300',
    },
    none: {
        icon: HelpCircle,
        colorClass: 'text-gray-500',
        bgClass: 'bg-gray-50',
        borderClass: 'border-gray-200',
    },
}

export function ActionCard({ action, onFileUploadRequest }: ActionCardProps) {
    const navigate = useNavigate()
    const config = ACTION_CONFIG[action.type] || ACTION_CONFIG.none
    const Icon = config.icon

    if (action.type === 'none') return null

    const handleClick = () => {
        switch (action.type) {
            case 'upload_file':
                onFileUploadRequest?.()
                break
            case 'derive_to_advisor':
                navigate('/legal-adviser')
                break
            case 'provide_context':
                // The context fields are shown in the description; this is informational
                break
        }
    }

    return (
        <button
            onClick={handleClick}
            className={`w-full mt-3 p-4 rounded-xl border ${config.borderClass} ${config.bgClass} text-left transition-all duration-200 hover:shadow-sm group animate-fade-in`}
        >
            <div className="flex items-start gap-3">
                <div className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center ${config.bgClass}`}>
                    <Icon className={`w-5 h-5 ${config.colorClass}`} />
                </div>
                <div className="flex-1 min-w-0">
                    <p className={`font-semibold text-sm ${config.colorClass}`}>
                        {action.label}
                    </p>
                    <p className="text-xs text-gray-600 mt-0.5 leading-relaxed">
                        {action.description}
                    </p>
                </div>
                {action.type !== 'provide_context' && (
                    <ArrowRight className={`w-4 h-4 flex-shrink-0 mt-1 ${config.colorClass} opacity-50 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all`} />
                )}
            </div>
        </button>
    )
}
