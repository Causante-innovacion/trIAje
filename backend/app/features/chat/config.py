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
                "esquela de observación", "tacha", "inscripción denegada",
                "observación de sunarp", "observación registral",
            ],
            derivation_reason="Derivar para análisis de la observación registral.",
        ),
        GatilloConfig(
            intention=Intention.FORMALIZACION,
            trigger_phrases=[
                "conflicto entre fundadores", "conflicto interno",
                "pelea entre socios fundadores",
            ],
            derivation_reason="Derivar por crisis de gobernanza.",
        ),
    ],
    Intention.IDENTIDAD_RUC: [
        GatilloConfig(
            intention=Intention.IDENTIDAD_RUC,
            trigger_phrases=[
                "fiscalización de sunat", "fiscalización sunat",
                "cierre temporal", "embargo", "embargo sunat",
                "operamos sin ruc", "ingresos sin ruc",
                "ruc cancelado",
            ],
            derivation_reason="Derivar por riesgo fiscal inminente.",
        ),
    ],
    Intention.DONACIONES: [
        GatilloConfig(
            intention=Intention.DONACIONES,
            trigger_phrases=[
                "fondos extranjeros para marchas",
                "financiamiento de activismo político",
                "fondos para denunciar al estado",
                "auditoría de apci", "auditoría apci",
                "multa de 500 uit", "multa apci",
                "reporte tardío apci",
            ],
            derivation_reason="Derivar: alto riesgo de infracción muy grave (hasta 500 UIT).",
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
    ],
    Intention.CONTRATACION: [
        GatilloConfig(
            intention=Intention.CONTRATACION,
            trigger_phrases=[
                "sunafil", "denuncia por beneficios sociales",
                "despido intempestivo", "despido arbitrario",
                "locador con horario fijo", "desnaturalización de contrato",
                "accidente de voluntario", "accidente laboral",
            ],
            derivation_reason="Derivar: riesgo de multa SUNAFIL o responsabilidad laboral.",
        ),
    ],
    Intention.PROPIEDAD_INTELECTUAL: [
        GatilloConfig(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            trigger_phrases=[
                "notificación de indecopi", "demanda por infracción de derechos",
                "uso indebido de software", "carta por plagio",
                "filtración de información confidencial",
            ],
            derivation_reason="Derivar: requiere defensa técnica en INDECOPI.",
        ),
    ],
    Intention.DATOS_PERSONALES: [
        GatilloConfig(
            intention=Intention.DATOS_PERSONALES,
            trigger_phrases=[
                "filtración de datos de víctimas", "venta de base de datos",
                "denuncia de usuario", "datos de menores",
                "hackeo de base de datos", "hackeo",
                "auditoría minjus", "notificación de auditoría",
            ],
            derivation_reason="Derivar: riesgo legal extremo por datos personales.",
        ),
    ],
    Intention.GOBERNANZA: [
        GatilloConfig(
            intention=Intention.GOBERNANZA,
            trigger_phrases=[
                "presidente actúa sin poderes", "actos sin facultades",
                "exceso de facultades", "conflicto grave entre directores",
                "crisis institucional",
            ],
            derivation_reason="Derivar: ineficacia de actos ante terceros.",
        ),
    ],
    Intention.ALIANZAS: [
        GatilloConfig(
            intention=Intention.ALIANZAS,
            trigger_phrases=[
                "incumplimiento de aliado", "incumplimiento contractual",
                "demanda por daños y perjuicios", "resolución de contrato",
            ],
            derivation_reason="Derivar: demanda por daños y perjuicios.",
        ),
    ],
    Intention.PERMISOS: [
        GatilloConfig(
            intention=Intention.PERMISOS,
            trigger_phrases=[
                "evento de más de 3000 personas", "evento masivo",
                "trabajo con niños", "trabajo con menores",
                "niños huérfanos", "menores de edad",
            ],
            derivation_reason="Derivar: proceso complejo de seguridad o riesgo con menores.",
        ),
    ],
    Intention.MARCA_IDENTIDAD: [
        GatilloConfig(
            intention=Intention.MARCA_IDENTIDAD,
            trigger_phrases=[
                "oposición de tercero", "oposición al registro",
                "alguien usa mi logo", "usan mi marca sin permiso",
                "usurpación de marca", "robo de marca",
            ],
            derivation_reason="Derivar: requiere defensa técnica legal ante INDECOPI.",
        ),
    ],
    Intention.SEGURIDAD_INFORMACION: [
        GatilloConfig(
            intention=Intention.SEGURIDAD_INFORMACION,
            trigger_phrases=[
                "borraron nuestra base de datos", "sabotaje informático",
                "amenaza de hackeo", "borrar archivos",
                "ex-miembro amenaza", "ataque informático",
            ],
            derivation_reason="Derivar: posible delito informático grave.",
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
            trigger_keywords=["error", "observacion", "problema", "rectif", "rechaz", "incorrecto", "equivoc"],
        ),
        AmberContextField(
            intention=Intention.FORMALIZACION,
            field_name="tiempo_ausencia",
            field_description="Tiempo que lleva ausente el fundador",
            example_prompt="¿Cuánto tiempo lleva ausente el fundador? ¿Se ha intentado contactarlo?",
            trigger_keywords=["ausente", "fundador", "desapareci", "no localiz", "no se presenta", "no aparece"],
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
    ],
    Intention.DONACIONES: [
        AmberContextField(
            intention=Intention.DONACIONES,
            field_name="tipo_bien",
            field_description="Tipo de bien a recibir del extranjero",
            example_prompt="¿Qué tipo de bienes vas a recibir del extranjero? (ej: equipos, alimentos, medicinas)",
            trigger_keywords=["recibir", "donacion", "bien", "equipo", "material", "mercancia", "importar", "entregan"],
        ),
        AmberContextField(
            intention=Intention.DONACIONES,
            field_name="origen_fondos",
            field_description="Origen de los fondos o cooperación",
            example_prompt="¿De dónde provienen los fondos? ¿Es cooperación técnica internacional o donación privada?",
            trigger_keywords=["fondos", "cooperacion", "dinero", "transferencia", "financ", "subvencion", "pago"],
        ),
    ],
    Intention.TRIBUTACION: [
        AmberContextField(
            intention=Intention.TRIBUTACION,
            field_name="actividad_comercial",
            field_description="Detalle de la actividad comercial",
            example_prompt="¿Podrías describir qué tipo de actividad comercial realizan y cómo reinvierten los ingresos?",
            trigger_keywords=["vend", "cobr", "servicio", "actividad", "ingres", "comerci", "factur", "operar", "giro"],
        ),
        AmberContextField(
            intention=Intention.TRIBUTACION,
            field_name="monto_operacion",
            field_description="Monto de la operación gravada",
            example_prompt="¿Cuál es el monto aproximado de la operación de consultoría?",
            trigger_keywords=["consultoria", "monto", "importe", "valor", "precio", "cobrar", "factura", "cuanto"],
        ),
    ],
    Intention.CONTRATACION: [
        AmberContextField(
            intention=Intention.CONTRATACION,
            field_name="cantidad_voluntarios",
            field_description="Cantidad de voluntarios",
            example_prompt="¿Cuántos voluntarios tiene actualmente tu organización?",
            trigger_keywords=["voluntario", "voluntariado", "cuantos", "personal", "equipo", "colabor"],
        ),
        AmberContextField(
            intention=Intention.CONTRATACION,
            field_name="modalidad_contrato",
            field_description="Modalidad de contratación actual",
            example_prompt="¿Bajo qué modalidad están contratados actualmente? (ej: locación de servicios, planilla, convenio)",
            trigger_keywords=["contrat", "modalidad", "vinculac", "planilla", "locacion", "locador", "modo"],
        ),
    ],
    Intention.PROPIEDAD_INTELECTUAL: [
        AmberContextField(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            field_name="tipo_contrato",
            field_description="Tipo de contrato de obra",
            example_prompt="¿Existe un contrato de trabajo o servicio con el creador de la obra?",
            trigger_keywords=["obra", "creador", "autor", "diseno", "fotograf", "contrat", "encargad", "creo"],
        ),
        AmberContextField(
            intention=Intention.PROPIEDAD_INTELECTUAL,
            field_name="licencia_uso",
            field_description="Tipo de licencia de uso",
            example_prompt="¿Bajo qué tipo de licencia se están utilizando las imágenes? (ej: Creative Commons, dominio público, sin licencia)",
            trigger_keywords=["imagen", "foto", "uso", "licencia", "material", "publicar", "usar", "reproduc"],
        ),
    ],
    Intention.DATOS_PERSONALES: [
        AmberContextField(
            intention=Intention.DATOS_PERSONALES,
            field_name="volumen_datos",
            field_description="Volumen de datos personales tratados",
            example_prompt="¿Aproximadamente cuántos registros de datos personales manejan?",
            trigger_keywords=["base de datos", "registros", "datos", "beneficiari", "cuantas personas", "fichero"],
        ),
        AmberContextField(
            intention=Intention.DATOS_PERSONALES,
            field_name="ubicacion_destino",
            field_description="País destino de transferencia de datos",
            example_prompt="¿A qué país se transferirían los datos? Necesito verificar si tiene nivel adecuado de protección.",
            trigger_keywords=["transferir", "enviar", "compartir", "pais", "extranjero", "internac", "sede"],
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
    ],
    Intention.ALIANZAS: [
        AmberContextField(
            intention=Intention.ALIANZAS,
            field_name="tipo_aporte",
            field_description="Tipo de aporte al consorcio",
            example_prompt="¿Qué tipo de aportes realizará cada organización al consorcio?",
            trigger_keywords=["consorcio", "alianza", "aportar", "aporte", "participar", "colaborar", "convenio"],
        ),
    ],
    Intention.PERMISOS: [
        AmberContextField(
            intention=Intention.PERMISOS,
            field_name="distrito",
            field_description="Distrito donde se realizará el evento",
            example_prompt="¿En qué distrito se realizará el evento? Cada municipalidad tiene su propio TUPA.",
            trigger_keywords=["evento", "municipalidad", "permiso", "autorizacion", "licencia", "actividad", "realizarse"],
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
    "**¿Qué puedo hacer por ti?**\n"
    "Puedo ayudarte a preparar la documentación necesaria para tu reunión con el asesor legal. "
    "¿Deseas que te ayude a organizar tu caso?"
)


# =============================================================================
# MENSAJE AMARILLO (editable)
# =============================================================================

AMBER_CONTEXT_TEMPLATE = (
    "{partial_answer}\n\n"
    "---\n\n"
    "🟡 **Para darte una orientación más precisa sobre tu caso específico, necesito algunos datos adicionales:**\n\n"
    "{questions}\n\n"
    "Con esta información podré ajustar la orientación a tu situación concreta."
)


# =============================================================================
# DETECTORES DE ANÁLISIS DE PROYECTO (editable)
# Frases que indican que el usuario quiere analizar un proyecto completo.
# =============================================================================

PROJECT_ANALYSIS_TRIGGERS: List[str] = [
    "analizar mi proyecto",
    "evaluar mi proyecto",
    "viabilidad de mi proyecto",
    "viabilidad legal",
    "evaluar viabilidad",
    "analizar viabilidad",
    "revisar mi proyecto",
    "es viable mi proyecto",
    "mi proyecto es legal",
    "proyecto es viable",
    "quiero formalizar mi proyecto",
    "plan de negocio",
    "evaluar mi emprendimiento",
    "tengo un proyecto",
    "quiero emprender",
]


# =============================================================================
# DISCLAIMERS ESTÁNDAR (editable)
# =============================================================================

STANDARD_DISCLAIMERS: List[str] = [
    "Esta respuesta no constituye asesoría legal vinculante.",
    "Verifica la información con la normativa vigente.",
    "Para casos específicos, consulta con un abogado especializado.",
]
