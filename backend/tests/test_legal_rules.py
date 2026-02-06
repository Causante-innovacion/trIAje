"""
Tests para el módulo de reglas legales.

Verificar que:
- Las reglas se activan cuando deben
- No se activan cuando no deben
- Las severidades son coherentes
- El multi-org se comporta como esperas
- Los gaps producidos son explicables a un abogado
"""

import pytest
from datetime import datetime

from app.modules.intake.schemas import (
    LegalProfile,
    IdentityData,
    FormalizationData,
    IncomeData,
    InternationalCooperationData,
    HumanResourcesData,
    AccountingData,
    GovernanceData,
    IntangiblesData,
    OrganizationProfile,
    OrganizationRole,
    NormalizedProjectIntake,
    ProjectInfo,
    ToolType,
    ToolSpecificData,
    EvaluationSpecificData,
    ProjectRiskAssessment,
)
from app.modules.legal_rules import (
    LegalRequirementsResolver,
    LegalIntention,
    LegalGap,
    GapSeverity,
    LegalRequirementsResult,
)
from app.modules.legal_rules.rules import (
    RULE_LEGAL_STATUS,
    RULE_RUC,
    RULE_APCI_REGISTRATION,
    RULE_IR_EXONERATION,
    RULE_LABOR_CONTRACTS,
    RULE_LOCACION_RISK,
    RULE_ACCOUNTING_RECORDS,
    RULE_GOVERNANCE_BODIES,
    RULE_LEGAL_REPRESENTATIVE,
    RULE_DATA_PROTECTION,
    RULE_INTELLECTUAL_PROPERTY,
    RequirementStatus,
)


# =============================================================================
# FIXTURES - Perfiles de prueba
# =============================================================================

def create_empty_profile() -> LegalProfile:
    """Perfil completamente vacío"""
    return LegalProfile()


def create_informal_collective() -> LegalProfile:
    """Colectivo no formalizado que maneja dinero - caso crítico"""
    return LegalProfile(
        identity=IdentityData(
            org_type="Colectivo / iniciativa no formalizada",
            org_purpose="Ambiental",
            seeks_profits=False,
        ),
        formalization=FormalizationData(
            has_legal_status="No",
            ruc_status="No lo tengo",
            special_registries=["Ninguno"],
        ),
        income=IncomeData(
            handles_money=True,
            receives_foreign_funds=False,
            income_sources=["Donaciones"],
        ),
        international_cooperation=InternationalCooperationData(
            receives_international_cooperation=False,
            apci_status="No aplica",
        ),
        human_resources=HumanResourcesData(
            hiring_modalities=["Voluntariado"],
            contracts_valid="No aplica",
        ),
        accounting=AccountingData(
            has_accounting_records="No",
            available_documents=["Ninguno"],
        ),
        governance=GovernanceData(
            has_governance_bodies=False,
            has_legal_representative="No",
        ),
        intangibles=IntangiblesData(
            intangible_assets=["Ninguno"],
        ),
    )


def create_formalized_ong() -> LegalProfile:
    """ONG formalizada y en regla - caso verde"""
    return LegalProfile(
        identity=IdentityData(
            org_type="ONG",
            org_purpose="Asistencial / social",
            seeks_profits=False,
        ),
        formalization=FormalizationData(
            has_legal_status="Sí",
            ruc_status="Lo tengo",
            special_registries=["Exonerada de Impuesto a la renta", "APCI"],
        ),
        income=IncomeData(
            handles_money=True,
            receives_foreign_funds=True,
            income_sources=["Donaciones", "Cooperación internacional"],
        ),
        international_cooperation=InternationalCooperationData(
            receives_international_cooperation=True,
            apci_status="Registrado",
        ),
        human_resources=HumanResourcesData(
            hiring_modalities=["Planilla", "Voluntariado"],
            contracts_valid="Sí",
        ),
        accounting=AccountingData(
            has_accounting_records="Sí, completos",
            available_documents=["Estatuto o acta de constitución", "Estados financieros", "Memorias anuales"],
        ),
        governance=GovernanceData(
            has_governance_bodies=True,
            has_legal_representative="Sí",
        ),
        intangibles=IntangiblesData(
            intangible_assets=["Software de terceros"],
        ),
    )


