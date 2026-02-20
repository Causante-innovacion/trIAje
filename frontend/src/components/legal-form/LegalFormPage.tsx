import { useState, useEffect, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { evaluationApi } from '../../shared/services/api'
import { mapBackendToProjectEvaluation, BackendEvaluationResponse } from '../../types/evaluation.types'
import { useChatStore } from '../../stores/chatStore'
import {
  Check, ChevronLeft, ChevronRight, Fingerprint, Gavel, Banknote, Users,
  BookOpen, Network, Lightbulb, Info, Lock, Building2, LucideIcon,
  Globe, ClipboardList,
} from 'lucide-react'
import { OrganizationCard } from './OrganizationCard'
import { ProgressTracker } from './ProgressTracker'
import { FormBlock } from './FormBlock'
import { YesNoButtons, SingleSelect, MultiSelectChips } from './FormInputs'
import { HelpTooltip } from './HelpTooltip'
import clsx from 'clsx'

// ─── Types ───────────────────────────────────────────────────────────────────

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
  apciStatus: string | null
  // Block 5: HR
  hiringModalities: string[]
  contractsValid: string | null
  // Block 6: Accounting
  hasAccountingRecords: string | null
  accountingRecordsDetail: string | null
  availableDocuments: string[]
  // Block 7: Governance
  governanceBodies: boolean | null
  hasLegalRepresentative: string | null
  // Block 8: Intangibles
  intangibleAssets: string[]
  // Tool Specific
  tool: 'evaluation' | 'compliance' | 'query'
  toolSpecific: {
    evaluationGoals?: string[]
    legalAreas?: string[]
    urgency?: string
    hasReceivedNotification?: boolean | null
    complianceGoal?: string
    timeline?: string
    queryArea?: string
    specificQuestion?: string
  }
  isCompleted: boolean
  hasConfirmed: boolean
}

// ─── Constants ───────────────────────────────────────────────────────────────

const DEFAULT_ORGANIZATIONS: Organization[] = [
  { id: '1', name: 'Organización 1', role: 'Ejecutor principal', progress: 0, color: '#B3994C', icon: Building2 },
]
const ORG_COLORS = ['#B3994C', '#8F86A3', '#D7D100']

const initialFormState: FormState = {
  orgType: null, orgTypeOther: '', orgPurpose: null, orgPurposeOther: '',
  seeksProfits: null, hasLegalStatus: null, ruc: null, additionalRegistries: [],
  handlesMoney: null, incomeSources: [], receivesForeignFunds: null,
  apciStatus: null, hiringModalities: [], contractsValid: null,
  hasAccountingRecords: null, accountingRecordsDetail: null, availableDocuments: [],
  governanceBodies: null, hasLegalRepresentative: null, intangibleAssets: [],
  tool: 'evaluation', toolSpecific: {}, isCompleted: false, hasConfirmed: false,
}

const getStorageKey = (orgId: string) => `gpt_legal_form_progress_${orgId}`

// ─── Progress Calculation ────────────────────────────────────────────────────

const calculateProgress = (form: FormState) => {
  let completedCount = 0
  let totalCount = 0
  const add = (c: number, t: number) => { completedCount += c; totalCount += t }

  let b1 = 0; if (form.orgType) b1++; if (form.orgPurpose) b1++; if (form.seeksProfits !== null) b1++; add(b1, 3)
  let b2 = 0; if (form.hasLegalStatus) b2++; if (form.ruc) b2++; if (form.additionalRegistries.length > 0) b2++; add(b2, 3)
  let b3 = 0; if (form.handlesMoney !== null) b3++; if (form.incomeSources.length > 0) b3++; if (form.receivesForeignFunds !== null) b3++; add(b3, 3)
  let b4 = 0; if (form.receivesForeignFunds === true && form.apciStatus) b4 = 2; if (form.receivesForeignFunds === false) b4 = 2; add(b4, 2)
  let b5 = 0; if (form.hiringModalities.length > 0) b5++; if (form.contractsValid !== null) b5++; add(b5, 2)
  let b6 = 0; if (form.hasAccountingRecords !== null) b6++; if (form.availableDocuments.length > 0) b6++; add(b6, 2)
  let b7 = 0; if (form.governanceBodies !== null) b7++; if (form.hasLegalRepresentative !== null) b7++; add(b7, 2)
  let b8 = 0; if (form.intangibleAssets.length > 0) b8++; add(b8, 1)
  let b9 = 0
  if (form.tool === 'evaluation') {
    if (form.toolSpecific.evaluationGoals?.length) b9++; if (form.toolSpecific.legalAreas?.length) b9++; if (form.toolSpecific.urgency) b9++; add(b9, 3)
  } else if (form.tool === 'compliance') {
    if (form.toolSpecific.complianceGoal) b9++; if (form.toolSpecific.timeline) b9++; add(b9, 2)
  } else if (form.tool === 'query') {
    if (form.toolSpecific.queryArea) b9++; if (form.toolSpecific.specificQuestion) b9++; add(b9, 2)
  } else { add(0, 0) }
  let pct = Math.round((completedCount / totalCount) * 100)
  if (pct === 100 && !form.isCompleted) pct = 99
  return pct
}

// ─── Question Number Badge ──────────────────────────────────────────────────

function QNum({ num, done }: { num: number; done: boolean }) {
  return (
    <span
      className={clsx(
        'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0',
        done ? 'bg-causante-ocre text-white' : 'bg-gray-200 text-gray-500'
      )}
    >
      {num}
    </span>
  )
}

