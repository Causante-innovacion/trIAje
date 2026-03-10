"""
Chat Feature - Configuración editable de intenciones, gatillos y semáforo.

Este archivo centraliza todas las reglas de clasificación del sistema.
Para agregar, modificar o eliminar intenciones o gatillos, editar las tablas de abajo.
No requiere cambios de código en el clasificador ni en el servicio.
"""

from enum import Enum
from typing import Dict, List
from pydantic import BaseModel


# =============================================================================
# ENUMS
# =============================================================================

class Intention(str, Enum):
    """Las 13 intenciones del sistema GPT Legal (Fase 2)."""
    FORMALIZACION = "formalizacion"
    IDENTIDAD_RUC = "identidad_ruc"
    DONACIONES = "donaciones"
    TRIBUTACION = "tributacion"
    CONTRATACION = "contratacion"
    PROPIEDAD_INTELECTUAL = "propiedad_intelectual"
    DATOS_PERSONALES = "datos_personales"
    PREPARACION_ASESORIA = "preparacion_asesoria"
    GOBERNANZA = "gobernanza"
    ALIANZAS = "alianzas"
    PERMISOS = "permisos"
    MARCA_IDENTIDAD = "marca_identidad"
    SEGURIDAD_INFORMACION = "seguridad_informacion"
    FUERA_DE_ALCANCE = "fuera_de_alcance"


class Semaphore(str, Enum):
    """Semáforo de clasificación de riesgo."""
    VERDE = "verde"
    AMARILLO = "amarillo"
    ROJO = "rojo"


# =============================================================================
# MODELOS DE CONFIGURACIÓN
# =============================================================================

class IntentionConfig(BaseModel):
    """Configuración de una intención."""
    id: Intention
    name: str
    description: str
    keywords: List[str]
    example_questions: List[str]


class GatilloConfig(BaseModel):
    """Configuración de un gatillo (trigger) que activa ROJO."""
    intention: Intention
    trigger_phrases: List[str]
    derivation_reason: str


class AmberContextField(BaseModel):
    """Dato mínimo requerido para resolver un caso AMARILLO."""
    intention: Intention
    field_name: str
    field_description: str
    example_prompt: str
    trigger_keywords: List[str] = []  # Si definidos, el campo solo aplica si alguno aparece en el mensaje


# =============================================================================
# TABLA DE INTENCIONES (editable)
# =============================================================================

INTENTIONS: Dict[Intention, IntentionConfig] = {
    Intention.FORMALIZACION: IntentionConfig(
        id=Intention.FORMALIZACION,
        name="Formalización y Registros",
        description="Procesos de creación de existencia legal: constitución de asociaciones civiles, fundaciones, comités e inscripción en SUNARP.",
        keywords=[
            "asociación civil", "fundación", "comité", "constituir", "inscripción",
            "SUNARP", "personería jurídica", "estatuto", "escritura pública",
            "registros públicos", "reserva de nombre", "formalizar", "constitución",
            "formalizacion", "formalización", "formalizar empresa", "constituir empresa",
            "crear empresa", "crear asociacion", "registrar empresa", "registrar asociacion",
        ],
        example_questions=[
            "¿Cómo constituyo una asociación civil?",
            "¿Qué debe incluir el estatuto?",
            "¿Cómo pido reserva de nombre en SUNARP?",
        ],
    ),
    Intention.IDENTIDAD_RUC: IntentionConfig(
        id=Intention.IDENTIDAD_RUC,
        name="Identidad Tributaria y RUC",
        description="Obtención del RUC, modificación de datos en ficha RUC, baja provisional o definitiva, reactivación de RUC, y transición entre persona natural y jurídica.",
        keywords=[
            "RUC", "SUNAT", "ficha RUC", "domicilio fiscal", "representante legal",
            "registro contribuyente", "clave SOL", "persona natural", "persona jurídica",
            "inscripción tributaria", "baja de RUC", "baja provisional", "baja temporal",
            "dar de baja", "suspensión de RUC", "cancelación de RUC", "reactivar RUC",
            "estado baja", "baja definitiva", "reactivación de RUC",
        ],
        example_questions=[
            "¿Qué documentos necesito para sacar RUC?",
            "¿Plazo para actualizar domicilio fiscal?",
            "Diferencia entre RUC 10 y RUC 20",
        ],
    ),
    Intention.DONACIONES: IntentionConfig(
        id=Intention.DONACIONES,
        name="Donaciones y Cooperación",
        description="Recepción de fondos, registro ante APCI, emisión de certificados de donación, cumplimiento de Ley 32301.",
        keywords=[
            "donación", "cooperación", "APCI", "ONGD", "fondos", "subvención",
            "certificado donación", "cooperación internacional", "CTI", "ENIEX",
            "IPREDA", "crowdfunding", "transparencia",
        ],
        example_questions=[
            "¿Qué es una ONGD?",
            "¿Es obligatorio estar en APCI?",
            "¿Cómo emito un certificado de donación?",
        ],
    ),
    Intention.TRIBUTACION: IntentionConfig(
        id=Intention.TRIBUTACION,
        name="Tributación para Sostenibilidad",
        description="Gestión de la exoneración del IR, aplicación del IGV en operaciones comerciales, sostenibilidad de organizaciones sin fines de lucro.",
        keywords=[
            "impuesto", "renta", "IGV", "exoneración", "tributación", "OSAL",
            "sin fines de lucro", "beneficio tributario", "formulario 2119",
            "declaración jurada", "UIT",
        ],
        example_questions=[
            "¿Qué es el beneficio de exoneración?",
            "¿Cómo pido la exoneración del IR?",
            "¿Vigencia de la exoneración?",
        ],
    ),
    Intention.CONTRATACION: IntentionConfig(
        id=Intention.CONTRATACION,
        name="Contratación, Voluntariado y Locación",
        description="Diferenciación entre formas de vinculación: laboral, voluntariado, locación de servicios, modalidades formativas.",
        keywords=[
            "voluntariado", "voluntario", "contrato", "locación de servicios",
            "modalidad formativa", "practicante", "pasantía", "convenio",
            "beneficios sociales", "planilla", "trabajador", "colaborador",
            "sunafil", "denuncia laboral", "demanda laboral", "despido",
            "inspección laboral",
        ],
        example_questions=[
            "¿Qué es el voluntariado?",
            "¿Edad mínima para ser voluntario?",
            "Derechos del voluntario",
        ],
    ),
    Intention.PROPIEDAD_INTELECTUAL: IntentionConfig(
        id=Intention.PROPIEDAD_INTELECTUAL,
        name="Propiedad Intelectual y Confidencialidad",
        description="Protección de activos intangibles: derechos de autor, marcas, confidencialidad, contratos NDA.",
        keywords=[
            "derechos de autor", "propiedad intelectual", "copyright", "marca",
            "logo", "NDA", "confidencialidad", "INDECOPI", "obra",
            "licencia", "plagio", "creación",
        ],
        example_questions=[
            "¿Cómo protejo mis reportajes?",
            "¿Qué son derechos morales?",
            "¿Límite de protección de derechos de autor?",
        ],
    ),
    Intention.DATOS_PERSONALES: IntentionConfig(
        id=Intention.DATOS_PERSONALES,
        name="Datos Personales y Privacidad",
        description="Obligaciones sobre recopilación, almacenamiento y uso de datos personales. Ley 29733 y Reglamento 2025.",
        keywords=[
            "datos personales", "privacidad", "consentimiento", "base de datos",
            "protección de datos", "ANPDP", "datos sensibles", "términos y condiciones",
            "política de privacidad", "oficial de datos",
        ],
        example_questions=[
            "¿Qué es el consentimiento informado?",
            "¿Debo registrar mi base de datos?",
            "¿Qué son datos sensibles?",
        ],
    ),
    Intention.PREPARACION_ASESORIA: IntentionConfig(
        id=Intention.PREPARACION_ASESORIA,
        name="Preparación para Asesoría Legal",
        description="Ordenamiento documental para consultar a un abogado. Checklist y contexto mínimo previo a derivación.",
        keywords=[
            "asesor", "abogado", "reunión", "checklist", "documentos",
            "vigencia de poder", "libros obligatorios", "actas", "preparar caso",
        ],
        example_questions=[
            "¿Qué documentos debo ordenar para un abogado?",
            "¿Cómo pido vigencia de poder?",
            "¿Qué libros son obligatorios?",
        ],
    ),
    Intention.GOBERNANZA: IntentionConfig(
        id=Intention.GOBERNANZA,
        name="Gobernanza Interna y Conflictos",
        description="Estructura de órganos de gobierno, quórum, exclusión de asociados, validez de acuerdos.",
        keywords=[
            "gobernanza", "asamblea", "quórum", "directiva", "elección",
            "exclusión", "impugnar", "acuerdo", "estatuto", "socio",
            "presidente", "consejo directivo",
        ],
        example_questions=[
            "¿Quórum para asamblea?",
            "¿Cómo se excluye a un socio?",
            "¿Puedo impugnar un acuerdo?",
        ],
    ),
    Intention.ALIANZAS: IntentionConfig(
        id=Intention.ALIANZAS,
        name="Contratos, Alianzas y Consorcios",
        description="Formalización de acuerdos entre organizaciones, consorcios, convenios de colaboración.",
        keywords=[
            "consorcio", "alianza", "convenio", "asociación en participación",
            "contrato asociativo", "proyecto conjunto", "colaboración",
        ],
        example_questions=[
            "¿Qué es un consorcio?",
            "¿Debo registrar el consorcio?",
            "Responsabilidad en la alianza",
        ],
    ),
    Intention.PERMISOS: IntentionConfig(
        id=Intention.PERMISOS,
        name="Permisos y Regulación Sectorial",
        description="Requisitos para actividades reguladas: eventos, trabajo con menores, educación, salud.",
        keywords=[
            "permiso", "TUPA", "municipalidad", "evento", "espectáculo público",
            "licencia funcionamiento", "autorización", "regulación",
        ],
        example_questions=[
            "¿Permiso para evento en calle?",
            "¿Qué es espectáculo público?",
            "¿Límite de ruido permitido?",
        ],
    ),
    Intention.MARCA_IDENTIDAD: IntentionConfig(
        id=Intention.MARCA_IDENTIDAD,
        name="Marca, Identidad y Reputación",
        description="Registro de marcas ante INDECOPI, lemas comerciales, defensa ante usurpación de identidad.",
        keywords=[
            "marca", "registro de marca", "nombre comercial", "INDECOPI",
            "lema comercial", "búsqueda fonética", "signo distintivo",
        ],
        example_questions=[
            "¿Requisitos para registrar una marca?",
            "¿Qué es nombre comercial?",
        ],
    ),
    Intention.SEGURIDAD_INFORMACION: IntentionConfig(
        id=Intention.SEGURIDAD_INFORMACION,
        name="Seguridad de la Información",
        description="Protocolos de seguridad para proteger datos, secreto profesional, respuesta ante ataques informáticos.",
        keywords=[
            "seguridad", "ciberseguridad", "hackeo", "delito informático",
            "secreto profesional", "backup", "protección de archivos",
            "acceso", "contraseña",
        ],
        example_questions=[
            "¿Cómo protejo mis archivos?",
            "¿Qué es el secreto profesional?",
        ],
    ),
    Intention.FUERA_DE_ALCANCE: IntentionConfig(
        id=Intention.FUERA_DE_ALCANCE,
        name="Fuera de Alcance",
        description="Consultas que no corresponden al ámbito legal del sistema.",
        keywords=[],
        example_questions=[],
    ),
}


