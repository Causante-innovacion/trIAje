import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Download, ArrowLeft, FileText } from 'lucide-react'
import { LegalAdviserPackage } from '../../types/adviser.types'
import { LoadingScreen } from '../output-evaluation/LoadingScreen'
import { OrganizationProfileCard } from './OrganizationProfileCard'
import { CriticalTopicsSection } from './CriticalTopicsSection'
import { LawyerQuestionsSection } from './LawyerQuestionsSection'
import { RequiredDocumentsChecklist } from './RequiredDocumentsChecklist'
import { InternalDecisionsChecklist } from './InternalDecisionsChecklist'
import { mockAdviserData } from './mockAdviserData'
import clsx from 'clsx'

export function LegalAdviserPage() {
    const navigate = useNavigate()
    const location = useLocation()
    const [isLoading, setIsLoading] = useState(true)
    const [adviserData, setAdviserData] = useState<LegalAdviserPackage | null>(null)
    const [isScrolled, setIsScrolled] = useState(false)

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 20)
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    useEffect(() => {
        const stateData = (location.state as { adviserData?: LegalAdviserPackage })?.adviserData

        if (stateData) {
            const timer = setTimeout(() => {
                setAdviserData(stateData)
                setIsLoading(false)
            }, 2000)
            return () => clearTimeout(timer)
        }

        // No data passed - use mock data for development
        const timer = setTimeout(() => {
            setAdviserData(mockAdviserData)
            setIsLoading(false)
        }, 2000)
        return () => clearTimeout(timer)
    }, [location.state])

    if (isLoading) {
        return <LoadingScreen />
    }

    if (!adviserData) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center animate-slide-up">
                    <div className="w-16 h-16 rounded-2xl bg-cream flex items-center justify-center mx-auto mb-4">
                        <FileText className="w-8 h-8 text-gold" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">No se pudo cargar el paquete</h3>
                    <p className="text-sm text-gray-500 mb-6 max-w-xs">
                        No encontramos datos del asesor legal. Intenta realizar una nueva consulta.
                    </p>
                    <button
                        onClick={() => navigate('/')}
                        className="btn-action-primary"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Volver al inicio
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header with scroll detection */}
            <header className={clsx(
                'sticky top-0 z-50 transition-all duration-300',
                isScrolled
                    ? 'bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm'
                    : 'bg-white border-b border-transparent'
            )}>
                <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="bg-gold w-5 h-5 transform rotate-45 rounded-sm" />
                        <div>
                            <h1 className="font-bold text-lg text-gray-900">GPT Legal</h1>
                            <p className="text-xs text-gray-500">
                                Legal Consultations / {adviserData.organizationProfile.entityName}
                            </p>
                        </div>
                    </div>

                    <button className="btn-action-primary text-sm">
                        <Download className="w-4 h-4" />
                        Descargar PDF
                    </button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-10 space-y-10">
                {/* Title */}
                <div className="text-center animate-slide-up">
                    <div className="flex items-center justify-center gap-3 mb-3">
                        <div className="bg-gold w-6 h-6 transform rotate-45 rounded-sm" />
                        <h2 className="font-heading text-3xl md:text-4xl font-bold text-gray-900">{adviserData.pageTitle}</h2>
                    </div>
                    <p className="text-sm text-gray-500 uppercase tracking-wide font-medium">
                        {adviserData.pageSubtitle}
                    </p>
                </div>

                {/* Organization Profile */}
                <section className="animate-slide-up stagger-1">
                    <OrganizationProfileCard
                        profile={adviserData.organizationProfile}
                        fundingDescription={adviserData.fundingDescription}
                    />
                </section>

                {/* Critical Topics */}
                <section className="animate-slide-up stagger-2">
                    <CriticalTopicsSection
                        topics={adviserData.criticalTopics}
                        fundingRange={adviserData.fundingCritical}
                    />
                </section>

                {/* Lawyer Questions */}
                <section className="animate-slide-up stagger-3">
                    <LawyerQuestionsSection questions={adviserData.lawyerQuestions} />
                </section>

                {/* Two Column Layout for Checklists */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-slide-up stagger-4">
                    <RequiredDocumentsChecklist documents={adviserData.requiredDocuments} />
                    <InternalDecisionsChecklist decisions={adviserData.internalDecisions} />
                </div>
            </main>
        </div>
    )
}