// ─── Main Component ──────────────────────────────────────────────────────────

export function LegalFormPage() {
  const navigate = useNavigate()
  const extractedPlan = useChatStore((s) => s.extractedPlan)

  // ── Organizations ──
  const baseOrganizations = useMemo<Organization[]>(() => {
    if (extractedPlan && extractedPlan.raw_extractions.team_and_partners.length > 0) {
      return extractedPlan.raw_extractions.team_and_partners.map((org, i) => ({
        id: String(i + 1), name: org.name,
        role: org.role_raw || 'Ejecutor principal', progress: 0,
        color: ORG_COLORS[i % ORG_COLORS.length], icon: Building2,
      }))
    }
    return DEFAULT_ORGANIZATIONS
  }, [extractedPlan])

  const [selectedOrg, setSelectedOrg] = useState<string>('1')
  const [organizations, setOrganizations] = useState<Organization[]>(baseOrganizations)
  const [form, setForm] = useState<FormState>(initialFormState)
  const [currentBlock, setCurrentBlock] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // ── Storage ──
  useEffect(() => {
    try {
      const oldKey = 'gpt_legal_form_progress'
      const oldData = localStorage.getItem(oldKey)
      if (oldData && !localStorage.getItem(getStorageKey('1'))) {
        localStorage.setItem(getStorageKey('1'), oldData)
        localStorage.removeItem(oldKey)
      }
    } catch (e) { console.error('Failed to migrate data', e) }
  }, [])

  useEffect(() => {
    try {
      const saved = localStorage.getItem(getStorageKey(selectedOrg))
      setForm(saved ? JSON.parse(saved) : initialFormState)
    } catch { setForm(initialFormState) }
  }, [selectedOrg])

  useEffect(() => {
    const updatedOrgs = baseOrganizations.map(org => {
      if (org.id === selectedOrg) return { ...org, progress: calculateProgress(form) }
      try {
        const saved = localStorage.getItem(getStorageKey(org.id))
        if (saved) return { ...org, progress: calculateProgress(JSON.parse(saved)) }
      } catch { /* ignore */ }
      return { ...org, progress: 0 }
    })
    setOrganizations(updatedOrgs)
  }, [form, selectedOrg])

  useEffect(() => {
    try { localStorage.setItem(getStorageKey(selectedOrg), JSON.stringify(form)) } catch { /* ignore */ }
  }, [form])

  // ── Completed counts per block ──
  const calculateCompleted = useCallback(() => {
    let block1 = 0, block2 = 0, block3 = 0, block4 = 0, block5 = 0, block6 = 0, block7 = 0, block8 = 0, block9 = 0
    if (form.orgType) block1++; if (form.orgPurpose) block1++; if (form.seeksProfits !== null) block1++
    if (form.hasLegalStatus) block2++; if (form.ruc) block2++; if (form.additionalRegistries.length > 0) block2++
    if (form.handlesMoney !== null) block3++; if (form.incomeSources.length > 0) block3++; if (form.receivesForeignFunds !== null) block3++
    if (form.receivesForeignFunds === true && form.apciStatus) block4 = 2
    if (form.receivesForeignFunds === false) block4 = 2
    if (form.hiringModalities.length > 0) block5++; if (form.contractsValid !== null) block5++
    if (form.hasAccountingRecords !== null) block6++
    if (form.availableDocuments.length > 0 || form.orgType === 'Colectivo / iniciativa no formalizada') block6++
    if (form.governanceBodies !== null) block7++
    if (form.hasLegalRepresentative !== null || form.orgType === 'Colectivo / iniciativa no formalizada') block7++
    if (form.intangibleAssets.length > 0) block8++
    if (form.tool === 'evaluation') {
      if (form.toolSpecific.evaluationGoals?.length) block9++
      if (form.toolSpecific.legalAreas?.length) block9++
      if (form.toolSpecific.urgency) block9++
    } else if (form.tool === 'compliance') {
      if (form.toolSpecific.complianceGoal) block9++; if (form.toolSpecific.timeline) block9++
    } else if (form.tool === 'query') {
      if (form.toolSpecific.queryArea) block9++; if (form.toolSpecific.specificQuestion) block9++
    }
    return { block1, block2, block3, block4, block5, block6, block7, block8, block9 }
  }, [form])

  const completed = calculateCompleted()
  const getBlock9Total = () => form.tool === 'evaluation' ? 3 : 2

  const BLOCKS = [
    { id: 'identity', name: 'Identidad', icon: Fingerprint, color: 'blue', completed: completed.block1, total: 3 },
    { id: 'formalization', name: 'Formalización', icon: Gavel, color: 'purple', completed: completed.block2, total: 3 },
    { id: 'income', name: 'Ingresos', icon: Banknote, color: 'green', completed: completed.block3, total: 3 },
    { id: 'intl', name: 'Coop. Int.', icon: Globe, color: 'cyan', completed: completed.block4, total: 2 },
    { id: 'hr', name: 'RRHH', icon: Users, color: 'orange', completed: completed.block5, total: 2 },
    { id: 'accounting', name: 'Contable', icon: BookOpen, color: 'teal', completed: completed.block6, total: 2 },
    { id: 'governance', name: 'Gobernanza', icon: Network, color: 'indigo', completed: completed.block7, total: 2 },
    { id: 'intangibles', name: 'Intangibles', icon: Lightbulb, color: 'pink', completed: completed.block8, total: 1 },
    { id: 'tool', name: 'Solicitud', icon: ClipboardList, color: 'red', completed: completed.block9, total: getBlock9Total() },
  ]

  const totalQuestions = BLOCKS.reduce((a, b) => a + b.total, 0)
  const completedQuestions = BLOCKS.reduce((a, b) => a + b.completed, 0)

  // ── Form helpers ──
  const updateForm = <K extends keyof FormState>(field: K, value: FormState[K]) => setForm(p => ({ ...p, [field]: value }))
  const updateToolSpecific = (field: string, value: any) => setForm(p => ({ ...p, toolSpecific: { ...p.toolSpecific, [field]: value } }))

  // ── Navigation ──
  const isLastBlock = currentBlock === BLOCKS.length - 1

  const goNext = () => {
    if (currentBlock < BLOCKS.length - 1) {
      let next = currentBlock + 1
      // Skip block 3 (international cooperation) if doesn't apply
      if (next === 3 && form.receivesForeignFunds === false) next++
      setCurrentBlock(Math.min(next, BLOCKS.length - 1))
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const goPrev = () => {
    if (currentBlock > 0) {
      let prev = currentBlock - 1
      if (prev === 3 && form.receivesForeignFunds === false) prev--
      setCurrentBlock(Math.max(prev, 0))
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  // ── Submit ──
  const buildLegalProfile = (f: FormState) => ({
    identity: {
      org_type: f.orgType || null, org_type_other: f.orgTypeOther || null,
      org_purpose: f.orgPurpose || null, org_purpose_other: f.orgPurposeOther || null,
      seeks_profits: f.seeksProfits === 'Con fines de lucro (puede haber reparto)' ? true : (f.seeksProfits === 'Sin fines de lucro (no se reparten excedentes)' ? false : null),
    },
    formalization: { has_legal_status: f.hasLegalStatus, ruc_status: f.ruc, special_registries: f.additionalRegistries },
    income: { handles_money: f.handlesMoney, receives_foreign_funds: f.receivesForeignFunds, income_sources: f.incomeSources },
    international_cooperation: { receives_international_cooperation: f.receivesForeignFunds, apci_status: f.apciStatus },
    human_resources: { hiring_modalities: f.hiringModalities, contracts_valid: f.contractsValid },
    accounting: {
      has_accounting_records: f.hasAccountingRecords === 'Sí' && f.accountingRecordsDetail ? `Sí, ${f.accountingRecordsDetail.toLowerCase()}` : f.hasAccountingRecords,
      available_documents: f.availableDocuments,
    },
    governance: { has_governance_bodies: f.governanceBodies, has_legal_representative: f.hasLegalRepresentative },
    intangibles: { intangible_assets: f.intangibleAssets },
  })

  const buildToolSpecific = (f: FormState) => {
    if (f.tool === 'evaluation') return { evaluation: { evaluation_goals: f.toolSpecific.evaluationGoals || [], legal_areas: f.toolSpecific.legalAreas || [], urgency: f.toolSpecific.urgency || null, has_received_notification: f.toolSpecific.hasReceivedNotification } }
    if (f.tool === 'compliance') return { compliance: { compliance_goal: f.toolSpecific.complianceGoal || null, timeline: f.toolSpecific.timeline || null } }
    return { query: { query_area: f.toolSpecific.queryArea || null, specific_question: f.toolSpecific.specificQuestion || null } }
  }

  const handleSubmit = async () => {
    if (completedQuestions !== totalQuestions || !form.hasConfirmed) return
    setIsSubmitting(true)
    const completedForm = { ...form, isCompleted: true }
    setForm(completedForm)
    try {
      localStorage.setItem(getStorageKey(selectedOrg), JSON.stringify(completedForm))
      const allOrgsCompleted = organizations.every(org => org.id === selectedOrg ? true : org.progress === 100)
      if (form.tool === 'evaluation' && allOrgsCompleted) {
        const orgProfiles = organizations.map(org => {
          const savedJson = org.id === selectedOrg ? JSON.stringify(completedForm) : localStorage.getItem(getStorageKey(org.id))
          const orgForm: FormState = savedJson ? JSON.parse(savedJson) : completedForm
          return { id: org.id, name: org.name, role: org.role, legal_profile: buildLegalProfile(orgForm) }
        })
        const projectIntake = {
          tool: form.tool, organizations: orgProfiles, tool_specific: buildToolSpecific(completedForm),
          risk_assessment: { overall_risk_level: 'LOW', derivation_color: 'green', derivation_required: false, organization_risks: [], shared_signals: [], shared_reasons: [], detected_intentions: [] },
          total_organizations: organizations.length,
        }
        const evaluationResponse = await evaluationApi.evaluateIntake(projectIntake)
        const backendData: BackendEvaluationResponse = evaluationResponse.data
        const orgNames = organizations.map(o => ({ id: o.id, name: o.name, role: o.role }))
        const evaluationData = mapBackendToProjectEvaluation(backendData, orgNames)
        navigate('/evaluation', { state: { evaluationData } })
      } else if (!allOrgsCompleted) {
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

  // ─── Block Content Renderers ───────────────────────────────────────────────

  const renderBlock1 = () => (
    <FormBlock title="Identidad y naturaleza" subtitle="¿Cómo está conformada tu organización?" icon={Fingerprint}>
      <div className="space-y-8">
        {/* Q1 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3">
              <QNum num={1} done={!!form.orgType} />
              <span className="text-sm font-semibold text-gray-900">¿Cuál es la forma legal actual de su organización o grupo?</span>
            </label>
            <HelpTooltip text={"Selecciona la figura jurídica que mejor describa tu organización.\n\n- **Asociación:** Persona jurídica sin fines de lucro.\n- **Fundación:** Persona jurídica sin fines de lucro, creada a partir de un patrimonio.\n- **Empresa:** Persona jurídica con fines de lucro (SAC, SRL, EIRL, etc.).\n- **Colectivo / iniciativa no formalizada:** Grupo no inscrito.\n- **Otro:** Especifica (ej. Comité, Cooperativa, etc.).\n\n**Nota:** \"ONG\" no es una forma legal en Perú, sino un estatus administrativo ante APCI."} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <select
              value={form.orgType || ''} onChange={(e) => updateForm('orgType', e.target.value)} disabled={form.isCompleted}
              className={clsx('w-full rounded-full border-gray-200 text-sm py-3 px-5 focus:ring-causante-ocre focus:border-causante-ocre bg-white', form.isCompleted && 'opacity-50 cursor-not-allowed')}
            >
              <option value="">Selecciona una opción</option>
              <option value="Asociación">Asociación</option>
              <option value="Fundación">Fundación</option>
              <option value="Empresa">Empresa</option>
              <option value="Colectivo / iniciativa no formalizada">Colectivo / iniciativa no formalizada</option>
              <option value="Otro">Otro</option>
            </select>
            <input type="text" value={form.orgTypeOther} onChange={(e) => updateForm('orgTypeOther', e.target.value)} placeholder="Otro (especificar)" disabled={form.isCompleted}
              className={clsx('w-full rounded-full border-gray-200 text-sm py-3 px-5', form.isCompleted && 'opacity-50 cursor-not-allowed')}
            />
          </div>
        </div>

        {/* Q2 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3">
              <QNum num={2} done={!!form.orgPurpose} />
              <span className="text-sm font-semibold text-gray-900">¿Cuál describe mejor el objeto o fin principal?</span>
            </label>
            <HelpTooltip text={"Indica la actividad principal:\n\nEducativo, Cultural, Ambiental, Asistencial / social, Tecnológico / innovación, u Otro."} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <select
              value={form.orgPurpose || ''} onChange={(e) => updateForm('orgPurpose', e.target.value)} disabled={form.isCompleted}
              className={clsx('w-full rounded-full border-gray-200 text-sm py-3 px-5 focus:ring-causante-ocre focus:border-causante-ocre bg-white', form.isCompleted && 'opacity-50 cursor-not-allowed')}
            >
              <option value="">Selecciona una opción</option>
              <option value="Educativo">Educativo</option>
              <option value="Cultural">Cultural</option>
              <option value="Ambiental">Ambiental</option>
              <option value="Asistencial / social">Asistencial / social</option>
              <option value="Tecnológico / innovación">Tecnológico / innovación</option>
              <option value="Otro">Otro</option>
            </select>
            <input type="text" value={form.orgPurposeOther} onChange={(e) => updateForm('orgPurposeOther', e.target.value)} placeholder="Otro (especificar)" disabled={form.isCompleted}
              className={clsx('w-full rounded-full border-gray-200 text-sm py-3 px-5', form.isCompleted && 'opacity-50 cursor-not-allowed')}
            />
          </div>
        </div>

        {/* Q3 */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3">
              <QNum num={3} done={!!form.seeksProfits} />
              <span className="text-sm font-semibold text-gray-900">¿Su entidad es con o sin fines de lucro?</span>
            </label>
            <HelpTooltip text={"Determina el régimen legal y tributario.\n\n- **Sin fines de lucro:** Excedentes se reinvierten.\n- **Con fines de lucro:** Utilidades se pueden distribuir.\n- **Aún no definido:** Está evaluando."} />
          </div>
          <SingleSelect
            options={['Sin fines de lucro (no se reparten excedentes)', 'Con fines de lucro (puede haber reparto)', 'Aún no definido / Estamos evaluando']}
            value={form.seeksProfits} onChange={(val) => updateForm('seeksProfits', val)} disabled={form.isCompleted}
          />
          {(form.orgType === 'Asociación' || form.orgType === 'Fundación') && form.seeksProfits === 'Con fines de lucro (puede haber reparto)' && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex gap-3 text-red-700 text-sm animate-fade-in">
              <Info className="w-5 h-5 flex-shrink-0" />
              <span><strong>Alerta:</strong> Las asociaciones y fundaciones son sin fines de lucro por ley.</span>
            </div>
          )}
        </div>
      </div>
    </FormBlock>
  )

  const renderBlock2 = () => (
    <FormBlock title="Nivel de formalización" subtitle="Estado legal y registros de tu organización" icon={Gavel}>
      <div className="space-y-8">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={4} done={!!form.hasLegalStatus} /><span className="text-sm font-semibold text-gray-900">¿Cuenta con personería jurídica vigente?</span></label>
            <HelpTooltip text={"Sí: Inscrita en Registros Públicos.\nNo: Opera de hecho.\nEn trámite: Proceso iniciado."} />
          </div>
          <SingleSelect options={['Sí', 'No', 'En trámite']} value={form.hasLegalStatus} onChange={(val) => updateForm('hasLegalStatus', val)} disabled={form.isCompleted} />
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={5} done={!!form.ruc} /><span className="text-sm font-semibold text-gray-900">¿Cuál es la situación del RUC?</span></label>
            <HelpTooltip text={"El RUC identifica a la organización ante SUNAT."} />
          </div>
          <SingleSelect options={['Lo tengo', 'No lo tengo', 'En trámite']} value={form.ruc} onChange={(val) => updateForm('ruc', val)} disabled={form.isCompleted} />
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={6} done={form.additionalRegistries.length > 0} /><span className="text-sm font-semibold text-gray-900">¿Cuentan con algún registro especial además de SUNARP y SUNAT?</span></label>
            <HelpTooltip text={"Registros tributarios que otorgan beneficios:\n\n- Registro de Entidades Exoneradas del IR\n- Registro de Entidades Receptoras de Donaciones\n- Ninguno / No sé"} />
          </div>
          <MultiSelectChips
            options={['Registro de Entidades Exoneradas del Impuesto a la Renta (SUNAT)', 'Registro de Entidades Receptoras de Donaciones (SUNAT)', 'Ninguno / No sé']}
            value={form.additionalRegistries} onChange={(val) => updateForm('additionalRegistries', val)} disabled={form.isCompleted}
          />
        </div>
      </div>
    </FormBlock>
  )

  const renderBlock3 = () => (
    <FormBlock title="Fuentes de ingreso y fondos" subtitle="¿Cómo se financia tu organización?" icon={Banknote}>
      <div className="space-y-8">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={7} done={form.handlesMoney !== null} /><span className="text-sm font-semibold text-gray-900">¿La organización maneja o manejará dinero?</span></label>
            <HelpTooltip text={"Indica si la organización realiza actividades económicas que impliquen ingresos o egresos de dinero."} />
          </div>
          <YesNoButtons value={form.handlesMoney} onChange={(val) => updateForm('handlesMoney', val)} disabled={form.isCompleted} />
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={8} done={form.receivesForeignFunds !== null} /><span className="text-sm font-semibold text-gray-900">¿Recibe o planea recibir fondos desde fuera del Perú?</span></label>
            <HelpTooltip text={"Fondos extranjeros pueden implicar requisitos adicionales como registro en APCI."} />
          </div>
          <YesNoButtons value={form.receivesForeignFunds} onChange={(val) => updateForm('receivesForeignFunds', val)} disabled={form.isCompleted} />
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={9} done={form.incomeSources.length > 0} /><span className="text-sm font-semibold text-gray-900">¿De dónde provienen o provendrán los ingresos?</span></label>
            <HelpTooltip text={"Selecciona todas las fuentes de financiamiento."} />
          </div>
          <MultiSelectChips
            options={['Donaciones', 'Venta de servicios o productos', 'Fondos públicos', 'Fondos privados', 'Cooperación internacional', 'Aún no recibe ingresos']}
            value={form.incomeSources} onChange={(val) => updateForm('incomeSources', val)} disabled={form.isCompleted}
          />
        </div>
      </div>
    </FormBlock>
  )

  const renderBlock4 = () => (
    <FormBlock title="Cooperación Internacional" subtitle="Estado ante APCI" icon={Globe}>
      <div className="space-y-6">
        {form.receivesForeignFunds === true ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-3"><QNum num={10} done={!!form.apciStatus} /><span className="text-sm font-semibold text-gray-900">¿Cuál es su estado en APCI?</span></label>
              <HelpTooltip text={"APCI regula organizaciones que reciben fondos del extranjero.\n\n- Registrado: Ya inscrito.\n- Necesita: Recibe fondos pero no registrado.\n- No aplica: Exento de registro."} />
            </div>
            <SingleSelect options={['Registrado', 'Necesita', 'No aplica']} value={form.apciStatus} onChange={(val) => updateForm('apciStatus', val)} columns={3} disabled={form.isCompleted} />
          </div>
        ) : (
          <div className="p-6 bg-cream rounded-2xl text-gray-500 text-sm text-center">
            <p>No recibe fondos del extranjero, por lo que esta sección no aplica.</p>
          </div>
        )}
      </div>
    </FormBlock>
  )

  const renderBlock5 = () => (
    <FormBlock title="Recursos humanos" subtitle="¿Cómo se vincula el personal con la organización?" icon={Users}>
      <div className="space-y-8">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={11} done={form.hiringModalities.length > 0} /><span className="text-sm font-semibold text-gray-900">¿Bajo qué modalidades contrata personal?</span></label>
            <HelpTooltip text={"Planilla (DL 728), Locación de Servicios, Voluntariado, Prácticas, o Ninguno."} />
          </div>
          <MultiSelectChips options={['Planilla', 'Locación de servicios', 'Voluntariado', 'Prácticas', 'Ninguno']} value={form.hiringModalities} onChange={(val) => updateForm('hiringModalities', val)} disabled={form.isCompleted} />
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={12} done={form.contractsValid !== null} /><span className="text-sm font-semibold text-gray-900">¿Los contratos o acuerdos están vigentes?</span></label>
            <HelpTooltip text={"Indica si los contratos están al día y cumplen con los requisitos legales."} />
          </div>
          <SingleSelect options={['Sí', 'No', 'No aplica']} value={form.contractsValid} onChange={(val) => updateForm('contractsValid', val)} columns={3} disabled={form.isCompleted} />
        </div>
      </div>
    </FormBlock>
  )

  const renderBlock6 = () => (
    <FormBlock title="Información contable" subtitle="Estado contable y documentos administrativos" icon={BookOpen}>
      <div className="space-y-8">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={13} done={form.hasAccountingRecords !== null} /><span className="text-sm font-semibold text-gray-900">¿Existen registros contables o financieros?</span></label>
            <HelpTooltip text={"Se refiere a si la organización lleva algún control de ingresos, egresos, libros contables o estados financieros."} />
          </div>
          <SingleSelect options={['Sí', 'No', 'En proceso']} value={form.hasAccountingRecords}
            onChange={(val) => {
              if (form.isCompleted) return
              updateForm('hasAccountingRecords', val)
              if (val === 'Sí' && form.accountingRecordsDetail === null) updateForm('accountingRecordsDetail', 'Completos')
              if (val !== 'Sí') updateForm('accountingRecordsDetail', null)
            }}
            columns={3} disabled={form.isCompleted}
          />
          {form.hasAccountingRecords === 'Sí' && (
            <>
              <div className="grid grid-cols-2 gap-3 mt-3">
                <button type="button" onClick={() => !form.isCompleted && updateForm('accountingRecordsDetail', 'Completos')} disabled={form.isCompleted}
                  className={clsx('p-3 rounded-full text-sm font-medium transition-all', form.accountingRecordsDetail === 'Completos' ? 'border-2 border-causante-ocre bg-gold-50 text-gray-900' : 'border border-gray-200 hover:border-causante-ocre/40', form.isCompleted && 'opacity-50 cursor-not-allowed')}>
                  Completos
                </button>
                <button type="button" onClick={() => !form.isCompleted && updateForm('accountingRecordsDetail', 'Parciales')} disabled={form.isCompleted}
                  className={clsx('p-3 rounded-full text-sm font-medium transition-all', form.accountingRecordsDetail === 'Parciales' ? 'border-2 border-causante-ocre bg-gold-50 text-gray-900' : 'border border-gray-200 hover:border-causante-ocre/40', form.isCompleted && 'opacity-50 cursor-not-allowed')}>
                  Parciales
                </button>
              </div>
              <div className="p-4 bg-gold-50 border border-causante-ocre/20 rounded-2xl flex gap-3 text-gray-700 text-sm animate-fade-in">
                <Info className="w-5 h-5 flex-shrink-0 text-causante-ocre" />
                <span><strong>Advertencia:</strong> No suba archivos financieros reales; solo proporcione descripciones generales.</span>
              </div>
            </>
          )}
        </div>

        {form.orgType === 'Colectivo / iniciativa no formalizada' ? (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-2xl text-sm text-blue-800 flex gap-3 animate-fade-in">
            <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold mb-1">Nota sobre Colectivos:</p>
              <p>Al ser una iniciativa no formalizada, operan como una "Asociación no inscrita". Se recomienda formalizar para proteger el patrimonio personal.</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-3"><QNum num={14} done={form.availableDocuments.length > 0} /><span className="text-sm font-semibold text-gray-900">¿Cuenta con alguno de estos documentos?</span></label>
              <HelpTooltip text={"Documentos administrativos y legales básicos."} />
            </div>
            <MultiSelectChips options={['Estatuto o acta de constitución', 'Libros de actas', 'Estados financieros', 'Memorias anuales', 'Plan de uso de fondos', 'Ninguno']} value={form.availableDocuments} onChange={(val) => updateForm('availableDocuments', val)} disabled={form.isCompleted} />
          </div>
        )}
      </div>
    </FormBlock>
  )

  const renderBlock7 = () => (
    <FormBlock title="Gobernanza y representación" subtitle="Estructura interna y representación legal" icon={Network}>
      <div className="space-y-8">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={15} done={form.governanceBodies !== null} /><span className="text-sm font-semibold text-gray-900">¿Tiene órganos de gobierno definidos?</span></label>
            <HelpTooltip text={"Estructuras como asamblea general, junta directiva, consejo directivo, etc."} />
          </div>
          <YesNoButtons value={form.governanceBodies} onChange={(val) => updateForm('governanceBodies', val)} disabled={form.isCompleted} />
        </div>

        {form.orgType !== 'Colectivo / iniciativa no formalizada' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-3"><QNum num={16} done={form.hasLegalRepresentative !== null} /><span className="text-sm font-semibold text-gray-900">¿Existe una persona designada como representante legal?</span></label>
              <HelpTooltip text={"El representante legal actúa en nombre de la organización ante terceros."} />
            </div>
            <SingleSelect options={['Sí', 'No', 'En trámite']} value={form.hasLegalRepresentative} onChange={(val) => updateForm('hasLegalRepresentative', val)} columns={3} disabled={form.isCompleted} />
          </div>
        )}
      </div>
    </FormBlock>
  )

  const renderBlock8 = () => (
    <FormBlock title="Uso de intangibles y datos" subtitle="Recursos intangibles que pueden requerir protección" icon={Lightbulb}>
      <div className="space-y-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3"><QNum num={17} done={form.intangibleAssets.length > 0} /><span className="text-sm font-semibold text-gray-900">¿La organización utiliza alguno de los siguientes?</span></label>
            <HelpTooltip text={"Software propio, Software de terceros, Bases de datos de usuarios, Marca o símbolos, Contenido con derechos de autor, o Ninguno."} />
          </div>
          <MultiSelectChips options={['Software propio', 'Software de terceros', 'Bases de datos de usuarios', 'Marca o símbolos distintivos', 'Contenido con derechos de autor', 'Ninguno']} value={form.intangibleAssets} onChange={(val) => updateForm('intangibleAssets', val)} disabled={form.isCompleted} />
          {form.intangibleAssets.includes('Bases de datos de usuarios') && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex gap-3 text-red-700 text-sm animate-fade-in">
              <Info className="w-5 h-5 flex-shrink-0" />
              <span><strong>Aviso de Privacidad:</strong> Recuerde cumplir con la Ley de Protección de Datos Personales.</span>
            </div>
          )}
        </div>
      </div>
    </FormBlock>
  )

  const renderBlock9 = () => (
    <FormBlock title="Detalle de la Solicitud" subtitle="¿Qué necesitas de esta evaluación?" icon={ClipboardList}>
      <div className="space-y-8">
        {form.tool === 'evaluation' && (
          <>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-3"><QNum num={18} done={!!form.toolSpecific.evaluationGoals?.length} /><span className="text-sm font-semibold text-gray-900">¿Cuáles son sus objetivos principales?</span></label>
                <HelpTooltip text={"Formalización, Gestión de riesgos, Preparación para auditoría, Mejora de gobernanza, o Resolver un conflicto actual."} />
              </div>
              <MultiSelectChips options={['Formalización', 'Gestión de riesgos', 'Preparación para auditoría', 'Mejora de gobernanza', 'Resolver un conflicto actual']}
                value={form.toolSpecific.evaluationGoals || []} onChange={(val) => updateToolSpecific('evaluationGoals', val)} disabled={form.isCompleted}
              />
              {form.toolSpecific.evaluationGoals?.includes('Resolver un conflicto actual') && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex gap-3 text-red-700 text-sm">
                  <Info className="w-5 h-5 flex-shrink-0" /><span><strong>Aviso:</strong> Su caso podría ser derivado a un especialista humano.</span>
                </div>
              )}
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-3"><QNum num={19} done={!!form.toolSpecific.legalAreas?.length} /><span className="text-sm font-semibold text-gray-900">¿Qué áreas legales le preocupan más?</span></label>
                <HelpTooltip text={"Tributario, Cooperación internacional, Laboral, Propiedad intelectual, Contratos, Formalización, Gobernanza, Protección de Datos."} />
              </div>
              <MultiSelectChips options={['Tributario', 'Cooperación internacional (APCI)', 'Laboral', 'Propiedad intelectual', 'Contratos', 'Formalización', 'Gobernanza', 'Protección de Datos']}
                value={form.toolSpecific.legalAreas || []} onChange={(val) => updateToolSpecific('legalAreas', val)} disabled={form.isCompleted}
              />
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-3"><QNum num={20} done={!!form.toolSpecific.urgency} /><span className="text-sm font-semibold text-gray-900">¿Con qué rapidez necesita orientación?</span></label>
                <HelpTooltip text={"Inmediata, Semanal, o Informativa."} />
              </div>
              <SingleSelect options={['Inmediata (tengo un plazo venciendo)', 'Semanal (planeamiento)', 'Informativa (estoy explorando)']}
                value={form.toolSpecific.urgency || null} onChange={(val) => updateToolSpecific('urgency', val)} disabled={form.isCompleted}
              />
              {form.toolSpecific.urgency === 'Inmediata (tengo un plazo venciendo)' && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-2xl space-y-3 animate-fade-in">
                  <p className="text-red-800 font-semibold text-sm">¿Ha recibido una notificación formal (SUNAT/APCI)?</p>
                  <YesNoButtons value={form.toolSpecific.hasReceivedNotification ?? null} onChange={(val) => updateToolSpecific('hasReceivedNotification', val)} disabled={form.isCompleted} />
                  {form.toolSpecific.hasReceivedNotification === true && <p className="text-red-700 text-xs italic">Se ha activado la derivación prioritaria a un especialista humano.</p>}
                </div>
              )}
            </div>
          </>
        )}

        {form.tool === 'compliance' && (
          <>
            <div className="space-y-3">
              <label className="flex items-center gap-3"><QNum num={18} done={!!form.toolSpecific.complianceGoal} /><span className="text-sm font-semibold text-gray-900">Objetivo de cumplimiento</span></label>
              <SingleSelect options={['Formalizar la organización', 'Registrar en APCI', 'Cumplir obligaciones SUNAT', 'Regularizar situación laboral', 'Obtener exoneración de IR', 'Inscribirse como receptora de donaciones']}
                value={form.toolSpecific.complianceGoal || null} onChange={(val) => updateToolSpecific('complianceGoal', val)} disabled={form.isCompleted}
              />
            </div>
            <div className="space-y-3">
              <label className="flex items-center gap-3"><QNum num={19} done={!!form.toolSpecific.timeline} /><span className="text-sm font-semibold text-gray-900">Plazo estimado</span></label>
              <SingleSelect options={['Lo antes posible', '1-3 meses', '3-6 meses', 'Sin prisa específica']}
                value={form.toolSpecific.timeline || null} onChange={(val) => updateToolSpecific('timeline', val)} disabled={form.isCompleted}
              />
            </div>
          </>
        )}

        {form.tool === 'query' && (
          <>
            <div className="space-y-3">
              <label className="flex items-center gap-3"><QNum num={18} done={!!form.toolSpecific.queryArea} /><span className="text-sm font-semibold text-gray-900">Área de la consulta</span></label>
              <SingleSelect options={['Formalización y registros', 'Tributación', 'Contratación de personal', 'Cooperación internacional', 'Propiedad intelectual', 'Donaciones', 'Gobernanza', 'Otro']}
                value={form.toolSpecific.queryArea || null} onChange={(val) => updateToolSpecific('queryArea', val)} disabled={form.isCompleted}
              />
            </div>
            <div className="space-y-3">
              <label className="flex items-center gap-3"><QNum num={19} done={!!form.toolSpecific.specificQuestion} /><span className="text-sm font-semibold text-gray-900">Detalle su consulta específica</span></label>
              <textarea
                className={clsx('w-full rounded-2xl border-gray-200 text-sm py-3 px-5 min-h-[100px] focus:ring-causante-ocre focus:border-causante-ocre', form.isCompleted && 'opacity-50 cursor-not-allowed')}
                placeholder="Escriba aquí su consulta..." value={form.toolSpecific.specificQuestion || ''}
                onChange={(e) => updateToolSpecific('specificQuestion', e.target.value)} disabled={form.isCompleted}
              />
            </div>
          </>
        )}
      </div>
    </FormBlock>
  )

  const blockRenderers = [renderBlock1, renderBlock2, renderBlock3, renderBlock4, renderBlock5, renderBlock6, renderBlock7, renderBlock8, renderBlock9]

  // ─── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-white">
      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Header */}
        <section className="mb-8">
          <button onClick={() => navigate('/chat')} className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-900 transition-colors mb-6">
            <ChevronLeft className="w-4 h-4" /> Volver al chat
          </button>
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 rounded-lg bg-causante-ocre rotate-45 flex-shrink-0" />
            <div>
              <h1 className="font-heading text-2xl md:text-3xl font-bold text-gray-900">Ficha Legal Mínima</h1>
              <p className="text-sm text-gray-400 mt-1">Completa cada sección para generar tu evaluación legal</p>
            </div>
          </div>
        </section>

        {/* Organization Selector */}
        {organizations.length > 1 && (
          <section className="mb-8">
            <h2 className="font-heading text-base font-semibold mb-3 text-gray-700">Organización</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {organizations.map((org) => (
                <OrganizationCard key={org.id} organization={org} isSelected={selectedOrg === org.id} onClick={() => setSelectedOrg(org.id)} />
              ))}
            </div>
          </section>
        )}

        {/* Progress */}
        <ProgressTracker
          steps={BLOCKS}
          currentStep={currentBlock}
          onStepClick={(i) => { setCurrentBlock(i); window.scrollTo({ top: 0, behavior: 'smooth' }) }}
          completedQuestions={completedQuestions}
          totalQuestions={totalQuestions}
          isFinished={form.isCompleted}
        />

        {/* Current Block */}
        <div className="mb-8" key={currentBlock}>
          {blockRenderers[currentBlock]()}
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between gap-4 mb-6">
          <button
            onClick={goPrev}
            disabled={currentBlock === 0}
            className={clsx(
              'btn-secondary flex items-center gap-2',
              currentBlock === 0 && 'opacity-30 cursor-not-allowed'
            )}
          >
            <ChevronLeft className="w-4 h-4" /> Anterior
          </button>

          {!isLastBlock ? (
            <button onClick={goNext} className="btn-primary flex items-center gap-2">
              Siguiente <ChevronRight className="w-4 h-4" />
            </button>
          ) : (
            // On last block: show confirm + submit
            <div className="flex items-center gap-3">
              {completedQuestions === totalQuestions && !form.isCompleted && !form.hasConfirmed && (
                <button
                  onClick={() => setForm(p => ({ ...p, hasConfirmed: true }))}
                  className="btn-accent flex items-center gap-2"
                >
                  <Check className="w-4 h-4" /> Confirmar datos
                </button>
              )}

              <button
                onClick={handleSubmit}
                disabled={completedQuestions !== totalQuestions || !form.hasConfirmed || isSubmitting || form.isCompleted}
                className={clsx(
                  'flex items-center gap-2 px-8 py-3 rounded-full font-semibold transition-all duration-200',
                  completedQuestions === totalQuestions && form.hasConfirmed && !isSubmitting && !form.isCompleted
                    ? 'bg-black text-white hover:bg-gray-800'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                )}
              >
                {form.isCompleted && <Check className="w-4 h-4" />}
                {!form.isCompleted && (!form.hasConfirmed || completedQuestions !== totalQuestions) && <Lock className="w-4 h-4" />}
                {isSubmitting ? 'Enviando...' : form.isCompleted ? 'Completada' : 'Generar evaluación'}
              </button>
            </div>
          )}
        </div>

        {/* Status Text */}
        <p className="text-center text-xs text-gray-400 mb-12">
          {form.isCompleted
            ? 'La ficha ha sido enviada correctamente'
            : isLastBlock && completedQuestions < totalQuestions
              ? `Faltan ${totalQuestions - completedQuestions} preguntas por responder`
              : isLastBlock && !form.hasConfirmed
                ? 'Confirma tus datos para generar la evaluación'
                : `Sección ${currentBlock + 1} de ${BLOCKS.length}`}
        </p>

        {/* Confirmation disclaimer - shown on last block when all complete */}
        {isLastBlock && completedQuestions === totalQuestions && !form.isCompleted && (
          <div className="bg-cream rounded-3xl p-6 mb-12 animate-fade-in">
            <div className="flex items-start gap-4">
              <Info className="w-6 h-6 text-causante-ocre flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-heading font-bold text-base mb-2">Confirmación</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  La información brindada será utilizada para generar un diagnóstico legal preliminar.
                  Este documento no reemplaza la asesoría legal especializada pero sirve como línea base
                  de cumplimiento en el contexto peruano.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}