# =============================================================================
# TABLA DE GATILLOS ROJO (editable)
# Para agregar un gatillo: añadir una entrada al dict con la intención correspondiente.
# =============================================================================

GATILLOS: Dict[Intention, List[GatilloConfig]] = {
    Intention.FORMALIZACION: [
        GatilloConfig(
            intention=Intention.FORMALIZACION,
            trigger_phrases=[
                "esquela de observación", "esquela sunarp", "tacha",
                "inscripción denegada", "rechazo sunarp", "rechazo sunat",
                "observación de sunarp", "observación registral",
                "observación de sunat",
            ],
            derivation_reason="Derivar para análisis de la observación/tacha/rechazo registral.",
        ),
        GatilloConfig(
            intention=Intention.FORMALIZACION,
            trigger_phrases=[
                "exige cláusulas en el estatuto", "cláusulas de compliance",
                "cláusulas de auditoría", "cláusula de veto", "destino forzoso de bienes",
                "prohibiciones en estatuto", "donante exige estatuto",
                "gobierno exige estatuto", "entidad exige cláusula",
            ],
            derivation_reason="Derivar: exigencia de cláusulas específicas por entidad externa requiere redacción legal especializada.",
        ),
        GatilloConfig(
            intention=Intention.FORMALIZACION,
            trigger_phrases=[
                "oficial de cumplimiento", "anticorrupción", "LAFT",
                "lavado de activos", "compliance a medida", "compliance estatutario",
                "compliance organizacional",
            ],
            derivation_reason="Derivar: requiere análisis de riesgo y cumplimiento regulatorio especializado.",
        ),
        GatilloConfig(
            intention=Intention.FORMALIZACION,
            trigger_phrases=[
                "redactar estatuto", "redacción del estatuto", "revisar estatuto",
                "redactar minuta", "redacción de minuta", "ajustes para notaría",
                "ajustes para firma notarial", "revisar escritura pública",
                "redactar escritura", "lista para notario",
            ],
            derivation_reason="Derivar: redacción/revisión final de estatuto o escritura pública es asesoría legal específica.",
        ),
        GatilloConfig(
            intention=Intention.FORMALIZACION,
            trigger_phrases=[
                "conflicto entre fundadores", "conflicto interno",
                "pelea entre socios fundadores", "disputa sobre constitución",
                "validez de constitución", "cláusulas atípicas de control",
                "cláusulas de gobernanza conflictivas",
            ],
            derivation_reason="Derivar por conflicto de gobernanza en constitución; requiere mediación/asesoría especializada.",
        ),
    ],
    Intention.IDENTIDAD_RUC: [
        GatilloConfig(
            intention=Intention.IDENTIDAD_RUC,
            trigger_phrases=[
                "requerimiento de sunat", "notificación sunat", "carta inductiva",
                "carta de sunat", "inconsistencia ruc sunarp", "inconsistencia entre ruc",
                "ruc y sunarp no coinciden",
            ],
            derivation_reason="Derivar con copia del requerimiento; requiere análisis de contingencia fiscal.",
        ),
        GatilloConfig(
            intention=Intention.IDENTIDAD_RUC,
            trigger_phrases=[
                "fiscalización de sunat", "fiscalización sunat",
                "cierre temporal", "embargo", "embargo sunat",
                "operamos sin ruc", "ingresos sin ruc",
                "recibimos fondos sin ruc", "emitimos comprobantes sin ruc",
            ],
            derivation_reason="Derivar por riesgo fiscal inminente.",
        ),
        GatilloConfig(
            intention=Intention.IDENTIDAD_RUC,
            trigger_phrases=[
                "ruc cancelado", "ruc rechazado", "ruc en condición anómala",
                "ruc anomalo", "baja definitiva ruc", "ruc dado de baja",
            ],
            derivation_reason="Derivar: requiere análisis de causa y plan de recuperación de RUC.",
        ),
        GatilloConfig(
            intention=Intention.IDENTIDAD_RUC,
            trigger_phrases=[
                "regularizar ingresos sin ruc", "regularizar operaciones sin ruc",
                "operaciones pasadas sin ruc", "ingresos anteriores sin ruc",
                "contratos sin ruc previo",
            ],
            derivation_reason="Derivar: requiere plan integral de regularización con SUNAT.",
        ),
        GatilloConfig(
            intention=Intention.IDENTIDAD_RUC,
            trigger_phrases=[
                "sunarp observó y tramitar ruc", "partida no válida y ruc",
                "sin partida válida tramitar ruc",
            ],
            derivation_reason="Derivar: viabilidad del RUC depende de resolución de observación en SUNARP.",
        ),
    ],
    Intention.DONACIONES: [
        GatilloConfig(
            intention=Intention.DONACIONES,
            trigger_phrases=[
                "fondos internacionales sin apci", "recibí fondos sin apci",
                "recibimos fondos extranjeros sin estar en apci",
                "operamos sin apci", "fondos sin inscripción apci",
            ],
            derivation_reason="Derivar: requiere evaluación de riesgo y plan de regularización ante APCI.",
        ),
        GatilloConfig(
            intention=Intention.DONACIONES,
            trigger_phrases=[
                "fondos extranjeros para marchas",
                "financiamiento de activismo político",
                "fondos para denunciar al estado",
                "auditoría de apci", "auditoría apci",
                "requerimiento de apci", "requerimiento apci",
                "procedimiento en apci", "multa de 500 uit", "multa apci",
                "reporte tardío apci", "observación apci",
            ],
            derivation_reason="Derivar: alto riesgo de infracción (hasta 500 UIT) o procedimiento formal APCI.",
        ),
        GatilloConfig(
            intention=Intention.DONACIONES,
            trigger_phrases=[
                "disputa con donante", "conflicto con donante",
                "donante reclama fondos", "donante objeta uso de fondos",
                "disputa sobre destino de fondos", "conflicto sobre uso de fondos",
            ],
            derivation_reason="Derivar: requiere análisis de contrato y posición legal frente al donante.",
        ),
    ],
    Intention.TRIBUTACION: [
        GatilloConfig(
            intention=Intention.TRIBUTACION,
            trigger_phrases=[
                "dividendo", "bonificación a socios", "retiro de utilidades",
                "reparto de excedentes", "reparto entre socios",
                "fines de lucro en estatuto", "objeto social lucrativo",
                "notificación de reparo", "reparo tributario",
            ],
            derivation_reason="Derivar: causal de pérdida del beneficio tributario.",
        ),
        GatilloConfig(
            intention=Intention.TRIBUTACION,
            trigger_phrases=[
                "requerimiento sunat", "fiscalización sunat", "fiscalizacion sunat",
                "requerimiento sunat exoneración", "fiscalización de exoneración",
                "carta inductiva sunat", "resolución sunat cuestiona",
                "sunat cuestiona exoneración", "sunat cuestiona actividad",
                "notificación sunat", "notificacion sunat",
                "denuncia sunat", "denuncia de sunat", "denuncia ante sunat",
                "multa sunat", "sanción sunat", "sancion sunat",
                "sunat nos denunció", "sunat nos denuncio",
                "auditoría sunat", "auditoria sunat",
                "deuda tributaria coactiva", "cobranza coactiva sunat",
            ],
            derivation_reason="Derivar con copia del requerimiento; requiere defensa técnica ante SUNAT.",
        ),
        GatilloConfig(
            intention=Intention.TRIBUTACION,
            trigger_phrases=[
                "gastos no alineados con fines", "gastos fuera del objeto",
                "gastos ajenos a fines estatutarios", "proyectos no relacionados con objeto social",
            ],
            derivation_reason="Derivar: requiere análisis de cumplimiento normativo y riesgo de reparo.",
        ),
        GatilloConfig(
            intention=Intention.TRIBUTACION,
            trigger_phrases=[
                "regularizar pagos en efectivo", "regularizar sin comprobantes",
                "ingresos no declarados previos", "períodos sin declarar",
                "ingresos pasados sin documentar",
            ],
            derivation_reason="Derivar: requiere plan de regularización y posible reconciliación con SUNAT.",
        ),
        GatilloConfig(
            intention=Intention.TRIBUTACION,
            trigger_phrases=[
                "devolución de igv", "reintegro de igv", "saldo a favor igv",
                "igv en operaciones mixtas", "igv cooperación internacional",
            ],
            derivation_reason="Derivar: requiere análisis detallado de tratamiento tributario mixto.",
        ),
    ],
    Intention.CONTRATACION: [
        GatilloConfig(
            intention=Intention.CONTRATACION,
            trigger_phrases=[
                "sunafil", "denuncia por beneficios sociales",
                "demanda laboral", "carta notarial laboral",
                "conciliación laboral", "inspección sunafil",
                "procedimiento laboral formal",
            ],
            derivation_reason="Derivar: procedimiento laboral formal activo.",
        ),
        GatilloConfig(
            intention=Intention.CONTRATACION,
            trigger_phrases=[
                "despido intempestivo", "despido arbitrario",
                "hostigamiento laboral", "hostigamiento sexual",
                "accidente de voluntario", "accidente laboral",
                "embarazo trabajadora", "licencia por maternidad",
                "ajustes razonables trabajador",
            ],
            derivation_reason="Derivar: requiere especialista en derecho laboral.",
        ),
        GatilloConfig(
            intention=Intention.CONTRATACION,
            trigger_phrases=[
                "trabajador extranjero sin visa", "sin permiso de trabajo",
                "visa turista trabaja", "estatus migratorio vencido",
                "extranjero sin autorización laboral",
            ],
            derivation_reason="Derivar: requiere validación migratoria previa a contratación.",
        ),
        GatilloConfig(
            intention=Intention.CONTRATACION,
            trigger_phrases=[
                "contratar menores de edad", "trabajo con menores de edad",
                "prácticas preprofesionales menores",
                "actividades restringidas menores",
            ],
            derivation_reason="Derivar: requiere cumplimiento de protecciones específicas para menores.",
        ),
    ],
    Intention.PROPIEDAD_INTELECTUAL: [
        GatilloConfig(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            trigger_phrases=[
                "notificación de indecopi", "demanda por infracción de derechos",
                "carta notarial por marca", "carta notarial por derechos",
                "carta por plagio", "reclamo por derechos de autor",
                "conflicto por ip", "filtración de información confidencial",
            ],
            derivation_reason="Derivar: requiere defensa técnica en INDECOPI o proceso judicial.",
        ),
        GatilloConfig(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            trigger_phrases=[
                "redactar contrato de derechos", "revisar contrato de derechos",
                "contrato de cesión de derechos", "revisión contrato freelancer derechos",
                "redacción nda propiedad intelectual",
            ],
            derivation_reason="Derivar: redacción/revisión de contratos de derechos es asesoría legal específica.",
        ),
        GatilloConfig(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            trigger_phrases=[
                "transferencia internacional gdpr", "gdpr datos contenido",
                "lopd", "compliance internacional contenido",
                "transferencia contenido regulación privacidad",
            ],
            derivation_reason="Derivar: requiere análisis de compliance internacional de privacidad.",
        ),
        GatilloConfig(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            trigger_phrases=[
                "estrategia de protección ip", "qué registrar y cómo defender",
                "estrategia de registro de activos", "cómo evitar litigios ip",
                "plan de protección intelectual",
            ],
            derivation_reason="Derivar: diseño de estrategia de protección requiere asesoría legal especializada.",
        ),
    ],
    Intention.DATOS_PERSONALES: [
        GatilloConfig(
            intention=Intention.DATOS_PERSONALES,
            trigger_phrases=[
                "filtración de datos de víctimas", "venta de base de datos",
                "hackeo de base de datos", "hackeo", "brecha de datos",
                "acceso no autorizado datos", "filtración datos",
            ],
            derivation_reason="Derivar: requiere protocolo de incidente y potencial reporte a ANPDP.",
        ),
        GatilloConfig(
            intention=Intention.DATOS_PERSONALES,
            trigger_phrases=[
                "reclamo apdp", "requerimiento apdp", "notificación apdp",
                "auditoría minjus", "notificación de auditoría datos",
                "denuncia usuario datos", "reclamo de titular de datos",
            ],
            derivation_reason="Derivar: procedimiento formal ante ANPDP/Minjus activo.",
        ),
        GatilloConfig(
            intention=Intention.DATOS_PERSONALES,
            trigger_phrases=[
                "redactar política de privacidad", "revisar política de privacidad",
                "redactar términos y condiciones", "mapeo de responsabilidades datos",
                "asesoría política de privacidad", "diseño de política de datos",
            ],
            derivation_reason="Derivar: redacción de políticas de privacidad y T&C es asesoría legal especializada.",
        ),
    ],
    Intention.PREPARACION_ASESORIA: [
        GatilloConfig(
            intention=Intention.PREPARACION_ASESORIA,
            trigger_phrases=[
                "estructurar defensa", "preparar defensa ante requerimiento",
                "cómo defenderme de sunat", "cómo defenderme de sunarp",
                "cómo responder a fiscalización", "estrategia de defensa legal",
            ],
            derivation_reason="Derivar: estructurar defensa ante procedimiento formal es asesoría legal específica.",
        ),
    ],
    Intention.GOBERNANZA: [
        GatilloConfig(
            intention=Intention.GOBERNANZA,
            trigger_phrases=[
                "presidente actúa sin poderes", "actos sin facultades",
                "exceso de facultades", "conflicto grave entre directores",
                "crisis institucional", "conflicto bloquea operación",
                "disputa directivos bloquea",
            ],
            derivation_reason="Derivar: ineficacia de actos ante terceros o bloqueo operativo.",
        ),
        GatilloConfig(
            intention=Intention.GOBERNANZA,
            trigger_phrases=[
                "malversación de fondos", "autocontratación",
                "nepotismo", "abuso de poder directivos",
                "sospecha de fraude interno", "desvío de fondos",
            ],
            derivation_reason="Derivar: sospecha de malversación/fraude requiere actuación legal urgente.",
        ),
        GatilloConfig(
            intention=Intention.GOBERNANZA,
            trigger_phrases=[
                "cambio de figura jurídica", "convertir asociación a fundación",
                "transformar organización", "cambiar tipo de entidad",
            ],
            derivation_reason="Derivar: cambio de forma jurídica requiere asesoría legal especializada.",
        ),
        GatilloConfig(
            intention=Intention.GOBERNANZA,
            trigger_phrases=[
                "redactar cláusulas estatutarias", "revisar cláusulas de voto",
                "redactar cláusulas de exclusión", "modificar cláusulas de control",
                "redacción de estatuto gobernanza",
            ],
            derivation_reason="Derivar: redacción/revisión de cláusulas estatutarias es asesoría legal específica.",
        ),
    ],
    Intention.ALIANZAS: [
        GatilloConfig(
            intention=Intention.ALIANZAS,
            trigger_phrases=[
                "incumplimiento de aliado", "incumplimiento contractual",
                "demanda por daños y perjuicios", "resolución de contrato alianza",
                "demanda relacionada con alianza", "requerimiento por consorcio",
            ],
            derivation_reason="Derivar: conflicto o demanda en alianza requiere asesoría legal.",
        ),
        GatilloConfig(
            intention=Intention.ALIANZAS,
            trigger_phrases=[
                "redactar convenio de cooperación", "redacción legal de convenio",
                "redactar acuerdo multi-actor", "redactar contrato asociativo",
            ],
            derivation_reason="Derivar: redacción legal de convenio multi-actor es asesoría legal específica.",
        ),
    ],
    Intention.PERMISOS: [
        GatilloConfig(
            intention=Intention.PERMISOS,
            trigger_phrases=[
                "evento de más de 3000 personas", "evento masivo",
                "trabajo con niños", "trabajo con menores de edad",
                "niños huérfanos", "menores de edad programa",
            ],
            derivation_reason="Derivar: proceso complejo de seguridad o riesgo con menores.",
        ),
        GatilloConfig(
            intention=Intention.PERMISOS,
            trigger_phrases=[
                "requerimiento de municipio", "notificación municipalidad",
                "sanción de municipio", "requerimiento minsa", "notificación minsa",
                "requerimiento minedu", "sanción de autoridad",
                "clausura", "multa municipal",
            ],
            derivation_reason="Derivar: requerimiento o sanción de autoridad activa requiere defensa.",
        ),
    ],
    Intention.MARCA_IDENTIDAD: [
        GatilloConfig(
            intention=Intention.MARCA_IDENTIDAD,
            trigger_phrases=[
                "carta notarial por marca", "reclamo formal por nombre",
                "amenaza legal por marca", "oposición de tercero",
                "oposición al registro", "alguien usa mi logo",
                "usan mi marca sin permiso", "usurpación de marca",
                "robo de marca", "disputa indecopi marca",
                "procedimiento formal indecopi",
            ],
            derivation_reason="Derivar: reclamo o disputa por marca requiere defensa técnica legal ante INDECOPI.",
        ),
    ],
    Intention.SEGURIDAD_INFORMACION: [
        GatilloConfig(
            intention=Intention.SEGURIDAD_INFORMACION,
            trigger_phrases=[
                "borraron nuestra base de datos", "sabotaje informático",
                "amenaza de hackeo", "borrar archivos",
                "ex-miembro amenaza", "ataque informático",
                "brecha de seguridad", "incidente de seguridad reportado",
            ],
            derivation_reason="Derivar: posible delito informático grave; requiere protocolo de incidente.",
        ),
        GatilloConfig(
            intention=Intention.SEGURIDAD_INFORMACION,
            trigger_phrases=[
                "información confidencial publicada", "información filtrada a tercero",
                "divulgación no autorizada", "secreto divulgado",
            ],
            derivation_reason="Derivar: divulgación de información confidencial requiere actuación legal urgente.",
        ),
        GatilloConfig(
            intention=Intention.SEGURIDAD_INFORMACION,
            trigger_phrases=[
                "redactar nda", "redacción de nda", "política de seguridad redactar",
                "protocolo de incidente redactar", "asesoría política de seguridad",
            ],
            derivation_reason="Derivar: redacción de NDA y políticas de seguridad es asesoría legal especializada.",
        ),
        GatilloConfig(
            intention=Intention.SEGURIDAD_INFORMACION,
            trigger_phrases=[
                "mal uso información por miembro", "miembro divulgó información",
                "aliado usó información indebidamente", "investigar uso indebido información",
            ],
            derivation_reason="Derivar: posible uso indebido por miembro/aliado requiere investigación legal.",
        ),
    ],
}


