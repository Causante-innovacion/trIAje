import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { evaluationApi } from '../../shared/services/api'
import { mapBackendToProjectEvaluation, BackendEvaluationResponse } from '../../types/evaluation.types'
import { useChatStore } from '../../stores/chatStore'
import {
  Check, ChevronLeft, ChevronRight, Fingerprint, Gavel, Banknote, Users,
  Lightbulb, Building2, LucideIcon,
  ClipboardList, ArrowLeft, Pencil, RefreshCw,
} from 'lucide-react'
import { OrganizationCard } from './OrganizationCard'
import { ProgressTracker } from './ProgressTracker'
import { FormBlock } from './FormBlock'
import { SingleSelect, MultiSelectChips } from './FormInputs'
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
  // Block 1: Identificación y Naturaleza
  identityV2: string | null
  orgPurpose: string | null
  orgPurposeOther: string
  // Block 2: Situación SUNAT
  sunatV2: string | null
  // Block 3: Fondos y Cooperación
  fundsV2: string | null
  // Block 4: Recursos Humanos
  hiringV2: string[]
  // Block 5: Activos e Intangibles
  intangiblesV2: string[]
  // Block 6: Nivel de Urgencia
  urgencyV2: string | null

  // Tool Specific Info (kept for API compatibility)
  tool: 'evaluation' | 'compliance' | 'query'
  toolSpecific: {
    evaluationGoals?: string[]
    legalAreas?: string[]
    urgency?: string
    hasReceivedNotification?: boolean | null
  }

  // States
  isCompleted: boolean
  hasConfirmed: boolean
}

// ─── Constants ───────────────────────────────────────────────────────────────

const DEFAULT_ORGANIZATIONS: Organization[] = [
  { id: '1', name: 'Organización 1', role: 'Ejecutor principal', progress: 0, color: '#B3994C', icon: Building2 },
]
const ORG_COLORS = ['#B3994C', '#8F86A3', '#D7D100']

const initialFormState: FormState = {
  identityV2: null,
  orgPurpose: null,
  orgPurposeOther: '',
  sunatV2: null,
  fundsV2: null,
  hiringV2: [],
  intangiblesV2: [],
  urgencyV2: null,
  tool: 'evaluation',
  toolSpecific: {},
  isCompleted: false,
  hasConfirmed: false,
}

const getStorageKey = (orgId: string) => `gpt_legal_form_progress_${orgId}`

const TTL_MS = 24 * 60 * 60 * 1000 // 24 horas

function loadFromStorage(orgId: string): FormState {
  try {
    const raw = localStorage.getItem(getStorageKey(orgId))
    if (!raw) return initialFormState
    const parsed = JSON.parse(raw)
    // Support both old format (raw FormState) and new format ({ data, timestamp })
    const timestamp: number = parsed.timestamp ?? 0
    const data: FormState = parsed.data ?? parsed
    if (timestamp && Date.now() - timestamp > TTL_MS) {
      localStorage.removeItem(getStorageKey(orgId))
      return initialFormState
    }
    return data
  } catch { return initialFormState }
}

function saveToStorage(orgId: string, form: FormState): void {
  try {
    localStorage.setItem(getStorageKey(orgId), JSON.stringify({ data: form, timestamp: Date.now() }))
  } catch { /* ignore */ }
}

// ─── Progress Calculation ────────────────────────────────────────────────────

const calculateProgress = (form: FormState) => {
  let completedCount = 0
  const totalCount = 7
  if (form.identityV2) completedCount++
  if (form.orgPurpose) completedCount++
  if (form.sunatV2) completedCount++
  if (form.fundsV2) completedCount++
  if (form.hiringV2.length > 0) completedCount++
  if (form.intangiblesV2.length > 0) completedCount++
  if (form.urgencyV2) completedCount++

  let pct = Math.round((completedCount / totalCount) * 100)
  if (pct === 100 && !form.isCompleted) pct = 99
  return pct
}

// ─── Question Number Badge ──────────────────────────────────────────────────

