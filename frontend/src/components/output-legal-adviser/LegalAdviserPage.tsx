import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Download } from 'lucide-react'
import { LegalAdviserPackage } from '../../types/adviser.types'
import { LoadingScreen } from '../output-evaluation/LoadingScreen'
import { OrganizationProfileCard } from './OrganizationProfileCard'
import { CriticalTopicsSection } from './CriticalTopicsSection'
import { LawyerQuestionsSection } from './LawyerQuestionsSection'
import { RequiredDocumentsChecklist } from './RequiredDocumentsChecklist'
import { InternalDecisionsChecklist } from './InternalDecisionsChecklist'
import { mockAdviserData } from './mockAdviserData'

export function LegalAdviserPage() {
    const navigate = useNavigate()
    const location = useLocation()
    const [isLoading, setIsLoading] = useState(true)
    const [adviserData, setAdviserData] = useState<LegalAdviserPackage | null>(null)

    useEffect(() => {
        const stateData = (location.state as { adviserData?: LegalAdviserPackage })?.adviserData

        if (stateData) {
            // Brief loading screen for UX, then show real data
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
                <div className="text-center">
                    <p className="text-gray-600">No se pudo cargar el paquete de asesor legal.</p>
                    <button
                        onClick={() => navigate('/chat')}
                        className="mt-4 px-6 py-2 bg-yellow-400 text-white rounded-full hover:bg-yellow-500"
                    >
                        Volver al inicio
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="bg-yellow-400 w-5 h-5 transform rotate-45 rounded-sm" />
                        <div>
                            <h1 className="font-bold text-lg text-gray-900">GPT Legal</h1>
                            <p className="text-xs text-gray-500">
                                Legal Consultations / {adviserData.organizationProfile.entityName}
                            </p>
                        </div>
                    </div>

                    <button className="flex items-center gap-2 px-4 py-2 bg-yellow-400 text-white rounded-lg hover:bg-yellow-500 transition-colors">
                        <Download className="w-4 h-4" />
                        <span className="font-semibold text-sm">Descargar PDF</span>
                    </button>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
                {/* Title */}
                <div className="text-center">
                    <div className="flex items-center justify-center gap-2 mb-2">
                        <div className="bg-yellow-400 w-6 h-6 transform rotate-45 rounded-sm" />
                        <h2 className="text-3xl font-bold text-gray-900">{adviserData.pageTitle}</h2>
                    </div>
                    <p className="text-sm text-gray-500 uppercase tracking-wide">
                        {adviserData.pageSubtitle}
                    </p>
                </div>

                {/* Organization Profile */}
                <OrganizationProfileCard
                    profile={adviserData.organizationProfile}
                    fundingDescription={adviserData.fundingDescription}
                />

                {/* Critical Topics */}
                <CriticalTopicsSection
                    topics={adviserData.criticalTopics}
                    fundingRange={adviserData.fundingCritical}
                />

                {/* Lawyer Questions */}
                <LawyerQuestionsSection questions={adviserData.lawyerQuestions} />

                {/* Two Column Layout for Checklists */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Required Documents */}
                    <RequiredDocumentsChecklist documents={adviserData.requiredDocuments} />

                    {/* Internal Decisions */}
                    <InternalDecisionsChecklist decisions={adviserData.internalDecisions} />
                </div>
            </main>
        </div>
    )
}
