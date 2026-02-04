import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, Fingerprint, Gavel, Banknote, Users, BookOpen, Network, Lightbulb, Info, Lock, Check, X, Building2, Landmark, Home, LucideIcon } from 'lucide-react'
import { OrganizationCard } from './OrganizationCard'
import { ProgressTracker } from './ProgressTracker'
import { FormBlock } from './FormBlock'
import { YesNoButtons, SingleSelect, MultiSelectChips } from './FormInputs'

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
  hiringModalities: [],
  contractsValid: null,
  hasAccountingRecords: null,
  accountingRecordsDetail: null,
  availableDocuments: [],
  governanceBodies: null,
  hasLegalRepresentative: null,
  intangibleAssets: [],
}

export function LegalFormPage() {
  const navigate = useNavigate()
  const [selectedOrg, setSelectedOrg] = useState<string>('1')
  const [form, setForm] = useState<FormState>(initialFormState)

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
    if (form.hiringModalities.length > 0) block4++
    if (form.contractsValid !== null) block4++

    // Block 5
    if (form.hasAccountingRecords !== null) block5++
    if (form.availableDocuments.length > 0) block5++

    // Block 6
    if (form.governanceBodies !== null) block6++
    if (form.hasLegalRepresentative !== null) block6++

    // Block 7
    if (form.intangibleAssets.length > 0) block7++

    return { block1, block2, block3, block4, block5, block6, block7 }
  }

  const completed = calculateCompleted()

  const BLOCKS = [
    { id: 'identity', name: 'Identidad', icon: Fingerprint, color: 'blue', completed: completed.block1, total: 3 },
    { id: 'formalization', name: 'Formalización', icon: Gavel, color: 'purple', completed: completed.block2, total: 3 },
    { id: 'income', name: 'Fuentes de Ingreso', icon: Banknote, color: 'green', completed: completed.block3, total: 3 },
    { id: 'hr', name: 'Recursos Humanos', icon: Users, color: 'orange', completed: completed.block4, total: 2 },
    { id: 'accounting', name: 'Info Contable', icon: BookOpen, color: 'teal', completed: completed.block5, total: 2 },
    { id: 'governance', name: 'Gobernanza', icon: Network, color: 'indigo', completed: completed.block6, total: 2 },
    { id: 'intangibles', name: 'Intangibles', icon: Lightbulb, color: 'pink', completed: completed.block7, total: 1 },
  ]

  const totalQuestions = BLOCKS.reduce((acc, block) => acc + block.total, 0)
  const completedQuestions = BLOCKS.reduce((acc, block) => acc + block.completed, 0)

  const handleBack = () => {
    navigate('/chat')
  }

  const updateForm = <K extends keyof FormState>(field: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }))
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
            {MOCK_ORGANIZATIONS.map((org) => (
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
                      className="w-full rounded-xl border-yellow-300 bg-yellow-50 text-sm py-3 px-4 focus:ring-yellow-400 focus:border-yellow-400"
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
                      className="w-full rounded-xl border-gray-200 text-sm py-3 px-4"
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
                      className="w-full rounded-xl border-yellow-300 bg-yellow-50 text-sm py-3 px-4 focus:ring-yellow-400 focus:border-yellow-400"
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
                      className="w-full rounded-xl border-gray-200 text-sm py-3 px-4"
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
                  />
                </div>
              </div>
            </FormBlock>

            {/* Block 4: Human Resources */}
            <FormBlock
              title="4. Recursos humanos"
              icon={Users}
              iconColor="orange"
              completed={completed.block4}
              total={2}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.hiringModalities.length > 0)}>10</span>
                      <span className="text-sm font-semibold">¿Existen registros contables de los últimos 2 años?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <MultiSelectChips
                    options={['Donaciones', 'Venta de servicios o productos', 'Fondos públicos', 'Fondos privados']}
                    value={form.hiringModalities}
                    onChange={(val) => updateForm('hiringModalities', val)}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.contractsValid !== null)}>11</span>
                      <span className="text-sm font-semibold">¿Los contratos o acuerdos están actualmente vigentes?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <SingleSelect
                    options={['Sí', 'No', 'No aplica']}
                    value={form.contractsValid}
                    onChange={(val) => updateForm('contractsValid', val)}
                    columns={3}
                  />
                </div>
              </div>
            </FormBlock>

            {/* Block 5: Accounting */}
            <FormBlock
              title="5. Información contable y administrativa"
              icon={BookOpen}
              iconColor="teal"
              completed={completed.block5}
              total={2}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.hasAccountingRecords !== null)}>12</span>
                      <span className="text-sm font-semibold">¿Existen registros contables o financieros?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <div className="flex justify-between w-full">
                    <button
                      type="button"
                      onClick={() => {
                        updateForm('hasAccountingRecords', 'Sí')
                        if (form.accountingRecordsDetail === null) {
                          updateForm('accountingRecordsDetail', 'Completos')
                        }
                      }}
                      className={`p-3 rounded-xl text-xs font-medium transition-all text-center flex items-center justify-center gap-2 ${form.hasAccountingRecords === 'Sí'
                        ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                        : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50'
                        }`}
                      style={{ width: '201px', height: '73px' }}
                    >
                      <Check className={`w-4 h-4 ${form.hasAccountingRecords === 'Sí' ? 'text-green-500' : 'text-gray-400'}`} />
                      Sí
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        updateForm('hasAccountingRecords', 'No')
                        updateForm('accountingRecordsDetail', null)
                      }}
                      className={`p-3 rounded-xl text-xs font-medium transition-all text-center flex items-center justify-center gap-2 ${form.hasAccountingRecords === 'No'
                        ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                        : 'border border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        }`}
                      style={{ width: '201px', height: '73px' }}
                    >
                      <X className={`w-4 h-4 ${form.hasAccountingRecords === 'No' ? 'text-red-400' : 'text-gray-400'}`} />
                      No
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        updateForm('hasAccountingRecords', 'En proceso')
                        updateForm('accountingRecordsDetail', null)
                      }}
                      className={`p-3 rounded-xl text-xs font-medium transition-all text-center ${form.hasAccountingRecords === 'En proceso'
                        ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                        : 'border border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        }`}
                      style={{ width: '201px', height: '73px' }}
                    >
                      En proceso
                    </button>
                  </div>
                  {form.hasAccountingRecords === 'Sí' && (
                    <div className="grid grid-cols-2 gap-3 mt-3">
                      <button
                        type="button"
                        onClick={() => updateForm('accountingRecordsDetail', 'Completos')}
                        className={`p-3 rounded-xl text-xs font-medium transition-all text-center ${form.accountingRecordsDetail === 'Completos'
                          ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                          : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50'
                          }`}
                        style={{ width: '151px', height: '55px' }}
                      >
                        Completos
                      </button>
                      <button
                        type="button"
                        onClick={() => updateForm('accountingRecordsDetail', 'Parciales')}
                        className={`p-3 rounded-xl text-xs font-medium transition-all text-center ${form.accountingRecordsDetail === 'Parciales'
                          ? 'border-2 border-yellow-400 bg-yellow-50 text-yellow-800'
                          : 'border border-gray-200 hover:border-yellow-300 hover:bg-yellow-50'
                          }`}
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
                      <span className={getQuestionNumberClass(form.availableDocuments.length > 0)}>13</span>
                      <span className="text-sm font-semibold">¿La organización cuenta con alguno de los siguientes documentos?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <MultiSelectChips
                    options={['Estatuto o acta de constitución', 'Libros de actas', 'Estados financieros', 'Ninguno']}
                    value={form.availableDocuments}
                    onChange={(val) => updateForm('availableDocuments', val)}
                  />
                </div>
              </div>
            </FormBlock>

            {/* Block 6: Governance */}
            <FormBlock
              title="6. Gobernanza y representación"
              icon={Network}
              iconColor="indigo"
              completed={completed.block6}
              total={2}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.governanceBodies !== null)}>14</span>
                      <span className="text-sm font-semibold">¿La organización tiene órganos de gobierno definidos (asamblea, consejo, directorio, etc.)?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <YesNoButtons
                    value={form.governanceBodies}
                    onChange={(val) => updateForm('governanceBodies', val)}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.hasLegalRepresentative !== null)}>15</span>
                      <span className="text-sm font-semibold">¿Existe una persona designada como representante legal?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <SingleSelect
                    options={['Sí', 'No', 'En trámite']}
                    value={form.hasLegalRepresentative}
                    onChange={(val) => updateForm('hasLegalRepresentative', val)}
                    columns={3}
                  />
                </div>
              </div>
            </FormBlock>

            {/* Block 7: Intangibles */}
            <FormBlock
              title="7. Uso de intangibles y datos"
              icon={Lightbulb}
              iconColor="pink"
              completed={completed.block7}
              total={1}
            >
              <div className="space-y-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <span className={getQuestionNumberClass(form.intangibleAssets.length > 0)}>16</span>
                      <span className="text-sm font-semibold">¿La organización utiliza alguno de los siguientes?</span>
                    </label>
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                  </div>
                  <MultiSelectChips
                    options={['Software propio', 'Software de terceros', 'Bases de datos de usuarios', 'Marca o símbolos distintivos', 'Ninguno']}
                    value={form.intangibleAssets}
                    onChange={(val) => updateForm('intangibleAssets', val)}
                  />
                </div>
              </div>
            </FormBlock>

            {/* Confirmation Block */}
            <section className="bg-yellow-50 border-2 border-yellow-200 rounded-2xl p-8">
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
                  <button className="flex-1 py-4 bg-white border border-gray-200 rounded-xl font-bold hover:bg-gray-50">
                    No, revisar
                  </button>
                  <button className="flex-1 py-4 bg-yellow-400 text-white font-bold rounded-xl shadow-lg shadow-yellow-200 hover:bg-yellow-500">
                    Sí, continuar
                  </button>
                </div>
              </div>
            </section>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex flex-col items-center gap-4 pb-20">
          <button
            className={`w-full max-w-md py-6 rounded-2xl flex flex-col items-center justify-center gap-1 transition-all ${completedQuestions === totalQuestions
              ? 'bg-yellow-400 text-white cursor-pointer hover:bg-yellow-500'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            disabled={completedQuestions !== totalQuestions}
          >
            <div className="flex items-center gap-2">
              <Lock className="w-5 h-5" />
              <span className="text-lg font-bold">Completar Ficha</span>
            </div>
            <span className="text-xs uppercase tracking-widest font-bold">
              {completedQuestions === totalQuestions
                ? 'Listo para generar'
                : `Faltan ${totalQuestions - completedQuestions} preguntas por responder`}
            </span>
          </button>
          <p className="text-xs text-gray-400 uppercase font-bold tracking-widest text-center px-8">
            Debes completar todos los campos obligatorios para finalizar
          </p>
        </div>
      </main>
    </div>
  )
}
