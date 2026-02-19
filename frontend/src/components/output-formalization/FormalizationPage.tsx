import { useState } from 'react'
import { FileDown, ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { mockFormalizationData } from './mockFormalizationData'
import { FormalizationCard } from './FormalizationCard'
import { FormalizationDetailView } from './FormalizationDetailView'
import { exportFormalizationToDocx } from './formalizationExport'

export function FormalizationPage() {
    const navigate = useNavigate()
    const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null)
    const [isExporting, setIsExporting] = useState(false)

    const handleExport = async () => {
        if (isExporting) return
        setIsExporting(true)
        try {
            await exportFormalizationToDocx(data)
        } catch (err) {
            console.error('Error al exportar ruta de formalización:', err)
        } finally {
            setIsExporting(false)
        }
    }

    const data = mockFormalizationData
    const selectedRoute = selectedRouteId
        ? data.routes.find(r => r.id === selectedRouteId) ?? null
        : null

    if (selectedRoute) {
        return (
            <FormalizationDetailView
                route={selectedRoute}
                onBack={() => setSelectedRouteId(null)}
            />
        )
    }

    return (
        <div className="min-h-screen bg-[#f5f4f0]">
            <div className="max-w-5xl mx-auto px-4 py-12">

                {/* Top bar */}
                <div className="flex items-center justify-between mb-10">
                    <button
                        onClick={() => navigate(-1)}
                        className="flex items-center gap-2 text-sm font-semibold text-gray-500 hover:text-gray-800 transition-colors group"
                    >
                        <ArrowLeft className="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-0.5" />
                        Volver
                    </button>

                    <button
                        onClick={handleExport}
                        disabled={isExporting}
                        className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gold text-white text-sm font-semibold hover:bg-gold-dark transition-colors shadow-sm disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                        <FileDown className="w-4 h-4" />
                        {isExporting ? 'Generando...' : 'Descargar Guía'}
                    </button>
                </div>

                {/* Hero section */}
                <div className="mb-10 animate-slide-up">
                    <p className="text-xs font-black tracking-[0.2em] text-gold uppercase mb-2">
                        Portal de Servicios
                    </p>
                    <h1 className="text-4xl md:text-5xl font-black text-gray-900 mb-4 leading-tight">
                        Ruta de formalización
                    </h1>
                    <p className="text-base text-gray-500 max-w-xl leading-relaxed">
                        Acceda a nuestra biblioteca inteligente de procesos legales. Seleccione el trámite que desea gestionar para visualizar una guía paso a paso generada por IA.
                    </p>
                </div>

                {/* Cards grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 animate-slide-up stagger-1">
                    {data.routes.map(route => (
                        <FormalizationCard
                            key={route.id}
                            route={route}
                            onViewDetail={setSelectedRouteId}
                        />
                    ))}
                </div>

                {/* Footer note */}
                <p className="text-center text-xs text-gray-400 mt-14">
                    Ruta personalizada para{' '}
                    <span className="font-semibold text-gray-500">{data.organizationName}</span>
                    {' '}— {data.subtitle}.
                </p>
            </div>
        </div>
    )
}
