"""
Legal Rules - Business Rules Definitions
Reglas de negocio para determinar requisitos legales.

ESTRUCTURA DE CADA REGLA:
- id: Identificador único
- intention: Área legal que cubre
- trigger: Función que determina si la regla aplica
- check: Función que verifica el cumplimiento
- requirements: Requisitos asociados
- gap_generator: Función que genera la brecha si no cumple
"""

from typing import Any, Callable
from dataclasses import dataclass, field

from app.modules.intake.schemas import LegalProfile
from .schemas import (
    LegalIntention,
    LegalRequirement,
    RequirementStatus,
    LegalGap,
    GapSeverity,
)


@dataclass
class LegalRule:
    """Definición de una regla legal"""
    id: str
    name: str
    intention: LegalIntention
    description: str

    # Función que determina si la regla aplica dado un LegalProfile
    # (profile) -> bool
    trigger: Callable[[LegalProfile], bool]

    # Función que verifica cumplimiento
    # (profile) -> RequirementStatus
    check: Callable[[LegalProfile], RequirementStatus]

    # Metadata
    related_laws: list[str] = field(default_factory=list)
    required_documents: list[str] = field(default_factory=list)
    required_registrations: list[str] = field(default_factory=list)

    # Generador de brecha si no cumple
    # (profile, org_id, org_name) -> LegalGap | None
    gap_generator: Callable[[LegalProfile, str, str], LegalGap | None] = None

    # Severidad por defecto de la brecha
    default_gap_severity: GapSeverity = GapSeverity.MEDIUM


# =============================================================================
# REGLAS DE FORMALIZACIÓN
# =============================================================================

RULE_LEGAL_STATUS = LegalRule(
    id="formalization_legal_status",
    name="Personería Jurídica",
    intention=LegalIntention.FORMALIZATION,
    description="Organizaciones que manejan dinero deben tener personería jurídica",
    related_laws=["Código Civil Art. 76-98", "Ley de Asociaciones"],
    required_documents=["Estatuto o acta de constitución"],
    required_registrations=["Inscripción en Registros Públicos"],
    trigger=lambda p: p.income.handles_money is True,
    check=lambda p: (
        RequirementStatus.FULFILLED if p.formalization.has_legal_status == "Sí"
        else RequirementStatus.PARTIALLY_FULFILLED if p.formalization.has_legal_status == "En trámite"
        else RequirementStatus.NOT_FULFILLED
    ),
    default_gap_severity=GapSeverity.CRITICAL,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_legal_status_{org_id}",
        requirement_id="formalization_legal_status",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.CRITICAL,
        intention=LegalIntention.FORMALIZATION,
        description="La organización maneja dinero sin personería jurídica",
        impact="Riesgo de responsabilidad personal de los miembros. Imposibilidad de abrir cuentas bancarias institucionales. Limitaciones para recibir donaciones formales.",
        recommendation="Iniciar proceso de formalización como asociación, fundación u otra figura jurídica apropiada.",
        rag_query_hint="requisitos constitución asociación civil Perú registros públicos",
        source_fields=["income.handles_money", "formalization.has_legal_status"],
    ) if p.formalization.has_legal_status != "Sí" else None,
)

RULE_RUC = LegalRule(
    id="formalization_ruc",
    name="Registro Único de Contribuyente (RUC)",
    intention=LegalIntention.TAXATION,
    description="Organizaciones que manejan dinero deben tener RUC",
    related_laws=["Decreto Legislativo 943", "Resolución SUNAT 210-2004"],
    required_registrations=["RUC activo en SUNAT"],
    trigger=lambda p: p.income.handles_money is True,
    check=lambda p: (
        RequirementStatus.FULFILLED if p.formalization.ruc_status == "Lo tengo"
        else RequirementStatus.PARTIALLY_FULFILLED if p.formalization.ruc_status == "En trámite"
        else RequirementStatus.NOT_FULFILLED
    ),
    default_gap_severity=GapSeverity.HIGH,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_ruc_{org_id}",
        requirement_id="formalization_ruc",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.HIGH,
        intention=LegalIntention.TAXATION,
        description="La organización maneja dinero sin RUC",
        impact="Imposibilidad de emitir comprobantes de pago. Riesgo de multas tributarias. Limitaciones para operar formalmente.",
        recommendation="Tramitar RUC ante SUNAT como persona jurídica.",
        rag_query_hint="requisitos obtener RUC asociación sin fines de lucro SUNAT",
        source_fields=["income.handles_money", "formalization.ruc_status"],
    ) if p.formalization.ruc_status != "Lo tengo" else None,
)


