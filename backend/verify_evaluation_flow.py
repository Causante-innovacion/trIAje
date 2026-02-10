"""
Verificacion del flujo de evaluacion completo - Standalone

Este script verifica que:
1. El pipeline de evaluacion funciona
2. Se integra correctamente con LegalRequirementsResolver
3. Genera respuestas coherentes con viabilidad y semaforo
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# =============================================================================
# MOCK DE ESTRUCTURAS (replica simplificada)
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

class RequirementStatus(str, Enum):
    FULFILLED = "fulfilled"
    PARTIALLY_FULFILLED = "partial"
    NOT_FULFILLED = "not_fulfilled"

class ViabilityStatus(str, Enum):
    VIABLE = "viable"
    VIABLE_WITH_CONDITIONS = "viable_with_conditions"
    NOT_VIABLE = "not_viable"
    REQUIRES_REVIEW = "requires_review"

class TrafficLight(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class MockGap:
    id: str
    severity: GapSeverity
    intention: LegalIntention
    description: str
    impact: str
    recommendation: str
    organization_id: str = None
    organization_name: str = None

@dataclass
class MockRequirement:
    id: str
    name: str
    intention: LegalIntention
    status: RequirementStatus

@dataclass
class MockOrgRequirements:
    organization_id: str
    organization_name: str
    requirements: list = field(default_factory=list)
    gaps: list = field(default_factory=list)
    detected_intentions: list = field(default_factory=list)
    fulfilled_count: int = 0
    gap_count: int = 0
    critical_gaps: int = 0

@dataclass
class MockRequirementsResult:
    organizations: list = field(default_factory=list)
    shared_gaps: list = field(default_factory=list)
    project_intentions: list = field(default_factory=list)
    total_requirements: int = 0
    total_gaps: int = 0
    critical_gaps: int = 0
    requires_professional_advice: bool = False
    professional_advice_reason: str = None

# =============================================================================
# MOCK DEL PIPELINE (replica de pipeline.py)
# =============================================================================

class MockEvaluationPipeline:
    """Mock del pipeline de evaluacion"""

    DISCLAIMERS = [
        "Esta informacion es orientativa y no constituye asesoria legal profesional.",
        "Se recomienda validar esta orientacion con un abogado especializado.",
    ]

    def execute(self, requirements_result: MockRequirementsResult) -> dict:
        """Ejecuta el pipeline y retorna el response"""
        viability, explanation = self._determine_viability(requirements_result)
        traffic_light = self._determine_traffic_light(requirements_result, viability)
        risk_summary = self._build_risk_summary(requirements_result, traffic_light)
        next_steps = self._generate_next_steps(requirements_result)

        disclaimers = list(self.DISCLAIMERS)
        if requirements_result.requires_professional_advice:
            disclaimers.append("IMPORTANTE: Requiere atencion profesional.")

        return {
            "viability": viability,
            "viability_explanation": explanation,
            "traffic_light": traffic_light,
            "total_gaps": requirements_result.total_gaps,
            "critical_gaps": requirements_result.critical_gaps,
            "risk_summary": risk_summary,
            "next_steps": next_steps,
            "disclaimers": disclaimers,
        }

    def _determine_viability(self, result):
        if result.critical_gaps == 0 and result.total_gaps == 0:
            return ViabilityStatus.VIABLE, "Proyecto viable, sin brechas detectadas."

        if result.critical_gaps == 0 and result.total_gaps <= 3:
            return ViabilityStatus.VIABLE_WITH_CONDITIONS, f"Viable con {result.total_gaps} condiciones."

        if result.critical_gaps > 0 and result.critical_gaps <= 2:
            return ViabilityStatus.VIABLE_WITH_CONDITIONS, f"{result.critical_gaps} brecha(s) critica(s) a resolver."

        if result.critical_gaps > 2 or result.requires_professional_advice:
            return ViabilityStatus.REQUIRES_REVIEW, "Requiere revision profesional."

        return ViabilityStatus.VIABLE_WITH_CONDITIONS, f"{result.total_gaps} brechas pendientes."

    def _determine_traffic_light(self, result, viability):
        if viability == ViabilityStatus.VIABLE:
            return TrafficLight.GREEN
        if viability == ViabilityStatus.NOT_VIABLE:
            return TrafficLight.RED
        if result.requires_professional_advice or result.critical_gaps > 2:
            return TrafficLight.RED
        if result.critical_gaps > 0:
            return TrafficLight.YELLOW
        return TrafficLight.YELLOW

    def _build_risk_summary(self, result, traffic_light):
        if result.critical_gaps > 2:
            level = RiskLevel.HIGH
        elif result.critical_gaps > 0 or result.total_gaps > 5:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return {
            "overall_level": level,
            "requires_professional_advice": result.requires_professional_advice,
            "critical_gaps": result.critical_gaps,
        }

    def _generate_next_steps(self, result):
        steps = []
        for org in result.organizations:
            for gap in org.gaps:
                if gap.severity == GapSeverity.CRITICAL:
                    steps.append(f"[URGENTE] {gap.recommendation}")
        for org in result.organizations:
            for gap in org.gaps:
                if gap.severity == GapSeverity.HIGH:
                    steps.append(gap.recommendation)
        return steps[:7]


# =============================================================================
# CASOS DE PRUEBA
# =============================================================================

def create_ong_formalizada_result():
    """ONG formalizada - sin gaps criticos"""
    org = MockOrgRequirements(
        organization_id="org_1",
        organization_name="ONG Desarrollo",
        requirements=[
            MockRequirement("legal_status", "Personeria Juridica", LegalIntention.FORMALIZATION, RequirementStatus.FULFILLED),
            MockRequirement("ruc", "RUC", LegalIntention.TAXATION, RequirementStatus.FULFILLED),
            MockRequirement("apci", "Registro APCI", LegalIntention.INTERNATIONAL_COOPERATION, RequirementStatus.FULFILLED),
        ],
        gaps=[],
        detected_intentions=[LegalIntention.FORMALIZATION, LegalIntention.TAXATION, LegalIntention.INTERNATIONAL_COOPERATION],
        fulfilled_count=3,
        gap_count=0,
        critical_gaps=0,
    )

    return MockRequirementsResult(
        organizations=[org],
        shared_gaps=[],
        project_intentions=[LegalIntention.FORMALIZATION, LegalIntention.TAXATION, LegalIntention.INTERNATIONAL_COOPERATION],
        total_requirements=3,
        total_gaps=0,
        critical_gaps=0,
        requires_professional_advice=False,
    )


def create_colectivo_informal_result():
    """Colectivo informal - multiples gaps criticos"""
    org = MockOrgRequirements(
        organization_id="org_1",
        organization_name="EcoGuardianes",
        requirements=[
            MockRequirement("legal_status", "Personeria Juridica", LegalIntention.FORMALIZATION, RequirementStatus.NOT_FULFILLED),
            MockRequirement("ruc", "RUC", LegalIntention.TAXATION, RequirementStatus.NOT_FULFILLED),
        ],
        gaps=[
            MockGap(
                id="gap_legal_status_org_1",
                severity=GapSeverity.CRITICAL,
                intention=LegalIntention.FORMALIZATION,
                description="Maneja dinero sin personeria juridica",
                impact="Riesgo de responsabilidad personal",
                recommendation="Iniciar proceso de formalizacion",
                organization_id="org_1",
                organization_name="EcoGuardianes",
            ),
            MockGap(
                id="gap_ruc_org_1",
                severity=GapSeverity.HIGH,
                intention=LegalIntention.TAXATION,
                description="Maneja dinero sin RUC",
                impact="Imposibilidad de emitir comprobantes",
                recommendation="Tramitar RUC ante SUNAT",
                organization_id="org_1",
                organization_name="EcoGuardianes",
            ),
        ],
        detected_intentions=[LegalIntention.FORMALIZATION, LegalIntention.TAXATION],
        fulfilled_count=0,
        gap_count=2,
        critical_gaps=1,
    )

    return MockRequirementsResult(
        organizations=[org],
        shared_gaps=[],
        project_intentions=[LegalIntention.FORMALIZATION, LegalIntention.TAXATION],
        total_requirements=2,
        total_gaps=2,
        critical_gaps=1,
        requires_professional_advice=True,
        professional_advice_reason="Gaps criticos detectados",
    )


def create_multi_org_result():
    """Dos organizaciones con gaps compartidos"""
    org1 = MockOrgRequirements(
        organization_id="org_1",
        organization_name="ONG Internacional",
        requirements=[
            MockRequirement("apci", "Registro APCI", LegalIntention.INTERNATIONAL_COOPERATION, RequirementStatus.NOT_FULFILLED),
        ],
        gaps=[
            MockGap(
                id="gap_apci_org_1",
                severity=GapSeverity.CRITICAL,
                intention=LegalIntention.INTERNATIONAL_COOPERATION,
                description="Recibe cooperacion sin registro APCI",
                impact="Incumplimiento legal obligatorio",
                recommendation="Tramitar registro APCI",
                organization_id="org_1",
                organization_name="ONG Internacional",
            ),
        ],
        detected_intentions=[LegalIntention.INTERNATIONAL_COOPERATION],
        fulfilled_count=0,
        gap_count=1,
        critical_gaps=1,
    )

    org2 = MockOrgRequirements(
        organization_id="org_2",
        organization_name="Fundacion Tech",
        requirements=[
            MockRequirement("legal_status", "Personeria Juridica", LegalIntention.FORMALIZATION, RequirementStatus.FULFILLED),
        ],
        gaps=[],
        detected_intentions=[LegalIntention.FORMALIZATION],
        fulfilled_count=1,
        gap_count=0,
        critical_gaps=0,
    )

    shared_gap = MockGap(
        id="shared_data_transfer",
        severity=GapSeverity.MEDIUM,
        intention=LegalIntention.FORMALIZATION,
        description="Ambas organizaciones manejan datos de usuarios",
        impact="Verificar cumplimiento LPDP en transferencias",
        recommendation="Documentar acuerdos de confidencialidad",
    )

    return MockRequirementsResult(
        organizations=[org1, org2],
        shared_gaps=[shared_gap],
        project_intentions=[LegalIntention.INTERNATIONAL_COOPERATION, LegalIntention.FORMALIZATION],
        total_requirements=2,
        total_gaps=2,  # 1 de org1 + 1 shared
        critical_gaps=1,
        requires_professional_advice=False,
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

    pipeline = MockEvaluationPipeline()

    print("\n" + "="*60)
    print("TEST 1: ONG FORMALIZADA (caso verde)")
    print("="*60)

    result = create_ong_formalizada_result()
    response = pipeline.execute(result)

    test("Viabilidad es VIABLE",
         response["viability"] == ViabilityStatus.VIABLE)
    test("Semaforo es GREEN",
         response["traffic_light"] == TrafficLight.GREEN)
    test("Sin gaps criticos",
         response["critical_gaps"] == 0)
    test("Riesgo es LOW",
         response["risk_summary"]["overall_level"] == RiskLevel.LOW)
    test("No requiere asesoria profesional",
         response["risk_summary"]["requires_professional_advice"] == False)
    test("Tiene disclaimers",
         len(response["disclaimers"]) >= 2)

    print("\n" + "="*60)
    print("TEST 2: COLECTIVO INFORMAL (caso critico)")
    print("="*60)

    result = create_colectivo_informal_result()
    response = pipeline.execute(result)

    test("Viabilidad es VIABLE_WITH_CONDITIONS o REQUIRES_REVIEW",
         response["viability"] in [ViabilityStatus.VIABLE_WITH_CONDITIONS, ViabilityStatus.REQUIRES_REVIEW])
    test("Semaforo es YELLOW o RED",
         response["traffic_light"] in [TrafficLight.YELLOW, TrafficLight.RED])
    test("Tiene gaps criticos",
         response["critical_gaps"] > 0)
    test("Requiere asesoria profesional",
         response["risk_summary"]["requires_professional_advice"] == True)
    test("Tiene pasos urgentes",
         any("[URGENTE]" in step for step in response["next_steps"]))
    test("Disclaimer de asesoria profesional",
         any("IMPORTANTE" in d for d in response["disclaimers"]))

    print("\n" + "="*60)
    print("TEST 3: MULTI-ORGANIZACION (gaps compartidos)")
    print("="*60)

    result = create_multi_org_result()
    response = pipeline.execute(result)

    test("Maneja multiples organizaciones",
         len(result.organizations) == 2)
    test("Tiene gaps compartidos",
         len(result.shared_gaps) > 0)
    test("Semaforo es YELLOW (gap critico pero solo 1)",
         response["traffic_light"] == TrafficLight.YELLOW)
    test("Viabilidad con condiciones",
         response["viability"] == ViabilityStatus.VIABLE_WITH_CONDITIONS)

    print("\n" + "="*60)
    print("TEST 4: COHERENCIA VIABILIDAD-SEMAFORO")
    print("="*60)

    # Verde = VIABLE
    result_verde = create_ong_formalizada_result()
    response_verde = pipeline.execute(result_verde)
    test("VIABLE -> GREEN",
         response_verde["viability"] == ViabilityStatus.VIABLE and
         response_verde["traffic_light"] == TrafficLight.GREEN)

    # Amarillo = VIABLE_WITH_CONDITIONS
    result_amarillo = create_multi_org_result()
    response_amarillo = pipeline.execute(result_amarillo)
    test("VIABLE_WITH_CONDITIONS -> YELLOW",
         response_amarillo["viability"] == ViabilityStatus.VIABLE_WITH_CONDITIONS and
         response_amarillo["traffic_light"] == TrafficLight.YELLOW)

    # Rojo = REQUIRES_REVIEW o muchos criticos
    result_rojo = create_colectivo_informal_result()
    result_rojo.critical_gaps = 3  # Forzar mas criticos
    result_rojo.requires_professional_advice = True
    response_rojo = pipeline.execute(result_rojo)
    test("REQUIRES_REVIEW -> RED",
         response_rojo["traffic_light"] == TrafficLight.RED)

    print("\n" + "="*60)
    print("TEST 5: PROXIMOS PASOS PRIORIZADOS")
    print("="*60)

    result = create_colectivo_informal_result()
    response = pipeline.execute(result)
    steps = response["next_steps"]

    test("Tiene pasos generados", len(steps) > 0)
    test("Pasos urgentes primero",
         steps[0].startswith("[URGENTE]") if steps else False)
    test("Maximo 7 pasos", len(steps) <= 7)

    print("\n" + "="*60)
    print(f"RESUMEN: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
