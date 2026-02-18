export interface FormalizationItem {
    title: string
    detail: string
}

export interface FormalizationStage {
    id: string
    number: number
    title: string
    iconType: 'user' | 'mapPin' | 'building' | 'monitor' | 'fileText' | 'globe' | 'briefcase' | 'shield' | 'award' | 'users'
    items: FormalizationItem[]
}

export interface FormalizationRoute {
    id: string
    number: string
    iconType: 'receipt' | 'globe' | 'building2' | 'store' | 'copyright' | 'userCheck'
    title: string
    description: string
    fullTitle: string
    stages: FormalizationStage[]
}

export interface FormalizationPackage {
    organizationName: string
    subtitle: string
    routes: FormalizationRoute[]
}

export const mockFormalizationData: FormalizationPackage = {
    organizationName: 'Archivo de la Memoria Marica del Perú',
    subtitle: 'Ruta personalizada generada en base a la ficha legal completada',
    routes: [
        {
            id: 'ruc',
            number: '01',
            iconType: 'receipt',
            title: 'Obtención de RUC',
            description:
                'Guía completa para el registro tributario de personas naturales y jurídicas ante la SUNAT. Incluye requisitos y formularios.',
            fullTitle: 'Obtención de RUC (Registro Único de Contribuyentes)',
            stages: [
                {
                    id: 'ruc-s1',
                    number: 1,
                    title: 'Requisitos Personales / Representante',
                    iconType: 'user',
                    items: [
                        {
                            title: 'DNI del Representante Legal',
                            detail: 'Original y copia legible para trámites presenciales si fuera necesario.',
                        },
                        {
                            title: 'Vigencia de Poder',
                            detail: 'Documento expedido por SUNARP con una antigüedad no mayor a 30 días calendario.',
                        },
                    ],
                },
                {
                    id: 'ruc-s2',
                    number: 2,
                    title: 'Domicilio Fiscal',
                    iconType: 'mapPin',
                    items: [
                        {
                            title: 'Recibo de Servicios',
                            detail: 'Documento original de luz, agua, telefonía fija o internet con antigüedad no mayor a 2 meses.',
                        },
                        {
                            title: 'Contrato de Alquiler',
                            detail: 'Copia del contrato de alquiler o documento de propiedad debidamente legalizado.',
                        },
                    ],
                },
                {
                    id: 'ruc-s3',
                    number: 3,
                    title: 'Documentación de la Organización',
                    iconType: 'building',
                    items: [
                        {
                            title: 'Acta de Constitución',
                            detail: 'Copia certificada o legalizada del acta donde se funda la organización.',
                        },
                        {
                            title: 'Estatutos',
                            detail: 'Copia de los estatutos aprobados e inscritos formalmente.',
                        },
                        {
                            title: 'Inscripción SUNARP',
                            detail: 'Resolución o constancia de inscripción en los Registros Públicos.',
                        },
                        {
                            title: 'Documentación Adicional',
                            detail: 'Otros documentos de propiedad o vinculación si aplica según el rubro.',
                        },
                    ],
                },
                {
                    id: 'ruc-s4',
                    number: 4,
                    title: 'Pasos en SUNAT Virtual',
                    iconType: 'monitor',
                    items: [
                        {
                            title: 'Pre-inscripción',
                            detail: 'Llenado del Formulario Virtual 2119 a través del portal institucional.',
                        },
                        {
                            title: 'Generación de Clave SOL',
                            detail: 'Obtención de credenciales de acceso para operaciones en línea.',
                        },
                        {
                            title: 'Validación de Datos',
                            detail: 'Confirmación de datos de contacto (correo y celular) y domicilio fiscal.',
                        },
                        {
                            title: 'Programación de Cita',
                            detail: 'Coordinación de cita presencial en centros de atención si el trámite lo requiere.',
                        },
                    ],
                },
            ],
        },
        {
            id: 'apci',
            number: '02',
            iconType: 'globe',
            title: 'Registro APCI',
            description:
                'Gestión y cumplimiento para la Agencia Peruana de Cooperación Internacional. Trámites para ONGs y entidades extranjeras.',
            fullTitle: 'Registro ante la APCI (Agencia Peruana de Cooperación Internacional)',
            stages: [
                {
                    id: 'apci-s1',
                    number: 1,
                    title: 'Elegibilidad y Clasificación',
                    iconType: 'shield',
                    items: [
                        {
                            title: 'Verificación de Naturaleza Jurídica',
                            detail: 'Confirmar que la entidad califica como ENIEX, ONGD o asociación con fondos del exterior según los criterios APCI.',
                        },
                        {
                            title: 'Determinar Tipo de Registro',
                            detail: 'Clasificar entre registro como ONGD nacional, ENIEX extranjera o fuente cooperante según origen de los fondos.',
                        },
                    ],
                },
                {
                    id: 'apci-s2',
                    number: 2,
                    title: 'Documentación Requerida',
                    iconType: 'fileText',
                    items: [
                        {
                            title: 'Escritura Pública de Constitución',
                            detail: 'Copia certificada notarialmente de la escritura pública o estatutos de creación.',
                        },
                        {
                            title: 'Partida Registral Vigente',
                            detail: 'Copia literal de la partida registral emitida por SUNARP con antigüedad no mayor a 30 días.',
                        },
                        {
                            title: 'RUC Vigente',
                            detail: 'Ficha RUC actualizada ante la SUNAT, indicando la actividad principal de la entidad.',
                        },
                        {
                            title: 'Memoria Descriptiva de Actividades',
                            detail: 'Documento que describe los proyectos y actividades de cooperación realizadas o proyectadas.',
                        },
                    ],
                },
                {
                    id: 'apci-s3',
                    number: 3,
                    title: 'Presentación ante APCI',
                    iconType: 'globe',
                    items: [
                        {
                            title: 'Ingreso del Expediente',
                            detail: 'Presentación del expediente físico en la Mesa de Partes de la sede APCI en Lima o vía trámite documentario.',
                        },
                        {
                            title: 'Pago de Derechos',
                            detail: 'Cancelación de la tasa establecida según el TUPA vigente de la APCI.',
                        },
                        {
                            title: 'Número de Expediente',
                            detail: 'Recepción del número de expediente para seguimiento del proceso de inscripción.',
                        },
                    ],
                },
                {
                    id: 'apci-s4',
                    number: 4,
                    title: 'Seguimiento y Resolución',
                    iconType: 'monitor',
                    items: [
                        {
                            title: 'Plazo de Evaluación',
                            detail: 'El plazo regular de evaluación por parte de APCI es de 30 días hábiles desde la admisión.',
                        },
                        {
                            title: 'Subsanación de Observaciones',
                            detail: 'En caso de observaciones, la entidad tiene 5 días hábiles para subsanar la documentación requerida.',
                        },
                        {
                            title: 'Resolución de Inscripción',
                            detail: 'Emisión de la resolución directoral que formaliza el registro en el padrón APCI.',
                        },
                    ],
                },
            ],
        },
        {
            id: 'sunarp',
            number: '03',
            iconType: 'building2',
            title: 'Constitución y SUNARP',
            description:
                'Pasos críticos para la formalización de empresas, elaboración de minutas y registros en los registros públicos.',
            fullTitle: 'Constitución Formal e Inscripción en SUNARP',
            stages: [
                {
                    id: 'sunarp-s1',
                    number: 1,
                    title: 'Elaboración de Minuta',
                    iconType: 'fileText',
                    items: [
                        {
                            title: 'Definición del Tipo de Entidad',
                            detail: 'Determinar si se constituirá como Asociación Civil, Fundación, Comité u otro tipo según el objeto social.',
                        },
                        {
                            title: 'Redacción de Estatutos',
                            detail: 'Elaboración del documento que regula el funcionamiento interno, órganos de gobierno y fines de la organización.',
                        },
                        {
                            title: 'Acta de Asamblea Constitutiva',
                            detail: 'Documento que acredita la reunión fundacional donde se aprueba la creación y los estatutos.',
                        },
                    ],
                },
                {
                    id: 'sunarp-s2',
                    number: 2,
                    title: 'Escritura Pública Notarial',
                    iconType: 'award',
                    items: [
                        {
                            title: 'Elección de Notaría',
                            detail: 'Selección de notario público para la elevación a escritura pública de la minuta de constitución.',
                        },
                        {
                            title: 'Presentación de DNIs de Socios Fundadores',
                            detail: 'Documento de identidad vigente de todos los miembros fundadores que suscribirán la escritura.',
                        },
                        {
                            title: 'Firma de la Escritura',
                            detail: 'Suscripción de la escritura pública ante notario por parte de todos los fundadores o sus apoderados.',
                        },
                    ],
                },
                {
                    id: 'sunarp-s3',
                    number: 3,
                    title: 'Inscripción en Registros Públicos',
                    iconType: 'building',
                    items: [
                        {
                            title: 'Ingreso del Parte Notarial',
                            detail: 'La notaría envía el parte notarial a la Oficina Registral correspondiente de SUNARP.',
                        },
                        {
                            title: 'Pago de Derechos Registrales',
                            detail: 'Cancelación de la tasa de inscripción según el TUPA de SUNARP vigente.',
                        },
                        {
                            title: 'Calificación Registral',
                            detail: 'El registrador público evalúa el título en un plazo de 7 días hábiles.',
                        },
                        {
                            title: 'Asiento Registral',
                            detail: 'Extensión del asiento de inscripción en la Partida Electrónica asignada a la entidad.',
                        },
                    ],
                },
                {
                    id: 'sunarp-s4',
                    number: 4,
                    title: 'Post-inscripción',
                    iconType: 'monitor',
                    items: [
                        {
                            title: 'Obtención de Partida Registral',
                            detail: 'Descarga del CRI (Certificado Registral Inmobiliario) o copia literal de la partida electrónica.',
                        },
                        {
                            title: 'Registro del Representante Legal',
                            detail: 'Inscripción del presidente o representante legal con poderes para vincular a la entidad.',
                        },
                    ],
                },
            ],
        },
        {
            id: 'licencia',
            number: '04',
            iconType: 'store',
            title: 'Licencia de Funcionamiento',
            description:
                'Trámites municipales para la apertura de establecimientos comerciales y certificados de Inspección Técnica (ITSE).',
            fullTitle: 'Licencia Municipal de Funcionamiento',
            stages: [
                {
                    id: 'lic-s1',
                    number: 1,
                    title: 'Requisitos Previos',
                    iconType: 'building',
                    items: [
                        {
                            title: 'Zonificación y Compatibilidad de Uso',
                            detail: 'Verificar que la actividad a desarrollar es compatible con el uso de suelo del inmueble según el plano de zonificación municipal.',
                        },
                        {
                            title: 'Condiciones del Local',
                            detail: 'El establecimiento debe cumplir con las normas técnicas de seguridad en defensa civil y accesibilidad.',
                        },
                    ],
                },
                {
                    id: 'lic-s2',
                    number: 2,
                    title: 'Documentación para la Municipalidad',
                    iconType: 'fileText',
                    items: [
                        {
                            title: 'Solicitud de Licencia',
                            detail: 'Formato de solicitud emitido por la municipalidad correspondiente al distrito donde opera el establecimiento.',
                        },
                        {
                            title: 'Declaración Jurada de Observancia',
                            detail: 'Declaración de cumplimiento de las condiciones de seguridad establecidas por INDECI.',
                        },
                        {
                            title: 'Vigencia de Poder Notarial',
                            detail: 'Para personas jurídicas, presentar vigencia de poder del representante legal.',
                        },
                        {
                            title: 'Plano de Distribución del Local',
                            detail: 'Plano a escala indicando distribución de ambientes, salidas de emergencia y equipos de seguridad.',
                        },
                    ],
                },
                {
                    id: 'lic-s3',
                    number: 3,
                    title: 'Inspección Técnica de Seguridad (ITSE)',
                    iconType: 'shield',
                    items: [
                        {
                            title: 'Solicitud de ITSE',
                            detail: 'Presentación de solicitud ante el CGBVP o municipalidad según el área del establecimiento.',
                        },
                        {
                            title: 'Visita de Inspección',
                            detail: 'Inspectores verifican extintores, señalización de emergencia, salidas y sistemas eléctricos.',
                        },
                        {
                            title: 'Certificado de ITSE',
                            detail: 'Obtención del certificado favorable de inspección técnica, válido por 1 año renovable.',
                        },
                    ],
                },
                {
                    id: 'lic-s4',
                    number: 4,
                    title: 'Emisión de Licencia',
                    iconType: 'award',
                    items: [
                        {
                            title: 'Pago de Tasa Municipal',
                            detail: 'Cancelación del derecho de trámite según el TUPA del municipio correspondiente.',
                        },
                        {
                            title: 'Placa de Licencia',
                            detail: 'Recepción y exhibición obligatoria de la placa de licencia en lugar visible del establecimiento.',
                        },
                    ],
                },
            ],
        },
        {
            id: 'propiedad',
            number: '05',
            iconType: 'copyright',
            title: 'Propiedad Intelectual',
            description:
                'Protección de activos intangibles. Registro de marcas, patentes y derechos de autor ante INDECOPI.',
            fullTitle: 'Registro de Propiedad Intelectual ante INDECOPI',
            stages: [
                {
                    id: 'pi-s1',
                    number: 1,
                    title: 'Identificación de Activos a Proteger',
                    iconType: 'shield',
                    items: [
                        {
                            title: 'Nombres y Logotipos (Marcas)',
                            detail: 'Identificar el nombre comercial, logotipo y slogan que identifican a la organización o sus productos.',
                        },
                        {
                            title: 'Obras Artísticas y Contenidos (Derechos de Autor)',
                            detail: 'Inventariar publicaciones, fotografías, videos, software y materiales creativos generados por la organización.',
                        },
                        {
                            title: 'Desarrollos Técnicos (Patentes)',
                            detail: 'Identificar innovaciones tecnológicas o procedimientos originales susceptibles de patentarse.',
                        },
                    ],
                },
                {
                    id: 'pi-s2',
                    number: 2,
                    title: 'Búsqueda de Antecedentes',
                    iconType: 'monitor',
                    items: [
                        {
                            title: 'Búsqueda de Marcas en INDECOPI',
                            detail: 'Realizar búsqueda en el portal TMSEARCH de INDECOPI para verificar disponibilidad del signo a registrar.',
                        },
                        {
                            title: 'Clases de Niza',
                            detail: 'Determinar en qué clase(s) de la Clasificación Internacional de Niza se registrará la marca según los productos/servicios.',
                        },
                    ],
                },
                {
                    id: 'pi-s3',
                    number: 3,
                    title: 'Presentación de Solicitud',
                    iconType: 'fileText',
                    items: [
                        {
                            title: 'Formulario de Solicitud INDECOPI',
                            detail: 'Completar el formulario de solicitud de registro de marca en la plataforma virtual de INDECOPI.',
                        },
                        {
                            title: 'Reproducción de la Marca',
                            detail: 'Adjuntar imagen del logotipo o signo a registrar en formato digital con especificaciones técnicas requeridas.',
                        },
                        {
                            title: 'Pago de la Tasa',
                            detail: 'Cancelación de la tasa oficial de registro por cada clase de productos o servicios solicitados.',
                        },
                    ],
                },
                {
                    id: 'pi-s4',
                    number: 4,
                    title: 'Proceso de Registro',
                    iconType: 'award',
                    items: [
                        {
                            title: 'Examen de Forma',
                            detail: 'INDECOPI verifica que la solicitud cumple con los requisitos formales en un plazo de 15 días hábiles.',
                        },
                        {
                            title: 'Publicación en Gaceta Electrónica',
                            detail: 'La marca se publica por 30 días para que terceros puedan presentar oposiciones.',
                        },
                        {
                            title: 'Resolución de Registro',
                            detail: 'Emisión del certificado de registro de marca con vigencia de 10 años renovables.',
                        },
                    ],
                },
            ],
        },
        {
            id: 'contratos',
            number: '06',
            iconType: 'userCheck',
            title: 'Contratos Laborales',
            description:
                'Modelos estandarizados y personalizados para la contratación de personal bajo normativa vigente.',
            fullTitle: 'Formalización de Contratos Laborales y de Servicios',
            stages: [
                {
                    id: 'ct-s1',
                    number: 1,
                    title: 'Clasificación del Vínculo',
                    iconType: 'users',
                    items: [
                        {
                            title: 'Relación Laboral (Planilla)',
                            detail: 'Aplicable cuando existe subordinación, horario fijo y exclusividad. Genera beneficios de ley: CTS, gratificaciones, vacaciones.',
                        },
                        {
                            title: 'Locación de Servicios (Recibo por Honorarios)',
                            detail: 'Para prestadores independientes sin subordinación. No genera beneficios laborales pero requiere cuidado en la ejecución para evitar desnaturalización.',
                        },
                        {
                            title: 'Contratos de Voluntariado',
                            detail: 'Regulados por la Ley N° 29094. No generan relación laboral pero deben formalizarse para proteger a ambas partes.',
                        },
                    ],
                },
                {
                    id: 'ct-s2',
                    number: 2,
                    title: 'Registro de Planilla (Si Aplica)',
                    iconType: 'monitor',
                    items: [
                        {
                            title: 'Registro en T-REGISTRO (SUNAT)',
                            detail: 'Alta del empleador y registro de trabajadores en el sistema de planilla electrónica de SUNAT.',
                        },
                        {
                            title: 'Afiliación a EsSalud',
                            detail: 'Todo trabajador en planilla debe estar afiliado al seguro regular de EsSalud (9% del sueldo a cargo del empleador).',
                        },
                        {
                            title: 'Elección del Sistema de Pensiones',
                            detail: 'El trabajador debe elegir entre ONP (13%) o AFP según su preferencia en el momento del ingreso.',
                        },
                    ],
                },
                {
                    id: 'ct-s3',
                    number: 3,
                    title: 'Redacción de Contratos',
                    iconType: 'fileText',
                    items: [
                        {
                            title: 'Cláusulas Esenciales',
                            detail: 'Objeto del contrato, remuneración, jornada de trabajo, lugar de prestación y duración.',
                        },
                        {
                            title: 'Cláusulas de Confidencialidad',
                            detail: 'Protección de información sensible de la organización y de los beneficiarios atendidos.',
                        },
                        {
                            title: 'Cesión de Derechos sobre Creaciones',
                            detail: 'Cláusula que transfiere a la organización los derechos patrimoniales sobre obras creadas en el marco del contrato.',
                        },
                    ],
                },
                {
                    id: 'ct-s4',
                    number: 4,
                    title: 'Registro y Formalización',
                    iconType: 'award',
                    items: [
                        {
                            title: 'Registro de Contratos Sujetos a Modalidad',
                            detail: 'Los contratos a plazo fijo mayores a 1 mes deben registrarse en el Ministerio de Trabajo dentro de los 15 días de su celebración.',
                        },
                        {
                            title: 'Entrega de Boletas de Pago',
                            detail: 'Obligación mensual de entrega de boleta de pago detallada al trabajador, física o digitalmente.',
                        },
                        {
                            title: 'Declaración PDT Planilla Electrónica',
                            detail: 'Presentación mensual de la planilla electrónica (PDT 601) ante SUNAT dentro de los plazos establecidos.',
                        },
                    ],
                },
            ],
        },
    ],
}