# =============================================================================
# REGLAS DE COOPERACIÓN INTERNACIONAL (APCI)
# =============================================================================

RULE_APCI_REGISTRATION = LegalRule(
    id="apci_registration",
    name="Registro en APCI",
    intention=LegalIntention.INTERNATIONAL_COOPERATION,
    description="Organizaciones que reciben cooperación internacional deben registrarse en APCI",
    related_laws=[
        "Ley 27692 - Ley de la APCI",
        "DS 028-2003-RE",
        "Directiva 001-2012-APCI"
    ],
    required_documents=["Plan de uso de fondos", "Memorias anuales"],
    required_registrations=["Registro en APCI"],
    trigger=lambda p: (
        p.international_cooperation.receives_international_cooperation is True
        or p.income.receives_foreign_funds is True
        or "Cooperación internacional" in p.income.income_sources
    ),
    check=lambda p: (
        RequirementStatus.FULFILLED if p.international_cooperation.apci_status == "Registrado"
        else RequirementStatus.NOT_FULFILLED if p.international_cooperation.apci_status == "Necesita registro"
        else RequirementStatus.NOT_APPLICABLE
    ),
    default_gap_severity=GapSeverity.CRITICAL,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_apci_{org_id}",
        requirement_id="apci_registration",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.CRITICAL,
        intention=LegalIntention.INTERNATIONAL_COOPERATION,
        description="La organización recibe o planea recibir cooperación internacional sin registro en APCI",
        impact="Incumplimiento legal obligatorio. Posibles sanciones. Impedimento para recibir nuevos fondos internacionales. Riesgo reputacional con cooperantes.",
        recommendation="Iniciar trámite de inscripción en el Registro de ENIEX de APCI.",
        rag_query_hint="requisitos registro APCI ENIEX cooperación técnica internacional Perú",
        source_fields=["international_cooperation.receives_international_cooperation", "international_cooperation.apci_status", "income.receives_foreign_funds"],
    ) if p.international_cooperation.apci_status == "Necesita registro" else None,
)


# =============================================================================
# REGLAS DE EXONERACIÓN TRIBUTARIA
# =============================================================================

RULE_IR_EXONERATION = LegalRule(
    id="taxation_ir_exoneration",
    name="Exoneración de Impuesto a la Renta",
    intention=LegalIntention.TAXATION,
    description="ONGs sin fines de lucro pueden solicitar exoneración del IR",
    related_laws=[
        "TUO Ley del Impuesto a la Renta Art. 19",
        "DS 179-2004-EF",
        "Resolución SUNAT"
    ],
    required_documents=["Estatuto con cláusula de no distribución de utilidades"],
    required_registrations=["Inscripción como entidad exonerada en SUNAT"],
    trigger=lambda p: (
        p.identity.seeks_profits is False
        and p.identity.org_type in ["Asociación", "Fundación", "ONG"]
        and p.formalization.has_legal_status == "Sí"
    ),
    check=lambda p: (
        RequirementStatus.FULFILLED if "Exonerada de Impuesto a la renta" in p.formalization.special_registries
        else RequirementStatus.NOT_FULFILLED
    ),
    default_gap_severity=GapSeverity.MEDIUM,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_ir_exon_{org_id}",
        requirement_id="taxation_ir_exoneration",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.MEDIUM,
        intention=LegalIntention.TAXATION,
        description="La organización sin fines de lucro no ha solicitado exoneración del Impuesto a la Renta",
        impact="Pago innecesario de impuestos. Menor disponibilidad de recursos para fines institucionales.",
        recommendation="Evaluar si cumple requisitos y solicitar inscripción como entidad exonerada ante SUNAT.",
        rag_query_hint="requisitos exoneración impuesto renta asociaciones sin fines de lucro SUNAT",
        source_fields=["identity.seeks_profits", "identity.org_type", "formalization.special_registries"],
    ) if "Exonerada de Impuesto a la renta" not in p.formalization.special_registries else None,
)