def create_ong_needs_apci() -> LegalProfile:
    """ONG que recibe cooperación pero no está en APCI - gap crítico"""
    return LegalProfile(
        identity=IdentityData(
            org_type="ONG",
            org_purpose="Educativo",
            seeks_profits=False,
        ),
        formalization=FormalizationData(
            has_legal_status="Sí",
            ruc_status="Lo tengo",
            special_registries=["Exonerada de Impuesto a la renta"],
        ),
        income=IncomeData(
            handles_money=True,
            receives_foreign_funds=True,
            income_sources=["Cooperación internacional"],
        ),
        international_cooperation=InternationalCooperationData(
            receives_international_cooperation=True,
            apci_status="Necesita registro",
        ),
        human_resources=HumanResourcesData(
            hiring_modalities=["Planilla"],
            contracts_valid="Sí",
        ),
        accounting=AccountingData(
            has_accounting_records="Sí, completos",
            available_documents=["Estatuto o acta de constitución", "Estados financieros"],
        ),
        governance=GovernanceData(
            has_governance_bodies=True,
            has_legal_representative="Sí",
        ),
        intangibles=IntangiblesData(
            intangible_assets=["Bases de datos de usuarios"],
        ),
    )


def create_association_with_locacion() -> LegalProfile:
    """Asociación que usa locación de servicios - riesgo laboral"""
    return LegalProfile(
        identity=IdentityData(
            org_type="Asociación",
            org_purpose="Cultural",
            seeks_profits=False,
        ),
        formalization=FormalizationData(
            has_legal_status="Sí",
            ruc_status="Lo tengo",
            special_registries=["Ninguno"],
        ),
        income=IncomeData(
            handles_money=True,
            receives_foreign_funds=False,
            income_sources=["Donaciones", "Venta de servicios o productos"],
        ),
        international_cooperation=InternationalCooperationData(
            receives_international_cooperation=False,
            apci_status="No aplica",
        ),
        human_resources=HumanResourcesData(
            hiring_modalities=["Locación de servicios"],
            contracts_valid="Sí",
        ),
        accounting=AccountingData(
            has_accounting_records="Sí, parciales",
            available_documents=["Estatuto o acta de constitución"],
        ),
        governance=GovernanceData(
            has_governance_bodies=True,
            has_legal_representative="Sí",
        ),
        intangibles=IntangiblesData(
            intangible_assets=["Marca o símbolos distintivos"],
        ),
    )


def create_tech_foundation() -> LegalProfile:
    """Fundación tecnológica con activos intangibles"""
    return LegalProfile(
        identity=IdentityData(
            org_type="Fundación",
            org_purpose="Tecnológico / innovación",
            seeks_profits=False,
        ),
        formalization=FormalizationData(
            has_legal_status="Sí",
            ruc_status="Lo tengo",
            special_registries=["Exonerada de Impuesto a la renta"],
        ),
        income=IncomeData(
            handles_money=True,
            receives_foreign_funds=False,
            income_sources=["Fondos privados"],
        ),
        international_cooperation=InternationalCooperationData(
            receives_international_cooperation=False,
            apci_status="No aplica",
        ),
        human_resources=HumanResourcesData(
            hiring_modalities=["Planilla"],
            contracts_valid="Sí",
        ),
        accounting=AccountingData(
            has_accounting_records="Sí, completos",
            available_documents=["Estatuto o acta de constitución", "Estados financieros"],
        ),
        governance=GovernanceData(
            has_governance_bodies=True,
            has_legal_representative="Sí",
        ),
        intangibles=IntangiblesData(
            intangible_assets=["Software propio", "Bases de datos de usuarios", "Contenido con derechos de autor"],
        ),
    )


# =============================================================================
# TESTS - Reglas individuales
# =============================================================================