# =============================================================================
# TABLA DE CONTEXTO MÍNIMO PARA AMARILLO (editable)
# Campos que el sistema debe solicitar antes de responder en Amarillo.
# =============================================================================

AMBER_CONTEXT_FIELDS: Dict[Intention, List[AmberContextField]] = {
    Intention.FORMALIZACION: [
        AmberContextField(
            intention=Intention.FORMALIZACION,
            field_name="tipo_error",
            field_description="Tipo de error en la escritura pública",
            example_prompt="¿Podrías indicarme qué tipo de error tiene la escritura? (ej: error de nombre, de domicilio, de objeto social)",
            trigger_keywords=["error", "rectif", "rechaz", "incorrecto", "equivoc", "corregir escritura", "rectificar escritura"],
        ),
        AmberContextField(
            intention=Intention.FORMALIZACION,
            field_name="fundadores_firma",
            field_description="Situación de los fundadores respecto a la firma",
            example_prompt="¿Cuántos fundadores hay y todos podrán firmar? ¿Alguno tiene impedimento conocido (ausente, extranjería, sin poder)?",
            trigger_keywords=["ausente", "fundador", "desapareci", "no localiz", "no se presenta", "firma", "fundador no puede", "poder notarial"],
        ),
        AmberContextField(
            intention=Intention.FORMALIZACION,
            field_name="etapa_asociacion",
            field_description="Etapa actual de la asociación",
            example_prompt="¿En qué etapa se encuentra la asociación? (no constituida / en proceso / inscrita en SUNARP / ya con RUC)",
            trigger_keywords=["constituir", "inscri", "sunarp", "etapa", "proceso", "empezar", "estan constituidos"],
        ),
        AmberContextField(
            intention=Intention.FORMALIZACION,
            field_name="plazo_critico",
            field_description="Plazo crítico del trámite",
            example_prompt="¿Hay un plazo crítico? ¿Cuándo necesita estar completo el trámite?",
            trigger_keywords=["plazo", "urgente", "cuando", "fecha limite", "vencimiento", "rapido", "ya"],
        ),
        AmberContextField(
            intention=Intention.FORMALIZACION,
            field_name="abogado_gestor",
            field_description="Si ya tienen abogado o gestor",
            example_prompt="¿Ya tienen abogado o gestor? ¿Quién ha llevado los trámites hasta ahora?",
            trigger_keywords=["abogado", "gestor", "notario", "tramite", "quien", "han hecho", "llevan"],
        ),
        AmberContextField(
            intention=Intention.FORMALIZACION,
            field_name="exigencia_externa",
            field_description="Cambios exigidos por entidad externa",
            example_prompt="¿Los cambios en el estatuto son por exigencia de alguien externo? ¿Quién exige y con qué fundamento?",
            trigger_keywords=["donante exige", "exigencia", "requiere clausula", "condicion donante", "fundamento externo", "clausulas exigidas"],
        ),
    ],
    Intention.IDENTIDAD_RUC: [
        AmberContextField(
            intention=Intention.IDENTIDAD_RUC,
            field_name="motivo_baja",
            field_description="Motivo o tipo de la baja en SUNAT",
            example_prompt="¿La baja fue iniciada por SUNAT (de oficio) o la solicitaron ustedes? ¿Es provisional o definitiva?",
            trigger_keywords=["baja", "suspendid", "cancelad", "estado baja", "dado de baja"],
        ),
        AmberContextField(
            intention=Intention.IDENTIDAD_RUC,
            field_name="etapa_tramite",
            field_description="En qué etapa del trámite con SUNAT se encuentra",
            example_prompt="¿En qué etapa del trámite con SUNAT se encuentran actualmente? (ej: recién notificados, en proceso de subsanación, pendiente de resolución)",
            trigger_keywords=["baja", "suspendid", "cancelad", "tramit", "ruc", "reactivar", "ficha"],
        ),
        AmberContextField(
            intention=Intention.IDENTIDAD_RUC,
            field_name="inscripcion_sunarp",
            field_description="Estado de inscripción en SUNARP",
            example_prompt="¿Está inscrita la asociación en SUNARP? ¿Con qué fecha y número de partida?",
            trigger_keywords=["sunarp", "partida", "inscrita", "registrada", "constituida", "partida registral"],
        ),
        AmberContextField(
            intention=Intention.IDENTIDAD_RUC,
            field_name="tiempo_sin_ruc",
            field_description="Tiempo operando sin RUC y comprobantes emitidos",
            example_prompt="¿Cuánto tiempo han operado sin RUC? ¿Han emitido comprobantes o recibido dinero en ese período?",
            trigger_keywords=["sin ruc", "tiempo", "comprobante", "factura", "recibido dinero", "operamos sin"],
        ),
        AmberContextField(
            intention=Intention.IDENTIDAD_RUC,
            field_name="representante_legal",
            field_description="Representante legal ante SUNAT",
            example_prompt="¿Quién será el representante legal ante SUNAT? ¿Es la misma persona inscrita en SUNARP?",
            trigger_keywords=["representante", "quien firma", "representacion", "poder", "cambio representante"],
        ),
        AmberContextField(
            intention=Intention.IDENTIDAD_RUC,
            field_name="domicilio_fiscal",
            field_description="Domicilio fiscal declarado",
            example_prompt="¿Cuál es el domicilio fiscal que declararán? ¿Es donde opera realmente la organización?",
            trigger_keywords=["domicilio", "direccion", "fiscal", "sede", "donde", "lugar"],
        ),
        AmberContextField(
            intention=Intention.IDENTIDAD_RUC,
            field_name="tipo_notificacion_sunat",
            field_description="Si hay notificación formal o es consulta preventiva",
            example_prompt="¿Han recibido notificación o requerimiento formal de SUNAT, o es una consulta preventiva?",
            trigger_keywords=["notificacion", "requerimiento", "carta sunat", "preventiva", "consulta previa"],
        ),
        AmberContextField(
            intention=Intention.IDENTIDAD_RUC,
            field_name="actividad_principal",
            field_description="Actividad principal y secundarias a registrar",
            example_prompt="¿Cuál es la actividad principal que registrarán (CIIU)? ¿Hay actividades secundarias que generen ingresos gravados?",
            trigger_keywords=["actividad", "ciiu", "giro", "secundaria", "gravada", "rubro", "que hacen"],
        ),
    ],
    Intention.DONACIONES: [
        AmberContextField(
            intention=Intention.DONACIONES,
            field_name="tipo_bien",
            field_description="Tipo de bien a recibir del extranjero",
            example_prompt="¿Qué tipo de bienes recibirán? (ej: equipos, alimentos, medicinas, fondos dinerarios)",
            trigger_keywords=["recibir", "bien", "equipo", "material", "mercancia", "importar", "entregan", "especie"],
        ),
        AmberContextField(
            intention=Intention.DONACIONES,
            field_name="origen_donacion",
            field_description="Tipo, monto y origen exacto de la donación",
            example_prompt="¿Cuál es el tipo, monto y origen exacto de la donación? (país, organización donante, propósito declarado)",
            trigger_keywords=["fondos", "cooperacion", "dinero", "transferencia", "financ", "subvencion", "origen", "pais donante"],
        ),
        AmberContextField(
            intention=Intention.DONACIONES,
            field_name="inscripcion_apci",
            field_description="Estado de inscripción en APCI",
            example_prompt="¿Está inscrita la organización en APCI? Si sí, ¿bajo qué modalidad (ONGD, ENIEX, IPREDA) y cuándo vence?",
            trigger_keywords=["apci", "ongd", "eniex", "ipreda", "inscripcion apci", "vigencia apci", "modalidad apci"],
        ),
        AmberContextField(
            intention=Intention.DONACIONES,
            field_name="contrato_donante",
            field_description="Existencia de contrato con el donante",
            example_prompt="¿Hay contrato, acuerdo o carta de intención con el donante? ¿Tiene exigencias específicas (hitos, auditorías, destino forzoso)?",
            trigger_keywords=["contrato", "acuerdo", "carta intencion", "exigencia", "condicion donante", "hitos", "auditoria donante"],
        ),
        AmberContextField(
            intention=Intention.DONACIONES,
            field_name="canal_recepcion",
            field_description="Canal de recepción de fondos",
            example_prompt="¿Cómo se recibirán los fondos? (transferencia bancaria, en especie, a través de canal APCI)",
            trigger_keywords=["recibir fondos", "canal", "transferencia bancaria", "especie", "como llegan", "metodo"],
        ),
        AmberContextField(
            intention=Intention.DONACIONES,
            field_name="plazo_fondos",
            field_description="Plazo para recibir o gastar los fondos",
            example_prompt="¿Hay un plazo crítico para la recepción o el gasto de fondos? ¿Cuándo vence la inscripción APCI?",
            trigger_keywords=["plazo", "vencimiento", "gastar", "ejecutar", "fecha limite", "proximo vencimiento"],
        ),
    ],
    Intention.TRIBUTACION: [
        AmberContextField(
            intention=Intention.TRIBUTACION,
            field_name="actividad_comercial",
            field_description="Detalle de la actividad comercial",
            example_prompt="¿Podrías describir qué tipo de actividad comercial realizan y cómo reinvierten los ingresos en los fines estatutarios?",
            trigger_keywords=["vend", "cobr", "servicio", "actividad", "ingres", "comerci", "factur", "operar", "giro"],
        ),
        AmberContextField(
            intention=Intention.TRIBUTACION,
            field_name="tipo_ingresos",
            field_description="Tipo y volumen de ingresos",
            example_prompt="¿Qué tipo de ingresos genera la organización? (servicios, talleres, ventas, mixto) ¿Cuál es el volumen aproximado?",
            trigger_keywords=["tipo ingres", "volumen", "cuanto ingres", "taller", "servicios cobrados", "ventas"],
        ),
        AmberContextField(
            intention=Intention.TRIBUTACION,
            field_name="frecuencia_ingresos",
            field_description="Frecuencia de generación de ingresos",
            example_prompt="¿Con qué frecuencia se generan estos ingresos? (mensual, por temporadas, ocasional)",
            trigger_keywords=["frecuencia", "mensual", "temporada", "ocasional", "periodicidad", "cada vez", "regularmente"],
        ),
        AmberContextField(
            intention=Intention.TRIBUTACION,
            field_name="monto_anual_ratio",
            field_description="Relación entre ingresos por servicios y donaciones",
            example_prompt="¿Cuál es el monto anual aproximado de ingresos por servicios/ventas versus donaciones?",
            trigger_keywords=["monto", "cuanto", "anual", "proporcion", "porcentaje", "donacion vs", "servicios vs"],
        ),
        AmberContextField(
            intention=Intention.TRIBUTACION,
            field_name="documentacion_destino",
            field_description="Documentación del destino de ingresos",
            example_prompt="¿Está documentado el destino de los ingresos en fines estatutarios? ¿Cómo se registra contablemente?",
            trigger_keywords=["contabilidad", "registro", "destino", "estatutario", "documenta", "fines", "reinvertir"],
        ),
        AmberContextField(
            intention=Intention.TRIBUTACION,
            field_name="monto_operacion",
            field_description="Monto de la operación específica",
            example_prompt="¿Cuál es el monto de la operación o contrato específico que consultas?",
            trigger_keywords=["consultoria", "monto operacion", "importe", "valor", "precio", "cobrar", "cuanto cobra"],
        ),
        AmberContextField(
            intention=Intention.TRIBUTACION,
            field_name="notificacion_sunat_trib",
            field_description="Si hay notificación de SUNAT o es consulta preventiva",
            example_prompt="¿Han recibido notificación o requerimiento de SUNAT, o es una consulta preventiva?",
            trigger_keywords=["notificacion sunat", "requerimiento tributario", "carta inductiva", "sunat notifica", "preventiva"],
        ),
    ],
    Intention.CONTRATACION: [
        AmberContextField(
            intention=Intention.CONTRATACION,
            field_name="funciones_tiempo",
            field_description="Funciones exactas y tiempo de contratación",
            example_prompt="¿Qué funciones realizará exactamente y por cuánto tiempo? ¿Es una tarea puntual o un rol permanente?",
            trigger_keywords=["funciones", "tiempo", "plazo", "cuanto", "contrat", "duracion", "rol", "tarea"],
        ),
        AmberContextField(
            intention=Intention.CONTRATACION,
            field_name="nivel_subordinacion",
            field_description="Nivel de subordinación y condiciones de trabajo",
            example_prompt="¿Habrá horario fijo, supervisión directa o exclusividad? ¿La persona usará herramientas de la organización?",
            trigger_keywords=["horario", "supervision", "herramientas", "exclusiv", "reportar", "subordinacion", "fijo"],
        ),
        AmberContextField(
            intention=Intention.CONTRATACION,
            field_name="cantidad_voluntarios",
            field_description="Cantidad de voluntarios",
            example_prompt="¿Cuántos voluntarios tiene actualmente tu organización?",
            trigger_keywords=["voluntario", "voluntariado", "cuantos voluntarios", "equipo", "colabor"],
        ),
        AmberContextField(
            intention=Intention.CONTRATACION,
            field_name="modalidad_contrato",
            field_description="Modalidad de contratación actual o propuesta",
            example_prompt="¿Bajo qué modalidad están contratados o piensan contratar? (locación de servicios, planilla, convenio de prácticas)",
            trigger_keywords=["contrat", "modalidad", "vinculac", "planilla", "locacion", "locador", "modo contrat"],
        ),
        AmberContextField(
            intention=Intention.CONTRATACION,
            field_name="costo_contratacion",
            field_description="Costo mensual o total de la contratación",
            example_prompt="¿Cuál es el costo mensual o total que se pagará por el servicio o contratación?",
            trigger_keywords=["cuanto pagar", "costo", "monto contrat", "honorario", "sueldo", "remuneracion"],
        ),
        AmberContextField(
            intention=Intention.CONTRATACION,
            field_name="nacionalidad_migratorio",
            field_description="Nacionalidad y estatus migratorio",
            example_prompt="¿Es una contratación nacional o extranjera? Si es extranjero, ¿tiene estatus migratorio claro para trabajar en Perú?",
            trigger_keywords=["extranjero", "migratorio", "visa", "permiso trabajo", "nacional", "nacionalidad"],
        ),
        AmberContextField(
            intention=Intention.CONTRATACION,
            field_name="vinculo_previo",
            field_description="Vínculo familiar o previo con la persona",
            example_prompt="¿Hay relaciones familiares o vínculo previo con la persona a contratar?",
            trigger_keywords=["familiar", "pariente", "vinculo previo", "conocido", "relacion previa"],
        ),
    ],
    Intention.PROPIEDAD_INTELECTUAL: [
        AmberContextField(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            field_name="tipo_activo",
            field_description="Tipo exacto de activo o contenido a proteger",
            example_prompt="¿Qué tipo exacto de activo quieren proteger? (artículo, video, código, marca, diseño, metodología, base de datos)",
            trigger_keywords=["activo", "contenido", "obra", "video", "codigo", "marca", "diseno", "que proteger", "material"],
        ),
        AmberContextField(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            field_name="tipo_contrato",
            field_description="Tipo de contrato con el creador de la obra",
            example_prompt="¿Existe un contrato de trabajo o de servicio con el creador de la obra?",
            trigger_keywords=["obra", "creador", "autor", "fotograf", "contrat", "encargad", "creo", "quien hizo"],
        ),
        AmberContextField(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            field_name="co_creadores",
            field_description="Co-creadores involucrados y sus roles",
            example_prompt="¿Hay co-creadores o socios involucrados? ¿Cuántos y qué rol tiene cada uno?",
            trigger_keywords=["co-creador", "co-autor", "varios creadores", "equipo creo", "juntos", "colaboracion", "multi-actor"],
        ),
        AmberContextField(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            field_name="licencia_uso",
            field_description="Licencia de uso del activo",
            example_prompt="¿Bajo qué tipo de licencia se usará o se está usando el activo? (propia, Creative Commons, GPL, sin licencia)",
            trigger_keywords=["imagen", "foto", "uso", "licencia", "material", "publicar", "usar", "reproduc", "gpl", "agpl"],
        ),
        AmberContextField(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            field_name="uso_activo",
            field_description="Cómo se usará el activo",
            example_prompt="¿Cómo se usará el activo? (solo interno, publicado abiertamente, comercial, bajo licencia a terceros)",
            trigger_keywords=["uso", "publicar", "comercial", "distribuir", "difundir", "como usar"],
        ),
        AmberContextField(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            field_name="alcance_proteccion",
            field_description="Alcance geográfico de la protección",
            example_prompt="¿Se necesita protección solo en Perú o en múltiples países?",
            trigger_keywords=["paises", "internacional", "peru solo", "extranjero", "jurisdiccion", "donde proteger"],
        ),
        AmberContextField(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            field_name="riesgo_conflicto",
            field_description="Riesgo de conflicto con terceros",
            example_prompt="¿Hay riesgo de conflicto o similitud conocida con activos de terceros?",
            trigger_keywords=["similar", "conflicto", "tercero", "otro similar", "competencia", "parecido", "riesgo pi"],
        ),
    ],
    Intention.DATOS_PERSONALES: [
        AmberContextField(
            intention=Intention.DATOS_PERSONALES,
            field_name="tipo_datos_sensibles",
            field_description="Tipo de datos personales y si son sensibles",
            example_prompt="¿Qué tipo de datos maneja exactamente? ¿Hay datos sensibles (salud, origen étnico, religión, orientación sexual, biométricos, de menores)?",
            trigger_keywords=["tipo datos", "datos sensibles", "que datos", "informacion personal", "sensible", "salud", "biologico"],
        ),
        AmberContextField(
            intention=Intention.DATOS_PERSONALES,
            field_name="volumen_datos",
            field_description="Volumen de datos personales tratados",
            example_prompt="¿Aproximadamente cuántos registros de datos personales manejan?",
            trigger_keywords=["base de datos", "registros", "datos", "beneficiari", "cuantas personas", "fichero", "volumen"],
        ),
        AmberContextField(
            intention=Intention.DATOS_PERSONALES,
            field_name="metodo_recopilacion",
            field_description="Cómo se recopilan los datos",
            example_prompt="¿Cómo se recopilan los datos? (formulario presencial, en línea, importados de terceros, entrevistas)",
            trigger_keywords=["recopila", "recoge", "obtiene", "formulario", "como llegan", "importa", "encuesta"],
        ),
        AmberContextField(
            intention=Intention.DATOS_PERSONALES,
            field_name="almacenamiento",
            field_description="Dónde y cómo se almacenan los datos",
            example_prompt="¿Cómo se almacenan actualmente los datos? (Excel, base de datos propia, plataforma de tercero, cloud)",
            trigger_keywords=["almacena", "guarda", "excel", "nube", "cloud", "donde estan", "plataforma datos", "drive"],
        ),
        AmberContextField(
            intention=Intention.DATOS_PERSONALES,
            field_name="control_acceso",
            field_description="Quién tiene acceso a los datos",
            example_prompt="¿Quién tiene acceso a los datos? (solo staff propio, compartido con aliados, acceso externo)",
            trigger_keywords=["acceso", "quien ve", "quien tiene", "personal", "aliado", "compartido datos"],
        ),
        AmberContextField(
            intention=Intention.DATOS_PERSONALES,
            field_name="ubicacion_destino",
            field_description="País destino de transferencia de datos",
            example_prompt="¿A qué país se transferirían los datos? Necesito verificar si tiene nivel adecuado de protección.",
            trigger_keywords=["transferir", "enviar", "compartir pais", "extranjero datos", "internac", "sede externa"],
        ),
        AmberContextField(
            intention=Intention.DATOS_PERSONALES,
            field_name="incidente_previo",
            field_description="Incidente, brecha o reclamo previo",
            example_prompt="¿Ha habido algún incidente, brecha de seguridad o reclamo de titular de datos previo? ¿Cuándo?",
            trigger_keywords=["incidente", "brecha", "filtro", "reclamo datos", "antes", "previo", "ya paso"],
        ),
    ],
    Intention.PREPARACION_ASESORIA: [
        AmberContextField(
            intention=Intention.PREPARACION_ASESORIA,
            field_name="tipo_asesoria",
            field_description="Tipo de asesoría que busca",
            example_prompt="¿Qué tipo de asesoría busca? (formalización, tributaria, laboral, conflicto, situación específica)",
            trigger_keywords=["asesoria", "consulta", "ayuda", "tipo asesoria", "que necesita", "orientacion"],
        ),
        AmberContextField(
            intention=Intention.PREPARACION_ASESORIA,
            field_name="documentacion_actual",
            field_description="Documentación disponible y faltante",
            example_prompt="¿Qué documentación tiene hoy y cuál le falta para estar en orden?",
            trigger_keywords=["documentacion", "documentos", "tiene documentos", "falta", "incompleto", "que tengo"],
        ),
        AmberContextField(
            intention=Intention.PREPARACION_ASESORIA,
            field_name="discrepancias",
            field_description="Discrepancias o contradicciones entre documentos",
            example_prompt="¿Hay discrepancias o contradicciones entre documentos? (ej: estatuto vs. acta, SUNARP vs. SUNAT)",
            trigger_keywords=["discrepancia", "contradiccion", "no coincide", "diferencia", "inconsistente", "contradicen"],
        ),
        AmberContextField(
            intention=Intention.PREPARACION_ASESORIA,
            field_name="situacion_critica",
            field_description="Si hay situación crítica o plazo próximo",
            example_prompt="¿Hay una situación crítica o un plazo próximo? ¿Qué puede pasar si no se actúa a tiempo?",
            trigger_keywords=["plazo", "urgente", "critico", "fecha", "vence", "proximo", "inmediato", "rapido"],
        ),
    ],
    Intention.GOBERNANZA: [
        AmberContextField(
            intention=Intention.GOBERNANZA,
            field_name="motivo_exclusion",
            field_description="Motivo de exclusión del socio",
            example_prompt="¿Cuál es el motivo de la exclusión? ¿Está contemplado en el estatuto?",
            trigger_keywords=["exclu", "expulsar", "retirar socio", "separar", "sacar socio", "miembro"],
        ),
        AmberContextField(
            intention=Intention.GOBERNANZA,
            field_name="fecha_acta",
            field_description="Fecha del acta impugnada",
            example_prompt="¿Cuándo se realizó la asamblea y cuándo se inscribió el acuerdo?",
            trigger_keywords=["asamblea", "acuerdo", "acta", "decision", "votacion", "reunion", "impugnar"],
        ),
        AmberContextField(
            intention=Intention.GOBERNANZA,
            field_name="estructura_organos",
            field_description="Estructura de órganos de la organización",
            example_prompt="¿Cuál es la estructura de órganos actuales? (quién está en la junta, cuántos socios, cómo se toman las decisiones)",
            trigger_keywords=["junta", "directiva", "organos", "socios", "estructura", "quienes dirigen"],
        ),
        AmberContextField(
            intention=Intention.GOBERNANZA,
            field_name="conflicto_especifico",
            field_description="Descripción del conflicto o situación específica",
            example_prompt="¿Cuál es el conflicto o situación específica? ¿Quién está involucrado y qué posiciones tienen?",
            trigger_keywords=["conflicto", "problema", "situacion", "quien involucrado", "disputa", "que paso"],
        ),
        AmberContextField(
            intention=Intention.GOBERNANZA,
            field_name="estatuto_dice",
            field_description="Qué establece el estatuto sobre el tema",
            example_prompt="¿Qué dice el estatuto sobre este tema? ¿Lo han revisado recientemente?",
            trigger_keywords=["estatuto", "dice estatuto", "establece", "previsto en estatuto", "reglamento interno"],
        ),
        AmberContextField(
            intention=Intention.GOBERNANZA,
            field_name="historial_actas",
            field_description="Precedente en asambleas o actas previas",
            example_prompt="¿Hay precedente de asambleas o actas relacionadas con este tema?",
            trigger_keywords=["acta", "asamblea previa", "precedente", "anterior", "ya ocurrio", "decision previa"],
        ),
    ],
    Intention.ALIANZAS: [
        AmberContextField(
            intention=Intention.ALIANZAS,
            field_name="socios_alianza",
            field_description="Socios involucrados en la alianza",
            example_prompt="¿Quiénes son los socios/aliados exactamente? ¿Cuántas organizaciones participan y cuáles son sus roles?",
            trigger_keywords=["socios", "aliados", "organizaciones", "quienes participan", "cuantos", "actores"],
        ),
        AmberContextField(
            intention=Intention.ALIANZAS,
            field_name="tipo_aporte",
            field_description="Tipo de aporte de cada organización",
            example_prompt="¿Qué tipo de aportes realizará cada organización? (fondos, recursos, servicios, know-how)",
            trigger_keywords=["consorcio", "alianza", "aportar", "aporte", "participar", "colaborar", "convenio"],
        ),
        AmberContextField(
            intention=Intention.ALIANZAS,
            field_name="objetivo_proyecto",
            field_description="Objetivo y duración del proyecto conjunto",
            example_prompt="¿Cuál es el proyecto u objetivo compartido? ¿Cuánto tiempo durará?",
            trigger_keywords=["objetivo", "proyecto conjunto", "duracion", "tiempo alianza", "cuanto dura", "que hacen juntos"],
        ),
        AmberContextField(
            intention=Intention.ALIANZAS,
            field_name="fondos_alianza",
            field_description="Fondos involucrados en la alianza",
            example_prompt="¿Hay fondos involucrados? ¿Cuánto, de dónde provienen y cómo se distribuyen entre los aliados?",
            trigger_keywords=["fondos alianza", "dinero", "distribuir fondos", "cuanto fondos", "presupuesto", "de donde fondos"],
        ),
        AmberContextField(
            intention=Intention.ALIANZAS,
            field_name="documentacion_alianza",
            field_description="Documentación actual de la alianza",
            example_prompt="¿Hay documentación actual? (contrato, acuerdo de cooperación, carta de intención, convenio firmado)",
            trigger_keywords=["contrato alianza", "acuerdo", "documentacion", "firmado", "carta intencion"],
        ),
        AmberContextField(
            intention=Intention.ALIANZAS,
            field_name="conflicto_alianza",
            field_description="Conflicto o incumplimiento en la alianza",
            example_prompt="¿Existe conflicto o incumplimiento? ¿Qué ocurrió específicamente y cuándo?",
            trigger_keywords=["conflicto alianza", "incumplimiento", "problema aliado", "disputa", "que paso"],
        ),
        AmberContextField(
            intention=Intention.ALIANZAS,
            field_name="transferencia_datos_fondos",
            field_description="Transferencia de datos o fondos entre aliados",
            example_prompt="¿Se transfiere información sensible o fondos entre los aliados? ¿Cuáles y hacia quién?",
            trigger_keywords=["transferir informacion", "datos aliados", "compartir datos", "entre aliados", "fondos aliados"],
        ),
    ],
    Intention.PERMISOS: [
        AmberContextField(
            intention=Intention.PERMISOS,
            field_name="actividad_exacta",
            field_description="Actividad exacta a realizar",
            example_prompt="¿Cuál es exactamente la actividad que desean realizar? (evento, capacitación, distribución, investigación, servicio)",
            trigger_keywords=["actividad", "evento", "capacitacion", "taller", "que van a hacer", "realizaran", "activar"],
        ),
        AmberContextField(
            intention=Intention.PERMISOS,
            field_name="distrito",
            field_description="Lugar donde se realizará la actividad",
            example_prompt="¿En qué distrito y tipo de espacio se realizará? (espacio público, local privado, institución, virtual)",
            trigger_keywords=["evento", "municipalidad", "permiso", "autorizacion", "licencia", "realizarse", "donde", "lugar"],
        ),
        AmberContextField(
            intention=Intention.PERMISOS,
            field_name="num_participantes",
            field_description="Número estimado de participantes",
            example_prompt="¿Cuántas personas participarán aproximadamente?",
            trigger_keywords=["cuantas personas", "asistentes", "participantes", "aforo", "cuantos", "personas esperan"],
        ),
        AmberContextField(
            intention=Intention.PERMISOS,
            field_name="fecha_horario",
            field_description="Fecha y horario de la actividad",
            example_prompt="¿Cuándo se realizará y en qué horario? ¿Ya está programada la fecha?",
            trigger_keywords=["cuando", "fecha", "horario", "dia", "hora", "programado", "agenda"],
        ),
        AmberContextField(
            intention=Intention.PERMISOS,
            field_name="poblacion_vulnerable",
            field_description="Si involucra menores o población vulnerable",
            example_prompt="¿La actividad involucra menores de edad o población vulnerable? ¿Cuál?",
            trigger_keywords=["menor", "nino", "adolescente", "vulnerable", "discapacidad", "poblacion especial"],
        ),
        AmberContextField(
            intention=Intention.PERMISOS,
            field_name="notificacion_autoridad",
            field_description="Notificación formal de autoridad o consulta preventiva",
            example_prompt="¿Han recibido notificación formal de alguna autoridad (municipio, MINSA, MINEDU), o es una consulta preventiva?",
            trigger_keywords=["notificacion autoridad", "requerimiento municipal", "carta autoridad", "preventiva", "sancion"],
        ),
    ],
    Intention.MARCA_IDENTIDAD: [
        AmberContextField(
            intention=Intention.MARCA_IDENTIDAD,
            field_name="nombre_marca",
            field_description="Nombre o marca exacta a proteger",
            example_prompt="¿Cuál es exactamente el nombre, marca o logo que se quiere proteger o que está en disputa?",
            trigger_keywords=["nombre", "marca", "logo", "identidad", "denominacion", "signo", "que nombre"],
        ),
        AmberContextField(
            intention=Intention.MARCA_IDENTIDAD,
            field_name="organizacion_similar",
            field_description="Organización similar que pueda causar confusión",
            example_prompt="¿Hay otra organización con nombre similar o que pueda confundirse? ¿Cuánto se parecen?",
            trigger_keywords=["similar", "parecido", "confundir", "otra organizacion", "mismo nombre", "se llama igual"],
        ),
        AmberContextField(
            intention=Intention.MARCA_IDENTIDAD,
            field_name="antiguedad",
            field_description="Antigüedad de ambas organizaciones",
            example_prompt="¿Desde cuándo operan ambas organizaciones con ese nombre? ¿Quién fue primero?",
            trigger_keywords=["cuando", "desde", "primero", "antiguedad", "quien comenzo", "tiempo operando"],
        ),
        AmberContextField(
            intention=Intention.MARCA_IDENTIDAD,
            field_name="registro_actual",
            field_description="Estado de registro en SUNARP o INDECOPI",
            example_prompt="¿La organización (o la otra) ya está registrada en SUNARP o en INDECOPI con ese nombre? ¿Cuándo?",
            trigger_keywords=["registrado", "indecopi", "sunarp", "inscrito", "cuando registro", "ya inscrito"],
        ),
        AmberContextField(
            intention=Intention.MARCA_IDENTIDAD,
            field_name="tipo_notificacion_marca",
            field_description="Si hay notificación formal o es consulta preventiva",
            example_prompt="¿Han recibido notificación formal, carta notarial o requerimiento, o es una consulta preventiva?",
            trigger_keywords=["notificacion", "carta notarial marca", "formal", "preventiva", "consulta marca", "alerta"],
        ),
    ],
    Intention.SEGURIDAD_INFORMACION: [
        AmberContextField(
            intention=Intention.SEGURIDAD_INFORMACION,
            field_name="tipo_informacion_sensible",
            field_description="Tipo de información sensible que maneja la organización",
            example_prompt="¿Qué tipo de información sensible maneja la organización? (estrategia, finanzas, datos de beneficiarios, fuentes, contratos)",
            trigger_keywords=["informacion sensible", "tipo informacion", "que datos", "que maneja", "confidencial", "secreto"],
        ),
        AmberContextField(
            intention=Intention.SEGURIDAD_INFORMACION,
            field_name="acceso_personal",
            field_description="Número de personas con acceso a información sensible",
            example_prompt="¿Cuántas personas tienen acceso a la información sensible? ¿Solo staff o también aliados/terceros?",
            trigger_keywords=["cuantas personas acceso", "quien tiene acceso", "personal con acceso", "equipo accede"],
        ),
        AmberContextField(
            intention=Intention.SEGURIDAD_INFORMACION,
            field_name="control_acceso_seguridad",
            field_description="Cómo se documenta el acceso a la información",
            example_prompt="¿Cómo se documenta actualmente quién accede a qué información? (logs, permisos, control manual)",
            trigger_keywords=["documenta acceso", "registro acceso", "log", "control acceso", "quien accede", "permisos"],
        ),
        AmberContextField(
            intention=Intention.SEGURIDAD_INFORMACION,
            field_name="plataformas_compartidas",
            field_description="Plataformas o sistemas compartidos",
            example_prompt="¿Hay plataformas o sistemas compartidos entre el equipo? (Slack, Google Drive, email, bases de datos, CRM)",
            trigger_keywords=["slack", "drive", "email", "sistema", "plataforma", "compartido", "herramienta compartida", "google"],
        ),
        AmberContextField(
            intention=Intention.SEGURIDAD_INFORMACION,
            field_name="incidente_sospecha",
            field_description="Incidente previo o sospecha de brecha",
            example_prompt="¿Ha habido algún incidente o hay sospecha de brecha de seguridad? ¿Cuándo y qué ocurrió?",
            trigger_keywords=["incidente", "brecha", "sospecha", "cuando paso", "que paso seguridad", "detectaron"],
        ),
    ],
}