# =============================================================================
# REGLAS LABORALES
# =============================================================================

RULE_LABOR_CONTRACTS = LegalRule(
    id="labor_contracts_valid",
    name="Contratos Laborales Válidos",
    intention=LegalIntention.HIRING,
    description="Personal contratado debe tener contratos válidos según modalidad",
    related_laws=[
        "TUO DL 728 - Ley de Productividad y Competitividad Laboral",
        "DS 003-97-TR"
    ],
    required_documents=["Contratos de trabajo", "Boletas de pago"],
    trigger=lambda p: (
        "Planilla" in p.human_resources.hiring_modalities
        or "Locación de servicios" in p.human_resources.hiring_modalities
    ),
    check=lambda p: (
        RequirementStatus.FULFILLED if p.human_resources.contracts_valid == "Sí"
        else RequirementStatus.NOT_FULFILLED if p.human_resources.contracts_valid == "No"
        else RequirementStatus.UNKNOWN
    ),
    default_gap_severity=GapSeverity.HIGH,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_labor_{org_id}",
        requirement_id="labor_contracts_valid",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.HIGH,
        intention=LegalIntention.HIRING,
        description="La organización contrata personal sin contratos válidos",
        impact="Riesgo de demandas laborales. Multas de SUNAFIL. Responsabilidad por beneficios sociales no pagados.",
        recommendation="Regularizar situación contractual de todo el personal. Revisar si locadores cumplen criterios de independencia.",
        rag_query_hint="requisitos contratos laborales asociaciones sin fines de lucro SUNAFIL",
        source_fields=["human_resources.hiring_modalities", "human_resources.contracts_valid"],
    ) if p.human_resources.contracts_valid == "No" else None,
)

RULE_LOCACION_RISK = LegalRule(
    id="labor_locacion_risk",
    name="Riesgo de Desnaturalización de Locación",
    intention=LegalIntention.HIRING,
    description="Locación de servicios con subordinación puede desnaturalizarse en relación laboral",
    related_laws=[
        "Código Civil Art. 1764",
        "Principio de primacía de la realidad",
        "Jurisprudencia del TC"
    ],
    trigger=lambda p: "Locación de servicios" in p.human_resources.hiring_modalities,
    check=lambda p: RequirementStatus.UNKNOWN,  # Requiere análisis caso por caso
    default_gap_severity=GapSeverity.MEDIUM,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_locacion_{org_id}",
        requirement_id="labor_locacion_risk",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.MEDIUM,
        intention=LegalIntention.HIRING,
        description="La organización usa locación de servicios - verificar que no haya subordinación",
        impact="Si existe subordinación, horario fijo y herramientas del empleador, el contrato puede desnaturalizarse. Responsabilidad por beneficios laborales retroactivos.",
        recommendation="Auditar contratos de locación: verificar autonomía real, ausencia de subordinación, prestación sin exclusividad.",
        rag_query_hint="desnaturalización locación servicios relación laboral subordinación Perú",
        source_fields=["human_resources.hiring_modalities"],
    ),
)


# =============================================================================
# REGLAS DE CONTABILIDAD
# =============================================================================