class TestRuleLegalStatus:
    """Tests para RULE_LEGAL_STATUS (personería jurídica)"""

    def test_trigger_when_handles_money(self):
        """Debe activarse cuando maneja dinero"""
        profile = create_informal_collective()
        assert RULE_LEGAL_STATUS.trigger(profile) is True

    def test_no_trigger_when_no_money(self):
        """No debe activarse si no maneja dinero"""
        profile = create_empty_profile()
        profile.income.handles_money = False
        assert RULE_LEGAL_STATUS.trigger(profile) is False

    def test_fulfilled_when_has_legal_status(self):
        """Debe estar cumplido si tiene personería"""
        profile = create_formalized_ong()
        assert RULE_LEGAL_STATUS.check(profile) == RequirementStatus.FULFILLED

    def test_not_fulfilled_when_no_legal_status(self):
        """Debe estar incumplido si no tiene personería"""
        profile = create_informal_collective()
        assert RULE_LEGAL_STATUS.check(profile) == RequirementStatus.NOT_FULFILLED

    def test_partial_when_in_progress(self):
        """Debe estar parcial si está en trámite"""
        profile = create_informal_collective()
        profile.formalization.has_legal_status = "En trámite"
        assert RULE_LEGAL_STATUS.check(profile) == RequirementStatus.PARTIALLY_FULFILLED

    def test_gap_generated_when_not_fulfilled(self):
        """Debe generar gap crítico cuando no cumple"""
        profile = create_informal_collective()
        gap = RULE_LEGAL_STATUS.gap_generator(profile, "org_1", "Mi Colectivo")

        assert gap is not None
        assert gap.severity == GapSeverity.CRITICAL
        assert gap.intention == LegalIntention.FORMALIZATION
        assert "personería jurídica" in gap.description.lower()


class TestRuleRUC:
    """Tests para RULE_RUC"""

    def test_trigger_when_handles_money(self):
        profile = create_informal_collective()
        assert RULE_RUC.trigger(profile) is True

    def test_fulfilled_when_has_ruc(self):
        profile = create_formalized_ong()
        assert RULE_RUC.check(profile) == RequirementStatus.FULFILLED

    def test_not_fulfilled_when_no_ruc(self):
        profile = create_informal_collective()
        assert RULE_RUC.check(profile) == RequirementStatus.NOT_FULFILLED


class TestRuleAPCI:
    """Tests para RULE_APCI_REGISTRATION"""

    def test_trigger_when_receives_international_coop(self):
        """Debe activarse cuando recibe cooperación internacional"""
        profile = create_ong_needs_apci()
        assert RULE_APCI_REGISTRATION.trigger(profile) is True

    def test_trigger_when_receives_foreign_funds(self):
        """Debe activarse cuando recibe fondos del exterior"""
        profile = create_empty_profile()
        profile.income.receives_foreign_funds = True
        assert RULE_APCI_REGISTRATION.trigger(profile) is True

    def test_trigger_when_income_source_coop(self):
        """Debe activarse cuando tiene cooperación en fuentes de ingreso"""
        profile = create_empty_profile()
        profile.income.income_sources = ["Cooperación internacional"]
        assert RULE_APCI_REGISTRATION.trigger(profile) is True

    def test_no_trigger_when_no_international(self):
        """No debe activarse si no hay componente internacional"""
        profile = create_association_with_locacion()
        assert RULE_APCI_REGISTRATION.trigger(profile) is False

    def test_fulfilled_when_registered(self):
        profile = create_formalized_ong()
        assert RULE_APCI_REGISTRATION.check(profile) == RequirementStatus.FULFILLED

    def test_not_fulfilled_when_needs_registration(self):
        profile = create_ong_needs_apci()
        assert RULE_APCI_REGISTRATION.check(profile) == RequirementStatus.NOT_FULFILLED

    def test_gap_is_critical(self):
        """Gap de APCI debe ser crítico"""
        profile = create_ong_needs_apci()
        gap = RULE_APCI_REGISTRATION.gap_generator(profile, "org_1", "Mi ONG")

        assert gap is not None
        assert gap.severity == GapSeverity.CRITICAL
        assert "APCI" in gap.description


