"""
Verificacion de logica de reglas legales - Standalone (sin dependencias)

Este script verifica que la logica de las reglas es correcta
sin necesitar pydantic ni otras dependencias.
"""

from dataclasses import dataclass, field
from typing import Callable, Any
from enum import Enum

# =============================================================================
# MOCK DE ESTRUCTURAS (replica simplificada de schemas.py)
# =============================================================================

class GapSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class LegalIntention(str, Enum):
    FORMALIZATION = "formalization"
    TAXATION = "taxation"
    INTERNATIONAL_COOPERATION = "international_cooperation"
    HIRING = "hiring"
    ACCOUNTING = "accounting"
    GOVERNANCE = "governance"
    DATA_PROTECTION = "data_protection"
    INTELLECTUAL_PROPERTY = "intellectual_property"

class RequirementStatus(str, Enum):
    FULFILLED = "fulfilled"
    PARTIALLY_FULFILLED = "partial"
    NOT_FULFILLED = "not_fulfilled"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"

@dataclass
class MockIdentity:
    org_type: str = None
    org_purpose: str = None
    seeks_profits: bool = None

@dataclass
class MockFormalization:
    has_legal_status: str = None
    ruc_status: str = None
    special_registries: list = field(default_factory=list)

@dataclass
class MockIncome:
    handles_money: bool = None
    receives_foreign_funds: bool = None
    income_sources: list = field(default_factory=list)

@dataclass
class MockIntlCoop:
    receives_international_cooperation: bool = None
    apci_status: str = None

@dataclass
class MockHR:
    hiring_modalities: list = field(default_factory=list)
    contracts_valid: str = None

@dataclass
class MockAccounting:
    has_accounting_records: str = None
    available_documents: list = field(default_factory=list)

@dataclass
class MockGovernance:
    has_governance_bodies: bool = None
    has_legal_representative: str = None

@dataclass
class MockIntangibles:
    intangible_assets: list = field(default_factory=list)

@dataclass
class MockProfile:
    identity: MockIdentity = field(default_factory=MockIdentity)
    formalization: MockFormalization = field(default_factory=MockFormalization)
    income: MockIncome = field(default_factory=MockIncome)
    international_cooperation: MockIntlCoop = field(default_factory=MockIntlCoop)
    human_resources: MockHR = field(default_factory=MockHR)
    accounting: MockAccounting = field(default_factory=MockAccounting)
    governance: MockGovernance = field(default_factory=MockGovernance)
    intangibles: MockIntangibles = field(default_factory=MockIntangibles)

@dataclass
class MockGap:
    id: str
    severity: GapSeverity
    intention: LegalIntention
    description: str
    impact: str
    recommendation: str
    rag_query_hint: str = None
    source_fields: list = field(default_factory=list)

# =============================================================================
# REGLAS (replica de rules.py)
# =============================================================================

@dataclass
class MockRule:
    id: str
    name: str
    intention: LegalIntention
    trigger: Callable[[MockProfile], bool]
    check: Callable[[MockProfile], RequirementStatus]
    default_gap_severity: GapSeverity
    gap_generator: Callable[[MockProfile, str, str], MockGap] = None

# Regla: Personeria Juridica
RULE_LEGAL_STATUS = MockRule(
    id="formalization_legal_status",
    name="Personeria Juridica",
    intention=LegalIntention.FORMALIZATION,
    trigger=lambda p: p.income.handles_money is True,
    check=lambda p: (
        RequirementStatus.FULFILLED if p.formalization.has_legal_status == "Si"
        else RequirementStatus.PARTIALLY_FULFILLED if p.formalization.has_legal_status == "En tramite"
        else RequirementStatus.NOT_FULFILLED
    ),
    default_gap_severity=GapSeverity.CRITICAL,
    gap_generator=lambda p, org_id, org_name: MockGap(
        id=f"gap_legal_status_{org_id}",
        severity=GapSeverity.CRITICAL,
        intention=LegalIntention.FORMALIZATION,
        description="La organizacion maneja dinero sin personeria juridica",
        impact="Riesgo de responsabilidad personal",
        recommendation="Iniciar proceso de formalizacion",
        source_fields=["income.handles_money", "formalization.has_legal_status"],
    ) if p.formalization.has_legal_status != "Si" else None,
)