RULE_ACCOUNTING_RECORDS = LegalRule(
    id="accounting_records",
    name="Registros Contables",
    intention=LegalIntention.ACCOUNTING,
    description="Organizaciones que manejan dinero deben llevar contabilidad",
    related_laws=[
        "Ley General de Sociedades",
        "Código de Comercio",
        "Resoluciones SUNAT sobre libros contables"
    ],
    required_documents=["Libros contables", "Estados financieros"],
    trigger=lambda p: p.income.handles_money is True,
    check=lambda p: (
        RequirementStatus.FULFILLED if p.accounting.has_accounting_records == "Sí, completos"
        else RequirementStatus.PARTIALLY_FULFILLED if p.accounting.has_accounting_records in ["Sí, parciales", "En proceso"]
        else RequirementStatus.NOT_FULFILLED
    ),
    default_gap_severity=GapSeverity.HIGH,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_accounting_{org_id}",
        requirement_id="accounting_records",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.HIGH,
        intention=LegalIntention.ACCOUNTING,
        description="La organización maneja dinero sin registros contables completos",
        impact="Incumplimiento de obligaciones tributarias. Imposibilidad de rendir cuentas a donantes. Riesgo en fiscalizaciones.",
        recommendation="Implementar sistema de contabilidad. Considerar contador externo si no hay capacidad interna.",
        rag_query_hint="obligaciones contables asociaciones sin fines de lucro libros contables SUNAT",
        source_fields=["income.handles_money", "accounting.has_accounting_records"],
    ) if p.accounting.has_accounting_records in ["No", None] else None,
)


# =============================================================================
# REGLAS DE GOBERNANZA
# =============================================================================

RULE_GOVERNANCE_BODIES = LegalRule(
    id="governance_bodies",
    name="Órganos de Gobierno",
    intention=LegalIntention.GOVERNANCE,
    description="Asociaciones y fundaciones deben tener órganos de gobierno constituidos",
    related_laws=[
        "Código Civil Art. 81-84",
        "Estatutos de la organización"
    ],
    required_documents=["Estatuto", "Libros de actas"],
    trigger=lambda p: p.identity.org_type in ["Asociación", "Fundación", "ONG"],
    check=lambda p: (
        RequirementStatus.FULFILLED if p.governance.has_governance_bodies is True
        else RequirementStatus.NOT_FULFILLED
    ),
    default_gap_severity=GapSeverity.MEDIUM,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_governance_{org_id}",
        requirement_id="governance_bodies",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.MEDIUM,
        intention=LegalIntention.GOVERNANCE,
        description="La organización no tiene órganos de gobierno constituidos",
        impact="Posible irregularidad estatutaria. Dificultades para tomar decisiones válidas. Riesgo en representación legal.",
        recommendation="Constituir asamblea general y consejo directivo según estatutos. Documentar en libro de actas.",
        rag_query_hint="órganos gobierno asociación asamblea consejo directivo Código Civil",
        source_fields=["identity.org_type", "governance.has_governance_bodies"],
    ) if p.governance.has_governance_bodies is not True else None,
)

RULE_LEGAL_REPRESENTATIVE = LegalRule(
    id="governance_legal_rep",
    name="Representante Legal",
    intention=LegalIntention.GOVERNANCE,
    description="Organizaciones formalizadas deben tener representante legal inscrito",
    related_laws=["Código Civil", "Reglamento de Registros Públicos"],
    required_registrations=["Poder inscrito en Registros Públicos"],
    trigger=lambda p: p.formalization.has_legal_status == "Sí",
    check=lambda p: (
        RequirementStatus.FULFILLED if p.governance.has_legal_representative == "Sí"
        else RequirementStatus.PARTIALLY_FULFILLED if p.governance.has_legal_representative == "En trámite"
        else RequirementStatus.NOT_FULFILLED
    ),
    default_gap_severity=GapSeverity.HIGH,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_legal_rep_{org_id}",
        requirement_id="governance_legal_rep",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.HIGH,
        intention=LegalIntention.GOVERNANCE,
        description="La organización no tiene representante legal inscrito",
        impact="Imposibilidad de realizar actos jurídicos válidos. No puede firmar contratos, abrir cuentas bancarias, etc.",
        recommendation="Elegir representante legal según estatutos e inscribir poder en Registros Públicos.",
        rag_query_hint="inscripción representante legal asociación Registros Públicos SUNARP",
        source_fields=["formalization.has_legal_status", "governance.has_legal_representative"],
    ) if p.governance.has_legal_representative not in ["Sí", "En trámite"] else None,
)


# =============================================================================
# REGLAS DE PROTECCIÓN DE DATOS
# =============================================================================

