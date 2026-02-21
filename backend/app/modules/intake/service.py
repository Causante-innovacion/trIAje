"""
Intake Module - Service
Recolección, validación y normalización de datos de la Ficha Legal Mínima
"""

from datetime import datetime

from .questions import get_question_set, get_question_by_id
from .schemas import (
    DerivationColor,
    IntakeRequest,
    IntakeValidationResponse,
    NormalizedIntake,
    QuestionSet,
    RiskAssessment,
    RiskLevel,
    RiskSignal,
    ToolType,
    ValidationError,
    ValidationWarning,
    ValidOptions,
)


class IntakeService:
    """
    Servicio de intake: recolecta, valida y normaliza datos estructurados.
    Implementa las funciones del intake_module según la documentación:
    - render_question_set()
    - enforce_selector_inputs()
    - validate_required_fields()
    - normalize_answers()
    """

    def render_question_set(self, tool: ToolType) -> QuestionSet:
        """
        Retorna el conjunto completo de preguntas para una herramienta.
        Incluye Ficha Legal Mínima + preguntas específicas de la herramienta.
        """
        return get_question_set(tool)

    def validate(self, request: IntakeRequest) -> IntakeValidationResponse:
        """
        Valida el intake completo y retorna errores, warnings y evaluación de riesgo.
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # 1. Validar campos requeridos
        errors.extend(self._validate_required_fields(request))

        # 2. Validar opciones de selector
        errors.extend(self._enforce_selector_inputs(request))

        # 3. Validar consistencia cross-field
        cross_errors, cross_warnings = self._validate_cross_field(request)
        errors.extend(cross_errors)
        warnings.extend(cross_warnings)

        # 4. Evaluar riesgos
        risk_assessment = self._assess_risk(request)

        # 5. Si es válido, normalizar datos
        normalized_data = None
        if not errors:
            normalized_data = self._normalize(request, risk_assessment)

        return IntakeValidationResponse(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            risk_assessment=risk_assessment,
            normalized_data=normalized_data,
        )

    def _validate_required_fields(self, request: IntakeRequest) -> list[ValidationError]:
        """Valida que todos los campos requeridos estén presentes (V2)"""
        errors = []
        lp = request.legal_profile

        # Bloque 1: Identidad
        if not lp.identity.identity_v2:
            errors.append(ValidationError(
                field="identity_v2",
                message="Debe seleccionar cómo está organizada su iniciativa",
                block="identity"
            ))
        if not lp.identity.org_purpose:
            errors.append(ValidationError(
                field="org_purpose",
                message="Debe seleccionar el fin principal de la organización",
                block="identity"
            ))

        # Bloque 2: SUNAT
        if not lp.sunat.sunat_v2:
            errors.append(ValidationError(
                field="sunat_v2",
                message="Debe indicar su relación actual con la SUNAT",
                block="sunat"
            ))

        # Bloque 3: Fondos
        if not lp.funds.funds_v2:
            errors.append(ValidationError(
                field="funds_v2",
                message="Debe indicar si recibe fondos extranjeros o de cooperación",
                block="funds"
            ))

        # Bloque 4: RRHH
        if not lp.human_resources.hiring_v2:
            errors.append(ValidationError(
                field="hiring_v2",
                message="Debe seleccionar al menos una modalidad de vinculación",
                block="human_resources"
            ))

        # Bloque 5: Intangibles
        if not lp.intangibles.intangibles_v2:
            errors.append(ValidationError(
                field="intangibles_v2",
                message="Debe seleccionar los activos que gestiona (o 'Ninguno')",
                block="intangibles"
            ))

        # Bloque 6: Urgencia
        if not lp.urgency.urgency_v2:
            errors.append(ValidationError(
                field="urgency_v2",
                message="Debe indicar el nivel de urgencia de su consulta",
                block="urgency"
            ))

        return errors

    def _enforce_selector_inputs(self, request: IntakeRequest) -> list[ValidationError]:
        """Verifica que los valores correspondan a opciones válidas V2"""
        errors = []
        lp = request.legal_profile

        if lp.identity.identity_v2 and lp.identity.identity_v2 not in ValidOptions.IDENTITY_V2:
            errors.append(ValidationError(field="identity_v2", message="Opción de identidad no válida", block="identity"))
        
        if lp.identity.org_purpose and lp.identity.org_purpose not in ValidOptions.ORG_PURPOSES:
            errors.append(ValidationError(field="org_purpose", message="Opción de fin no válida", block="identity"))

        if lp.sunat.sunat_v2 and lp.sunat.sunat_v2 not in ValidOptions.SUNAT_V2:
            errors.append(ValidationError(field="sunat_v2", message="Opción SUNAT no válida", block="sunat"))

        if lp.funds.funds_v2 and lp.funds.funds_v2 not in ValidOptions.FUNDS_V2:
            errors.append(ValidationError(field="funds_v2", message="Opción de fondos no válida", block="funds"))

        for h in lp.human_resources.hiring_v2:
            if h not in ValidOptions.HIRING_V2:
                errors.append(ValidationError(field="hiring_v2", message=f"'{h}' no es una modalidad válida", block="human_resources"))

        for i in lp.intangibles.intangibles_v2:
            if i not in ValidOptions.INTANGIBLES_V2:
                errors.append(ValidationError(field="intangibles_v2", message=f"'{i}' no es un activo válido", block="intangibles"))

        if lp.urgency.urgency_v2 and lp.urgency.urgency_v2 not in ValidOptions.URGENCY_V2:
            errors.append(ValidationError(field="urgency_v2", message="Opción de urgencia no válida", block="urgency"))

        return errors

    def _validate_cross_field(
        self, request: IntakeRequest
    ) -> tuple[list[ValidationError], list[ValidationWarning]]:
        """Valida consistencia entre campos según Gatillos Críticos V2"""
        errors = []
        warnings = []
        lp = request.legal_profile

        # Alerta Asociación + Fines de Lucro
        if lp.identity.identity_v2 and "Asociación" in lp.identity.identity_v2:
            # En V2 la opción ya dice "Sin fines de lucro", pero si hubiera un checkbox separado...
            # Aquí la validación es intrínseca a la opción elegida.
            pass

        # Alerta No RUC + Planilla
        no_ruc = lp.sunat.sunat_v2 == "No tengo RUC: Somos un colectivo o aún no iniciamos trámites ante impuestos."
        has_planilla = "Personal en Planilla (Contrato de trabajo)." in lp.human_resources.hiring_v2
        if no_ruc and has_planilla:
            errors.append(ValidationError(
                field="hiring_v2",
                message="Inconsistencia Laboral: No se puede contratar en planilla sin un RUC activo.",
                block="human_resources"
            ))

        # Alerta Bases de Datos + Colectivo
        is_colectivo = lp.identity.identity_v2 == "Colectivo o Grupo: Iniciativa no formalizada (sin personería jurídica ante SUNARP)."
        has_db = "Bases de datos de usuarios o beneficiarios." in lp.intangibles.intangibles_v2
        if is_colectivo and has_db:
            warnings.append(ValidationWarning(
                field="intangibles_v2",
                message="Riesgo de Datos: Un grupo sin personería jurídica no puede cumplir plenamente la Ley de Protección de Datos Personales.",
                severity="medium"
            ))

        # Alerta Empresa + Voluntariado
        is_empresa = lp.identity.identity_v2 == "Empresa (SAC, SA, SRL, EIRL): Con fines de lucro; el objetivo es generar utilidades para los socios."
        has_voluntariado = "Voluntariado (Bajo la Ley de Voluntariado)." in lp.human_resources.hiring_v2
        if is_empresa and has_voluntariado:
            warnings.append(ValidationWarning(
                field="hiring_v2",
                message="Alerta de Desnaturalización: El voluntariado legal solo aplica a entidades sin fines de lucro. Riesgo de multas en empresas.",
                severity="medium"
            ))

        return errors, warnings

    def _assess_risk(self, request: IntakeRequest) -> RiskAssessment:
        """Evalúa riesgos y gatillos globales V2"""
        signals: list[RiskSignal] = []
        reasons: list[str] = []
        lp = request.legal_profile

        # Gatillo Global: Urgencia
        is_urgent = lp.urgency.urgency_v2 and "Urgente" in lp.urgency.urgency_v2
        if is_urgent:
            signals.append(RiskSignal(signal_type="global_trigger", description="Urgencia inmediata detectada", source_field="urgency_v2"))
            reasons.append("Se requiere derivación prioritaria a un especialista humano debido a plazos o notificaciones.")

        # Riesgo Laboral (Inconsistencia)
        no_ruc = lp.sunat.sunat_v2 == "No tengo RUC: Somos un colectivo o aún no iniciamos trámites ante impuestos."
        if no_ruc and "Personal en Planilla (Contrato de trabajo)." in lp.human_resources.hiring_v2:
            signals.append(RiskSignal(signal_type="labor_risk", description="Intento de planilla sin RUC", source_field="hiring_v2"))
            reasons.append("Riesgo crítico de incumplimiento laboral y tributario.")

        # Riesgo de Cooperación (Fondos sin registro)
        if lp.funds.funds_v2 == "Sí, pero no tenemos registro ante APCI o está vencido.":
            signals.append(RiskSignal(signal_type="apci_risk", description="Fondos extranjeros sin APCI vigente", source_field="funds_v2"))
            reasons.append("Es indispensable regularizar la situación ante APCI para gestionar fondos internacionales.")

        # Determinar nivel final
        derivation_required = is_urgent
        derivation_color = DerivationColor.RED if is_urgent else DerivationColor.GREEN
        risk_level = RiskLevel.HIGH if is_urgent else RiskLevel.LOW

        if signals and not is_urgent:
            derivation_color = DerivationColor.YELLOW
            risk_level = RiskLevel.MEDIUM

        return RiskAssessment(
            derivation_required=derivation_required,
            derivation_color=derivation_color,
            risk_level=risk_level,
            signals=signals,
            reasons=reasons,
        )

    def _normalize(
        self, request: IntakeRequest, risk_assessment: RiskAssessment
    ) -> NormalizedIntake:
        """Normaliza los datos del intake V2"""
        detected_intentions = self._detect_intentions(request)

        return NormalizedIntake(
            tool=request.tool,
            legal_profile=request.legal_profile,
            tool_specific=request.tool_specific,
            risk_assessment=risk_assessment,
            detected_intentions=detected_intentions,
            session_id=request.session_id,
            organization_id=request.organization_id,
            intake_timestamp=datetime.utcnow(),
            intake_version="2.0",
            jurisdiction="PE",
        )

    def _detect_intentions(self, request: IntakeRequest) -> list[str]:
        """Detecta intenciones legales V2"""
        intentions = []
        lp = request.legal_profile

        if lp.identity.identity_v2 == "Colectivo o Grupo: Iniciativa no formalizada (sin personería jurídica ante SUNARP).":
            intentions.append("formalization")
        
        if lp.sunat.sunat_v2 and "No tengo RUC" in lp.sunat.sunat_v2:
            intentions.append("taxation")

        if lp.human_resources.hiring_v2 and "Solo gestión de fundadores" not in lp.human_resources.hiring_v2:
            intentions.append("hiring")

        if lp.funds.funds_v2 and "Sí" in lp.funds.funds_v2:
            intentions.append("international_cooperation")

        if lp.intangibles.intangibles_v2 and "Ninguno" not in lp.intangibles.intangibles_v2:
            intentions.append("intellectual_property")

        return list(set(intentions))

    def validate_project(
        self, request: "ProjectIntakeRequest"
    ) -> "ProjectValidationResponse":
        """Valida un proyecto multi-org V2"""
        from .schemas import (
            IntakeRequest,
            ProjectValidationResponse,
            ProjectValidationError,
            ProjectRiskAssessment,
            OrganizationRiskAssessment,
            NormalizedProjectIntake,
            RiskSignal,
        )

        errors: list[ProjectValidationError] = []
        warnings: list[ValidationWarning] = []
        org_risks: list[OrganizationRiskAssessment] = []
        all_intentions: list[str] = []

        for org in request.organizations:
            temp_request = IntakeRequest(
                tool=request.tool,
                legal_profile=org.legal_profile,
                tool_specific=request.tool_specific,
                session_id=request.session_id,
                organization_id=org.id,
            )

            req_errors = self._validate_required_fields(temp_request)
            for err in req_errors:
                errors.append(ProjectValidationError(organization_id=org.id, organization_name=org.name, field=err.field, message=err.message, block=err.block))

            sel_errors = self._enforce_selector_inputs(temp_request)
            for err in sel_errors:
                errors.append(ProjectValidationError(organization_id=org.id, organization_name=org.name, field=err.field, message=err.message, block=err.block))

            cross_errors, cross_warnings = self._validate_cross_field(temp_request)
            for err in cross_errors:
                errors.append(ProjectValidationError(organization_id=org.id, organization_name=org.name, field=err.field, message=err.message, block=err.block))
            warnings.extend(cross_warnings)

            risk = self._assess_risk(temp_request)
            org_risks.append(OrganizationRiskAssessment(organization_id=org.id, organization_name=org.name, risk_level=risk.risk_level, signals=risk.signals))
            all_intentions.extend(self._detect_intentions(temp_request))

        shared_signals, shared_reasons = self._detect_shared_risks(request.organizations)
        project_risk = self._calculate_project_risk(org_risks, shared_signals)
        project_risk.organization_risks = org_risks
        project_risk.shared_signals = shared_signals
        project_risk.shared_reasons = shared_reasons
        project_risk.detected_intentions = list(set(all_intentions))

        normalized_data = None
        if not errors:
            normalized_data = NormalizedProjectIntake(
                tool=request.tool,
                project=request.project,
                organizations=request.organizations,
                tool_specific=request.tool_specific,
                risk_assessment=project_risk,
                session_id=request.session_id,
                intake_timestamp=datetime.utcnow(),
                intake_version="2.0",
                jurisdiction="PE",
                total_organizations=len(request.organizations),
            )

        return ProjectValidationResponse(valid=len(errors) == 0, errors=errors, warnings=warnings, risk_assessment=project_risk, normalized_data=normalized_data)

    def _detect_shared_risks(self, organizations: list["OrganizationProfile"]) -> tuple[list[RiskSignal], list[str]]:
        """Detecta riesgos compartidos V2"""
        signals: list[RiskSignal] = []
        reasons: list[str] = []

        if len(organizations) < 2:
            return signals, reasons

        # Orgs informales vinculadas a formales
        has_formal = any("Organización formal" in org.legal_profile.identity.identity_v2 or "Empresa" in org.legal_profile.identity.identity_v2 for org in organizations)
        has_informal = any("Colectivo" in org.legal_profile.identity.identity_v2 for org in organizations)
        
        if has_formal and has_informal:
            signals.append(RiskSignal(signal_type="informal_partner_risk", description="Mezcla de entidades formales e informales en el proyecto", source_field="identity_v2"))
            reasons.append("Riesgo de responsabilidad: Las entidades formales podrían asumir pasivos de las informales.")

        return signals, reasons

    def _calculate_project_risk(self, org_risks: list["OrganizationRiskAssessment"], shared_signals: list[RiskSignal]) -> "ProjectRiskAssessment":
        """Calcula riesgo agregado V2"""
        from .schemas import ProjectRiskAssessment
        max_risk = RiskLevel.LOW
        derivation_required = False
        derivation_color = DerivationColor.GREEN

        for r in org_risks:
            if r.risk_level == RiskLevel.HIGH:
                max_risk = RiskLevel.HIGH
                derivation_color = DerivationColor.RED
                derivation_required = True
            elif r.risk_level == RiskLevel.MEDIUM and max_risk == RiskLevel.LOW:
                max_risk = RiskLevel.MEDIUM
                derivation_color = DerivationColor.YELLOW

        return ProjectRiskAssessment(overall_risk_level=max_risk, derivation_color=derivation_color, derivation_required=derivation_required)

intake_service = IntakeService()


# Instancia singleton para uso en la aplicación
intake_service = IntakeService()
