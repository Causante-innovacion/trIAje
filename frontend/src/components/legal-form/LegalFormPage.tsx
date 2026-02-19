import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { evaluationApi } from '../../shared/services/api'
import { mapBackendToProjectEvaluation, BackendEvaluationResponse } from '../../types/evaluation.types'
import { useChatStore } from '../../stores/chatStore'
import { Check, ChevronLeft, Fingerprint, Gavel, Banknote, Users, BookOpen, Network, Lightbulb, Info, Lock, X, Building2, LucideIcon, Globe, ClipboardList } from 'lucide-react'
import { OrganizationCard } from './OrganizationCard'
import { ProgressTracker } from './ProgressTracker'
import { FormBlock } from './FormBlock'
import { YesNoButtons, SingleSelect, MultiSelectChips } from './FormInputs'
import { HelpTooltip } from './HelpTooltip'
import clsx from 'clsx'

interface Organization {
  id: string
  name: string
  role: string
  progress: number
  color: string
  icon: LucideIcon
}

interface FormState {
  // Block 1: Identity
  orgType: string | null
  orgTypeOther: string
  orgPurpose: string | null
  orgPurposeOther: string
  seeksProfits: string | null

  // Block 2: Formalization
  hasLegalStatus: string | null
  ruc: string | null
  additionalRegistries: string[]

  // Block 3: Income
  handlesMoney: boolean | null
  incomeSources: string[]
  receivesForeignFunds: boolean | null

  // Block 4: International Cooperation
  // receivesInternationalCooperation removed - mapped to receivesForeignFunds
  apciStatus: string | null

  // Block 4: HR
  hiringModalities: string[]
  contractsValid: string | null

  // Block 5: Accounting
  hasAccountingRecords: string | null
  accountingRecordsDetail: string | null
  availableDocuments: string[]

  // Block 6: Governance
  governanceBodies: boolean | null
  hasLegalRepresentative: string | null

  // Block 7: Intangibles
  intangibleAssets: string[]

  // Tool Specific
  tool: 'evaluation' | 'compliance' | 'query'
  toolSpecific: {
    // Evaluation
    evaluationGoals?: string[]
    legalAreas?: string[]
    urgency?: string
    hasReceivedNotification?: boolean | null // New field for urgent cases

    // Compliance
    complianceGoal?: string
    timeline?: string

    // Query
    queryArea?: string
    specificQuestion?: string
  }
  isCompleted: boolean
  hasConfirmed: boolean
}

const DEFAULT_ORGANIZATIONS: Organization[] = [
  { id: '1', name: 'Organización 1', role: 'Ejecutor principal', progress: 0, color: '#B3994C', icon: Building2 },
]

const ORG_COLORS = ['#B3994C', '#8F86A3', '#D7D100']

const initialFormState: FormState = {
  orgType: null,
  orgTypeOther: '',
  orgPurpose: null,
  orgPurposeOther: '',
  seeksProfits: null,
  hasLegalStatus: null,
  ruc: null,
  additionalRegistries: [],
  handlesMoney: null,
  incomeSources: [],
  receivesForeignFunds: null,
  apciStatus: null,
  hiringModalities: [],
  contractsValid: null,
  hasAccountingRecords: null,
  accountingRecordsDetail: null,
  availableDocuments: [],
  governanceBodies: null,
  hasLegalRepresentative: null,
  intangibleAssets: [],
  tool: 'evaluation', // Default to evaluation
  toolSpecific: {},
  isCompleted: false,
  hasConfirmed: false,
}

const getStorageKey = (orgId: string) => `gpt_legal_form_progress_${orgId}`

// Calculate completed questions for a given form state
const calculateProgress = (form: FormState) => {
  let completedCount = 0
  let totalCount = 0

  // Helper to add block totals
  const addBlock = (completed: number, total: number) => {
    completedCount += completed
    totalCount += total
  }

  // Block 1
  let b1 = 0
  if (form.orgType) b1++
  if (form.orgPurpose) b1++
  if (form.seeksProfits !== null) b1++
  addBlock(b1, 3)

  // Block 2
  let b2 = 0
  if (form.hasLegalStatus) b2++
  if (form.ruc) b2++
  if (form.additionalRegistries.length > 0) b2++
  addBlock(b2, 3)

  // Block 3
  let b3 = 0
  if (form.handlesMoney !== null) b3++
  if (form.incomeSources.length > 0) b3++
  if (form.receivesForeignFunds !== null) b3++
  addBlock(b3, 3)

  // Block 4
  let b4 = 0
  // Conditional on Q8 (receivesForeignFunds)
  if (form.receivesForeignFunds === true) {
    if (form.apciStatus) b4++
    // If YES, we expect 1 answer (apciStatus). Total for this block should be dynamic or fixed?
    // Let's say if YES, total=1. If NO, total=0 (skipped).
    // But existing structure has fixed totals.
    // If NO to Q8, this block is skipped or auto-completed.
  }
  // We will handle total logic in BLOCKS definition or here.
  // Let's count completion:
  if (form.receivesForeignFunds === true && form.apciStatus) b4 = 2 // Fully complete if YES
  if (form.receivesForeignFunds === false) b4 = 2 // Fully complete if NO (skipped)
  if (form.receivesForeignFunds === null) b4 = 0 // Not started since Q8 is in Block 3?
  // Actually Block 4 is separate. But it depends on Q8.
  // If Q8 is null, we can't show Block 4? 
  // Let's assume Q8 is answered in Block 3.
  addBlock(b4, 2)

  // Block 5 (Old 4)
  let b5 = 0
  if (form.hiringModalities.length > 0) b5++
  if (form.contractsValid !== null) b5++
  addBlock(b5, 2)

  // Block 6 (Old 5)
  let b6 = 0
  if (form.hasAccountingRecords !== null) b6++
  if (form.availableDocuments.length > 0) b6++
  addBlock(b6, 2)

  // Block 7 (Old 6)
  let b7 = 0
  if (form.governanceBodies !== null) b7++
  if (form.hasLegalRepresentative !== null) b7++
  addBlock(b7, 2)

  // Block 8 (Old 7)
  let b8 = 0
  if (form.intangibleAssets.length > 0) b8++
  addBlock(b8, 1)

  // Block 9: Tool Specific
  let b9 = 0
  if (form.tool === 'evaluation') {
    if (form.toolSpecific.evaluationGoals?.length) b9++
    if (form.toolSpecific.legalAreas?.length) b9++
    if (form.toolSpecific.urgency) {
      b9++
      // If urgency is 'Inmediata', check for notification
      if (form.toolSpecific.urgency.startsWith('Inmediata') && form.toolSpecific.hasReceivedNotification === undefined) {
        // Not counted yet
      } else if (form.toolSpecific.urgency.startsWith('Inmediata') && form.toolSpecific.hasReceivedNotification !== null) {
        // Counted as part of urgency step or separate?
        // Let's add weight if notification is answered
      }
    }
    addBlock(b9, 3)
  } else if (form.tool === 'compliance') {
    if (form.toolSpecific.complianceGoal) b9++
    if (form.toolSpecific.timeline) b9++
    addBlock(b9, 2)
  } else if (form.tool === 'query') {
    if (form.toolSpecific.queryArea) b9++
    if (form.toolSpecific.specificQuestion) b9++
    addBlock(b9, 2)
  } else {
    addBlock(0, 0)
  }

  let progressPercentage = Math.round((completedCount / totalCount) * 100)

  // Cap at 99% if 100% completed but not marked as finished
  if (progressPercentage === 100 && !form.isCompleted) {
    progressPercentage = 99
  }

  return progressPercentage
}

