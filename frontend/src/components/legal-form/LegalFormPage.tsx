import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { intakeApi, IntakeRequest } from '../../shared/services/api'
import { Check, ChevronLeft, Fingerprint, Gavel, Banknote, Users, BookOpen, Network, Lightbulb, Info, Lock, X, Building2, Landmark, Home, LucideIcon, Globe, ClipboardList } from 'lucide-react'
import { OrganizationCard } from './OrganizationCard'
import { ProgressTracker } from './ProgressTracker'
import { FormBlock } from './FormBlock'
import { YesNoButtons, SingleSelect, MultiSelectChips } from './FormInputs'
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
  seeksProfits: boolean | null

  // Block 2: Formalization
  hasLegalStatus: string | null
  ruc: string | null
  additionalRegistries: string[]

  // Block 3: Income
  handlesMoney: boolean | null
  incomeSources: string[]
  receivesForeignFunds: boolean | null

  // Block 4: International Cooperation
  receivesInternationalCooperation: boolean | null
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

const MOCK_ORGANIZATIONS: Organization[] = [
  { id: '1', name: 'AIESEC', role: 'Administrador', progress: 38, color: '#B3994C', icon: Building2 },
  { id: '2', name: 'CENDES', role: 'Editor', progress: 38, color: '#8F86A3', icon: Landmark },
  { id: '3', name: 'LANKI', role: 'Lector', progress: 10, color: '#D7D100', icon: Home },
]

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
  receivesInternationalCooperation: null,
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
  if (form.receivesInternationalCooperation !== null) b4++
  if (form.receivesInternationalCooperation === true && form.apciStatus) b4++
  if (form.receivesInternationalCooperation === false) b4++
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
    if (form.toolSpecific.urgency) b9++
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
  const [selectedOrg, setSelectedOrg] = useState<string>('1')
  const [organizations, setOrganizations] = useState<Organization[]>(MOCK_ORGANIZATIONS)

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
    const updatedOrgs = MOCK_ORGANIZATIONS.map(org => {
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
    if (form.receivesInternationalCooperation !== null) block4++
    if (form.receivesInternationalCooperation === true && form.apciStatus) block4++
    // If NO, apciStatus is not needed, so we count it as complete or we have 1 question total.
    // Let's adjust logic: 
    // If receivesIntlCoop is NULL -> 0/1 (or 0/2)
    // If receivesIntlCoop is FALSE -> 1/1 (completed)
    // If receivesIntlCoop is TRUE -> 1/2. If apciStatus set -> 2/2.
    // However, BLOCKS array defines 'total'. We need dynamic total or fixed max. 
    // Current design uses fixed total. Let's assume max questions = 2.
    // If NO, we might need to "fake" the second point or handle dynamic total in BLOCKS. 
    // Looking at BLOCKS definition, it uses `completed` and `total`.
    // Let's stick to fixed total of 2 for simplicity, and if NO, we grant 2 points? 
    // Or better: Max 2.
    // If NO -> block4 = 2 (auto-complete second part)
    if (form.receivesInternationalCooperation === false) block4++

    // Block 5 (Old 4)
    if (form.hiringModalities.length > 0) block5++
    if (form.contractsValid !== null) block5++

    // Block 6 (Old 5)
    if (form.hasAccountingRecords !== null) block6++
    if (form.availableDocuments.length > 0) block6++

    // Block 7 (Old 6)
    if (form.governanceBodies !== null) block7++
    if (form.hasLegalRepresentative !== null) block7++

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

  const handleSubmit = async () => {
    if (completedQuestions !== totalQuestions || !form.hasConfirmed) return

    setIsSubmitting(true)

    // Mark as completed before submitting
    const completedForm = { ...form, isCompleted: true }
    setForm(completedForm)
    try {
      localStorage.setItem(getStorageKey(selectedOrg), JSON.stringify(completedForm))

      // Map FormState to IntakeRequest
      const payload: IntakeRequest = {
        tool: form.tool,
        legalProfile: {
          orgType: form.orgType || '',
          orgTypeOther: form.orgTypeOther,
          orgPurpose: form.orgPurpose || '',
          orgPurposeOther: form.orgPurposeOther,
          seeksProfits: form.seeksProfits,

          hasLegalStatus: form.hasLegalStatus,
          rucStatus: form.ruc,
          specialRegistries: form.additionalRegistries,

          handlesMoney: form.handlesMoney,
          receivesForeignFunds: form.receivesForeignFunds,
          incomeSources: form.incomeSources,

          receivesInternationalCooperation: form.receivesInternationalCooperation,
          apciStatus: form.apciStatus,

          hiringModalities: form.hiringModalities,
          contractsValid: form.contractsValid,

          accountingRecords: form.hasAccountingRecords,
          accountingRecordsDetail: form.accountingRecordsDetail,
          availableDocuments: form.availableDocuments,

          hasGovernanceBodies: form.governanceBodies,
          hasLegalRepresentative: form.hasLegalRepresentative,

          intangibleAssets: form.intangibleAssets
        },
        toolSpecific: form.toolSpecific
      }

      await intakeApi.submit(payload)

      // Clear persistence on success (optional, or keep it as completed record)
      localStorage.removeItem(getStorageKey(selectedOrg))

      // Navigate to success or chat page
      navigate('/chat')

    } catch (error) {
      console.error('Error submitting intake:', error)
      // Could add toast notification here
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
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ChevronLeft className="w-5 h-5" />
            <div className="flex items-center gap-2">
              <div className="bg-yellow-400 w-5 h-5 transform rotate-45 rounded-sm" />
              <span className="font-bold text-lg">Ficha Legal Mínima</span>
            </div>
          </button>

          <div className="flex items-center gap-3">
            <img
              src="https://causante.org/wp-content/uploads/2025/03/causante-logo.webp"
              alt="GPT Legal"
              className="h-6"
            />
            <span className="font-semibold text-gray-900">GPT Legal</span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
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
                      <span className="text-sm font-semibold">¿Con cuál de las siguientes opciones se identifica mejor?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
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
                      <option value="ONG">ONG</option>
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
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
                      <span className={getQuestionNumberClass(form.seeksProfits !== null)}>3</span>
                      <span className="text-sm font-semibold">¿La organización busca generar ganancias para repartir entre sus miembros?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <YesNoButtons
                    value={form.seeksProfits}
                    onChange={(val) => updateForm('seeksProfits', val)}
                    disabled={form.isCompleted}
                  />
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
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
                      <span className="text-sm font-semibold">¿La organización está inscrita en algún registro especial?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <MultiSelectChips
                    options={['APCI', 'Exonerada de Impuesto a la renta', 'Ninguno']}
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <MultiSelectChips
                    options={['Donaciones', 'Venta de servicios o productos', 'Fondos públicos', 'Fondos privados', 'Aún no recibe ingresos']}
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
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.receivesInternationalCooperation !== null)}>10</span>
                      <span className="text-sm font-semibold">¿Recibe cooperación internacional?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <YesNoButtons
                    value={form.receivesInternationalCooperation}
                    onChange={(val) => {
                      updateForm('receivesInternationalCooperation', val)
                      if (val === false) updateForm('apciStatus', 'No aplica')
                    }}
                    disabled={form.isCompleted}
                  />
                </div>

                {form.receivesInternationalCooperation && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <label className="flex items-center gap-2">
                        <span className={getQuestionNumberClass(!!form.apciStatus)}>11</span>
                        <span className="text-sm font-semibold">¿Cuál es su estado en APCI?</span>
                      </label>
                      <Lightbulb className="w-4 h-4 text-yellow-400" />
                    </div>
                    <SingleSelect
                      options={['Registrado', 'Necesita', 'No aplica']}
                      value={form.apciStatus}
                      onChange={(val) => updateForm('apciStatus', val)}
                      columns={3}
                      disabled={form.isCompleted}
                    />
                  </div>
                )}
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <MultiSelectChips
                    options={['Planilla (DL 728)', 'Locación de Servicios', 'Volutariado', 'Practicantes', 'Ninguno']}
                    value={form.hiringModalities}
                    onChange={(val) => updateForm('hiringModalities', val)}
                    disabled={form.isCompleted}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center justify-between">
                      <label className="flex items-center gap-2">
                        <span className={getQuestionNumberClass(form.contractsValid !== null)}>13</span>
                        <span className="text-sm font-semibold">¿Los contratos o acuerdos están actualmente vigentes?</span>
                      </label>
                      <Lightbulb className="w-4 h-4 text-yellow-400" />
                    </div>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
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
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.availableDocuments.length > 0)}>15</span>
                      <span className="text-sm font-semibold">¿La organización cuenta con alguno de los siguientes documentos?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <MultiSelectChips
                    options={['Estatuto o acta de constitución', 'Libros de actas', 'Estados financieros', 'Ninguno']}
                    value={form.availableDocuments}
                    onChange={(val) => updateForm('availableDocuments', val)}
                    disabled={form.isCompleted}
                  />
                </div>
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <YesNoButtons
                    value={form.governanceBodies}
                    onChange={(val) => updateForm('governanceBodies', val)}
                    disabled={form.isCompleted}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.hasLegalRepresentative !== null)}>17</span>
                      <span className="text-sm font-semibold">¿Existe una persona designada como representante legal?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <SingleSelect
                    options={['Sí', 'No', 'En trámite']}
                    value={form.hasLegalRepresentative}
                    onChange={(val) => updateForm('hasLegalRepresentative', val)}
                    columns={3}
                    disabled={form.isCompleted}
                  />
                </div>
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
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <MultiSelectChips
                    options={['Software propio', 'Software de terceros', 'Bases de datos de usuarios', 'Marca o símbolos distintivos', 'Ninguno']}
                    value={form.intangibleAssets}
                    onChange={(val) => updateForm('intangibleAssets', val)}
                    disabled={form.isCompleted}
                  />
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
                      </div>
                      <MultiSelectChips
                        options={['Formalización', 'Gestión de riesgos', 'Preparación para auditoría', 'Mejora de gobernanza']}
                        value={form.toolSpecific.evaluationGoals || []}
                        onChange={(val) => updateToolSpecific('evaluationGoals', val)}
                        disabled={form.isCompleted}
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.toolSpecific.legalAreas?.length)}>20</span>
                          <span className="text-sm font-semibold">¿Qué áreas legales le preocupan más?</span>
                        </label>
                      </div>
                      <MultiSelectChips
                        options={['Tributario', 'Laboral', 'Corporativo', 'Propiedad Intelectual', 'Protección de Datos']}
                        value={form.toolSpecific.legalAreas || []}
                        onChange={(val) => updateToolSpecific('legalAreas', val)}
                        disabled={form.isCompleted}
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <span className={getQuestionNumberClass(!!form.toolSpecific.urgency)}>21</span>
                          <span className="text-sm font-semibold">¿Nivel de urgencia?</span>
                        </label>
                      </div>
                      <SingleSelect
                        options={['Alta', 'Media', 'Baja']}
                        value={form.toolSpecific.urgency || null}
                        onChange={(val) => updateToolSpecific('urgency', val)}
                        disabled={form.isCompleted}
                      />
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
                      <input
                        type="text"
                        className={clsx(
                          "w-full rounded-xl border-gray-200 text-sm py-3 px-4",
                          form.isCompleted && "opacity-50 cursor-not-allowed"
                        )}
                        placeholder="Ej. Cumplir normativa de protección de datos"
                        value={form.toolSpecific.complianceGoal || ''}
                        onChange={(e) => updateToolSpecific('complianceGoal', e.target.value)}
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
                        options={['Inmediato', '1-3 meses', '3-6 meses', '+6 meses']}
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
                        options={['Tributario', 'Laboral', 'Corporativo', 'Contratos', 'Otros']}
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