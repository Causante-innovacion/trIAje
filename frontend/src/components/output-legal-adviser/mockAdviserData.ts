import { LegalAdviserPackage } from '../../types/adviser.types'

export const mockAdviserData: LegalAdviserPackage = {
    pageTitle: 'Ruta de preparación para reunión con asesor legal',
    pageSubtitle: 'GENERADA EN BASE A LA FICHA LEGAL Y NECESIDADES',

    organizationProfile: {
        entityName: 'Archivo de la Memoria Marica del Perú',
        legalStatus: 'yellow',
        stage: 'prototipo',
        fundingTypes: ['nacional', 'extranjero']
    },

    legalStatusCards: [
        { id: '1', label: 'SUNARP', status: 'green' },
        { id: '2', label: 'RUC', status: 'yellow' },
        { id: '3', label: 'APCI', status: 'red' }
    ],

    fundingCritical: {
        min: '$10K',
        max: '$50K',
        description: 'Rango de necesidades internacionales proyectadas para el escalamiento del modelo operativo.'
    },

    fundingDescription: 'USD Internacional | Grants & VC',

    criticalTopics: [
        {
            id: '1',
            title: 'Ruta RUC / APCI',
            description: 'Necesidad de definir la estructura tributaria óptima para recibir fondos internacionales en contingencia ante SUNAT.',
            priority: 'URGENTE',
            actionLink: '#',
            actionLabel: 'Ver detalles de Ruta'
        },
        {
            id: '2',
            title: 'Formalización de contratos',
            description: 'Regularización de acuerdos con colaboradores independientes y cesión de derechos sobre activos digitales.',
            priority: 'URGENTE',
            actionLink: '#',
            actionLabel: 'Ver modelos necesarios'
        }
    ],

    lawyerQuestions: [
        {
            id: '1',
            number: 1,
            question: '¿Cuál es el régimen tributario óptimo para una asociación sin fines de lucro que recibe ingresos mixtos?'
        },
        {
            id: '2',
            number: 2,
            question: 'Estrategia de protección para un archivo digital transmedia.'
        },
        {
            id: '3',
            number: 3,
            question: 'Riesgos de desnaturalización de locación de servicios.'
        }
    ],

    requiredDocuments: [
        { id: '1', title: 'Presentar Estatutos', completed: true },
        { id: '2', title: 'Presentar partida registral de SUNARP', completed: false },
        { id: '3', title: 'Presentar contrato de colaboradores', completed: false }
    ],

    internalDecisions: [
        {
            id: '1',
            scenario: 'Escenario A: Registro APCI inmediato',
            options: [
                { id: 'a1', label: 'Opción A: Proceder con equipo interno' },
                { id: 'a2', label: 'Opción B: Contratar consultoría externa' }
            ]
        },
        {
            id: '2',
            scenario: 'Escenario B: Formalización Laboral',
            options: [
                { id: 'b1', label: 'Opción C: Esquema Mixto (Recibos + Planilla)' }
            ]
        }
    ]
}