# Regla: RUC
RULE_RUC = MockRule(
    id="formalization_ruc",
    name="RUC",
    intention=LegalIntention.TAXATION,
    trigger=lambda p: p.income.handles_money is True,
    check=lambda p: (
        RequirementStatus.FULFILLED if p.formalization.ruc_status == "Lo tengo"
        else RequirementStatus.PARTIALLY_FULFILLED if p.formalization.ruc_status == "En tramite"
        else RequirementStatus.NOT_FULFILLED
    ),
    default_gap_severity=GapSeverity.HIGH,
    gap_generator=lambda p, org_id, org_name: MockGap(
        id=f"gap_ruc_{org_id}",
        severity=GapSeverity.HIGH,
        intention=LegalIntention.TAXATION,
        description="La organizacion maneja dinero sin RUC",
        impact="Imposibilidad de emitir comprobantes",
        recommendation="Tramitar RUC ante SUNAT",
        source_fields=["income.handles_money", "formalization.ruc_status"],
    ) if p.formalization.ruc_status != "Lo tengo" else None,
)

# Regla: APCI
RULE_APCI = MockRule(
    id="apci_registration",
    name="Registro en APCI",
    intention=LegalIntention.INTERNATIONAL_COOPERATION,
    trigger=lambda p: (
        p.international_cooperation.receives_international_cooperation is True
        or p.income.receives_foreign_funds is True
        or "Cooperacion internacional" in (p.income.income_sources or [])
    ),
    check=lambda p: (
        RequirementStatus.FULFILLED if p.international_cooperation.apci_status == "Registrado"
        else RequirementStatus.NOT_FULFILLED if p.international_cooperation.apci_status == "Necesita registro"
        else RequirementStatus.NOT_APPLICABLE
    ),
    default_gap_severity=GapSeverity.CRITICAL,
    gap_generator=lambda p, org_id, org_name: MockGap(
        id=f"gap_apci_{org_id}",
        severity=GapSeverity.CRITICAL,
        intention=LegalIntention.INTERNATIONAL_COOPERATION,
        description="La organizacion recibe cooperacion internacional sin registro APCI",
        impact="Incumplimiento legal obligatorio",
        recommendation="Iniciar tramite en APCI",
        source_fields=["international_cooperation.apci_status"],
    ) if p.international_cooperation.apci_status == "Necesita registro" else None,
)

# Regla: Locacion de servicios (riesgo)
RULE_LOCACION = MockRule(
    id="labor_locacion_risk",
    name="Riesgo de Locacion",
    intention=LegalIntention.HIRING,
    trigger=lambda p: "Locacion de servicios" in (p.human_resources.hiring_modalities or []),
    check=lambda p: RequirementStatus.UNKNOWN,
    default_gap_severity=GapSeverity.MEDIUM,
    gap_generator=lambda p, org_id, org_name: MockGap(
        id=f"gap_locacion_{org_id}",
        severity=GapSeverity.MEDIUM,
        intention=LegalIntention.HIRING,
        description="Verificar que no haya subordinacion en locacion de servicios",
        impact="Riesgo de desnaturalizacion de contratos",
        recommendation="Auditar contratos de locacion",
        source_fields=["human_resources.hiring_modalities"],
    ),
)

# Regla: Datos personales
RULE_DATA = MockRule(
    id="data_protection",
    name="Proteccion de Datos",
    intention=LegalIntention.DATA_PROTECTION,
    trigger=lambda p: "Bases de datos de usuarios" in (p.intangibles.intangible_assets or []),
    check=lambda p: RequirementStatus.UNKNOWN,
    default_gap_severity=GapSeverity.MEDIUM,
    gap_generator=lambda p, org_id, org_name: MockGap(
        id=f"gap_data_{org_id}",
        severity=GapSeverity.MEDIUM,
        intention=LegalIntention.DATA_PROTECTION,
        description="Verificar cumplimiento de Ley de Proteccion de Datos",
        impact="Riesgo de sanciones ANPD",
        recommendation="Implementar politica de privacidad",
        source_fields=["intangibles.intangible_assets"],
    ),
)

ALL_RULES = [RULE_LEGAL_STATUS, RULE_RUC, RULE_APCI, RULE_LOCACION, RULE_DATA]

# =============================================================================
# PERFILES DE PRUEBA
# =============================================================================

