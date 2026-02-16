import { Shield, AlertTriangle, AlertCircle } from 'lucide-react'
import type { ChatClassification, SemaphoreLevel } from '../../types/chat'

interface SemaphoreBadgeProps {
    classification: ChatClassification
}

const SEMAPHORE_CONFIG: Record<SemaphoreLevel, {
    icon: typeof Shield
    label: string
    className: string
    bgClass: string
}> = {
    verde: {
        icon: Shield,
        label: 'Informativo',
        className: 'text-emerald-700',
        bgClass: 'bg-emerald-50 border-emerald-200',
    },
    amarillo: {
        icon: AlertTriangle,
        label: 'Requiere contexto',
        className: 'text-amber-700',
        bgClass: 'bg-amber-50 border-amber-200',
    },
    rojo: {
        icon: AlertCircle,
        label: 'Alerta legal',
        className: 'text-red-700',
        bgClass: 'bg-red-50 border-red-200',
    },
}

const INTENTION_LABELS: Record<string, string> = {
    formalizacion: 'Formalización',
    identidad_ruc: 'Identidad / RUC',
    donaciones: 'Donaciones',
    tributacion: 'Tributación',
    contratacion: 'Contratación',
    propiedad_intelectual: 'Propiedad Intelectual',
    datos_personales: 'Datos Personales',
    gobernanza: 'Gobernanza',
    alianzas: 'Alianzas',
    permisos: 'Permisos',
    marca_identidad: 'Marca / Identidad',
    seguridad_informacion: 'Seguridad de la Información',
    cooperacion_internacional: 'Cooperación Internacional',
    fuera_de_alcance: 'Fuera de alcance',
}

export function SemaphoreBadge({ classification }: SemaphoreBadgeProps) {
    const config = SEMAPHORE_CONFIG[classification.semaphore]
    const Icon = config.icon
    const intentionLabel = classification.intention_name
        || INTENTION_LABELS[classification.intention]
        || classification.intention

    return (
        <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium ${config.bgClass} ${config.className} animate-fade-in`}>
            <Icon className="w-3.5 h-3.5" />
            <span>{config.label}</span>
            <span className="opacity-50">·</span>
            <span className="opacity-75">{intentionLabel}</span>
            {classification.confidence > 0 && (
                <span className="opacity-40 text-[10px]">
                    {Math.round(classification.confidence * 100)}%
                </span>
            )}
        </div>
    )
}