function QNum({ num, done }: { num: number; done: boolean }) {
  return (
    <span
      className={clsx(
        'w-8 h-8 rounded-full flex items-center justify-center text-xs font-black flex-shrink-0 transition-all duration-300',
        done ? 'bg-causante-ocre text-white shadow-lg shadow-causante-ocre/20' : 'bg-gray-100 text-gray-400'
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
  const [currentStep, setCurrentStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [pendingNextOrg, setPendingNextOrg] = useState<{ id: string; name: string } | null>(null)

  // ── Storage ──
  useEffect(() => {
    setForm(loadFromStorage(selectedOrg))
    // Always start from step 1 when switching organization
    setCurrentStep(0)
  }, [selectedOrg])

  useEffect(() => {
    const updatedOrgs = baseOrganizations.map(org => {
      if (org.id === selectedOrg) return { ...org, progress: calculateProgress(form) }
      const saved = loadFromStorage(org.id)
      return { ...org, progress: calculateProgress(saved) }
    })
    setOrganizations(updatedOrgs)
  }, [form, selectedOrg, baseOrganizations])

  useEffect(() => {
    saveToStorage(selectedOrg, form)
  }, [form, selectedOrg])

  const completedQuestions = [
    !!form.identityV2,
    !!form.orgPurpose,
    !!form.sunatV2,
    !!form.fundsV2,
    form.hiringV2.length > 0,
    form.intangiblesV2.length > 0,
    !!form.urgencyV2,
  ].filter(Boolean).length

  const STEPS = [
    { id: 'identity', name: 'Identidad', icon: Fingerprint, completed: !!form.identityV2 ? 1 : 0, total: 1 },
    { id: 'purpose', name: 'Propósito', icon: Building2, completed: !!form.orgPurpose ? 1 : 0, total: 1 },
    { id: 'sunat', name: 'SUNAT', icon: Gavel, completed: !!form.sunatV2 ? 1 : 0, total: 1 },
    { id: 'funds', name: 'Fondos', icon: Banknote, completed: !!form.fundsV2 ? 1 : 0, total: 1 },
    { id: 'hr', name: 'Equipo', icon: Users, completed: form.hiringV2.length > 0 ? 1 : 0, total: 1 },
    { id: 'intangibles', name: 'Activos', icon: Lightbulb, completed: form.intangiblesV2.length > 0 ? 1 : 0, total: 1 },
    { id: 'urgency', name: 'Urgencia', icon: ClipboardList, completed: !!form.urgencyV2 ? 1 : 0, total: 1 },
  ]

  const totalQuestions = 7

  // ── Form helpers ──
  const updateForm = <K extends keyof FormState>(field: K, value: FormState[K]) => setForm(p => ({ ...p, [field]: value }))

  // ── Navigation ──
  const isLastStep = currentStep === STEPS.length - 1

  const goNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(prev => prev + 1)
    }
  }

  const goPrev = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  // ── Submit ──
  const buildLegalProfile = (f: FormState) => ({
    identity: {
      identity_v2: f.identityV2,
      org_purpose: f.orgPurpose,
      org_purpose_other: f.orgPurposeOther || null,
    },
    sunat: { sunat_v2: f.sunatV2 },
    funds: { funds_v2: f.fundsV2 },
    human_resources: { hiring_v2: f.hiringV2 },
    intangibles: { intangibles_v2: f.intangiblesV2 },
    urgency: { urgency_v2: f.urgencyV2 },
  })

  // Marks the form as completed (does NOT generate the diagnostic yet)
  const handleSubmit = () => {
    if (completedQuestions !== totalQuestions || !form.hasConfirmed) return
    const completedForm = { ...form, isCompleted: true }
    setForm(completedForm)
    saveToStorage(selectedOrg, completedForm)
  }

  // Unlocks the form for re-editing
  const handleResetForm = () => {
    const resetForm = { ...form, isCompleted: false, hasConfirmed: false }
    setForm(resetForm)
    saveToStorage(selectedOrg, resetForm)
    setCurrentStep(0)
  }

  // Calls the evaluation API and navigates to the diagnostic page
  const handleGenerateDiagnostic = async () => {
    if (!form.isCompleted) return
    setIsSubmitting(true)
    setSubmitError(null)
    try {
      const allOrgsCompleted = organizations.every(org => {
        if (org.id === selectedOrg) return form.isCompleted
        return loadFromStorage(org.id).isCompleted === true
      })

      if (!allOrgsCompleted) {
        const nextOrg = organizations.find(org => {
          if (org.id === selectedOrg) return false
          return loadFromStorage(org.id).isCompleted !== true
        })
        setPendingNextOrg(nextOrg ? { id: nextOrg.id, name: nextOrg.name } : null)
        setSubmitError(
          nextOrg
            ? `Falta completar la ficha de "${nextOrg.name}". Complétala para poder generar el diagnóstico.`
            : 'Debes completar la ficha de todas las organizaciones antes de generar el diagnóstico.'
        )
        setIsSubmitting(false)
        window.scrollTo({ top: 0, behavior: 'smooth' })
        return
      }

      const orgProfiles = organizations.map(org => {
        const orgForm: FormState = org.id === selectedOrg ? form : loadFromStorage(org.id)
        return { id: org.id, name: org.name, role: org.role, legal_profile: buildLegalProfile(orgForm) }
      })
      const projectIntake = {
        tool: form.tool, organizations: orgProfiles,
        tool_specific: { evaluation: { evaluation_goals: ["Evaluación general"], urgency: form.urgencyV2 } },
        risk_assessment: { overall_risk_level: 'LOW', derivation_color: 'green', derivation_required: false, organization_risks: [], shared_signals: [], shared_reasons: [], detected_intentions: [] },
        total_organizations: organizations.length,
      }
      const evaluationResponse = await evaluationApi.evaluateIntake(projectIntake)
      const backendData: BackendEvaluationResponse = evaluationResponse.data
      const orgNames = organizations.map(o => ({ id: o.id, name: o.name, role: o.role }))
      const evaluationData = mapBackendToProjectEvaluation(backendData, orgNames)
      useChatStore.getState().setLastEvaluationData(evaluationData)
      navigate('/evaluation', { state: { evaluationData } })
    } catch (error) {
      console.error('Error generating diagnostic:', error)
      setSubmitError('Ocurrió un error al generar el diagnóstico. Por favor intenta nuevamente.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // ─── Step Content Renderers ───────────────────────────────────────────────

  const renderStep1 = () => (
    <FormBlock title="Identificación" subtitle="Naturaleza de tu organización" icon={Fingerprint}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-3">
            <QNum num={1} done={!!form.identityV2} />
            <span className="text-base font-bold text-gray-900">¿Cómo está organizada tu iniciativa y qué hacen con el dinero?</span>
          </label>
          <HelpTooltip text={`**Formal (Asociación/Fundación)**: Sin fines de lucro. El patrimonio es de la entidad y los excedentes se reinvierten.
**Empresa**: Con fines de lucro. El objetivo es generar utilidad para socios. Hay dividendo y mayor carga fiscal. 
**Colectivo**: Sin personería jurídica. El riesgo legal recae directamente en las personas naturales.`} />
        </div>
        <SingleSelect
          options={[
            "Organización formal (Asociación o Fundación): Sin fines de lucro; el dinero se reinvierte en el objeto social.",
            "Empresa (SAC, SA, SRL, EIRL): Con fines de lucro; el objetivo es generar utilidades para los socios.",
            "Colectivo o Grupo: Iniciativa no formalizada (sin personería jurídica ante SUNARP)."
          ]}
          value={form.identityV2}
          onChange={(v) => updateForm('identityV2', v)}
          columns={1}
          disabled={form.isCompleted}
        />
      </div>
    </FormBlock>
  )

  const renderStep2 = () => (
    <FormBlock title="Propósito" subtitle="Objeto principal de la organización" icon={Building2}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-3">
            <QNum num={2} done={!!form.orgPurpose} />
            <span className="text-base font-bold text-gray-900">¿Cuál describe mejor el fin principal de la organización?</span>
          </label>
          <HelpTooltip text={`**Beneficios Fiscales**: El sector determina si puedes solicitar beneficios como la exoneración del Impuesto a la Renta.
**Marco Regulatorio**: Cada fin (Educativo, Ambiental, etc.) tiene leyes específicas que cumplir.`} />
        </div>
        <div className="space-y-4">
          <SingleSelect
            options={['Educativo', 'Cultural', 'Ambiental', 'Asistencial / Social', 'Tecnológico / Innovación', 'Otro']}
            value={form.orgPurpose}
            onChange={(v) => updateForm('orgPurpose', v)}
            columns={2}
            disabled={form.isCompleted}
          />
          {form.orgPurpose === 'Otro' && (
            <input
              type="text"
              value={form.orgPurposeOther}
              onChange={(e) => updateForm('orgPurposeOther', e.target.value)}
              placeholder="Especificar fin"
              disabled={form.isCompleted}
              className="w-full rounded-2xl border-gray-100 text-sm py-4 px-6 focus:ring-causante-ocre focus:border-causante-ocre bg-white shadow-inner"
            />
          )}
        </div>
      </div>
    </FormBlock>
  )

  const renderStep3 = () => (
    <FormBlock title="Situación Tributaria" subtitle="Relación con SUNAT" icon={Gavel}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-3">
            <QNum num={3} done={!!form.sunatV2} />
            <span className="text-base font-bold text-gray-900">¿Cómo es tu relación actual con la SUNAT?</span>
          </label>
          <HelpTooltip text={`**Activo**: Tu RUC está operando y puedes realizar actividades económicas.
**Habido**: SUNAT ha validado tu domicilio. Indispensable para contratar con el Estado o grandes empresas.
**No Habido**: Tienes restricciones para emitir facturas y estás sujeto a multas.`} />
        </div>
        <SingleSelect
          options={[
            "Tengo RUC y está al día: Emito comprobantes y mis declaraciones están vigentes.",
            "Tengo RUC, pero está pausado o con problemas: Estado 'Suspendido', 'Baja de Oficio' o figura como 'No Habido'.",
            "No tengo RUC: Somos un colectivo o aún no iniciamos trámites ante impuestos.",
            "No estoy seguro: Existe un número de RUC pero desconozco la situación legal actual."
          ]}
          value={form.sunatV2}
          onChange={(v) => updateForm('sunatV2', v)}
          columns={1}
          disabled={form.isCompleted}
        />
      </div>
    </FormBlock>
  )

  const renderStep4 = () => (
    <FormBlock title="Fondos" subtitle="Cooperación Internacional" icon={Banknote}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-3">
            <QNum num={4} done={!!form.fundsV2} />
            <span className="text-base font-bold text-gray-900">¿Recibes dinero de fuentes fuera del Perú?</span>
          </label>
          <HelpTooltip text={`**APCI**: Si recibes donaciones del extranjero (dinero o bienes), el registro es obligatorio.
**Gestión**: Permite acceder a beneficios arancelarios y asegura la transparencia ante el Estado.`} />
        </div>
        <SingleSelect
          options={[
            "No recibo fondos externos (Solo recibo dinero de ingresos propios o locales).",
            "Sí, y estamos registrados ante APCI (Vigente).",
            "Sí, pero no tenemos registro ante APCI o está vencido."
          ]}
          value={form.fundsV2}
          onChange={(v) => updateForm('fundsV2', v)}
          columns={1}
          disabled={form.isCompleted}
        />
      </div>
    </FormBlock>
  )

  const renderStep5 = () => (
    <FormBlock title="Equipo" subtitle="Recursos Humanos" icon={Users}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-3">
            <QNum num={5} done={form.hiringV2.length > 0} />
            <span className="text-base font-bold text-gray-900">¿Cómo vinculas a las personas de tu equipo?</span>
          </label>
          <HelpTooltip text={`**Planilla**: Existe horario, subordinación y pago fijo. Genera derechos sociales.
**Recibos por Honorarios**: Relación autónoma sin subordinación. Cuidado con la "desnaturalización".
**Voluntariado**: Debe ser bajo la Ley 28238 con acuerdo firmado.`} />
        </div>
        <MultiSelectChips
          options={[
            "Personal en Planilla (Contrato de trabajo).",
            "Locación de Servicios (Recibos por Honorarios).",
            "Voluntariado (Bajo la Ley de Voluntariado).",
            "Practicantes (Modalidades formativas).",
            "Solo gestión de fundadores (Sin pagos externos)."
          ]}
          value={form.hiringV2}
          onChange={(v) => updateForm('hiringV2', v)}
          disabled={form.isCompleted}
        />
      </div>
    </FormBlock>
  )

  const renderStep6 = () => (
    <FormBlock title="Activos" subtitle="Propiedad Intelectual" icon={Lightbulb}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-3">
            <QNum num={6} done={form.intangiblesV2.length > 0} />
            <span className="text-base font-bold text-gray-900">¿Qué tipo de activos gestionas?</span>
          </label>
          <HelpTooltip text={`**INDECOPI**: Es vital registrar tus marcas, logos y software para evitar plagios.
**Protección**: Sin registro oficial, un tercero podría apropiarse legalmente de tu identidad.`} />
        </div>
        <MultiSelectChips
          options={[
            "Software propio o desarrollado por terceros.",
            "Bases de datos de usuarios o beneficiarios.",
            "Marcas, logotipos o símbolos distintivos.",
            "Ninguno de los anteriores."
          ]}
          value={form.intangiblesV2}
          onChange={(v) => updateForm('intangiblesV2', v)}
          disabled={form.isCompleted}
        />
      </div>
    </FormBlock>
  )

  const renderStep7 = () => (
    <FormBlock title="Urgencia" subtitle="Prioridad de consulta" icon={ClipboardList}>
      <div className="space-y-10">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-3">
              <QNum num={7} done={!!form.urgencyV2} />
              <span className="text-base font-bold text-gray-900">¿Cuál es el nivel de urgencia?</span>
            </label>
            <HelpTooltip text={`**Urgente**: Aplica si tienes plazos legales corriendo (demandas, multas o cierres).
**Medio**: Para planificación y cumplimiento preventivo.
**Informativa**: Fase de exploración inicial.`} />
          </div>
          <SingleSelect
            options={[
              "Urgente: Tengo un plazo que vence pronto o recibí una notificación/demanda formal.",
              "Medio: Es para planeamiento, prevención o proyectos que recién van a empezar.",
              "Informativa: Solo estoy explorando el sistema o quiero aprender sobre el tema."
            ]}
            value={form.urgencyV2}
            onChange={(v) => updateForm('urgencyV2', v)}
            columns={1}
            disabled={form.isCompleted}
          />
        </div>

        {!form.isCompleted && isLastStep && (
          <div className="pt-6 border-t border-gray-50 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <label className="flex items-start gap-4 cursor-pointer group p-4 rounded-2xl bg-gray-50/50 border border-transparent hover:border-causante-ocre/20 transition-all">
              <div className="pt-1">
                <input
                  type="checkbox"
                  checked={form.hasConfirmed}
                  onChange={(e) => updateForm('hasConfirmed', e.target.checked)}
                  className="w-5 h-5 rounded border-gray-300 text-causante-ocre focus:ring-causante-ocre"
                />
              </div>
              <span className="text-[13px] text-gray-600 font-medium leading-relaxed group-hover:text-gray-900">
                Confirmo que la información proporcionada es veraz y autorizo su tratamiento para generar el diagnóstico legal.
              </span>
            </label>
          </div>
        )}

        {form.isCompleted && (
          <div className="pt-10 border-t border-gray-50 flex flex-col items-center">
            <div className="bg-green-50 text-green-700 px-8 py-5 rounded-3xl flex items-center gap-4 mb-8 shadow-sm">
              <Check className="w-6 h-6 stroke-[3]" />
              <span className="text-sm font-black uppercase tracking-widest">Ficha completada correctamente</span>
            </div>
            {submitError && (
              <div className="w-full mb-4 space-y-3">
                <div className="bg-amber-50 text-amber-700 border border-amber-200 px-6 py-3 rounded-2xl text-sm font-medium text-center">
                  {submitError}
                </div>
                {pendingNextOrg && (
                  <button
                    onClick={() => {
                      setSubmitError(null)
                      setPendingNextOrg(null)
                      setSelectedOrg(pendingNextOrg.id)
                    }}
                    className="w-full px-6 py-3 rounded-2xl font-bold text-[10px] tracking-widest text-white bg-causante-ocre hover:bg-opacity-90 transition-all flex items-center justify-center gap-2 uppercase shadow-lg shadow-causante-ocre/20"
                  >
                    Completar ficha de {pendingNextOrg.name}
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            )}
            <button
              onClick={handleGenerateDiagnostic}
              disabled={isSubmitting}
              className={clsx(
                'px-8 py-4 rounded-2xl font-black text-xs tracking-widest transition-all uppercase flex items-center gap-2 shadow-lg',
                isSubmitting
                  ? 'bg-gray-100 text-gray-400 shadow-none cursor-not-allowed'
                  : 'bg-causante-ocre text-white hover:bg-opacity-90 active:scale-[0.98] shadow-causante-ocre/20'
              )}
            >
              {isSubmitting ? 'GENERANDO...' : 'GENERAR DIAGNÓSTICO'}
              {!isSubmitting && <ChevronRight className="w-4 h-4" />}
            </button>
          </div>
        )}
      </div>
    </FormBlock>
  )

  const stepRenderers = [
    renderStep1, renderStep2, renderStep3, renderStep4, renderStep5, renderStep6, renderStep7
  ]

  return (
    <div className="min-h-screen bg-causante-crema">
      <div className="max-w-5xl mx-auto px-6 py-8 lg:py-12">
        {/* Header */}
        <div className="mb-10 relative text-center">
          <button
            onClick={() => navigate('/chat')}
            className="absolute left-0 top-1/2 -translate-y-1/2 flex items-center gap-2 text-sm font-semibold text-gray-400 hover:text-gray-700 transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-0.5" />
            <span className="hidden sm:inline">Volver al chat</span>
          </button>
          <h1 className="text-2xl sm:text-4xl font-black text-gray-900 mb-2 tracking-tight">Ficha Legal</h1>
          <p className="text-gray-400 text-xs sm:text-base max-w-2xl mx-auto leading-relaxed">
            Diagnóstico inteligente basado en la naturaleza de tu impacto.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left: Organizations & Steps Navigation */}
          <div className="lg:col-span-4 flex flex-col gap-6 lg:h-[620px] lg:sticky lg:top-8">
            <div className="bg-white rounded-[1.5rem] p-5 shadow-sm border border-gray-50 flex-shrink-0">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-[9px] font-black text-gray-300 uppercase tracking-[0.3em]">Organización</h2>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => {
                      const idx = organizations.findIndex(o => o.id === selectedOrg)
                      if (idx > 0) setSelectedOrg(organizations[idx - 1].id)
                    }}
                    disabled={organizations.findIndex(o => o.id === selectedOrg) === 0}
                    className="p-1 rounded-md hover:bg-gray-50 disabled:opacity-30 text-gray-400 transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="text-[10px] font-black text-gray-400">
                    {organizations.findIndex(o => o.id === selectedOrg) + 1} / {organizations.length}
                  </span>
                  <button
                    onClick={() => {
                      const idx = organizations.findIndex(o => o.id === selectedOrg)
                      if (idx < organizations.length - 1) setSelectedOrg(organizations[idx + 1].id)
                    }}
                    disabled={organizations.findIndex(o => o.id === selectedOrg) === organizations.length - 1}
                    className="p-1 rounded-md hover:bg-gray-50 disabled:opacity-30 text-gray-400 transition-colors"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="relative overflow-hidden group">
                <div className="transition-all duration-300 transform">
                  <OrganizationCard
                    organization={organizations.find(o => o.id === selectedOrg)!}
                    isSelected={true}
                    onClick={() => { }}
                  />
                </div>
              </div>

              {/* Summary Indicator */}
              <div className="mt-5 pt-5 border-t border-gray-50">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[10px] font-black text-gray-400 uppercase tracking-wider">Estado Global</span>
                  <span className={clsx(
                    "text-[10px] font-black px-2 py-0.5 rounded-full",
                    organizations.every(o => o.progress === 100) ? "bg-green-100 text-green-700" : "bg-causante-crema text-causante-ocre"
                  )}>
                    {organizations.filter(o => o.progress === 100).length} de {organizations.length} LISTAS
                  </span>
                </div>

                {organizations.some(o => o.progress < 100) ? (
                  <div className="space-y-2">
                    <p className="text-[10px] text-gray-400 font-medium">Pendientes:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {organizations.filter(o => o.progress < 100).map(org => (
                        <div key={org.id} className="px-2 py-1 bg-gray-50 rounded-lg border border-gray-100 flex items-center gap-1.5">
                          <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />
                          <span className="text-[9px] font-bold text-gray-500 whitespace-nowrap">{org.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 bg-green-50/50 p-3 rounded-xl border border-green-100">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <p className="text-[10px] font-bold text-green-700">Todas las organizaciones completadas</p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex-1 min-h-0">
              <ProgressTracker
                steps={STEPS}
                currentStep={currentStep}
                completedQuestions={completedQuestions}
                totalQuestions={totalQuestions}
                isFinished={form.isCompleted}
              />
            </div>
          </div>

          <div className="lg:col-span-8">
            <div className="bg-white rounded-[2.5rem] shadow-xl shadow-causante-ocre/5 border border-gray-50 overflow-hidden lg:h-[620px] flex flex-col">
              <div className="flex-1 overflow-y-auto p-6 sm:p-10 custom-scrollbar">
                {form.isCompleted ? (
                  /* ── Completed state view ─────────────────────────────────── */
                  <div className="h-full flex flex-col items-center justify-center text-center py-8 space-y-8">
                    {/* Badge */}
                    <div className="flex flex-col items-center gap-3">
                      <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center shadow-inner">
                        <Check className="w-8 h-8 text-green-600 stroke-[3]" />
                      </div>
                      <div>
                        <h3 className="text-xl font-black text-gray-900 tracking-tight">Ficha completada</h3>
                        <p className="text-sm text-gray-400 mt-1">
                          {organizations.find(o => o.id === selectedOrg)?.name}
                        </p>
                      </div>
                    </div>

                    {/* Data summary */}
                    <div className="w-full max-w-xs grid grid-cols-2 gap-2.5 text-left">
                      {[
                        { label: 'Tipo', value: form.identityV2?.startsWith('Organización') ? 'Formal (Asoc./Fund.)' : form.identityV2?.startsWith('Empresa') ? 'Empresa (SAC/SRL)' : form.identityV2?.startsWith('Colectivo') ? 'Colectivo' : null },
                        { label: 'Propósito', value: form.orgPurpose === 'Otro' ? form.orgPurposeOther || 'Otro' : form.orgPurpose },
                        { label: 'SUNAT', value: form.sunatV2?.startsWith('Tengo RUC y está al día') ? 'RUC activo' : form.sunatV2?.startsWith('Tengo RUC, pero') ? 'RUC con problemas' : form.sunatV2?.startsWith('No tengo RUC') ? 'Sin RUC' : form.sunatV2?.startsWith('No estoy') ? 'Desconocido' : null },
                        { label: 'Urgencia', value: form.urgencyV2?.startsWith('Urgente') ? '🔴 Urgente' : form.urgencyV2?.startsWith('Medio') ? '🟡 Medio' : form.urgencyV2?.startsWith('Informativa') ? '🟢 Explorando' : null },
                      ].filter(item => item.value).map(item => (
                        <div key={item.label} className="bg-gray-50 rounded-xl px-3 py-2.5">
                          <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wide">{item.label}</p>
                          <p className="text-xs font-semibold text-gray-700 mt-0.5 leading-tight">{item.value}</p>
                        </div>
                      ))}
                    </div>

                    {/* Error */}
                    {submitError && (
                      <p className="text-xs text-red-600 font-medium bg-red-50 border border-red-100 rounded-xl px-4 py-2 max-w-xs">{submitError}</p>
                    )}

                    {/* CTA buttons */}
                    <div className="flex flex-col items-center gap-3 w-full max-w-xs">
                      <button
                        onClick={handleGenerateDiagnostic}
                        disabled={isSubmitting}
                        className={clsx(
                          'w-full px-6 py-3.5 rounded-2xl font-black text-[10px] tracking-widest transition-all shadow-lg flex items-center justify-center gap-2 uppercase',
                          isSubmitting
                            ? 'bg-gray-100 text-gray-400 shadow-none cursor-not-allowed'
                            : 'bg-causante-ocre text-white hover:bg-opacity-90 active:scale-[0.98] shadow-causante-ocre/20'
                        )}
                      >
                        {isSubmitting ? (
                          <><RefreshCw className="w-3.5 h-3.5 animate-spin" /> Generando...</>
                        ) : (
                          <>Generar diagnóstico <ChevronRight className="w-3.5 h-3.5" /></>
                        )}
                      </button>
                      <button
                        onClick={handleResetForm}
                        disabled={isSubmitting}
                        className="w-full px-6 py-3 rounded-2xl font-bold text-[10px] tracking-widest text-gray-500 bg-gray-50 hover:bg-gray-100 border border-gray-100 transition-all flex items-center justify-center gap-2 uppercase disabled:opacity-50"
                      >
                        <Pencil className="w-3.5 h-3.5" />
                        Editar datos
                      </button>
                    </div>
                  </div>
                ) : (
                  stepRenderers[currentStep]()
                )}
              </div>

              {/* Navigation Footer — hidden when form is completed */}
              {!form.isCompleted && (
                <div className="px-6 sm:px-10 py-6 bg-gray-50/50 border-t border-gray-50 flex items-center justify-between">
                  <button
                    onClick={goPrev}
                    disabled={currentStep === 0}
                    className={clsx(
                      'flex items-center gap-3 text-sm font-black uppercase tracking-widest transition-all',
                      currentStep === 0 ? 'text-gray-200 cursor-not-allowed' : 'text-gray-500 hover:text-gray-900'
                    )}
                  >
                    <ChevronLeft className="w-6 h-6" />
                    Anterior
                  </button>

                  <div className="flex items-center gap-2">
                    {STEPS.map((_, i) => (
                      <div
                        key={i}
                        className={clsx(
                          'h-1.5 rounded-full transition-all duration-700',
                          i === currentStep ? 'w-8 bg-causante-ocre shadow-lg shadow-causante-ocre/30' : 'w-1.5 bg-gray-200'
                        )}
                      />
                    ))}
                  </div>

                  {isLastStep ? (
                    <button
                      onClick={handleSubmit}
                      disabled={isSubmitting || completedQuestions < totalQuestions || !form.hasConfirmed}
                      className={clsx(
                        'px-8 py-4 rounded-2xl font-black text-[10px] tracking-widest transition-all shadow-lg flex items-center gap-2 uppercase',
                        (isSubmitting || completedQuestions < totalQuestions || !form.hasConfirmed)
                          ? 'bg-gray-100 text-gray-400 shadow-none cursor-not-allowed'
                          : 'bg-causante-ocre text-white hover:bg-opacity-90 active:scale-[0.98] shadow-causante-ocre/20'
                      )}
                    >
                      {isSubmitting ? 'PROCESANDO...' : 'COMPLETAR FICHA'}
                      {!isSubmitting && <ChevronRight className="w-4 h-4" />}
                    </button>
                  ) : (
                    <button
                      onClick={goNext}
                      disabled={isLastStep}
                      className={clsx(
                        'flex items-center gap-3 text-sm font-black uppercase tracking-widest transition-all',
                        isLastStep ? 'text-gray-200 cursor-not-allowed' : 'text-causante-ocre hover:opacity-70'
                      )}
                    >
                      Siguiente
                      <ChevronRight className="w-6 h-6" />
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