class TestRuleIRExoneration:
    """Tests para RULE_IR_EXONERATION"""

    def test_trigger_for_nonprofit_formalized(self):
        """Debe activarse para ONG sin fines de lucro formalizada"""
        profile = create_formalized_ong()
        assert RULE_IR_EXONERATION.trigger(profile) is True

    def test_no_trigger_for_informal(self):
        """No debe activarse si no está formalizada"""
        profile = create_informal_collective()
        assert RULE_IR_EXONERATION.trigger(profile) is False

    def test_no_trigger_for_empresa(self):
        """No debe activarse para empresa con fines de lucro"""
        profile = create_empty_profile()
        profile.identity.org_type = "Empresa"
        profile.identity.seeks_profits = True
        profile.formalization.has_legal_status = "Sí"
        assert RULE_IR_EXONERATION.trigger(profile) is False

    def test_fulfilled_when_exonerated(self):
        profile = create_formalized_ong()
        assert RULE_IR_EXONERATION.check(profile) == RequirementStatus.FULFILLED

    def test_not_fulfilled_when_not_exonerated(self):
        profile = create_association_with_locacion()  # No tiene exoneración
        # Pero primero verifiquemos que la regla aplica
        profile.identity.seeks_profits = False
        assert RULE_IR_EXONERATION.check(profile) == RequirementStatus.NOT_FULFILLED


class TestRuleLabor:
    """Tests para reglas laborales"""

    def test_contracts_trigger_when_has_planilla(self):
        profile = create_formalized_ong()
        assert RULE_LABOR_CONTRACTS.trigger(profile) is True

    def test_contracts_trigger_when_has_locacion(self):
        profile = create_association_with_locacion()
        assert RULE_LABOR_CONTRACTS.trigger(profile) is True

    def test_contracts_no_trigger_when_only_volunteers(self):
        profile = create_informal_collective()  # Solo voluntariado
        assert RULE_LABOR_CONTRACTS.trigger(profile) is False

    def test_locacion_risk_trigger(self):
        """Riesgo de locación siempre se activa si hay locación"""
        profile = create_association_with_locacion()
        assert RULE_LOCACION_RISK.trigger(profile) is True

    def test_locacion_risk_always_generates_warning(self):
        """Siempre genera advertencia de verificar subordinación"""
        profile = create_association_with_locacion()
        gap = RULE_LOCACION_RISK.gap_generator(profile, "org_1", "Mi Asociación")

        assert gap is not None
        assert gap.severity == GapSeverity.MEDIUM
        assert "subordinación" in gap.description.lower() or "desnaturaliza" in gap.description.lower()


class TestRuleAccounting:
    """Tests para RULE_ACCOUNTING_RECORDS"""

    def test_trigger_when_handles_money(self):
        profile = create_informal_collective()
        assert RULE_ACCOUNTING_RECORDS.trigger(profile) is True

    def test_fulfilled_when_complete(self):
        profile = create_formalized_ong()
        assert RULE_ACCOUNTING_RECORDS.check(profile) == RequirementStatus.FULFILLED

    def test_partial_when_incomplete(self):
        profile = create_association_with_locacion()  # "Sí, parciales"
        assert RULE_ACCOUNTING_RECORDS.check(profile) == RequirementStatus.PARTIALLY_FULFILLED

    def test_not_fulfilled_when_none(self):
        profile = create_informal_collective()
        assert RULE_ACCOUNTING_RECORDS.check(profile) == RequirementStatus.NOT_FULFILLED


class TestRuleGovernance:
    """Tests para reglas de gobernanza"""

    def test_governance_bodies_trigger_for_association(self):
        profile = create_formalized_ong()
        assert RULE_GOVERNANCE_BODIES.trigger(profile) is True

    def test_governance_bodies_no_trigger_for_colectivo(self):
        profile = create_informal_collective()
        assert RULE_GOVERNANCE_BODIES.trigger(profile) is False

    def test_legal_rep_trigger_when_formalized(self):
        profile = create_formalized_ong()
        assert RULE_LEGAL_REPRESENTATIVE.trigger(profile) is True

    def test_legal_rep_no_trigger_when_informal(self):
        profile = create_informal_collective()
        assert RULE_LEGAL_REPRESENTATIVE.trigger(profile) is False