def create_informal_collective() -> MockProfile:
    """Colectivo informal que maneja dinero - multiples gaps criticos"""
    return MockProfile(
        identity=MockIdentity(org_type="Colectivo", seeks_profits=False),
        formalization=MockFormalization(has_legal_status="No", ruc_status="No lo tengo"),
        income=MockIncome(handles_money=True, receives_foreign_funds=False, income_sources=["Donaciones"]),
        international_cooperation=MockIntlCoop(receives_international_cooperation=False, apci_status="No aplica"),
        human_resources=MockHR(hiring_modalities=["Voluntariado"], contracts_valid="No aplica"),
        accounting=MockAccounting(has_accounting_records="No"),
        governance=MockGovernance(has_governance_bodies=False, has_legal_representative="No"),
        intangibles=MockIntangibles(intangible_assets=["Ninguno"]),
    )

def create_formalized_ong() -> MockProfile:
    """ONG formalizada y en regla"""
    return MockProfile(
        identity=MockIdentity(org_type="ONG", seeks_profits=False),
        formalization=MockFormalization(
            has_legal_status="Si",
            ruc_status="Lo tengo",
            special_registries=["APCI", "Exonerada de IR"]
        ),
        income=MockIncome(
            handles_money=True,
            receives_foreign_funds=True,
            income_sources=["Donaciones", "Cooperacion internacional"]
        ),
        international_cooperation=MockIntlCoop(
            receives_international_cooperation=True,
            apci_status="Registrado"
        ),
        human_resources=MockHR(hiring_modalities=["Planilla"], contracts_valid="Si"),
        accounting=MockAccounting(has_accounting_records="Si, completos"),
        governance=MockGovernance(has_governance_bodies=True, has_legal_representative="Si"),
        intangibles=MockIntangibles(intangible_assets=["Software de terceros"]),
    )

def create_ong_needs_apci() -> MockProfile:
    """ONG que recibe cooperacion pero sin APCI"""
    return MockProfile(
        identity=MockIdentity(org_type="ONG", seeks_profits=False),
        formalization=MockFormalization(has_legal_status="Si", ruc_status="Lo tengo"),
        income=MockIncome(
            handles_money=True,
            receives_foreign_funds=True,
            income_sources=["Cooperacion internacional"]
        ),
        international_cooperation=MockIntlCoop(
            receives_international_cooperation=True,
            apci_status="Necesita registro"
        ),
        human_resources=MockHR(hiring_modalities=["Planilla"], contracts_valid="Si"),
        accounting=MockAccounting(has_accounting_records="Si, completos"),
        governance=MockGovernance(has_governance_bodies=True, has_legal_representative="Si"),
        intangibles=MockIntangibles(intangible_assets=["Bases de datos de usuarios"]),
    )

def create_association_with_locacion() -> MockProfile:
    """Asociacion con locacion de servicios"""
    return MockProfile(
        identity=MockIdentity(org_type="Asociacion", seeks_profits=False),
        formalization=MockFormalization(has_legal_status="Si", ruc_status="Lo tengo"),
        income=MockIncome(handles_money=True, receives_foreign_funds=False),
        international_cooperation=MockIntlCoop(
            receives_international_cooperation=False,
            apci_status="No aplica"
        ),
        human_resources=MockHR(hiring_modalities=["Locacion de servicios"], contracts_valid="Si"),
        accounting=MockAccounting(has_accounting_records="Si, parciales"),
        governance=MockGovernance(has_governance_bodies=True, has_legal_representative="Si"),
        intangibles=MockIntangibles(intangible_assets=["Marca o simbolos"]),
    )

# =============================================================================
# TESTS
# =============================================================================