export function LegalFormPage() {
  const navigate = useNavigate()
  const extractedPlan = useChatStore((s) => s.extractedPlan)

  // Build initial organizations from extracted plan or use defaults
  const baseOrganizations = useMemo<Organization[]>(() => {
    if (extractedPlan && extractedPlan.raw_extractions.team_and_partners.length > 0) {
      return extractedPlan.raw_extractions.team_and_partners.map((org, i) => ({
        id: String(i + 1),
        name: org.name,
        role: org.role_raw || 'Ejecutor principal',
        progress: 0,
        color: ORG_COLORS[i % ORG_COLORS.length],
        icon: Building2,
      }))
    }
    return DEFAULT_ORGANIZATIONS
  }, [extractedPlan])

  const [selectedOrg, setSelectedOrg] = useState<string>('1')
  const [organizations, setOrganizations] = useState<Organization[]>(baseOrganizations)

  // Initialize form
  const [form, setForm] = useState<FormState>(initialFormState)

  // Migration logic
  useEffect(() => {
    try {
      const oldKey = 'gpt_legal_form_progress'
      const oldData = localStorage.getItem(oldKey)

      if (oldData && !localStorage.getItem(getStorageKey('1'))) {
        localStorage.setItem(getStorageKey('1'), oldData)
        localStorage.removeItem(oldKey)
        console.log('Migrated old data to organization 1')
      }
    } catch (e) {
      console.error('Failed to migrate data', e)
    }
  }, [])

  // Load form data when organization changes
  useEffect(() => {
    try {
      const saved = localStorage.getItem(getStorageKey(selectedOrg))
      if (saved) {
        setForm(JSON.parse(saved))
      } else {
        setForm(initialFormState)
      }
    } catch (e) {
      console.error('Failed to load form for org', selectedOrg, e)
      setForm(initialFormState)
    }
  }, [selectedOrg])

  // Update organizations progress on mount and when form changes (saved)
  useEffect(() => {
    const updatedOrgs = baseOrganizations.map(org => {
      try {
        // Use current form state for selected organization to get real-time updates
        if (org.id === selectedOrg) {
          return { ...org, progress: calculateProgress(form) }
        }

        // For other organizations, read from localStorage
        const saved = localStorage.getItem(getStorageKey(org.id))
        if (saved) {
          const orgForm: FormState = JSON.parse(saved)
          return { ...org, progress: calculateProgress(orgForm) }
        }
        return { ...org, progress: 0 }
      } catch (e) {
        return { ...org, progress: 0 }
      }
    })
    setOrganizations(updatedOrgs)
  }, [form, selectedOrg])


  // Save to localStorage on change
  useEffect(() => {
    try {
      localStorage.setItem(getStorageKey(selectedOrg), JSON.stringify(form))
    } catch (e) {
      console.error('Failed to save form progress', e)
    }
  }, [form]) // Removed selectedOrg dependency to avoid saving old form state to new org key on switch

  // Calculate completed questions dynamically
  const calculateCompleted = () => {
    let block1 = 0, block2 = 0, block3 = 0, block4 = 0, block5 = 0, block6 = 0, block7 = 0

    // Block 1
    if (form.orgType) block1++
    if (form.orgPurpose) block1++
    if (form.seeksProfits !== null) block1++

    // Block 2
    if (form.hasLegalStatus) block2++
    if (form.ruc) block2++
    if (form.additionalRegistries.length > 0) block2++

    // Block 3
    if (form.handlesMoney !== null) block3++
    if (form.incomeSources.length > 0) block3++
    if (form.receivesForeignFunds !== null) block3++

    // Block 4
    // If receivesForeignFunds (Q8) is TRUE -> 1 question (APCI status)
    // If receivesForeignFunds (Q8) is FALSE -> 0 questions (Block skipped/completed)
    // We treat it as 2 points if completed/skipped to match 'total=2' in BLOCKS
    if (form.receivesForeignFunds === true && form.apciStatus) block4 = 2
    if (form.receivesForeignFunds === false) block4 = 2

    // Block 5 (Old 4)
    if (form.hiringModalities.length > 0) block5++
    if (form.contractsValid !== null) block5++

    // Block 6 (Old 5)
    if (form.hasAccountingRecords !== null) block6++
    if (form.availableDocuments.length > 0 || form.orgType === 'Colectivo / iniciativa no formalizada') block6++

    // Block 7 (Old 6)
    if (form.governanceBodies !== null) block7++
    if (form.hasLegalRepresentative !== null || form.orgType === 'Colectivo / iniciativa no formalizada') block7++

    // Block 8 (Old 7)
    // Wait, let's create block8 variable
    let block8 = 0
    if (form.intangibleAssets.length > 0) block8++

    // Block 9: Tool Specific
    let block9 = 0
    // Tool selection removed from progress count as it is read-only

    // Tool specific questions

    // Tool specific questions
    if (form.tool === 'evaluation') {
      if (form.toolSpecific.evaluationGoals?.length) block9++
      if (form.toolSpecific.legalAreas?.length) block9++
      if (form.toolSpecific.urgency) block9++
    } else if (form.tool === 'compliance') {
      if (form.toolSpecific.complianceGoal) block9++
      if (form.toolSpecific.timeline) block9++
    } else if (form.tool === 'query') {
      if (form.toolSpecific.queryArea) block9++
      if (form.toolSpecific.specificQuestion) block9++
    }

    return { block1, block2, block3, block4, block5, block6, block7, block8, block9 }
  }

  const completed = calculateCompleted()

  // Calculate total for block 9 based on tool
  const getBlock9Total = () => {
    if (form.tool === 'evaluation') return 3
    if (form.tool === 'compliance') return 2
    if (form.tool === 'query') return 2
    return 0
  }

  const BLOCKS = [
    { id: 'identity', name: 'Identidad', icon: Fingerprint, color: 'blue', completed: completed.block1, total: 3 },
    { id: 'formalization', name: 'Formalización', icon: Gavel, color: 'purple', completed: completed.block2, total: 3 },
    { id: 'income', name: 'Fuentes de Ingreso', icon: Banknote, color: 'green', completed: completed.block3, total: 3 },
    { id: 'intl', name: 'Coop. Internacional', icon: Globe, color: 'cyan', completed: completed.block4, total: 2 },
    { id: 'hr', name: 'Recursos Humanos', icon: Users, color: 'orange', completed: completed.block5, total: 2 },
    { id: 'accounting', name: 'Info Contable', icon: BookOpen, color: 'teal', completed: completed.block6, total: 2 },
    { id: 'governance', name: 'Gobernanza', icon: Network, color: 'indigo', completed: completed.block7, total: 2 },
    { id: 'intangibles', name: 'Intangibles', icon: Lightbulb, color: 'pink', completed: completed.block8, total: 1 },
    { id: 'tool', name: 'Detalle Solicitud', icon: ClipboardList, color: 'red', completed: completed.block9, total: getBlock9Total() },
  ]

  const totalQuestions = BLOCKS.reduce((acc, block) => acc + block.total, 0)
  const completedQuestions = BLOCKS.reduce((acc, block) => acc + block.completed, 0)

  const handleBack = () => {
    navigate('/chat')
  }

  const [isSubmitting, setIsSubmitting] = useState(false)

  /** Maps flat FormState to nested backend LegalProfile structure */
  const buildLegalProfile = (f: FormState) => ({
    identity: {
      org_type: f.orgType || null,
      org_type_other: f.orgTypeOther || null,
      org_purpose: f.orgPurpose || null,
      org_purpose_other: f.orgPurposeOther || null,
      seeks_profits: f.seeksProfits === 'Con fines de lucro (puede haber reparto)' ? true : (f.seeksProfits === 'Sin fines de lucro (no se reparten excedentes)' ? false : null),
    },
    formalization: {
      has_legal_status: f.hasLegalStatus,
      ruc_status: f.ruc,
      special_registries: f.additionalRegistries,
    },
    income: {
      handles_money: f.handlesMoney,
      receives_foreign_funds: f.receivesForeignFunds,
      income_sources: f.incomeSources,
    },
    international_cooperation: {
      receives_international_cooperation: f.receivesForeignFunds,
      apci_status: f.apciStatus,
    },
    human_resources: {
      hiring_modalities: f.hiringModalities,
      contracts_valid: f.contractsValid,
    },
    accounting: {
      has_accounting_records: f.hasAccountingRecords === 'Sí' && f.accountingRecordsDetail
        ? `Sí, ${f.accountingRecordsDetail.toLowerCase()}`
        : f.hasAccountingRecords,
      available_documents: f.availableDocuments,
    },
    governance: {
      has_governance_bodies: f.governanceBodies,
      has_legal_representative: f.hasLegalRepresentative,
    },
    intangibles: {
      intangible_assets: f.intangibleAssets,
    },
  })

  /** Builds the tool_specific payload in backend format */
  const buildToolSpecific = (f: FormState) => {
    if (f.tool === 'evaluation') {
      return { evaluation: { evaluation_goals: f.toolSpecific.evaluationGoals || [], legal_areas: f.toolSpecific.legalAreas || [], urgency: f.toolSpecific.urgency || null, has_received_notification: f.toolSpecific.hasReceivedNotification } }
    }
    if (f.tool === 'compliance') {
      return { compliance: { compliance_goal: f.toolSpecific.complianceGoal || null, timeline: f.toolSpecific.timeline || null } }
    }
    return { query: { query_area: f.toolSpecific.queryArea || null, specific_question: f.toolSpecific.specificQuestion || null } }
  }

  const handleSubmit = async () => {
    if (completedQuestions !== totalQuestions || !form.hasConfirmed) return

    setIsSubmitting(true)

    // Mark as completed before submitting
    const completedForm = { ...form, isCompleted: true }
    setForm(completedForm)
    try {
      localStorage.setItem(getStorageKey(selectedOrg), JSON.stringify(completedForm))

      // Check if ALL organizations are completed
      const allOrgsCompleted = organizations.every(org => {
        if (org.id === selectedOrg) return true
        return org.progress === 100
      })

      if (form.tool === 'evaluation' && allOrgsCompleted) {
        // Collect all org FormStates from localStorage
        const orgProfiles = organizations.map(org => {
          const savedJson = org.id === selectedOrg
            ? JSON.stringify(completedForm)
            : localStorage.getItem(getStorageKey(org.id))
          const orgForm: FormState = savedJson ? JSON.parse(savedJson) : completedForm

          return {
            id: org.id,
            name: org.name,
            role: org.role,
            legal_profile: buildLegalProfile(orgForm),
          }
        })

        // Build NormalizedProjectIntake for backend
        const projectIntake = {
          tool: form.tool,
          organizations: orgProfiles,
          tool_specific: buildToolSpecific(completedForm),
          risk_assessment: {
            overall_risk_level: 'LOW',
            derivation_color: 'green',
            derivation_required: false,
            organization_risks: [],
            shared_signals: [],
            shared_reasons: [],
            detected_intentions: [],
          },
          total_organizations: organizations.length,
        }

        // Call evaluation endpoint
        const evaluationResponse = await evaluationApi.evaluateIntake(projectIntake)

        const backendData: BackendEvaluationResponse = evaluationResponse.data

        // Map to display type
        const orgNames = organizations.map(o => ({ id: o.id, name: o.name, role: o.role }))
        const evaluationData = mapBackendToProjectEvaluation(backendData, orgNames)

        navigate('/evaluation', { state: { evaluationData } })
      } else if (!allOrgsCompleted) {
        // Stay on page for user to fill next org
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } else {
        navigate('/chat')
      }

    } catch (error) {
      console.error('Error submitting intake:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const updateForm = <K extends keyof FormState>(field: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const updateToolSpecific = (field: string, value: any) => {
    setForm((prev) => ({
      ...prev,
      toolSpecific: {
        ...prev.toolSpecific,
        [field]: value
      }
    }))
  }

  // Helper function to get question number styling based on answered state
  const getQuestionNumberClass = (isAnswered: boolean) => {
    return isAnswered
      ? 'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-[#D6CF00] text-white'
      : 'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-[#E5E7EB] text-[#4B5563]'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Page Title */}
        <section className="mb-8">
          <button
            onClick={handleBack}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 transition-colors mb-4"
          >
            <ChevronLeft className="w-4 h-4" />
            Volver
          </button>
          <div className="flex items-center gap-3">
            <div className="bg-gold w-6 h-6 transform rotate-45 rounded-sm" />
            <h1 className="font-heading text-2xl md:text-3xl font-bold text-gray-900">Ficha Legal Mínima</h1>
          </div>
        </section>

        {/* Organization Selector */}
        <section className="mb-10">
          <h2 className="font-heading text-xl font-semibold mb-4">Seleccionar Organización</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {organizations.map((org) => (
              <OrganizationCard
                key={org.id}
                organization={org}
                isSelected={selectedOrg === org.id}
                onClick={() => setSelectedOrg(org.id)}
              />
            ))}
          </div>
        </section>

        {/* Progress Tracker */}
        <ProgressTracker
          completedQuestions={completedQuestions}
          totalQuestions={totalQuestions}
          blocks={BLOCKS}
          isFinished={form.isCompleted}
        />

        {/* Form Blocks */}
        <div className="flex justify-center">
          <div className="space-y-10 mb-20">
            {/* Block 1: Identity */}
            <FormBlock
              title="1. Identidad y naturaleza de la organización"
              icon={Fingerprint}
              iconColor="blue"
              completed={completed.block1}
              total={3}
            >
              <div className="space-y-6">
                {/* Question 1.1 */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(!!form.orgType)}>1</span>
                      <span className="text-sm font-semibold">¿Cuál es la forma legal actual de su organización o grupo?</span>
                    </label>
                    <HelpTooltip text={"Selecciona la figura jurídica que mejor describa tu organización. Es importante usar el término legal correcto:\n\n- **Asociación:** Persona jurídica sin fines de lucro, formada por un grupo de personas con un objetivo común (social, cultural, deportivo, etc.). Los excedentes se reinvierten, no se reparten.\n\n- **Fundación:** Persona jurídica sin fines de lucro, creada a partir de un patrimonio destinado a fines de interés general (educación, investigación, asistencia social). Tiene un consejo directivo que administra los bienes.\n\n- **Empresa:** Persona jurídica con fines de lucro (SAC, SRL, EIRL, etc.). Su objetivo es generar ganancias que pueden distribuirse entre los socios o accionistas.\n\n- **Colectivo / iniciativa no formalizada:** Grupo de personas que trabajan juntas sin haber inscrito una persona jurídica en Registros Públicos. Operan de hecho, como colectivos artísticos, proyectos comunitarios o agrupaciones informales.\n\n- **Otro:** Especifica si tu organización tiene una forma distinta (ej. Comité, Cooperativa, etc.).\n\n**Nota:** \"ONG\" no es una forma legal en Perú, sino un estatus administrativo que algunas organizaciones obtienen ante APCI para recibir cooperación internacional. Si tu organización es una ONG, selecciona \"Asociación\" o \"Fundación\" según corresponda."} />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <select
                      value={form.orgType || ''}
                      onChange={(e) => updateForm('orgType', e.target.value)}
                      disabled={form.isCompleted}
                      className={clsx(
                        "w-full rounded-xl border-yellow-300 bg-yellow-50 text-sm py-3 px-4 focus:ring-yellow-400 focus:border-yellow-400",
                        form.isCompleted && "opacity-50 cursor-not-allowed"
                      )}
                    >
                      <option value="">Selecciona una opción</option>
                      <option value="Asociación">Asociación</option>
                      <option value="Fundación">Fundación</option>
                      <option value="Empresa">Empresa</option>
                      <option value="Colectivo / iniciativa no formalizada">Colectivo / iniciativa no formalizada</option>
                      <option value="Otro">Otro</option>
                    </select>
                    <input
                      type="text"
                      value={form.orgTypeOther}
                      onChange={(e) => updateForm('orgTypeOther', e.target.value)}
                      placeholder="Otro (especificar)"
                      disabled={form.isCompleted}
                      className={clsx(
                        "w-full rounded-xl border-gray-200 text-sm py-3 px-4",
                        form.isCompleted && "opacity-50 cursor-not-allowed"
                      )}
                    />
                  </div>
                </div>

                {/* Question 1.2 */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(!!form.orgPurpose)}>2</span>
                      <span className="text-sm font-semibold">¿Cuál describe mejor el objeto o fin principal de la organización?</span>
                    </label>
                    <HelpTooltip text={"Indica la actividad principal para la que fue creada la organización:\n\nEducativo: Enfocado en enseñanza, formación o investigación.\n\nCultural: Promoción de arte, tradiciones, patrimonio cultural.\n\nAmbiental: Conservación del medio ambiente, ecología, sostenibilidad.\n\nAsistencial / social: Ayuda a personas en situación de vulnerabilidad, servicios sociales.\n\nTecnológico / innovación: Desarrollo de tecnología, investigación aplicada, innovación.\n\nOtro: Especifica si el fin es distinto."} />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <select
                      value={form.orgPurpose || ''}
                      onChange={(e) => updateForm('orgPurpose', e.target.value)}
                      disabled={form.isCompleted}
                      className={clsx(
                        "w-full rounded-xl border-yellow-300 bg-yellow-50 text-sm py-3 px-4 focus:ring-yellow-400 focus:border-yellow-400",
                        form.isCompleted && "opacity-50 cursor-not-allowed"
                      )}
                    >
                      <option value="">Selecciona una opción</option>
                      <option value="Educativo">Educativo</option>
                      <option value="Cultural">Cultural</option>
                      <option value="Ambiental">Ambiental</option>
                      <option value="Asistencial / social">Asistencial / social</option>
                      <option value="Tecnológico / innovación">Tecnológico / innovación</option>
                      <option value="Otro">Otro</option>
                    </select>
                    <input
                      type="text"
                      value={form.orgPurposeOther}
                      onChange={(e) => updateForm('orgPurposeOther', e.target.value)}
                      placeholder="Otro (especificar)"
                      disabled={form.isCompleted}
                      className={clsx(
                        "w-full rounded-xl border-gray-200 text-sm py-3 px-4",
                        form.isCompleted && "opacity-50 cursor-not-allowed"
                      )}
                    />
                  </div>
                </div>

                {/* Question 1.3 */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(!!form.seeksProfits)}>3</span>
                      <span className="text-sm font-semibold">¿Su entidad es con o sin fines de lucro?</span>
                    </label>
                    <HelpTooltip text={"Esta pregunta determina el régimen legal y tributario de la organización:\n\n- **Sin fines de lucro:** Los excedentes económicos se reinvierten íntegramente en el objeto social. Corresponde a asociaciones, fundaciones, comités. Pueden acceder a beneficios tributarios como la exoneración del Impuesto a la Renta.\n\n- **Con fines de lucro:** Las utilidades pueden distribuirse entre socios, accionistas o titulares. Corresponde a empresas (SAC, SRL, etc.). Están sujetas al régimen tributario general.\n\n- **Aún no definido / Estamos evaluando:** La organización está en etapa de formación y no ha decidido su naturaleza jurídica. Esta opción activa asesoría para definir la figura más adecuada.\n\n**Importante:** Si seleccionaste \"Asociación\" o \"Fundación\" en la pregunta anterior y aquí eliges \"Con fines de lucro\", existe una contradicción legal que será alertada, ya que estas figuras son estrictamente sin fines de lucro por ley."} />
                  </div>
                  <SingleSelect
                    options={[
                      'Sin fines de lucro (no se reparten excedentes)',
                      'Con fines de lucro (puede haber reparto)',
                      'Aún no definido / Estamos evaluando'
                    ]}
                    value={form.seeksProfits}
                    onChange={(val) => updateForm('seeksProfits', val)}
                    disabled={form.isCompleted}
                  />
                  {/* Alert for contradiction */}
                  {(form.orgType === 'Asociación' || form.orgType === 'Fundación') && form.seeksProfits === 'Con fines de lucro (puede haber reparto)' && (
                    <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2 text-red-700 text-sm">
                      <Info className="w-5 h-5 flex-shrink-0" />
                      <span><strong>Alerta:</strong> La figura legal es inadecuada para el fin declarado. Las asociaciones y fundaciones son sin fines de lucro por ley.</span>
                    </div>
                  )}
                </div>
              </div>
            </FormBlock>

            {/* Block 2: Formalization */}
            <FormBlock
              title="2. Nivel de formalización"
              icon={Gavel}
              iconColor="purple"
              completed={completed.block2}
              total={3}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(!!form.hasLegalStatus)}>4</span>
                      <span className="text-sm font-semibold">¿La organización cuenta actualmente con personería jurídica vigente?</span>
                    </label>
                    <HelpTooltip text={"La personería jurídica es el reconocimiento legal que permite a una organización actuar como sujeto de derechos y obligaciones.\n\nSí: Ya está inscrita en Registros Públicos y tiene existencia legal.\n\nNo: Opera de hecho, sin registro formal.\n\nEn trámite: Ya se inició el proceso de inscripción pero aún no está concluido."} />
                  </div>
                  <SingleSelect
                    options={['Sí', 'No', 'En trámite']}
                    value={form.hasLegalStatus}
                    onChange={(val) => updateForm('hasLegalStatus', val)}
                    disabled={form.isCompleted}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(!!form.ruc)}>5</span>
                      <span className="text-sm font-semibold">¿Cuál es la situación del RUC?</span>
                    </label>
                    <HelpTooltip text={"El RUC (Registro Único de Contribuyentes) es el número que identifica a la organización ante SUNAT para obligaciones tributarias.\n\nLo tengo: Ya está inscrito y activo.\n\nNo lo tengo: Nunca se ha tramitado.\n\nEn trámite: Se solicitó pero aún no se obtiene."} />
                  </div>
                  <SingleSelect
                    options={['Lo tengo', 'No lo tengo', 'En trámite']}
                    value={form.ruc}
                    onChange={(val) => updateForm('ruc', val)}
                    disabled={form.isCompleted}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.additionalRegistries.length > 0)}>6</span>
                      <span className="text-sm font-semibold">¿Cuentan con algún registro especial además de SUNARP y SUNAT?</span>
                    </label>
                    <HelpTooltip text={"Estos son registros tributarios administrados por SUNAT que otorgan beneficios específicos:\n\n- **Registro de Entidades Exoneradas del Impuesto a la Renta:** Inscripción que permite a asociaciones y fundaciones sin fines de lucro estar exoneradas del pago del Impuesto a la Renta por sus ingresos propios (si cumplen requisitos).\n\n- **Registro de Entidades Receptoras de Donaciones:** Permite emitir comprobantes de donación que son deducibles de impuestos para los donantes. Es necesario para recibir donaciones con beneficio tributario.\n\n- **Ninguno / No sé:** La organización no está inscrita en estos registros o desconoce su situación.\n\n**Nota:** Los registros relacionados con cooperación internacional (APCI) se consultan más adelante."} />
                  </div>
                  <MultiSelectChips
                    options={[
                      'Registro de Entidades Exoneradas del Impuesto a la Renta (SUNAT)',
                      'Registro de Entidades Receptoras de Donaciones (SUNAT)',
                      'Ninguno / No sé'
                    ]}
                    value={form.additionalRegistries}
                    onChange={(val) => updateForm('additionalRegistries', val)}
                    disabled={form.isCompleted}
                  />
                </div>
              </div>
            </FormBlock>

            {/* Block 3: Income Sources */}
            <FormBlock
              title="3. Fuentes de ingreso y manejo de fondos"
              icon={Banknote}
              iconColor="green"
              completed={completed.block3}
              total={3}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.handlesMoney !== null)}>7</span>
                      <span className="text-sm font-semibold">¿La organización maneja o manejará dinero?</span>
                    </label>
                    <HelpTooltip text={"Indica si la organización realiza actividades económicas que impliquen ingresos o egresos de dinero. Si es solo un proyecto sin fondos, responde \"No\". Esto ayuda a determinar obligaciones contables y tributarias."} />
                  </div>
                  <YesNoButtons
                    value={form.handlesMoney}
                    onChange={(val) => updateForm('handlesMoney', val)}
                    disabled={form.isCompleted}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.receivesForeignFunds !== null)}>8</span>
                      <span className="text-sm font-semibold">¿Recibe o planea recibir fondos desde fuera del Perú?</span>
                    </label>
                    <HelpTooltip text={"Se refiere a donaciones, transferencias o ingresos provenientes del extranjero. Esto puede implicar requisitos adicionales como el registro en APCI o regulaciones cambiarias."} />
                  </div>
                  <YesNoButtons
                    value={form.receivesForeignFunds}
                    onChange={(val) => updateForm('receivesForeignFunds', val)}
                    disabled={form.isCompleted}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.incomeSources.length > 0)}>9</span>
                      <span className="text-sm font-semibold">¿De dónde provienen o provendrán los ingresos?</span>
                    </label>
                    <HelpTooltip text={"Selecciona todas las fuentes de financiamiento:\n\nDonaciones: Aportes voluntarios sin contraprestación.\n\nVenta de servicios o productos: Ingresos por actividades comerciales.\n\nFondos públicos: Subvenciones del Estado peruano.\n\nFondos privados: Aportes de empresas, fundaciones u organismos internacionales.\n\nAún no recibe ingresos: La organización está en etapa inicial o sin actividad económica."} />
                  </div>
                  <MultiSelectChips
                    options={['Donaciones', 'Venta de servicios o productos', 'Fondos públicos', 'Fondos privados', 'Cooperación internacional', 'Aún no recibe ingresos']}
                    value={form.incomeSources}
                    onChange={(val) => updateForm('incomeSources', val)}
                    disabled={form.isCompleted}
                  />
                </div>
              </div>
            </FormBlock>

            {/* Block 4: International Cooperation */}
            <FormBlock
              title="4. Cooperación Internacional"
              icon={Globe}
              iconColor="cyan"
              completed={completed.block4}
              total={2}
            >
              <div className="space-y-6">
                <div className="space-y-6">
                  {form.receivesForeignFunds === true ? (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.apciStatus)}>11</span>
                          <span className="text-sm font-semibold">¿Cuál es su estado en APCI?</span>
                        </label>
                        <HelpTooltip text={"La Agencia Peruana de Cooperación Internacional (APCI) regula a las organizaciones que reciben fondos o cooperación técnica del extranjero.\n\n- **Registrado:** La organización ya está inscrita en el Registro de Organizaciones No Gubernamentales Receptoras de Cooperación Técnica Internacional (ENIEX) y está al día.\n\n- **Necesita:** La organización recibe fondos del extranjero pero aún no está registrada en APCI. Esto debe regularse para evitar infracciones.\n\n- **No aplica:** Aunque recibe fondos del extranjero, está exenta de registro (ej. ciertos convenios gubernamentales) o la cooperación no requiere inscripción.\n\n**Importante:** Operar sin registro en APCI cuando corresponde puede generar multas y la suspensión de beneficios."} />
                      </div>
                      <SingleSelect
                        options={['Registrado', 'Necesita', 'No aplica']}
                        value={form.apciStatus}
                        onChange={(val) => updateForm('apciStatus', val)}
                        columns={3}
                        disabled={form.isCompleted}
                      />
                    </div>
                  ) : (
                    <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg text-gray-500 text-sm text-center">
                      <p>No recibe fondos del extranjero, por lo que esta sección no aplica.</p>
                    </div>
                  )}
                </div>
              </div>
            </FormBlock>

            {/* Block 5: Human Resources */}
            <FormBlock
              title="5. Recursos humanos"
              icon={Users}
              iconColor="orange"
              completed={completed.block5}
              total={2}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.hiringModalities.length > 0)}>12</span>
                      <span className="text-sm font-semibold">¿Bajo qué modalidades contrata personal?</span>
                    </label>
                    <HelpTooltip text={"Selecciona las formas de vinculación laboral:\n\nPlanilla (DL 728): Contratos sujetos al régimen laboral privado, con todos los beneficios sociales.\n\nLocación de Servicios: Contratos civiles por servicios independientes, sin vínculo laboral (recibos por honorarios).\n\nVoluntariado: Personas que colaboran de manera solidaria sin remuneración (Ley del Voluntariado).\n\nPracticantes: Convenios de prácticas preprofesionales o profesionales.\n\nNinguno: No hay personal contratado."} />
                  </div>
                  <MultiSelectChips
                    options={['Planilla', 'Locación de servicios', 'Voluntariado', 'Prácticas', 'Ninguno']}
                    value={form.hiringModalities}
                    onChange={(val) => updateForm('hiringModalities', val)}
                    disabled={form.isCompleted}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.contractsValid !== null)}>13</span>
                      <span className="text-sm font-semibold">¿Los contratos o acuerdos están actualmente vigentes?</span>
                    </label>
                    <HelpTooltip text={"Indica si los contratos con trabajadores, voluntarios o prestadores de servicios están al día y cumplen con los requisitos legales. Si hay contratos vencidos o sin formalizar, responde \"No\". \"No aplica\" si no hay personal."} />
                  </div>
                  <SingleSelect
                    options={['Sí', 'No', 'No aplica']}
                    value={form.contractsValid}
                    onChange={(val) => updateForm('contractsValid', val)}
                    columns={3}
                    disabled={form.isCompleted}
                  />
                </div>
              </div>
            </FormBlock>

            {/* Block 6: Accounting */}
            <FormBlock
              title="6. Información contable y administrativa"
              icon={BookOpen}
              iconColor="teal"
              completed={completed.block6}
              total={2}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.hasAccountingRecords !== null)}>14</span>
                      <span className="text-sm font-semibold">¿Existen registros contables o financieros?</span>
                    </label>
                    <HelpTooltip text={"Se refiere a si la organización lleva algún control de ingresos, egresos, libros contables o estados financieros.\n\nSí: Lleva registros. Luego indica si son completos (todos los libros requeridos) o parciales (solo algunos).\n\nNo: No lleva ningún registro.\n\nEn proceso: Está implementando un sistema contable."} />
                  </div>
                  <div className="flex justify-between w-full">
                    <button
                      type="button"
                      onClick={() => !form.isCompleted && (() => {
                        updateForm('hasAccountingRecords', 'Sí')
                        if (form.accountingRecordsDetail === null) {
                          updateForm('accountingRecordsDetail', 'Completos')
                        }
                      })()}
                      disabled={form.isCompleted}
                      className={clsx(
                        "p-3 rounded-xl text-xs font-medium transition-all text-center flex items-center justify-center gap-2",
                        form.hasAccountingRecords === 'Sí'
                          ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                          : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50',
                        form.isCompleted && "opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200"
                      )}
                      style={{ width: '201px', height: '73px' }}
                    >
                      <Check className={`w-4 h-4 ${form.hasAccountingRecords === 'Sí' ? 'text-green-500' : 'text-gray-400'}`} />
                      Sí
                    </button>
                    <button
                      type="button"
                      onClick={() => !form.isCompleted && (() => {
                        updateForm('hasAccountingRecords', 'No')
                        updateForm('accountingRecordsDetail', null)
                      })()}
                      disabled={form.isCompleted}
                      className={clsx(
                        "p-3 rounded-xl text-xs font-medium transition-all text-center flex items-center justify-center gap-2",
                        form.hasAccountingRecords === 'No'
                          ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                          : 'border border-gray-200 hover:border-gray-300 hover:bg-gray-50',
                        form.isCompleted && "opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200"
                      )}
                      style={{ width: '201px', height: '73px' }}
                    >
                      <X className={`w-4 h-4 ${form.hasAccountingRecords === 'No' ? 'text-red-400' : 'text-gray-400'}`} />
                      No
                    </button>
                    <button
                      type="button"
                      onClick={() => !form.isCompleted && (() => {
                        updateForm('hasAccountingRecords', 'En proceso')
                        updateForm('accountingRecordsDetail', null)
                      })()}
                      disabled={form.isCompleted}
                      className={clsx(
                        "p-3 rounded-xl text-xs font-medium transition-all text-center",
                        form.hasAccountingRecords === 'En proceso'
                          ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                          : 'border border-gray-200 hover:border-gray-300 hover:bg-gray-50',
                        form.isCompleted && "opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200"
                      )}
                      style={{ width: '201px', height: '73px' }}
                    >
                      En proceso
                    </button>
                  </div>
                  {form.hasAccountingRecords === 'Sí' && (
                    <div className="grid grid-cols-2 gap-3 mt-3">
                      <button
                        type="button"
                        onClick={() => !form.isCompleted && updateForm('accountingRecordsDetail', 'Completos')}
                        disabled={form.isCompleted}
                        className={clsx(
                          "p-3 rounded-xl text-xs font-medium transition-all text-center",
                          form.accountingRecordsDetail === 'Completos'
                            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                            : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50',
                          form.isCompleted && "opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200"
                        )}
                        style={{ width: '151px', height: '55px' }}
                      >
                        Completos
                      </button>
                      <button
                        type="button"
                        onClick={() => !form.isCompleted && updateForm('accountingRecordsDetail', 'Parciales')}
                        disabled={form.isCompleted}
                        className={clsx(
                          "p-3 rounded-xl text-xs font-medium transition-all text-center",
                          form.accountingRecordsDetail === 'Parciales'
                            ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                            : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50',
                          form.isCompleted && "opacity-50 cursor-not-allowed hover:bg-transparent hover:border-gray-200"
                        )}
                        style={{ width: '151px', height: '55px' }}
                      >
                        Parciales
                      </button>
                    </div>
                  )}
                  {/* Warning for Q14 */}
                  {form.hasAccountingRecords === 'Sí' && (
                    <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex gap-2 text-yellow-800 text-sm animate-fade-in-up">
                      <Info className="w-5 h-5 flex-shrink-0" />
                      <span><strong>Advertencia:</strong> No debe subir archivos financieros reales; solo proporcione descripciones generales de su estado contable.</span>
                    </div>
                  )}
                </div>

                {form.orgType === 'Colectivo / iniciativa no formalizada' ? (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800 flex gap-3 animate-fade-in-up">
                    <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold mb-1">Nota sobre Colectivos:</p>
                      <p>Al ser una iniciativa no formalizada, legalmente operan como una "Asociación no inscrita". No tienen personería jurídica distinta a sus miembros. Se recomienda formalizar para proteger el patrimonio personal y acceder a financiamiento.</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3 animate-fade-in-up">
                    <div className="flex items-center justify-between">
                      <label className="flex items-center gap-2">
                        <span className={getQuestionNumberClass(form.availableDocuments.length > 0)}>15</span>
                        <span className="text-sm font-semibold">¿La organización cuenta con alguno de los siguientes documentos?</span>
                      </label>
                      <HelpTooltip text={"Documentos administrativos y legales básicos:\n\nEstatuto o acta de constitución: Documento fundacional que establece las reglas de la organización.\n\nLibros de actas: Registro de las reuniones de asamblea o directorio.\n\nEstados financieros: Balance general, estado de resultados, etc.\n\nNinguno: No posee ninguno de estos."} />
                    </div>
                    <MultiSelectChips
                      options={['Estatuto o acta de constitución', 'Libros de actas', 'Estados financieros', 'Memorias anuales', 'Plan de uso de fondos', 'Ninguno']}
                      value={form.availableDocuments}
                      onChange={(val) => updateForm('availableDocuments', val)}
                      disabled={form.isCompleted}
                    />
                  </div>
                )}
              </div>
            </FormBlock>

            {/* Block 7: Governance */}
            <FormBlock
              title="7. Gobernanza y representación"
              icon={Network}
              iconColor="indigo"
              completed={completed.block7}
              total={2}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.governanceBodies !== null)}>16</span>
                      <span className="text-sm font-semibold">¿La organización tiene órganos de gobierno definidos (asamblea, consejo, directorio, etc.)?</span>
                    </label>
                    <HelpTooltip text={"Estructuras internas como asamblea general, junta directiva, consejo directivo, etc. Estos son los espacios donde se toman decisiones colegiadas. Si no existen órganos formales, responde \"No\"."} />
                  </div>
                  <YesNoButtons
                    value={form.governanceBodies}
                    onChange={(val) => updateForm('governanceBodies', val)}
                    disabled={form.isCompleted}
                  />
                </div>

                {form.orgType === 'Colectivo / iniciativa no formalizada' ? (
                  <div className="hidden">
                    {/* Hidden for Colectivos as per requirements, removed duplicated microcopy to avoid clutter */}
                  </div>
                ) : (
                  <div className="space-y-3 animate-fade-in-up">
                    <div className="flex items-center justify-between">
                      <label className="flex items-center gap-2">
                        <span className={getQuestionNumberClass(form.hasLegalRepresentative !== null)}>17</span>
                        <span className="text-sm font-semibold">¿Existe una persona designada como representante legal?</span>
                      </label>
                      <HelpTooltip text={"El representante legal es quien tiene facultades para actuar en nombre de la organización ante terceros (bancos, SUNAT, notarías). Puede ser el presidente, director o apoderado. Si no hay designación formal, responde \"No\" o \"En trámite\"."} />
                    </div>
                    <SingleSelect
                      options={['Sí', 'No', 'En trámite']}
                      value={form.hasLegalRepresentative}
                      onChange={(val) => updateForm('hasLegalRepresentative', val)}
                      columns={3}
                      disabled={form.isCompleted}
                    />
                  </div>
                )}
              </div>
            </FormBlock>

            {/* Block 8: Intangibles */}
            <FormBlock
              title="8. Uso de intangibles y datos"
              icon={Lightbulb}
              iconColor="pink"
              completed={completed.block8}
              total={1}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.intangibleAssets.length > 0)}>18</span>
                      <span className="text-sm font-semibold">¿La organización utiliza alguno de los siguientes?</span>
                    </label>
                    <HelpTooltip text={"Recursos intangibles que pueden requerir protección legal:\n\nSoftware propio: Programas desarrollados internamente (posible propiedad intelectual).\n\nSoftware de terceros: Aplicaciones licenciadas (ej. Office, ERP) que implican cumplir términos de uso.\n\nBases de datos de usuarios: Información personal de beneficiarios, clientes o colaboradores (aplica protección de datos).\n\nMarca o símbolos distintivos: Nombres, logotipos, lemas (propiedad industrial).\n\nNinguno: No utiliza estos activos."} />
                  </div>
                  <MultiSelectChips
                    options={['Software propio', 'Software de terceros', 'Bases de datos de usuarios', 'Marca o símbolos distintivos', 'Contenido con derechos de autor', 'Ninguno']}
                    value={form.intangibleAssets}
                    onChange={(val) => updateForm('intangibleAssets', val)}
                    disabled={form.isCompleted}
                  />
                  {/* Warning for Data Protection */
                    form.intangibleAssets.includes('Bases de datos de usuarios') && (
                      <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2 text-red-700 text-sm animate-fade-in-up">
                        <Info className="w-5 h-5 flex-shrink-0" />
                        <span><strong>Aviso de Privacidad:</strong> El sistema ha detectado el manejo de datos personales. Recuerde cumplir con la Ley de Protección de Datos Personales. Este sistema no procesa bases de datos sensibles.</span>
                      </div>
                    )}
                </div>
              </div>
            </FormBlock>

            {/* Block 9: Tool Specific */}
            <FormBlock
              title="9. Detalle de la Solicitud"
              icon={ClipboardList}
              iconColor="red"
              completed={completed.block9}
              total={getBlock9Total()}
            >
              <div className="space-y-6">

                {form.tool === 'evaluation' && (
                  <>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.toolSpecific.evaluationGoals?.length)}>19</span>
                          <span className="text-sm font-semibold">¿Cuáles son sus objetivos principales?</span>
                        </label>
                        <HelpTooltip text={"Selecciona los propósitos de esta evaluación legal:\n\n- **Formalización:** Constituir legalmente la organización o regularizar su situación.\n\n- **Gestión de riesgos:** Identificar posibles problemas legales y prevenirlos.\n\n- **Preparación para auditoría:** Alistarse para una revisión externa o fiscalización.\n\n- **Mejora de gobernanza:** Fortalecer la estructura interna y la toma de decisiones.\n\n- **Resolver un conflicto actual:** La organización enfrenta un problema legal en curso (ej. disputa laboral, fiscalización, controversia con terceros).\n\n**⚠️ Importante:** Si seleccionas \"Resolver un conflicto actual\", el sistema activará un protocolo especial y podría derivar tu caso a un asesor humano, ya que este tipo de consultas requieren atención personalizada y no pueden resolverse completamente con recomendaciones automatizadas."} />
                      </div>
                      <MultiSelectChips
                        options={[
                          'Formalización',
                          'Gestión de riesgos',
                          'Preparación para auditoría',
                          'Mejora de gobernanza',
                          'Resolver un conflicto actual'
                        ]}
                        value={form.toolSpecific.evaluationGoals || []}
                        onChange={(val) => updateToolSpecific('evaluationGoals', val)}
                        disabled={form.isCompleted}
                      />
                      {/* Warning for Conflict */}
                      {form.toolSpecific.evaluationGoals?.includes('Resolver un conflicto actual') && (
                        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2 text-red-700 text-sm">
                          <Info className="w-5 h-5 flex-shrink-0" />
                          <span><strong>Aviso importante:</strong> El sistema no realiza mediación ni defensa en litigios activos. Su caso podría ser derivado a un especialista humano.</span>
                        </div>
                      )}
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.toolSpecific.legalAreas?.length)}>20</span>
                          <span className="text-sm font-semibold">¿Qué áreas legales le preocupan más?</span>
                        </label>
                        <HelpTooltip text={"Indica los temas jurídicos prioritarios:\n\nTributario: Impuestos, RUC, obligaciones fiscales.\n\nLaboral: Contratación, planilla, derechos de trabajadores.\n\nCorporativo: Estatutos, asambleas, representación legal.\n\nPropiedad Intelectual: Registro de marcas, derechos de autor, patentes.\n\nProtección de Datos: Manejo de información personal y cumplimiento de la ley de datos."} />
                      </div>
                      <MultiSelectChips
                        options={['Tributario', 'Cooperación internacional (APCI)', 'Laboral', 'Propiedad intelectual', 'Contratos', 'Formalización', 'Gobernanza', 'Protección de Datos']}
                        value={form.toolSpecific.legalAreas || []}
                        onChange={(val) => updateToolSpecific('legalAreas', val)}
                        disabled={form.isCompleted}
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.toolSpecific.urgency)}>21</span>
                          <span className="text-sm font-semibold">¿Con qué rapidez necesita una respuesta u orientación?</span>
                        </label>
                        <HelpTooltip text={"Define el nivel de urgencia para recibir orientación:\n\n- **Inmediata (tengo un plazo venciendo):** Existe una fecha límite próxima (ej. vence un plazo para declarar, presentar un documento, responder a un requerimiento). Esta opción activa una alerta prioritaria y se te preguntará si has recibido una notificación formal de SUNAT, APCI u otra entidad.\n\n- **Semanal (planeamiento):** Necesitas orientación en el corto plazo para tomar decisiones, pero sin una fecha límite apremiante.\n\n- **Informativa (estoy explorando):** Estás recopilando información general para conocimiento futuro, sin presión de tiempo.\n\n**Importante:** Si seleccionas \"Inmediata\", el sistema priorizará tu consulta y aplicará un protocolo de urgencia para evaluar si requieres derivación inmediata a un especialista."} />
                      </div>
                      <SingleSelect
                        options={[
                          'Inmediata (tengo un plazo venciendo)',
                          'Semanal (planeamiento)',
                          'Informativa (estoy explorando)'
                        ]}
                        value={form.toolSpecific.urgency || null}
                        onChange={(val) => updateToolSpecific('urgency', val)}
                        disabled={form.isCompleted}
                      />
                      {/* Urgent Case Follow-up */}
                      {form.toolSpecific.urgency === 'Inmediata (tengo un plazo venciendo)' && (
                        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg space-y-3 animate-fade-in-up">
                          <p className="text-red-800 font-semibold text-sm">¿Ha recibido una notificación formal (SUNAT/APCI) u otra entidad?</p>
                          <YesNoButtons
                            value={form.toolSpecific.hasReceivedNotification ?? null}
                            onChange={(val) => updateToolSpecific('hasReceivedNotification', val)}
                            disabled={form.isCompleted}
                          />
                          {form.toolSpecific.hasReceivedNotification === true && (
                            <p className="text-red-700 text-xs italic">Se ha activado la derivación prioritaria a un especialista humano.</p>
                          )}
                        </div>
                      )}
                    </div>
                  </>
                )}

                {form.tool === 'compliance' && (
                  <>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.toolSpecific.complianceGoal)}>19</span>
                          <span className="text-sm font-semibold">Objetivo de cumplimiento</span>
                        </label>
                      </div>
                      <SingleSelect
                        options={['Formalizar la organización', 'Registrar en APCI', 'Cumplir obligaciones SUNAT', 'Regularizar situación laboral', 'Obtener exoneración de IR', 'Inscribirse como receptora de donaciones']}
                        value={form.toolSpecific.complianceGoal || null}
                        onChange={(val) => updateToolSpecific('complianceGoal', val)}
                        disabled={form.isCompleted}
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.toolSpecific.timeline)}>20</span>
                          <span className="text-sm font-semibold">Plazo estimado</span>
                        </label>
                      </div>
                      <SingleSelect
                        options={['Lo antes posible', '1-3 meses', '3-6 meses', 'Sin prisa específica']}
                        value={form.toolSpecific.timeline || null}
                        onChange={(val) => updateToolSpecific('timeline', val)}
                        disabled={form.isCompleted}
                      />
                    </div>
                  </>
                )}

                {form.tool === 'query' && (
                  <>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.toolSpecific.queryArea)}>19</span>
                          <span className="text-sm font-semibold">Área de la consulta</span>
                        </label>
                      </div>
                      <SingleSelect
                        options={['Formalización y registros', 'Tributación', 'Contratación de personal', 'Cooperación internacional', 'Propiedad intelectual', 'Donaciones', 'Gobernanza', 'Otro']}
                        value={form.toolSpecific.queryArea || null}
                        onChange={(val) => updateToolSpecific('queryArea', val)}
                        disabled={form.isCompleted}
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.toolSpecific.specificQuestion)}>20</span>
                          <span className="text-sm font-semibold">Detalle su consulta específica</span>
                        </label>
                      </div>
                      <textarea
                        className={clsx(
                          "w-full rounded-xl border-gray-200 text-sm py-3 px-4 min-h-[100px]",
                          form.isCompleted && "opacity-50 cursor-not-allowed"
                        )}
                        placeholder="Escriba aquí su consulta..."
                        value={form.toolSpecific.specificQuestion || ''}
                        onChange={(e) => updateToolSpecific('specificQuestion', e.target.value)}
                        disabled={form.isCompleted}
                      />
                    </div>
                  </>
                )}
              </div>
            </FormBlock>

            {/* Confirmation Block - ONLY SHOW WHEN FULLY ANSWERED AND NOT ALREADY COMPLETED */}
            {completedQuestions === totalQuestions && !form.isCompleted && (
              <section className="bg-yellow-50 border-2 border-yellow-200 rounded-2xl p-8 transition-all animate-fade-in-up">
                <div className="flex items-start gap-4 mb-6">
                  <Info className="w-8 h-8 text-yellow-600 flex-shrink-0" />
                  <div>
                    <h3 className="font-bold text-lg mb-2">Confirmación y Uso de Información</h3>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      Al completar esta ficha, la organización reconoce que la información brindada será utilizada
                      para generar un diagnóstico legal preliminar. Este documento no reemplaza la asesoría legal
                      especializada pero sirve como línea base de cumplimiento en el contexto peruano.
                    </p>
                  </div>
                </div>
                <div className="flex flex-col items-center gap-4">
                  <p className="font-bold text-sm">¿Desea continuar con la generación de su ficha?</p>
                  <div className="flex gap-4 w-full max-w-sm">
                    <button
                      onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                      className="flex-1 py-4 bg-white border border-gray-200 rounded-xl font-bold hover:bg-gray-50 text-gray-700"
                    >
                      No, revisar
                    </button>
                    <button
                      onClick={() => setForm(prev => ({ ...prev, hasConfirmed: true }))}
                      disabled={form.hasConfirmed}
                      className={clsx(
                        "flex-1 py-4 rounded-xl font-bold shadow-lg transition-all",
                        form.hasConfirmed
                          ? "bg-green-500 text-white cursor-default"
                          : "bg-yellow-400 text-white shadow-yellow-200 hover:bg-yellow-500"
                      )}
                    >
                      {form.hasConfirmed ? "¡Confirmado!" : "Sí, continuar"}
                    </button>
                  </div>
                </div>
              </section>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex flex-col items-center gap-4 pb-20">
          <button
            onClick={handleSubmit}
            className={`w-full max-w-md py-6 rounded-2xl flex flex-col items-center justify-center gap-1 transition-all ${completedQuestions === totalQuestions && form.hasConfirmed && !isSubmitting && !form.isCompleted
              ? 'bg-yellow-400 text-white cursor-pointer hover:bg-yellow-500'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            disabled={completedQuestions !== totalQuestions || !form.hasConfirmed || isSubmitting || form.isCompleted}
          >

            <div className="flex items-center gap-2">
              {(!form.hasConfirmed || completedQuestions !== totalQuestions) && !form.isCompleted && (
                <Lock className="w-5 h-5" />
              )}
              {form.isCompleted && (
                <Check className="w-5 h-5" />
              )}
              <span className="text-lg font-bold">
                {isSubmitting
                  ? 'Enviando...'
                  : form.isCompleted
                    ? 'Ficha Completada'
                    : 'Completar Ficha'}
              </span>
            </div>
            {!form.isCompleted && (
              <span className="text-xs uppercase tracking-widest font-bold">
                {completedQuestions === totalQuestions
                  ? (form.hasConfirmed ? 'Listo para generar' : 'Confirme para continuar')
                  : `Faltan ${totalQuestions - completedQuestions} preguntas por responder`}
              </span>
            )}
          </button>
          <p className="text-xs text-gray-400 uppercase font-bold tracking-widest text-center px-8">
            {form.isCompleted
              ? "La ficha ha sido enviada correctamente y no puede ser modificada"
              : "Debes completar todos los campos obligatorios para finalizar"}
          </p>
        </div>
      </main>
    </div>
  )
}