"""
Legal Adviser Feature - Pipeline
Genera paquete de asesor legal desde NormalizedProjectIntake.

Flujo:
    NormalizedProjectIntake
            ↓
    LegalRequirementsResolver (mismas reglas que Evaluación)
            ↓
    LegalRequirementsResult (gaps detectados)
            ↓
    LegalAdviserResponse (tópicos críticos, preguntas, documentos, decisiones)
"""

from app.modules.intake.schemas import NormalizedProjectIntake, OrganizationProfile
from app.modules.legal_rules import (
    LegalRequirementsResolver,
    LegalRequirementsResult,
    LegalIntention,
    GapSeverity,
)

from .schemas import (
    LegalAdviserResponse,
    OrganizationProfileResponse,
    LegalStatusCardResponse,
    FundingRangeResponse,
    CriticalTopicResponse,
    LawyerQuestionResponse,
    RequiredDocumentResponse,
    InternalDecisionResponse,
    InternalDecisionOptionResponse,
)


class LegalAdviserPipeline:
    """
    Pipeline para generar paquete de preparación para reunión con asesor legal.
    """

    # Título por intención para los tópicos críticos
    INTENTION_TOPIC_META: dict[LegalIntention, dict] = {
        LegalIntention.FORMALIZATION: {
            "title": "Formalización Legal",
            "action_label": "Ver ruta de formalización",
        },
        LegalIntention.TAXATION: {
            "title": "Cumplimiento Tributario (SUNAT)",
            "action_label": "Ver obligaciones tributarias",
        },
        LegalIntention.INTERNATIONAL_COOPERATION: {
            "title": "Registro APCI",
            "action_label": "Ver proceso de registro APCI",
        },
        LegalIntention.HIRING: {
            "title": "Modalidades de Contratación",
            "action_label": "Ver opciones laborales",
        },
        LegalIntention.INTELLECTUAL_PROPERTY: {
            "title": "Propiedad Intelectual",
            "action_label": "Ver protección de activos",
        },
        LegalIntention.DATA_PROTECTION: {
            "title": "Protección de Datos Personales",
            "action_label": "Ver cumplimiento LPDP",
        },
        LegalIntention.GOVERNANCE: {
            "title": "Gobernanza Organizacional",
            "action_label": "Ver órganos de gobierno",
        },
        LegalIntention.ACCOUNTING: {
            "title": "Registros Contables",
            "action_label": "Ver obligaciones contables",
        },
        LegalIntention.DONATIONS: {
            "title": "Registro como Receptora de Donaciones",
            "action_label": "Ver proceso de registro SUNAT",
        },
    }

    # Preguntas estándar por intención
    INTENTION_QUESTIONS: dict[LegalIntention, list[str]] = {
        LegalIntention.FORMALIZATION: [
            "¿Cuál es la figura jurídica más adecuada para nuestra organización?",
            "¿Qué documentos necesitamos para constituirnos formalmente en SUNARP?",
        ],
        LegalIntention.TAXATION: [
            "¿Qué obligaciones tributarias tenemos ante SUNAT?",
            "¿Calificamos para exoneración del Impuesto a la Renta?",
        ],
        LegalIntention.INTERNATIONAL_COOPERATION: [
            "¿Necesitamos registro en APCI para recibir fondos del extranjero?",
            "¿Cuáles son las obligaciones de reporte periódico ante APCI?",
        ],
        LegalIntention.HIRING: [
            "¿Cuál es la modalidad contractual más adecuada para nuestro equipo?",
            "¿Qué beneficios sociales corresponden según cada modalidad?",
        ],
        LegalIntention.GOVERNANCE: [
            "¿Qué órganos de gobierno debemos tener formalmente constituidos?",
            "¿Cómo documentar correctamente las decisiones del directorio?",
        ],
        LegalIntention.INTELLECTUAL_PROPERTY: [
            "¿Cómo proteger nuestra marca, logo y contenidos digitales?",
            "¿Qué contratos necesitamos para proteger el software desarrollado internamente?",
        ],
        LegalIntention.DATA_PROTECTION: [
            "¿Cómo cumplir con la Ley de Protección de Datos Personales (LPDP)?",
            "¿Debemos inscribir nuestras bases de datos en el RNPDP?",
        ],
        LegalIntention.ACCOUNTING: [
            "¿Qué libros contables estamos obligados a llevar?",
            "¿Qué régimen contable aplica a nuestra organización?",
        ],
        LegalIntention.DONATIONS: [
            "¿Cómo registrarnos como entidad receptora de donaciones en SUNAT?",
            "¿Qué comprobantes debemos emitir por las donaciones recibidas?",
        ],
    }

    # Documentos base por tipo de organización
    DOCUMENTS_BY_ORG_TYPE: dict[str, list[tuple[str, str]]] = {
        "Asociación": [
            ("estatuto", "Estatuto vigente (con todas las modificaciones)"),
            ("acta_constitucion", "Acta de constitución"),
            ("partida_registral", "Partida registral actualizada (SUNARP)"),
            ("ruc", "Ficha RUC actualizada (SUNAT)"),
            ("libro_actas", "Libro de actas de asamblea y directorio"),
        ],
        "Fundación": [
            ("escritura", "Escritura pública de constitución"),
            ("estatuto", "Estatuto vigente"),
            ("partida_registral", "Partida registral actualizada (SUNARP)"),
            ("ruc", "Ficha RUC actualizada (SUNAT)"),
        ],
        "Empresa": [
            ("minuta", "Minuta de constitución"),
            ("escritura", "Escritura pública"),
            ("partida_registral", "Partida registral actualizada (SUNARP)"),
            ("ruc", "Ficha RUC actualizada (SUNAT)"),
        ],
        "Colectivo / iniciativa no formalizada": [
            ("acta_informal", "Acta o acuerdo de fundación del colectivo (si existe)"),
            ("lista_miembros", "Lista actualizada de miembros"),
        ],
    }

    STANDARD_DOCUMENTS: list[tuple[str, str]] = [
        ("dni_representante", "DNI del representante legal o apoderado"),
        ("presupuesto", "Estado de cuentas o presupuesto actual"),
    ]

    def __init__(self):
        self.resolver = LegalRequirementsResolver()

    def generate(self, intake: NormalizedProjectIntake) -> LegalAdviserResponse:
        """Genera el paquete completo de asesor legal."""
        requirements_result = self.resolver.resolve(intake)
        primary_org = intake.organizations[0]

        entity_name = primary_org.name or primary_org.legal_profile.identity.org_type or "Organización"

        return LegalAdviserResponse(
            page_title="Paquete de Asesor Legal",
            page_subtitle=f"Preparación para reunión con abogado — {entity_name}",
            organization_profile=self._build_org_profile(primary_org),
            legal_status_cards=self._build_legal_status_cards(primary_org),
            funding_critical=self._build_funding_range(primary_org, requirements_result),
            funding_description=self._build_funding_description(primary_org),
            income_sources=self._get_income_sources(primary_org),
            critical_topics=self._build_critical_topics(requirements_result),
            lawyer_questions=self._build_lawyer_questions(requirements_result),
            required_documents=self._build_required_documents(primary_org, requirements_result),
            internal_decisions=self._build_internal_decisions(primary_org),
        )

    # -------------------------------------------------------------------------
    # Private builders
    # -------------------------------------------------------------------------

    def _build_org_profile(self, org: OrganizationProfile) -> OrganizationProfileResponse:
        formalization = org.legal_profile.formalization
        income = org.legal_profile.income

        if formalization.has_legal_status == "Sí":
            legal_status = "green"
        elif formalization.has_legal_status == "En trámite":
            legal_status = "yellow"
        else:
            legal_status = "red"

        # Stage: piloto if formally registered + RUC, prototipo otherwise
        if formalization.has_legal_status == "Sí" and formalization.ruc_status == "Lo tengo":
            stage = "piloto"
        else:
            stage = "prototipo"

        funding_types: list[str] = []
        if income.receives_foreign_funds:
            funding_types.append("extranjero")
        if income.income_sources and any(
            s in income.income_sources
            for s in ["Donaciones", "Fondos privados", "Fondos públicos", "Venta de servicios o productos"]
        ):
            funding_types.append("nacional")
        if not funding_types:
            funding_types = ["nacional"]

        return OrganizationProfileResponse(
            entity_name=org.name or org.legal_profile.identity.org_type or "Organización",
            legal_status=legal_status,
            stage=stage,
            funding_types=funding_types,
        )

    def _build_legal_status_cards(self, org: OrganizationProfile) -> list[LegalStatusCardResponse]:
        formalization = org.legal_profile.formalization
        income = org.legal_profile.income
        intl = org.legal_profile.international_cooperation

        cards: list[LegalStatusCardResponse] = []

        # Personería jurídica (SUNARP)
        if formalization.has_legal_status == "Sí":
            sunarp_status = "green"
        elif formalization.has_legal_status == "En trámite":
            sunarp_status = "yellow"
        else:
            sunarp_status = "red"
        cards.append(LegalStatusCardResponse(id="sunarp", label="Personería Jurídica", status=sunarp_status))

        # RUC / SUNAT
        if formalization.ruc_status == "Lo tengo":
            ruc_status = "green"
        elif formalization.ruc_status == "En trámite":
            ruc_status = "yellow"
        else:
            ruc_status = "red"
        cards.append(LegalStatusCardResponse(id="ruc", label="RUC / SUNAT", status=ruc_status))

        # APCI — only if org receives foreign funds
        if income.receives_foreign_funds:
            if intl.apci_status == "Registrado":
                apci_status = "green"
            elif intl.apci_status == "No aplica":
                apci_status = "yellow"
            else:
                apci_status = "red"
            cards.append(LegalStatusCardResponse(id="apci", label="APCI", status=apci_status))

        return cards

    def _build_funding_range(
        self,
        org: OrganizationProfile,
        result: LegalRequirementsResult,
    ) -> FundingRangeResponse:
        income = org.legal_profile.income
        critical = result.critical_gaps
        total = result.total_gaps

        if income.receives_foreign_funds and critical > 0:
            return FundingRangeResponse(
                min="$5K",
                max="$30K",
                description="Estimado de inversión para regularizar situación legal y cumplimiento ante APCI/SUNAT.",
            )
        if critical > 0:
            return FundingRangeResponse(
                min="$2K",
                max="$15K",
                description="Estimado para atender las brechas críticas identificadas en el proceso de formalización.",
            )
        if total > 0:
            return FundingRangeResponse(
                min="$1K",
                max="$8K",
                description="Inversión estimada para completar los requisitos legales pendientes de menor complejidad.",
            )
        return FundingRangeResponse(
            min="$500",
            max="$3K",
            description="Costos de mantenimiento y cumplimiento regular de las obligaciones legales vigentes.",
        )

    def _build_funding_description(self, org: OrganizationProfile) -> str:
        income = org.legal_profile.income
        parts: list[str] = []

        if income.receives_foreign_funds:
            parts.append("USD Internacional")
        if income.income_sources:
            if "Donaciones" in income.income_sources:
                parts.append("Grants & Donaciones")
            if "Fondos privados" in income.income_sources:
                parts.append("Fondos Privados")
            if "Venta de servicios o productos" in income.income_sources:
                parts.append("Ingresos Propios")
            if "Fondos públicos" in income.income_sources:
                parts.append("Fondos Públicos")

        return " | ".join(parts) if parts else "Fuentes por definir"

    def _get_income_sources(self, org: OrganizationProfile) -> list[str]:
        sources = org.legal_profile.income.income_sources or []
        return [s for s in sources if s != "Aún no recibe ingresos"]

    def _build_critical_topics(self, result: LegalRequirementsResult) -> list[CriticalTopicResponse]:
        topics: list[CriticalTopicResponse] = []
        seen_intentions: set[LegalIntention] = set()

        all_gaps = [
            gap
            for org_req in result.organizations
            for gap in org_req.gaps
        ] + list(result.shared_gaps)

        for gap in all_gaps:
            if gap.severity not in (GapSeverity.CRITICAL, GapSeverity.HIGH):
                continue
            if gap.intention in seen_intentions:
                continue
            seen_intentions.add(gap.intention)

            meta = self.INTENTION_TOPIC_META.get(gap.intention, {})
            title = meta.get("title", gap.intention.value.replace("_", " ").title())
            action_label = meta.get("action_label")

            topics.append(CriticalTopicResponse(
                id=gap.id,
                title=title,
                description=gap.recommendation,
                priority="URGENTE",
                action_label=action_label,
            ))

        return topics[:6]

    def _build_lawyer_questions(self, result: LegalRequirementsResult) -> list[LawyerQuestionResponse]:
        questions: list[LawyerQuestionResponse] = []
        seen: set[str] = set()
        counter = 1

        for intention in result.project_intentions:
            for q_text in self.INTENTION_QUESTIONS.get(intention, []):
                if q_text not in seen and counter <= 10:
                    seen.add(q_text)
                    questions.append(LawyerQuestionResponse(id=f"q{counter}", number=counter, question=q_text))
                    counter += 1

        standard = [
            "¿Hay riesgos legales que no hemos identificado?",
            "¿Cuál es el cronograma realista para regularizar nuestra situación?",
            "¿Cuánto costaría regularizar completamente nuestra situación legal?",
        ]
        for q_text in standard:
            if q_text not in seen and counter <= 10:
                seen.add(q_text)
                questions.append(LawyerQuestionResponse(id=f"q{counter}", number=counter, question=q_text))
                counter += 1

        return questions

    def _build_required_documents(
        self,
        org: OrganizationProfile,
        result: LegalRequirementsResult,
    ) -> list[RequiredDocumentResponse]:
        docs: list[RequiredDocumentResponse] = []
        seen_ids: set[str] = set()
        profile = org.legal_profile
        org_type = profile.identity.org_type or ""
        available_docs = profile.accounting.available_documents

        type_docs = self.DOCUMENTS_BY_ORG_TYPE.get(
            org_type,
            self.DOCUMENTS_BY_ORG_TYPE["Asociación"],
        )

        for doc_id, doc_title in type_docs:
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)

            completed = False
            if doc_id == "partida_registral" and profile.formalization.has_legal_status == "Sí":
                completed = True
            elif doc_id == "ruc" and profile.formalization.ruc_status == "Lo tengo":
                completed = True
            elif doc_id in ("estatuto", "acta_constitucion", "escritura") and \
                    "Estatuto o acta de constitución" in available_docs:
                completed = True
            elif doc_id == "libro_actas" and "Libros de actas" in available_docs:
                completed = True

            docs.append(RequiredDocumentResponse(id=doc_id, title=doc_title, completed=completed))

        for doc_id, doc_title in self.STANDARD_DOCUMENTS:
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                docs.append(RequiredDocumentResponse(id=doc_id, title=doc_title, completed=False))

        if profile.income.receives_foreign_funds and \
                profile.international_cooperation.apci_status != "Registrado":
            docs.append(RequiredDocumentResponse(
                id="apci_cert",
                title="Certificado de inscripción en APCI (o constancia de trámite)",
                completed=False,
            ))

        return docs[:10]

    def _build_internal_decisions(self, org: OrganizationProfile) -> list[InternalDecisionResponse]:
        decisions: list[InternalDecisionResponse] = []
        profile = org.legal_profile
        formalization = profile.formalization
        income = profile.income
        hr = profile.human_resources
        identity = profile.identity

        # A: Legal figure (if not formalized)
        if formalization.has_legal_status != "Sí":
            options_a = [
                InternalDecisionOptionResponse(id="a1", label="Opción A: Asociación Civil (sin fines de lucro)"),
                InternalDecisionOptionResponse(id="a2", label="Opción B: Fundación (patrimonio afectado a fin altruista)"),
            ]
            if identity.seeks_profits:
                options_a.append(InternalDecisionOptionResponse(id="a3", label="Opción C: Empresa (SAC o SRL)"))
            else:
                options_a.append(InternalDecisionOptionResponse(id="a3", label="Opción C: Continuar como colectivo informal"))
            decisions.append(InternalDecisionResponse(
                id="decision_a",
                scenario="Escenario A: ¿Qué figura jurídica adoptar?",
                options=options_a,
            ))

        # B: Hiring modality
        has_hiring_needs = bool(hr.hiring_modalities) and "Ninguno" not in hr.hiring_modalities
        if has_hiring_needs or not hr.hiring_modalities:
            decisions.append(InternalDecisionResponse(
                id="decision_b",
                scenario="Escenario B: ¿Cómo contratar al equipo?",
                options=[
                    InternalDecisionOptionResponse(id="b1", label="Opción A: Planilla con todos los beneficios (DL 728)"),
                    InternalDecisionOptionResponse(id="b2", label="Opción B: Locación de servicios (honorarios)"),
                    InternalDecisionOptionResponse(id="b3", label="Opción C: Esquema mixto (planilla + honorarios)"),
                ],
            ))

        # C: Foreign funding management
        if income.receives_foreign_funds:
            decisions.append(InternalDecisionResponse(
                id="decision_c",
                scenario="Escenario C: ¿Cómo gestionar los fondos internacionales?",
                options=[
                    InternalDecisionOptionResponse(id="c1", label="Opción A: Registrarse en APCI como ENIEX"),
                    InternalDecisionOptionResponse(id="c2", label="Opción B: Recibir vía convenio con entidad ya registrada"),
                    InternalDecisionOptionResponse(id="c3", label="Opción C: Consultar exención aplicable al caso"),
                ],
            ))

        # D: Tax regime (always shown)
        decisions.append(InternalDecisionResponse(
            id="decision_d",
            scenario="Escenario D: ¿Qué régimen tributario adoptar?",
            options=[
                InternalDecisionOptionResponse(id="d1", label="Opción A: Régimen General (cualquier tipo de org.)"),
                InternalDecisionOptionResponse(id="d2", label="Opción B: Exoneración IR (Asoc./Fund. sin fines de lucro)"),
                InternalDecisionOptionResponse(id="d3", label="Opción C: Régimen Especial de Renta (RER) — solo empresas"),
            ],
        ))

        return decisions[:4]


# Singleton
_pipeline: LegalAdviserPipeline | None = None


def get_legal_adviser_pipeline() -> LegalAdviserPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = LegalAdviserPipeline()
    return _pipeline