class TestRuleDataProtection:
    """Tests para RULE_DATA_PROTECTION"""

    def test_trigger_when_has_user_database(self):
        profile = create_ong_needs_apci()  # Tiene "Bases de datos de usuarios"
        assert RULE_DATA_PROTECTION.trigger(profile) is True

    def test_no_trigger_when_no_database(self):
        profile = create_informal_collective()
        assert RULE_DATA_PROTECTION.trigger(profile) is False

    def test_always_generates_warning(self):
        """Siempre genera advertencia para verificar cumplimiento LPDP"""
        profile = create_ong_needs_apci()
        gap = RULE_DATA_PROTECTION.gap_generator(profile, "org_1", "Mi ONG")

        assert gap is not None
        assert gap.severity == GapSeverity.MEDIUM
        assert "LPDP" in gap.description or "datos" in gap.description.lower()


class TestRuleIntellectualProperty:
    """Tests para RULE_INTELLECTUAL_PROPERTY"""

    def test_trigger_when_has_own_software(self):
        profile = create_tech_foundation()
        assert RULE_INTELLECTUAL_PROPERTY.trigger(profile) is True

    def test_trigger_when_has_brand(self):
        profile = create_association_with_locacion()  # Tiene marca
        assert RULE_INTELLECTUAL_PROPERTY.trigger(profile) is True

    def test_no_trigger_when_only_third_party_software(self):
        profile = create_formalized_ong()  # Solo "Software de terceros"
        assert RULE_INTELLECTUAL_PROPERTY.trigger(profile) is False


# =============================================================================
# TESTS - Resolver completo
# =============================================================================

def create_test_project(
    organizations: list[tuple[str, str, LegalProfile]],
) -> NormalizedProjectIntake:
    """Helper para crear proyecto de prueba"""
    org_profiles = [
        OrganizationProfile(
            id=org_id,
            name=org_name,
            role=OrganizationRole.MAIN_EXECUTOR if i == 0 else OrganizationRole.CO_EXECUTOR,
            legal_profile=profile,
        )
        for i, (org_id, org_name, profile) in enumerate(organizations)
    ]

    return NormalizedProjectIntake(
        tool=ToolType.EVALUATION,
        project=ProjectInfo(id="proj_test", name="Proyecto de Prueba"),
        organizations=org_profiles,
        tool_specific=ToolSpecificData(
            evaluation=EvaluationSpecificData(
                evaluation_goals=["Viabilidad legal del proyecto"],
                legal_areas=["Formalización"],
                urgency="Corto plazo (semanas)",
            )
        ),
        risk_assessment=ProjectRiskAssessment(),
        total_organizations=len(org_profiles),
    )