def run_tests():
    passed = 0
    failed = 0

    def test(name: str, condition: bool, detail: str = ""):
        nonlocal passed, failed
        if condition:
            print(f"  [PASS] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name}")
            if detail:
                print(f"         -> {detail}")
            failed += 1

    print("\n" + "="*60)
    print("TEST 1: REGLA PERSONERIA JURIDICA")
    print("="*60)

    profile_informal = create_informal_collective()
    profile_formal = create_formalized_ong()

    # Trigger tests
    test("Trigger cuando maneja dinero",
         RULE_LEGAL_STATUS.trigger(profile_informal) == True)

    profile_no_money = MockProfile(income=MockIncome(handles_money=False))
    test("NO trigger cuando no maneja dinero",
         RULE_LEGAL_STATUS.trigger(profile_no_money) == False)

    # Status tests
    test("Status FULFILLED cuando tiene personeria",
         RULE_LEGAL_STATUS.check(profile_formal) == RequirementStatus.FULFILLED)

    test("Status NOT_FULFILLED cuando no tiene",
         RULE_LEGAL_STATUS.check(profile_informal) == RequirementStatus.NOT_FULFILLED)

    profile_tramite = MockProfile(formalization=MockFormalization(has_legal_status="En tramite"))
    test("Status PARTIAL cuando en tramite",
         RULE_LEGAL_STATUS.check(profile_tramite) == RequirementStatus.PARTIALLY_FULFILLED)

    # Gap tests
    gap = RULE_LEGAL_STATUS.gap_generator(profile_informal, "org_1", "Test")
    test("Genera gap cuando no cumple", gap is not None)
    test("Gap es CRITICAL", gap.severity == GapSeverity.CRITICAL)
    test("Gap tiene descripcion", len(gap.description) > 10)
    test("Gap tiene source_fields", len(gap.source_fields) > 0)

    gap_ok = RULE_LEGAL_STATUS.gap_generator(profile_formal, "org_1", "Test")
    test("NO genera gap cuando cumple", gap_ok is None)

    print("\n" + "="*60)
    print("TEST 2: REGLA RUC")
    print("="*60)

    test("Trigger cuando maneja dinero",
         RULE_RUC.trigger(profile_informal) == True)
    test("Status FULFILLED cuando tiene RUC",
         RULE_RUC.check(profile_formal) == RequirementStatus.FULFILLED)
    test("Status NOT_FULFILLED cuando no tiene RUC",
         RULE_RUC.check(profile_informal) == RequirementStatus.NOT_FULFILLED)
    test("Severidad es HIGH (no CRITICAL)",
         RULE_RUC.default_gap_severity == GapSeverity.HIGH)

    print("\n" + "="*60)
    print("TEST 3: REGLA APCI")
    print("="*60)

    profile_needs_apci = create_ong_needs_apci()

    # Trigger tests
    test("Trigger cuando recibe cooperacion intl",
         RULE_APCI.trigger(profile_needs_apci) == True)

    profile_receives_foreign = MockProfile(
        income=MockIncome(receives_foreign_funds=True)
    )
    test("Trigger cuando receives_foreign_funds=True",
         RULE_APCI.trigger(profile_receives_foreign) == True)

    profile_income_coop = MockProfile(
        income=MockIncome(income_sources=["Cooperacion internacional"])
    )
    test("Trigger cuando income_sources incluye cooperacion",
         RULE_APCI.trigger(profile_income_coop) == True)

    profile_no_intl = create_association_with_locacion()
    test("NO trigger cuando no hay componente internacional",
         RULE_APCI.trigger(profile_no_intl) == False)

    # Status tests
    test("Status FULFILLED cuando esta registrado",
         RULE_APCI.check(profile_formal) == RequirementStatus.FULFILLED)
    test("Status NOT_FULFILLED cuando necesita registro",
         RULE_APCI.check(profile_needs_apci) == RequirementStatus.NOT_FULFILLED)

    # Gap tests
    gap = RULE_APCI.gap_generator(profile_needs_apci, "org_1", "Test")
    test("Genera gap cuando necesita registro", gap is not None)
    test("Gap APCI es CRITICAL", gap.severity == GapSeverity.CRITICAL)
    test("Gap menciona APCI", "APCI" in gap.description or "apci" in gap.description.lower())

    print("\n" + "="*60)
    print("TEST 4: REGLA LOCACION DE SERVICIOS")
    print("="*60)

    profile_locacion = create_association_with_locacion()

    test("Trigger cuando tiene locacion",
         RULE_LOCACION.trigger(profile_locacion) == True)

    profile_planilla = MockProfile(
        human_resources=MockHR(hiring_modalities=["Planilla"])
    )
    test("NO trigger cuando solo planilla",
         RULE_LOCACION.trigger(profile_planilla) == False)

    gap = RULE_LOCACION.gap_generator(profile_locacion, "org_1", "Test")
    test("Siempre genera advertencia", gap is not None)
    test("Severidad es MEDIUM", gap.severity == GapSeverity.MEDIUM)
    test("Menciona subordinacion o desnaturalizacion",
         "subordinacion" in gap.description.lower() or "desnaturaliza" in gap.description.lower())

    print("\n" + "="*60)
    print("TEST 5: REGLA PROTECCION DE DATOS")
    print("="*60)

    profile_with_data = create_ong_needs_apci()  # Tiene base de datos
    profile_no_data = create_informal_collective()  # No tiene

    test("Trigger cuando tiene base de datos",
         RULE_DATA.trigger(profile_with_data) == True)
    test("NO trigger cuando no tiene base de datos",
         RULE_DATA.trigger(profile_no_data) == False)

    gap = RULE_DATA.gap_generator(profile_with_data, "org_1", "Test")
    test("Genera advertencia", gap is not None)
    test("Menciona datos o LPDP",
         "datos" in gap.description.lower() or "lpdp" in gap.description.lower())

    print("\n" + "="*60)
    print("TEST 6: COHERENCIA DE SEVERIDADES")
    print("="*60)

    test("Personeria juridica es CRITICAL (bloquea operacion)",
         RULE_LEGAL_STATUS.default_gap_severity == GapSeverity.CRITICAL)
    test("APCI es CRITICAL (obligacion legal)",
         RULE_APCI.default_gap_severity == GapSeverity.CRITICAL)
    test("RUC es HIGH (importante pero no bloquea)",
         RULE_RUC.default_gap_severity == GapSeverity.HIGH)
    test("Locacion es MEDIUM (advertencia)",
         RULE_LOCACION.default_gap_severity == GapSeverity.MEDIUM)
    test("Datos es MEDIUM (advertencia)",
         RULE_DATA.default_gap_severity == GapSeverity.MEDIUM)

    print("\n" + "="*60)
    print("TEST 7: CASO COLECTIVO INFORMAL (multiples gaps)")
    print("="*60)

    profile = create_informal_collective()
    gaps = []
    for rule in ALL_RULES:
        if rule.trigger(profile):
            status = rule.check(profile)
            if status != RequirementStatus.FULFILLED and rule.gap_generator:
                gap = rule.gap_generator(profile, "org_1", "Colectivo")
                if gap:
                    gaps.append(gap)

    test("Detecta multiples gaps", len(gaps) >= 2)
    critical_gaps = [g for g in gaps if g.severity == GapSeverity.CRITICAL]
    test("Tiene gaps criticos", len(critical_gaps) >= 1)

    gap_ids = [g.id for g in gaps]
    test("Detecta falta de personeria", any("legal_status" in g for g in gap_ids))
    test("Detecta falta de RUC", any("ruc" in g for g in gap_ids))

    print("\n" + "="*60)
    print("TEST 8: CASO ONG FORMALIZADA (pocos/ningun gap)")
    print("="*60)

    profile = create_formalized_ong()
    gaps = []
    for rule in ALL_RULES:
        if rule.trigger(profile):
            status = rule.check(profile)
            if status != RequirementStatus.FULFILLED and rule.gap_generator:
                gap = rule.gap_generator(profile, "org_1", "ONG")
                if gap:
                    gaps.append(gap)

    critical_gaps = [g for g in gaps if g.severity == GapSeverity.CRITICAL]
    test("No tiene gaps criticos", len(critical_gaps) == 0)

    print("\n" + "="*60)
    print("TEST 9: EXPLICABILIDAD DE GAPS (para abogado)")
    print("="*60)

    profile = create_informal_collective()
    for rule in ALL_RULES:
        if rule.trigger(profile) and rule.gap_generator:
            gap = rule.gap_generator(profile, "org_1", "Test")
            if gap:
                test(f"Gap {rule.id} tiene descripcion",
                     gap.description and len(gap.description) > 10)
                test(f"Gap {rule.id} tiene impacto",
                     gap.impact and len(gap.impact) > 10)
                test(f"Gap {rule.id} tiene recomendacion",
                     gap.recommendation and len(gap.recommendation) > 10)
                test(f"Gap {rule.id} tiene source_fields",
                     len(gap.source_fields) > 0)

    print("\n" + "="*60)
    print(f"RESUMEN: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