# =============================================================================
# SALUDOS Y MENSAJES CONVERSACIONALES (editable)
# =============================================================================

GREETING_PATTERNS: List[str] = [
    "hola", "buenos días", "buenos dias", "buenas tardes", "buenas noches",
    "buen día", "buen dia", "saludos", "qué tal", "que tal",
    "hey", "hi", "hello", "ey", "buenas",
]

GREETING_MESSAGE = (
    "¡Hola! 👋 Soy **JUSTO**, tu asistente legal especializado en derecho peruano "
    "para organizaciones civiles.\n\n"
    "Puedo ayudarte con temas como:\n\n"
    "- Formalización y registros (SUNARP)\n"
    "- Identidad tributaria y RUC (SUNAT)\n"
    "- Donaciones y cooperación internacional (APCI)\n"
    "- Tributación para organizaciones sin fines de lucro\n"
    "- Contratación, voluntariado y locación de servicios\n"
    "- Propiedad intelectual y derechos de autor\n"
    "- Protección de datos personales\n"
    "- Gobernanza interna y conflictos\n"
    "- Contratos, alianzas y consorcios\n"
    "- Permisos y regulación sectorial\n"
    "- Marca, identidad y reputación\n"
    "- Seguridad de la información\n\n"
    "¿En qué puedo ayudarte hoy?"
)