RULE_DATA_PROTECTION = LegalRule(
    id="data_protection",
    name="Protección de Datos Personales",
    intention=LegalIntention.DATA_PROTECTION,
    description="Organizaciones que manejan bases de datos de usuarios deben cumplir la LPDP",
    related_laws=[
        "Ley 29733 - Ley de Protección de Datos Personales",
        "DS 003-2013-JUS - Reglamento",
        "Directivas de la ANPD"
    ],
    required_documents=["Política de privacidad", "Consentimiento informado"],
    required_registrations=["Registro de banco de datos en ANPD (si aplica)"],
    trigger=lambda p: "Bases de datos de usuarios" in p.intangibles.intangible_assets,
    check=lambda p: RequirementStatus.UNKNOWN,  # Requiere análisis detallado
    default_gap_severity=GapSeverity.MEDIUM,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_data_{org_id}",
        requirement_id="data_protection",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.MEDIUM,
        intention=LegalIntention.DATA_PROTECTION,
        description="La organización maneja bases de datos de usuarios - verificar cumplimiento LPDP",
        impact="Posibles sanciones de la Autoridad de Protección de Datos. Riesgo reputacional. Responsabilidad civil por mal uso de datos.",
        recommendation="Implementar política de privacidad. Obtener consentimiento. Evaluar si requiere registro en ANPD.",
        rag_query_hint="Ley Protección Datos Personales 29733 obligaciones tratamiento datos Perú",
        source_fields=["intangibles.intangible_assets"],
    ),
)


# =============================================================================
# REGLAS DE PROPIEDAD INTELECTUAL
# =============================================================================

RULE_INTELLECTUAL_PROPERTY = LegalRule(
    id="intellectual_property",
    name="Protección de Propiedad Intelectual",
    intention=LegalIntention.INTELLECTUAL_PROPERTY,
    description="Activos intangibles propios deben estar protegidos",
    related_laws=[
        "Decreto Legislativo 822 - Ley de Derechos de Autor",
        "Decreto Legislativo 1075 - Marcas",
        "Decisión 486 CAN"
    ],
    required_registrations=["Registro de marca en INDECOPI", "Registro de software/obra"],
    trigger=lambda p: any(
        asset in p.intangibles.intangible_assets
        for asset in ["Software propio", "Marca o símbolos distintivos", "Contenido con derechos de autor"]
    ),
    check=lambda p: RequirementStatus.UNKNOWN,  # Requiere análisis detallado
    default_gap_severity=GapSeverity.LOW,
    gap_generator=lambda p, org_id, org_name: LegalGap(
        id=f"gap_ip_{org_id}",
        requirement_id="intellectual_property",
        organization_id=org_id,
        organization_name=org_name,
        severity=GapSeverity.LOW,
        intention=LegalIntention.INTELLECTUAL_PROPERTY,
        description="La organización tiene activos intangibles que podrían requerir protección",
        impact="Riesgo de uso no autorizado por terceros. Pérdida de exclusividad. Dificultad para defender derechos.",
        recommendation="Evaluar registro de marca en INDECOPI. Documentar autoría de software y contenidos.",
        rag_query_hint="registro marca INDECOPI derechos autor software asociación sin fines lucro",
        source_fields=["intangibles.intangible_assets"],
    ),
)


# =============================================================================
# LISTA COMPLETA DE REGLAS
# =============================================================================

LEGAL_RULES: list[LegalRule] = [
    # Formalización
    RULE_LEGAL_STATUS,
    RULE_RUC,

    # Cooperación Internacional
    RULE_APCI_REGISTRATION,

    # Tributario
    RULE_IR_EXONERATION,

    # Laboral
    RULE_LABOR_CONTRACTS,
    RULE_LOCACION_RISK,

    # Contabilidad
    RULE_ACCOUNTING_RECORDS,

    # Gobernanza
    RULE_GOVERNANCE_BODIES,
    RULE_LEGAL_REPRESENTATIVE,

    # Datos
    RULE_DATA_PROTECTION,

    # Propiedad Intelectual
    RULE_INTELLECTUAL_PROPERTY,
]


# Helper para obtener reglas por intención
def get_rules_by_intention(intention: LegalIntention) -> list[LegalRule]:
    """Obtiene todas las reglas de una intención específica"""
    return [rule for rule in LEGAL_RULES if rule.intention == intention]
