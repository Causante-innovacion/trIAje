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
        """Valida que todos los campos requeridos estén presentes"""
        errors = []
        lp = request.legal_profile

        # Bloque 1: Identidad (todos requeridos)
        if not lp.identity.org_type:
            errors.append(ValidationError(
                field="org_type",
                message="Debe seleccionar el tipo de organización",
                block="identity"
            ))
        if not lp.identity.org_purpose:
            errors.append(ValidationError(
                field="org_purpose",
                message="Debe seleccionar el fin principal de la organización",
                block="identity"
            ))
        if lp.identity.seeks_profits is None:
            errors.append(ValidationError(
                field="seeks_profits",
                message="Debe indicar si la organización busca generar ganancias",
                block="identity"
            ))

        # Bloque 2: Formalización
        if not lp.formalization.has_legal_status:
            errors.append(ValidationError(
                field="has_legal_status",
                message="Debe indicar si tiene personería jurídica",
                block="formalization"
            ))
        if not lp.formalization.ruc_status:
            errors.append(ValidationError(
                field="ruc_status",
                message="Debe indicar la situación del RUC",
                block="formalization"
            ))

        # Bloque 3: Ingresos
        if lp.income.handles_money is None:
            errors.append(ValidationError(
                field="handles_money",
                message="Debe indicar si maneja dinero",
                block="income"
            ))

        # Bloque 4: Cooperación Internacional (condicional)
        if lp.income.receives_foreign_funds is None:
            errors.append(ValidationError(
                field="receives_foreign_funds",
                message="Debe indicar si recibe fondos extranjeros",
                block="income"
            ))

        # Bloque 5: RRHH (modalidades requerido)
        if not lp.human_resources.hiring_modalities:
            errors.append(ValidationError(
                field="hiring_modalities",
                message="Debe seleccionar al menos una modalidad de contratación (o 'Ninguno')",
                block="human_resources"
            ))

        # Bloque 6: Contable
        if not lp.accounting.has_accounting_records:
            errors.append(ValidationError(
                field="has_accounting_records",
                message="Debe indicar si existen registros contables",
                block="accounting"
            ))

        # Bloque 7: Gobernanza
        if lp.governance.has_governance_bodies is None:
            errors.append(ValidationError(
                field="has_governance_bodies",
                message="Debe indicar si tiene órganos de gobierno",
                block="governance"
            ))

        # Bloque 8: Intangibles
        if not lp.intangibles.intangible_assets:
            errors.append(ValidationError(
                field="intangible_assets",
                message="Debe seleccionar los intangibles que utiliza (o 'Ninguno')",
                block="intangibles"
            ))

        # Validar campos específicos de herramienta
        errors.extend(self._validate_tool_specific_required(request))

        return errors

    def _validate_tool_specific_required(self, request: IntakeRequest) -> list[ValidationError]:
        """Valida campos requeridos específicos de cada herramienta"""
        errors = []
        ts = request.tool_specific

        if request.tool == ToolType.EVALUATION:
            if not ts.evaluation or not ts.evaluation.evaluation_goals:
                errors.append(ValidationError(
                    field="evaluation_goals",
                    message="Debe seleccionar al menos un objetivo de evaluación",
                    block="evaluation_specific"
                ))

        elif request.tool == ToolType.COMPLIANCE:
            if not ts.compliance or not ts.compliance.compliance_goal:
                errors.append(ValidationError(
                    field="compliance_goal",
                    message="Debe seleccionar el objetivo de cumplimiento",
                    block="compliance_specific"
                ))

        elif request.tool == ToolType.QUERY:
            if not ts.query or not ts.query.query_area:
                errors.append(ValidationError(
                    field="query_area",
                    message="Debe seleccionar el área de consulta",
                    block="query_specific"
                ))
            if not ts.query or not ts.query.specific_question:
                errors.append(ValidationError(
                    field="specific_question",
                    message="Debe escribir su consulta específica",
                    block="query_specific"
                ))

        return errors

    def _enforce_selector_inputs(self, request: IntakeRequest) -> list[ValidationError]:
        """Verifica que los valores correspondan a opciones válidas"""
        errors = []
        lp = request.legal_profile

        # Identidad
        if lp.identity.org_type and lp.identity.org_type not in ValidOptions.ORG_TYPES:
            errors.append(ValidationError(
                field="org_type",
                message=f"'{lp.identity.org_type}' no es un tipo de organización válido",
                block="identity"
            ))
        if lp.identity.org_purpose and lp.identity.org_purpose not in ValidOptions.ORG_PURPOSES:
            errors.append(ValidationError(
                field="org_purpose",
                message=f"'{lp.identity.org_purpose}' no es un fin válido",
                block="identity"
            ))

        # Formalización
        if lp.formalization.has_legal_status and lp.formalization.has_legal_status not in ValidOptions.YES_NO_IN_PROGRESS:
            errors.append(ValidationError(
                field="has_legal_status",
                message="Valor no válido para personería jurídica",
                block="formalization"
            ))
        if lp.formalization.ruc_status and lp.formalization.ruc_status not in ValidOptions.RUC_STATUS:
            errors.append(ValidationError(
                field="ruc_status",
                message="Valor no válido para situación de RUC",
                block="formalization"
            ))
        for registry in lp.formalization.special_registries:
            if registry not in ValidOptions.SPECIAL_REGISTRIES:
                errors.append(ValidationError(
                    field="special_registries",
                    message=f"'{registry}' no es un registro especial válido",
                    block="formalization"
                ))

        # Ingresos
        for source in lp.income.income_sources:
            if source not in ValidOptions.INCOME_SOURCES:
                errors.append(ValidationError(
                    field="income_sources",
                    message=f"'{source}' no es una fuente de ingreso válida",
                    block="income"
                ))

        # Cooperación internacional
        if lp.international_cooperation.apci_status and lp.international_cooperation.apci_status not in ValidOptions.APCI_STATUS:
            errors.append(ValidationError(
                field="apci_status",
                message="Valor no válido para situación APCI",
                block="international_cooperation"
            ))

        # RRHH
        for modality in lp.human_resources.hiring_modalities:
            if modality not in ValidOptions.HIRING_MODALITIES:
                errors.append(ValidationError(
                    field="hiring_modalities",
                    message=f"'{modality}' no es una modalidad de contratación válida",
                    block="human_resources"
                ))
        if lp.human_resources.contracts_valid and lp.human_resources.contracts_valid not in ValidOptions.YES_NO_NA:
            errors.append(ValidationError(
                field="contracts_valid",
                message="Valor no válido para vigencia de contratos",
                block="human_resources"
            ))

        # Contable
        if lp.accounting.has_accounting_records and lp.accounting.has_accounting_records not in ValidOptions.ACCOUNTING_STATUS:
            errors.append(ValidationError(
                field="has_accounting_records",
                message="Valor no válido para registros contables",
                block="accounting"
            ))
        for doc in lp.accounting.available_documents:
            if doc not in ValidOptions.AVAILABLE_DOCUMENTS:
                errors.append(ValidationError(
                    field="available_documents",
                    message=f"'{doc}' no es un documento válido",
                    block="accounting"
                ))

        # Gobernanza
        if lp.governance.has_legal_representative and lp.governance.has_legal_representative not in ValidOptions.YES_NO_IN_PROGRESS:
            errors.append(ValidationError(
                field="has_legal_representative",
                message="Valor no válido para representante legal",
                block="governance"
            ))

        # Intangibles
        for asset in lp.intangibles.intangible_assets:
            if asset not in ValidOptions.INTANGIBLE_ASSETS:
                errors.append(ValidationError(
                    field="intangible_assets",
                    message=f"'{asset}' no es un activo intangible válido",
                    block="intangibles"
                ))

        return errors

    def _validate_cross_field(
        self, request: IntakeRequest
    ) -> tuple[list[ValidationError], list[ValidationWarning]]:
        """
        Valida consistencia entre campos relacionados.
        Detecta inconsistencias lógicas.
        """
        errors = []
        warnings = []
        lp = request.legal_profile

        # Si recibe fondos extranjeros pero no tiene registro APCI
        if (lp.income.receives_foreign_funds and
            lp.international_cooperation.apci_status != "Registrado" and
            "APCI" not in lp.formalization.special_registries):
            warnings.append(ValidationWarning(
                field="apci_status",
                message="Recibe fondos extranjeros pero no está registrado en APCI. Esto podría ser un requisito pendiente.",
                severity="medium"
            ))

        # Si maneja dinero pero no tiene RUC
        if lp.income.handles_money and lp.formalization.ruc_status == "No lo tengo":
            warnings.append(ValidationWarning(
                field="ruc_status",
                message="Maneja dinero pero no tiene RUC. Esto podría generar problemas tributarios.",
                severity="medium"
            ))

        # Si tiene personal en planilla pero no tiene personería jurídica
        if ("Planilla" in lp.human_resources.hiring_modalities and
            lp.formalization.has_legal_status == "No"):
            errors.append(ValidationError(
                field="hiring_modalities",
                message="No puede tener personal en planilla sin personería jurídica",
                block="human_resources"
            ))

        # Si busca ganancias pero dice ser ONG/Asociación
        if (lp.identity.seeks_profits and
            lp.identity.org_type in ["Asociación", "Fundación", "ONG"]):
            warnings.append(ValidationWarning(
                field="seeks_profits",
                message="Las asociaciones, fundaciones y ONGs no pueden distribuir ganancias entre sus miembros.",
                severity="medium"
            ))

        # Si tiene contratos vigentes pero no tiene ninguna modalidad de contratación
        if (lp.human_resources.contracts_valid == "Sí" and
            "Ninguno" in lp.human_resources.hiring_modalities):
            errors.append(ValidationError(
                field="contracts_valid",
                message="Indica contratos vigentes pero no tiene modalidades de contratación",
                block="human_resources"
            ))

        # Si usa bases de datos de usuarios pero no tiene personería jurídica
        if ("Bases de datos de usuarios" in lp.intangibles.intangible_assets and
            lp.formalization.has_legal_status == "No"):
            warnings.append(ValidationWarning(
                field="intangible_assets",
                message="Maneja datos personales sin personería jurídica. Considere la formalización para cumplir con la Ley de Protección de Datos Personales.",
                severity="medium"
            ))

        return errors, warnings

    def _assess_risk(self, request: IntakeRequest) -> RiskAssessment:
        """
        Evalúa el nivel de riesgo y determina si requiere derivación a abogado.
        Implementa los criterios de color según la documentación legal.
        """
        signals: list[RiskSignal] = []
        reasons: list[str] = []
        lp = request.legal_profile

        # === SEÑALES DE RIESGO ALTO (posible derivación) ===

        # Sin personería jurídica pero maneja dinero o personal
        if lp.formalization.has_legal_status == "No":
            if lp.income.handles_money:
                signals.append(RiskSignal(
                    signal_type="structure_risk",
                    description="Maneja dinero sin personería jurídica",
                    source_field="has_legal_status"
                ))
                reasons.append("Operar sin personería jurídica manejando dinero genera riesgos legales significativos")

            if "Planilla" in lp.human_resources.hiring_modalities:
                signals.append(RiskSignal(
                    signal_type="labor_risk",
                    description="Intenta contratar en planilla sin personería jurídica",
                    source_field="hiring_modalities"
                ))
                reasons.append("No es posible tener trabajadores en planilla sin personería jurídica")

        # Recibe cooperación internacional sin registro APCI
        if (lp.international_cooperation.receives_international_cooperation and
            lp.international_cooperation.apci_status == "Necesita registro"):
            signals.append(RiskSignal(
                signal_type="apci_risk",
                description="Recibe cooperación internacional sin estar registrado en APCI",
                source_field="apci_status"
            ))
            reasons.append("El registro en APCI es obligatorio para recibir cooperación técnica internacional")

        # Sin registros contables manejando dinero
        if lp.income.handles_money and lp.accounting.has_accounting_records == "No":
            signals.append(RiskSignal(
                signal_type="accounting_risk",
                description="Maneja dinero sin registros contables",
                source_field="has_accounting_records"
            ))
            reasons.append("La falta de registros contables puede generar problemas tributarios y de transparencia")

        # Locación de servicios con posible subordinación (riesgo laboral)
        if "Locación de servicios" in lp.human_resources.hiring_modalities:
            signals.append(RiskSignal(
                signal_type="labor_risk",
                description="Usa locación de servicios - verificar que no haya subordinación",
                source_field="hiring_modalities"
            ))
            reasons.append("La locación de servicios mal utilizada puede derivar en demandas laborales")

        # === DETERMINAR NIVEL DE RIESGO Y COLOR ===

        derivation_required = False
        derivation_color = DerivationColor.GREEN
        risk_level = RiskLevel.LOW

        high_risk_signals = [s for s in signals if s.signal_type in [
            "labor_risk", "apci_risk"
        ]]
        medium_risk_signals = [s for s in signals if s.signal_type in [
            "structure_risk", "accounting_risk"
        ]]

        if len(high_risk_signals) >= 2:
            derivation_required = True
            derivation_color = DerivationColor.RED
            risk_level = RiskLevel.HIGH
        elif len(high_risk_signals) >= 1:
            derivation_color = DerivationColor.YELLOW
            risk_level = RiskLevel.HIGH
        elif len(medium_risk_signals) >= 2:
            derivation_color = DerivationColor.YELLOW
            risk_level = RiskLevel.MEDIUM
        elif len(signals) > 0:
            risk_level = RiskLevel.MEDIUM

        # === VERIFICAR INTENCIONES QUE SIEMPRE SON AMARILLAS/ROJAS ===

        # Query en áreas sensibles
        if request.tool == ToolType.QUERY:
            ts = request.tool_specific
            if ts.query and ts.query.query_area in [
                "Contratación de personal",
                "Cooperación internacional",
                "Propiedad intelectual"
            ]:
                if derivation_color == DerivationColor.GREEN:
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
        """Normaliza los datos del intake para procesamiento posterior"""
        # Detectar intenciones según las respuestas
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
        """
        Detecta las intenciones legales según la documentación del equipo legal.
        Las intenciones son:
        1. Formalización y registros
        2. Evaluación de viabilidad
        3. Financiamiento y tributación
        4. Contratación de personal
        5. Cooperación internacional
        6. Propiedad intelectual
        7. Preparación de reuniones
        8. Riesgos y gestión
        9. Registro de donaciones
        10. Casos grises (derivación)
        """
        intentions = []
        lp = request.legal_profile

        # Formalización y registros
        if (lp.formalization.has_legal_status in ["No", "En trámite"] or
            lp.formalization.ruc_status in ["No lo tengo", "En trámite"]):
            intentions.append("formalization")

        # Financiamiento y tributación
        if lp.income.handles_money or lp.income.income_sources:
            intentions.append("taxation")

        # Contratación de personal
        if lp.human_resources.hiring_modalities and "Ninguno" not in lp.human_resources.hiring_modalities:
            intentions.append("hiring")

        # Cooperación internacional
        if (lp.income.receives_foreign_funds or
            lp.international_cooperation.receives_international_cooperation):
            intentions.append("international_cooperation")

        # Propiedad intelectual
        if lp.intangibles.intangible_assets and "Ninguno" not in lp.intangibles.intangible_assets:
            intentions.append("intellectual_property")

        # Donaciones
        if "Donaciones" in lp.income.income_sources:
            intentions.append("donations")

        # Gobernanza
        if (lp.governance.has_governance_bodies is False or
            lp.governance.has_legal_representative in ["No", "En trámite"]):
            intentions.append("governance")

        # Basado en herramienta
        if request.tool == ToolType.EVALUATION:
            intentions.append("viability_evaluation")
        elif request.tool == ToolType.COMPLIANCE:
            intentions.append("compliance_route")

        return list(set(intentions))  # Eliminar duplicados


# Instancia singleton para uso en la aplicación
intake_service = IntakeService()
