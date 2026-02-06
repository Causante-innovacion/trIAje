"""
Legal Requirements Resolver
Aplica las reglas de negocio para determinar requisitos y brechas legales.
"""

from app.modules.intake.schemas import (
    LegalProfile,
    OrganizationProfile,
    NormalizedProjectIntake,
)
from .schemas import (
    LegalIntention,
    LegalRequirement,
    RequirementStatus,
    LegalGap,
    GapSeverity,
    OrganizationRequirements,
    LegalRequirementsResult,
)
from .rules import LEGAL_RULES, LegalRule


class LegalRequirementsResolver:
    """
    Resuelve los requisitos legales aplicables a un proyecto.

    Flujo:
    1. Recibe NormalizedProjectIntake (1-3 organizaciones)
    2. Para cada organización, evalúa todas las reglas
    3. Genera lista de requisitos y brechas
    4. Detecta riesgos compartidos entre organizaciones
    5. Retorna LegalRequirementsResult

    Este resultado se usa para:
    - Mostrar al usuario qué está cumpliendo y qué le falta
    - Generar queries específicos para el RAG
    - Alimentar al módulo de IA con contexto estructurado
    """

    def __init__(self, rules: list[LegalRule] | None = None):
        self.rules = rules or LEGAL_RULES

    def resolve(
        self,
        project: NormalizedProjectIntake,
    ) -> LegalRequirementsResult:
        """
        Resuelve requisitos para un proyecto completo.
        """
        result = LegalRequirementsResult()
        all_intentions: set[LegalIntention] = set()

        # Analizar cada organización
        for org in project.organizations:
            org_result = self._resolve_organization(org)
            result.organizations.append(org_result)

            # Acumular intenciones
            all_intentions.update(org_result.detected_intentions)

            # Acumular contadores
            result.total_requirements += len(org_result.requirements)
            result.total_gaps += org_result.gap_count
            result.critical_gaps += org_result.critical_gaps

        # Detectar riesgos compartidos
        if len(project.organizations) > 1:
            result.shared_gaps = self._detect_shared_gaps(project.organizations)
            result.total_gaps += len(result.shared_gaps)
            result.critical_gaps += sum(
                1 for g in result.shared_gaps if g.severity == GapSeverity.CRITICAL
            )

        # Intenciones del proyecto
        result.project_intentions = list(all_intentions)

        # Determinar si requiere asesoría profesional
        result.requires_professional_advice = (
            result.critical_gaps > 0
            or result.total_gaps >= 5
        )

        if result.requires_professional_advice:
            if result.critical_gaps > 0:
                result.professional_advice_reason = (
                    f"Se detectaron {result.critical_gaps} brechas críticas que "
                    "requieren atención profesional inmediata."
                )
            else:
                result.professional_advice_reason = (
                    f"La complejidad del caso ({result.total_gaps} brechas) "
                    "sugiere validación con un profesional."
                )

        return result

    def _resolve_organization(
        self,
        org: OrganizationProfile,
    ) -> OrganizationRequirements:
        """
        Resuelve requisitos para una organización específica.
        """
        org_result = OrganizationRequirements(
            organization_id=org.id,
            organization_name=org.name,
        )

        profile = org.legal_profile

        for rule in self.rules:
            # Verificar si la regla aplica
            if not rule.trigger(profile):
                continue

            # Crear requisito
            status = rule.check(profile)
            requirement = LegalRequirement(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                intention=rule.intention,
                status=status,
                related_laws=rule.related_laws,
                required_documents=rule.required_documents,
                required_registrations=rule.required_registrations,
            )

            org_result.requirements.append(requirement)

            # Registrar intención
            if rule.intention not in org_result.detected_intentions:
                org_result.detected_intentions.append(rule.intention)

            # Contar cumplidos
            if status == RequirementStatus.FULFILLED:
                org_result.fulfilled_count += 1
                continue

            # Generar brecha si no cumple
            if status in [RequirementStatus.NOT_FULFILLED, RequirementStatus.PARTIALLY_FULFILLED]:
                if rule.gap_generator:
                    gap = rule.gap_generator(profile, org.id, org.name)
                    if gap:
                        org_result.gaps.append(gap)
                        org_result.gap_count += 1
                        if gap.severity == GapSeverity.CRITICAL:
                            org_result.critical_gaps += 1

            # Generar brecha para status UNKNOWN si tiene generador
            elif status == RequirementStatus.UNKNOWN and rule.gap_generator:
                gap = rule.gap_generator(profile, org.id, org.name)
                if gap:
                    org_result.gaps.append(gap)
                    org_result.gap_count += 1
                    if gap.severity == GapSeverity.CRITICAL:
                        org_result.critical_gaps += 1

        return org_result

    def _detect_shared_gaps(
        self,
        organizations: list[OrganizationProfile],
    ) -> list[LegalGap]:
        """
        Detecta brechas compartidas entre organizaciones.
        """
        shared_gaps = []

        # Verificar si múltiples orgs manejan datos de usuarios
        orgs_with_data = [
            org for org in organizations
            if "Bases de datos de usuarios" in org.legal_profile.intangibles.intangible_assets
        ]
        if len(orgs_with_data) > 1:
            shared_gaps.append(LegalGap(
                id="shared_data_transfer",
                requirement_id="data_protection",
                severity=GapSeverity.MEDIUM,
                intention=LegalIntention.DATA_PROTECTION,
                description=f"{len(orgs_with_data)} organizaciones manejan bases de datos de usuarios",
                impact="Si hay transferencia de datos entre organizaciones, requiere consentimiento específico y medidas de seguridad.",
                recommendation="Verificar si hay flujo de datos entre organizaciones. Documentar bases legales para transferencia. Implementar acuerdos de confidencialidad.",
                rag_query_hint="transferencia datos personales entre organizaciones LPDP consentimiento",
                source_fields=["intangibles.intangible_assets"],
            ))

        # Verificar si hay relación empleador-financiador
        has_funder = any(
            org.role in ["Financiador", "Funder"]
            for org in organizations
        )
        has_employees = any(
            "Planilla" in org.legal_profile.human_resources.hiring_modalities
            for org in organizations
        )
        if has_funder and has_employees:
            shared_gaps.append(LegalGap(
                id="shared_labor_funding",
                requirement_id="labor_contracts_valid",
                severity=GapSeverity.MEDIUM,
                intention=LegalIntention.HIRING,
                description="Proyecto con financiador y organizaciones con empleados",
                impact="Si el financiador supervisa o dirige el trabajo, podría configurarse responsabilidad solidaria laboral.",
                recommendation="Documentar claramente que el financiador no tiene control sobre el personal del ejecutor.",
                rag_query_hint="responsabilidad solidaria laboral financiador proyecto ONG",
                source_fields=["human_resources.hiring_modalities"],
            ))

        # Verificar si múltiples orgs reciben cooperación internacional
        orgs_with_coop = [
            org for org in organizations
            if org.legal_profile.international_cooperation.receives_international_cooperation
        ]
        if len(orgs_with_coop) > 1:
            # Verificar si todas están registradas en APCI
            orgs_without_apci = [
                org for org in orgs_with_coop
                if org.legal_profile.international_cooperation.apci_status != "Registrado"
            ]
            if orgs_without_apci:
                shared_gaps.append(LegalGap(
                    id="shared_apci_multiple",
                    requirement_id="apci_registration",
                    severity=GapSeverity.HIGH,
                    intention=LegalIntention.INTERNATIONAL_COOPERATION,
                    description=f"{len(orgs_without_apci)} de {len(orgs_with_coop)} organizaciones que reciben cooperación no están en APCI",
                    impact="Todas las organizaciones que reciben fondos internacionales deben estar registradas individualmente.",
                    recommendation="Cada organización receptora debe completar su registro en APCI de forma independiente.",
                    rag_query_hint="múltiples ENIEX proyecto conjunto APCI requisitos",
                    source_fields=["international_cooperation.apci_status"],
                ))

        return shared_gaps

    def get_rag_queries(
        self,
        result: LegalRequirementsResult,
    ) -> list[dict]:
        """
        Genera queries para el RAG basados en las brechas detectadas.
        Útil para justificar y explicar los requisitos con normativa.
        """
        queries = []

        # Queries por brecha de cada organización
        for org in result.organizations:
            for gap in org.gaps:
                if gap.rag_query_hint:
                    queries.append({
                        "query": gap.rag_query_hint,
                        "intention": gap.intention.value,
                        "organization_id": gap.organization_id,
                        "gap_id": gap.id,
                        "priority": (
                            1 if gap.severity == GapSeverity.CRITICAL
                            else 2 if gap.severity == GapSeverity.HIGH
                            else 3
                        ),
                    })

        # Queries por brechas compartidas
        for gap in result.shared_gaps:
            if gap.rag_query_hint:
                queries.append({
                    "query": gap.rag_query_hint,
                    "intention": gap.intention.value,
                    "organization_id": None,
                    "gap_id": gap.id,
                    "priority": (
                        1 if gap.severity == GapSeverity.CRITICAL
                        else 2 if gap.severity == GapSeverity.HIGH
                        else 3
                    ),
                })

        # Ordenar por prioridad
        queries.sort(key=lambda x: x["priority"])

        return queries


# Instancia global
_resolver: LegalRequirementsResolver | None = None


def get_resolver() -> LegalRequirementsResolver:
    """Obtiene el resolver global"""
    global _resolver
    if _resolver is None:
        _resolver = LegalRequirementsResolver()
    return _resolver


def resolve_requirements(project: NormalizedProjectIntake) -> LegalRequirementsResult:
    """Función de conveniencia para resolver requisitos"""
    return get_resolver().resolve(project)