# =============================================================================
# MENSAJE FUERA DE ALCANCE (editable)
# =============================================================================

OUT_OF_SCOPE_MESSAGE = (
    "Lo siento, soy un asistente legal especializado en derecho peruano para "
    "organizaciones civiles. No puedo responder preguntas fuera de este ámbito.\n\n"
    "Puedo ayudarte con temas como:\n\n"
    "- Formalización y registros (SUNARP)\n"
    "- Identidad tributaria y RUC (SUNAT)\n"
    "- Donaciones y cooperación internacional (APCI)\n"
    "- Tributación para organizaciones sin fines de lucro\n"
    "- Contratación, voluntariado y locación de servicios\n"
    "- Propiedad intelectual y derechos de autor\n"
    "- Protección de datos personales\n"
    "- Gobernanza interna y conflictos\n"
    "- Contratos, alianzas y consorcios\n"
    "- Permisos y regulación sectorial\n"
    "- Marca, identidad y reputación\n"
    "- Seguridad de la información\n\n"
    "¿Tu consulta está relacionada con alguno de estos temas?"
)


# =============================================================================
# MENSAJE DE DERIVACIÓN ROJO (editable)
# =============================================================================

RED_DERIVATION_TEMPLATE = (
    "⚠️ **ALERTA: Esta consulta requiere atención profesional inmediata.**\n\n"
    "{reason}\n\n"
    "Este sistema no puede brindar asesoría sobre este caso específico porque "
    "involucra riesgos legales que requieren la intervención de un abogado especializado.\n\n"
    "**Para preparar tu reunión con el asesor, ten listos:**\n"
    "- Documentos constitutivos de la organización (estatutos, partida registral)\n"
    "- Descripción escrita del proyecto o situación a tratar\n"
    "- Contratos, acuerdos o comunicaciones relevantes al caso\n"
    "- Estado actual de inscripciones ante SUNARP, SUNAT, APCI (si aplica)\n"
    "- Cualquier notificación o requerimiento oficial recibido\n\n"
    "**¿Qué puedo hacer por ti?**\n"
    "Puedo ayudarte a preparar un paquete completo para el asesor: preguntas clave, "
    "lista de documentos y decisiones previas que debes tomar antes de la reunión. "
    "¿Deseas que lo prepare?"
)