class TestResolverSingleOrg:
    """Tests del resolver con una sola organización"""

    def test_informal_collective_multiple_critical_gaps(self):
        """Colectivo informal debe tener múltiples gaps críticos"""
        project = create_test_project([
            ("org_1", "EcoGuardianes", create_informal_collective())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        # Debe tener gaps
        assert result.total_gaps > 0
        assert result.critical_gaps > 0

        # Verificar gaps específicos
        org = result.organizations[0]
        gap_ids = [g.id for g in org.gaps]

        assert any("legal_status" in g for g in gap_ids), "Debe detectar falta de personería"
        assert any("ruc" in g for g in gap_ids), "Debe detectar falta de RUC"
        assert any("accounting" in g for g in gap_ids), "Debe detectar falta de contabilidad"

    def test_formalized_ong_minimal_gaps(self):
        """ONG formalizada debe tener pocos o ningún gap"""
        project = create_test_project([
            ("org_1", "ONG Desarrollo", create_formalized_ong())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        # No debe tener gaps críticos
        assert result.critical_gaps == 0

        # Puede tener advertencias menores, pero no errores graves
        org = result.organizations[0]
        for gap in org.gaps:
            assert gap.severity != GapSeverity.CRITICAL

    def test_ong_needs_apci_has_critical_gap(self):
        """ONG sin APCI que recibe cooperación debe tener gap crítico"""
        project = create_test_project([
            ("org_1", "ONG Internacional", create_ong_needs_apci())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        # Debe tener gap de APCI
        org = result.organizations[0]
        apci_gaps = [g for g in org.gaps if "apci" in g.id.lower()]

        assert len(apci_gaps) > 0, "Debe detectar necesidad de APCI"
        assert apci_gaps[0].severity == GapSeverity.CRITICAL

    def test_detected_intentions_coherent(self):
        """Las intenciones detectadas deben ser coherentes con el perfil"""
        project = create_test_project([
            ("org_1", "ONG Internacional", create_ong_needs_apci())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        org = result.organizations[0]

        # Debe detectar intención de cooperación internacional
        assert LegalIntention.INTERNATIONAL_COOPERATION in org.detected_intentions

        # Debe detectar intención de protección de datos (tiene base de datos)
        assert LegalIntention.DATA_PROTECTION in org.detected_intentions

    def test_requires_professional_advice_when_critical(self):
        """Debe requerir asesoría profesional cuando hay gaps críticos"""
        project = create_test_project([
            ("org_1", "Colectivo Informal", create_informal_collective())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        assert result.requires_professional_advice is True
        assert result.professional_advice_reason is not None


class TestResolverMultiOrg:
    """Tests del resolver con múltiples organizaciones"""

    def test_shared_data_gap_detected(self):
        """Debe detectar riesgo de transferencia de datos entre orgs"""
        project = create_test_project([
            ("org_1", "ONG 1", create_ong_needs_apci()),  # Tiene base de datos
            ("org_2", "Fundación Tech", create_tech_foundation()),  # También tiene base de datos
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        # Debe detectar gap compartido de datos
        shared_data_gaps = [
            g for g in result.shared_gaps
            if g.intention == LegalIntention.DATA_PROTECTION
        ]

        assert len(shared_data_gaps) > 0, "Debe detectar riesgo de transferencia de datos"

    def test_aggregates_gaps_from_all_orgs(self):
        """Debe agregar gaps de todas las organizaciones"""
        project = create_test_project([
            ("org_1", "Colectivo", create_informal_collective()),  # Muchos gaps
            ("org_2", "ONG Formal", create_formalized_ong()),  # Pocos gaps
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        # Debe tener gaps del colectivo
        assert result.total_gaps > 0

        # El colectivo debe tener más gaps que la ONG
        org_colectivo = next(o for o in result.organizations if o.organization_id == "org_1")
        org_ong = next(o for o in result.organizations if o.organization_id == "org_2")

        assert org_colectivo.gap_count > org_ong.gap_count

    def test_project_intentions_union_of_all(self):
        """Las intenciones del proyecto deben ser unión de todas las orgs"""
        project = create_test_project([
            ("org_1", "ONG Internacional", create_ong_needs_apci()),
            ("org_2", "Asociación Cultural", create_association_with_locacion()),
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        # Debe incluir intenciones de ambas orgs
        assert LegalIntention.INTERNATIONAL_COOPERATION in result.project_intentions
        assert LegalIntention.HIRING in result.project_intentions
        assert LegalIntention.INTELLECTUAL_PROPERTY in result.project_intentions  # Por la marca


class TestResolverRAGQueries:
    """Tests para generación de queries RAG"""

    def test_generates_rag_queries_for_gaps(self):
        """Debe generar queries RAG para cada gap"""
        project = create_test_project([
            ("org_1", "ONG Sin APCI", create_ong_needs_apci())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)
        queries = resolver.get_rag_queries(result)

        # Debe generar queries
        assert len(queries) > 0

        # Queries deben tener estructura correcta
        for q in queries:
            assert "query" in q
            assert "intention" in q
            assert "priority" in q

    def test_rag_queries_ordered_by_priority(self):
        """Queries RAG deben estar ordenadas por prioridad"""
        project = create_test_project([
            ("org_1", "Colectivo", create_informal_collective())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)
        queries = resolver.get_rag_queries(result)

        # Verificar orden: 1 (critical) antes que 2 (high) antes que 3 (medium/low)
        priorities = [q["priority"] for q in queries]
        assert priorities == sorted(priorities)


class TestSeverityCoherence:
    """Tests para verificar coherencia de severidades"""

    def test_legal_status_is_critical(self):
        """Falta de personería jurídica debe ser crítica"""
        from app.modules.legal_rules.rules import RULE_LEGAL_STATUS
        assert RULE_LEGAL_STATUS.default_gap_severity == GapSeverity.CRITICAL

    def test_apci_is_critical(self):
        """Falta de APCI debe ser crítica"""
        from app.modules.legal_rules.rules import RULE_APCI_REGISTRATION
        assert RULE_APCI_REGISTRATION.default_gap_severity == GapSeverity.CRITICAL

    def test_ruc_is_high(self):
        """Falta de RUC debe ser alta"""
        from app.modules.legal_rules.rules import RULE_RUC
        assert RULE_RUC.default_gap_severity == GapSeverity.HIGH

    def test_ir_exoneration_is_medium(self):
        """Falta de exoneración IR es medium (oportunidad, no obligación)"""
        from app.modules.legal_rules.rules import RULE_IR_EXONERATION
        assert RULE_IR_EXONERATION.default_gap_severity == GapSeverity.MEDIUM

    def test_ip_is_low(self):
        """Protección de PI es recomendación, no obligación"""
        from app.modules.legal_rules.rules import RULE_INTELLECTUAL_PROPERTY
        assert RULE_INTELLECTUAL_PROPERTY.default_gap_severity == GapSeverity.LOW


class TestGapExplainability:
    """Tests para verificar que los gaps son explicables a un abogado"""

    def test_gaps_have_description(self):
        """Todos los gaps deben tener descripción"""
        project = create_test_project([
            ("org_1", "Colectivo", create_informal_collective())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        for org in result.organizations:
            for gap in org.gaps:
                assert gap.description, f"Gap {gap.id} sin descripción"
                assert len(gap.description) > 10, f"Gap {gap.id} descripción muy corta"

    def test_gaps_have_impact(self):
        """Todos los gaps deben explicar el impacto"""
        project = create_test_project([
            ("org_1", "Colectivo", create_informal_collective())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        for org in result.organizations:
            for gap in org.gaps:
                assert gap.impact, f"Gap {gap.id} sin impacto"
                assert len(gap.impact) > 20, f"Gap {gap.id} impacto muy corto"

    def test_gaps_have_recommendation(self):
        """Todos los gaps deben tener recomendación accionable"""
        project = create_test_project([
            ("org_1", "Colectivo", create_informal_collective())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        for org in result.organizations:
            for gap in org.gaps:
                assert gap.recommendation, f"Gap {gap.id} sin recomendación"
                assert len(gap.recommendation) > 20, f"Gap {gap.id} recomendación muy corta"

    def test_gaps_have_rag_query_hint(self):
        """Todos los gaps deben tener hint para buscar en RAG"""
        project = create_test_project([
            ("org_1", "Colectivo", create_informal_collective())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        for org in result.organizations:
            for gap in org.gaps:
                assert gap.rag_query_hint, f"Gap {gap.id} sin rag_query_hint"

    def test_gaps_reference_source_fields(self):
        """Gaps deben indicar qué campos de la ficha los revelaron"""
        project = create_test_project([
            ("org_1", "Colectivo", create_informal_collective())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        for org in result.organizations:
            for gap in org.gaps:
                assert gap.source_fields, f"Gap {gap.id} sin source_fields"


# =============================================================================
# TESTS - Casos edge
# =============================================================================

class TestEdgeCases:
    """Tests para casos límite"""

    def test_empty_profile_no_crash(self):
        """Perfil vacío no debe causar crash"""
        project = create_test_project([
            ("org_1", "Vacío", create_empty_profile())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        # No debe crashear
        assert result is not None
        assert len(result.organizations) == 1

    def test_single_org_no_shared_gaps(self):
        """Un solo org no debe tener gaps compartidos"""
        project = create_test_project([
            ("org_1", "Solo", create_formalized_ong())
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        assert len(result.shared_gaps) == 0

    def test_three_orgs_max(self):
        """Debe manejar máximo 3 organizaciones"""
        project = create_test_project([
            ("org_1", "Org 1", create_formalized_ong()),
            ("org_2", "Org 2", create_tech_foundation()),
            ("org_3", "Org 3", create_association_with_locacion()),
        ])

        resolver = LegalRequirementsResolver()
        result = resolver.resolve(project)

        assert len(result.organizations) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