# =============================================================================
# MENSAJE AMARILLO (editable)
# =============================================================================

AMBER_CONTEXT_TEMPLATE = (
    "{partial_answer}\n\n"
    "---\n\n"
    "**Para darte una orientación más precisa sobre tu caso específico, necesito algunos datos adicionales:**\n\n"
    "{questions}\n\n"
    "*Sin confirmar estos datos, la orientación anterior es preliminar y está basada en supuestos generales. "
    "Con tu respuesta podré ajustarla a tu situación concreta.*"
)


# =============================================================================
# DETECTORES DE ANÁLISIS DE PROYECTO (editable)
# Frases que indican que el usuario quiere analizar un proyecto completo.
# =============================================================================

PROJECT_ANALYSIS_TRIGGERS: List[str] = [
    # Con "mi"
    "analizar mi proyecto",
    "evaluar mi proyecto",
    "revisar mi proyecto",
    "viabilidad de mi proyecto",
    "es viable mi proyecto",
    "mi proyecto es legal",
    "quiero formalizar mi proyecto",
    "evaluar mi emprendimiento",
    # Con "el / un / nuestro"
    "analizar el proyecto",
    "evaluar el proyecto",
    "revisar el proyecto",
    "analizar un proyecto",
    "evaluar un proyecto",
    "analizar nuestro proyecto",
    "evaluar nuestro proyecto",
    "revisar nuestro proyecto",
    "viabilidad del proyecto",
    "proyecto es viable",
    # Conjugaciones imperativas / indicativas
    "analiza mi proyecto",
    "analiza el proyecto",
    "analiza nuestro proyecto",
    "evalúa mi proyecto",
    "evalúa el proyecto",
    "revisa mi proyecto",
    # Otros
    "viabilidad legal",
    "evaluar viabilidad",
    "analizar viabilidad",
    "plan de negocio",
    "tengo un proyecto",
    "quiero emprender",
    "quiero formalizar mi proyecto",
]


# =============================================================================
# DISCLAIMERS ESTÁNDAR (editable)
# =============================================================================

STANDARD_DISCLAIMERS: List[str] = [
    "Esta respuesta no constituye asesoría legal vinculante.",
    "La orientación se basa en supuestos generales; puede variar según los detalles específicos de tu caso.",
    "Verifica la información con la normativa vigente o un abogado especializado.",
]


# =============================================================================
# RUTAS DE API (editable — deben coincidir con los prefijos definidos en main.py)
# =============================================================================

ADVISOR_PREP_ENDPOINT: str = "/api/v1/advisor-prep"


# =============================================================================
# PREGUNTAS DE PRE-CLARIFICACIÓN POR INTENCIÓN (editable)
# Una o dos preguntas clave que el sistema hace ANTES de responder cuando la
# consulta es una pregunta general informativa pero el contexto cambia mucho
# la orientación. Solo se activa si no hay señales de caso específico ya.
# =============================================================================

PRE_CLARIFY_QUESTIONS: Dict[Intention, List[str]] = {
    Intention.FORMALIZACION: [
        "¿La organización ya tiene personería jurídica inscrita en la Superintendencia Nacional de los Registros Públicos (SUNARP), o están en proceso de constituirla?",
        "¿Cuál es la actividad principal: presta servicios sin cobro, genera ingresos propios o recibe fondos de terceros (donaciones, convenios)?",
    ],
    Intention.IDENTIDAD_RUC: [
        "¿El Registro Único de Contribuyentes (RUC) que mencionas corresponde a una persona natural o a una persona jurídica (organización)?",
        "¿Cuál es el estado actual del RUC: activo, en baja provisional, dado de baja definitiva u otro?",
    ],
    Intention.DONACIONES: [
        "¿Tu organización opera con fondos nacionales, internacionales o ambos?",
        "¿Están inscritos ante la Agencia Peruana de Cooperación Internacional (APCI) o están evaluando hacerlo?",
    ],
    Intention.TRIBUTACION: [
        "¿La organización opera con o sin fines de lucro según sus estatutos?",
        "¿Cuenta actualmente con la exoneración del Impuesto a la Renta (IR) o está tramitándola?",
    ],
    Intention.CONTRATACION: [
        "¿La persona que quieres vincular recibirá una contraprestación económica regular (sueldo o pago mensual)?",
        "¿Se trata de una actividad temporal o continua dentro de la organización?",
    ],
    Intention.PROPIEDAD_INTELECTUAL: [
        "¿El contenido o marca fue creado por miembros de la organización, por terceros contratados, o es una combinación?",
        "¿Ya tienen algún registro ante el Instituto Nacional de Defensa de la Competencia y de la Protección de la Propiedad Intelectual (INDECOPI) o es la primera vez?",
    ],
    Intention.DATOS_PERSONALES: [
        "¿Los datos personales que manejan provienen de beneficiarios, donantes, voluntarios o de todos ellos?",
        "¿Tienen actualmente alguna política de privacidad o aviso de privacidad publicado?",
    ],
    Intention.GOBERNANZA: [
        "¿La organización tiene una asamblea general activa y una junta directiva vigente con mandato en curso?",
        "¿El conflicto o duda es sobre elecciones internas, toma de decisiones o exclusión de algún miembro?",
    ],
    Intention.ALIANZAS: [
        "¿El acuerdo que buscan es solo de colaboración (sin fondo compartido) o involucra recursos económicos conjuntos?",
        "¿Las partes del acuerdo son organizaciones peruanas, internacionales o ambas?",
    ],
    Intention.PERMISOS: [
        "¿El permiso que necesitan es para un evento puntual o para operar de forma permanente en un local?",
        "¿El trámite es ante una municipalidad, un ministerio o ambos?",
    ],
    Intention.MARCA_IDENTIDAD: [
        "¿Ya realizaron una búsqueda de anterioridad del nombre o logo que quieren registrar?",
        "¿El registro de marca es para el nombre de la organización, un producto/servicio, o ambos?",
    ],
    Intention.SEGURIDAD_INFORMACION: [
        "¿Manejan datos de personas vulnerables (menores, víctimas, beneficiarios de salud)?",
        "¿Ya tienen un protocolo o política interna de seguridad de la información?",
    ],
    Intention.PREPARACION_ASESORIA: [
        "¿La consulta con el asesor es urgente (plazo legal próximo) o es de planificación a futuro?",
        "¿Ya tienen documentos legales básicos (estatutos, actas, contratos) o hay que prepararlos desde cero?",
    ],
}

# Prompt de sistema para el flujo de pre-clarificación
PRE_CLARIFY_SYSTEM_PROMPT = (
    "Eres Justo, un asistente legal especializado en derecho peruano para organizaciones civiles. "
    "Tu tarea en este momento NO es responder la consulta, sino hacer UNA o DOS preguntas breves y precisas "
    "para entender mejor el contexto antes de orientar al usuario. "
    "Las preguntas deben ser directas, comprensibles para personas sin conocimientos legales, "
    "y deben cubrir la información que más cambiaría la orientación legal. "
    "NO respondas la consulta todavía. Solo presenta las preguntas de forma amigable. "
    "Finaliza con una frase breve como: 'Con esa información podré darte una orientación más precisa.' "
    "Responde en español. CRÍTICO: Tu razonamiento interno (dentro de <think>) DEBE estar en español."
)

# Plantilla de introducción para preguntas de pre-clarificación
PRE_CLARIFY_INTRO_TEMPLATE = (
    "Antes de orientarte sobre **{topic}**, necesito entender mejor tu situación. "
    "Esto me permitirá darte una respuesta adaptada a tu caso real:\n\n"
    "{questions}\n\n"
    "Con esas respuestas podré orientarte de forma mucho más precisa. 🙂"
)
