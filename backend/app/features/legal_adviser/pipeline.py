"""
Legal Adviser Feature - Pipeline (V2 Schema)
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

from app.modules.intake.schemas import NormalizedProjectIntake, OrganizationProfile, LegalProfile
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


# =============================================================================
# V2 HELPER FUNCTIONS (mirror the ones in rules.py)
# =============================================================================

def _is_formal_org(p: LegalProfile) -> bool:
    return (p.identity.identity_v2 or "").startswith("Organización formal")


def _is_empresa(p: LegalProfile) -> bool:
    return (p.identity.identity_v2 or "").startswith("Empresa")


def _is_colectivo(p: LegalProfile) -> bool:
    return (p.identity.identity_v2 or "").startswith("Colectivo")


def _has_legal_status(p: LegalProfile) -> bool:
    return _is_formal_org(p) or _is_empresa(p)


def _has_ruc(p: LegalProfile) -> bool:
    return "Tengo RUC y está al día" in (p.sunat.sunat_v2 or "")


def _ruc_has_problems(p: LegalProfile) -> bool:
    return "pausado o con problemas" in (p.sunat.sunat_v2 or "")


def _receives_foreign_funds(p: LegalProfile) -> bool:
    return (p.funds.funds_v2 or "").startswith("Sí")


def _has_apci(p: LegalProfile) -> bool:
    v = p.funds.funds_v2 or ""
    return "registrados ante APCI" in v and "Vigente" in v


def _seeks_profits(p: LegalProfile) -> bool:
    return _is_empresa(p)


def _org_type_label(p: LegalProfile) -> str:
    """Returns a short org type label for display."""
    if _is_formal_org(p):
        return "Asociación / Fundación"
    if _is_empresa(p):
        return "Empresa"
    return "Colectivo"


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
        "Asociación / Fundación": [
            ("estatuto", "Estatuto vigente (con todas las modificaciones)"),
            ("acta_constitucion", "Acta de constitución"),
            ("partida_registral", "Partida registral actualizada (SUNARP)"),
            ("ruc", "Ficha RUC actualizada (SUNAT)"),
            ("libro_actas", "Libro de actas de asamblea y directorio"),
        ],
        "Empresa": [
            ("minuta", "Minuta de constitución"),
            ("escritura", "Escritura pública"),
            ("partida_registral", "Partida registral actualizada (SUNARP)"),
            ("ruc", "Ficha RUC actualizada (SUNAT)"),
        ],
        "Colectivo": [
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
        """Genera el paquete completo de asesor legal (síncrono, sin evidencia RAG)."""
        requirements_result = self.resolver.resolve(intake)
        primary_org = intake.organizations[0]

        entity_name = primary_org.name or _org_type_label(primary_org.legal_profile)

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

    async def generate_async(self, intake: NormalizedProjectIntake) -> LegalAdviserResponse:
        """Genera el paquete completo con evidencia normativa (RAG)."""
        result = self.generate(intake)
        result.evidence_sources = await self._fetch_rag_evidence(intake, result)
        return result

    async def _fetch_rag_evidence(
        self,
        intake: NormalizedProjectIntake,
        result: LegalAdviserResponse,
    ) -> list[dict]:
        """Busca evidencia normativa en RAG para los tópicos críticos del paquete."""
        try:
            from app.modules.rag import get_rag_module
            rag = get_rag_module()
            if not rag:
                return []

            org_ids = [org.id for org in intake.organizations]
            queries = [
                f"{topic.title} {topic.description}"
                for topic in result.critical_topics[:3]
            ]
            if not queries:
                # Fallback: use lawyer questions as queries
                queries = [q.question for q in result.lawyer_questions[:2]]

            evidence: list[dict] = []
            seen_titles: set[str] = set()

            for query in queries:
                try:
                    rag_result = await rag.retrieve_for_project(
                        query=query,
                        organization_ids=org_ids,
                        top_k_initial=3,
                    )
                    for chunk in rag_result.chunks[:2]:
                        title = chunk.metadata.title
                        if title and title not in seen_titles:
                            seen_titles.add(title)
                            evidence.append({
                                "title": title,
                                "url": chunk.metadata.url,
                                "authority_level": chunk.metadata.authority_level,
                                "anchor": chunk.metadata.anchor,
                            })
                except Exception:
                    continue

            return evidence[:6]
        except Exception:
            return []

    # -------------------------------------------------------------------------
    # Private builders
    # -------------------------------------------------------------------------

    def _build_org_profile(self, org: OrganizationProfile) -> OrganizationProfileResponse:
        profile = org.legal_profile

        if _has_legal_status(profile):
            legal_status = "green"
        elif _is_colectivo(profile):
            legal_status = "red"
        else:
            legal_status = "yellow"

        # Stage: piloto if formally registered + RUC, prototipo otherwise
        if _has_legal_status(profile) and _has_ruc(profile):
            stage = "piloto"
        else:
            stage = "prototipo"

        funding_types: list[str] = []
        if _receives_foreign_funds(profile):
            funding_types.append("extranjero")
        # All formal orgs are assumed to have some national funding
        if _has_legal_status(profile):
            funding_types.append("nacional")
        if not funding_types:
            funding_types = ["nacional"]

        return OrganizationProfileResponse(
            entity_name=org.name or _org_type_label(profile),
            legal_status=legal_status,
            stage=stage,
            funding_types=funding_types,
        )

    def _build_legal_status_cards(self, org: OrganizationProfile) -> list[LegalStatusCardResponse]:
        profile = org.legal_profile

        cards: list[LegalStatusCardResponse] = []

        # Personería jurídica (SUNARP)
        if _has_legal_status(profile):
            sunarp_status = "green"
        elif _is_colectivo(profile):
            sunarp_status = "red"
        else:
            sunarp_status = "yellow"
        cards.append(LegalStatusCardResponse(id="sunarp", label="Personería Jurídica", status=sunarp_status))

        # RUC / SUNAT
        if _has_ruc(profile):
            ruc_status = "green"
        elif _ruc_has_problems(profile):
            ruc_status = "yellow"
        else:
            ruc_status = "red"
        cards.append(LegalStatusCardResponse(id="ruc", label="RUC / SUNAT", status=ruc_status))

        # APCI — only if org receives foreign funds
        if _receives_foreign_funds(profile):
            if _has_apci(profile):
                apci_status = "green"
            else:
                apci_status = "red"
            cards.append(LegalStatusCardResponse(id="apci", label="APCI", status=apci_status))

        return cards

    def _build_funding_range(
        self,
        org: OrganizationProfile,
        result: LegalRequirementsResult,
    ) -> FundingRangeResponse:
        profile = org.legal_profile
        critical = result.critical_gaps
        total = result.total_gaps

        if _receives_foreign_funds(profile) and critical > 0:
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
        profile = org.legal_profile
        parts: list[str] = []

        if _receives_foreign_funds(profile):
            parts.append("USD Internacional")
        if _has_legal_status(profile):
            parts.append("Fondos Nacionales")

        return " | ".join(parts) if parts else "Fuentes por definir"

    def _get_income_sources(self, org: OrganizationProfile) -> list[str]:
        profile = org.legal_profile
        sources: list[str] = []
        if _receives_foreign_funds(profile):
            sources.append("Cooperación internacional")
        if _has_legal_status(profile):
            sources.append("Ingresos formales")
        return sources if sources else ["Por definir"]

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
        org_type = _org_type_label(profile)

        type_docs = self.DOCUMENTS_BY_ORG_TYPE.get(
            org_type,
            self.DOCUMENTS_BY_ORG_TYPE["Asociación / Fundación"],
        )

        for doc_id, doc_title in type_docs:
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)

            completed = False
            if doc_id == "partida_registral" and _has_legal_status(profile):
                completed = True
            elif doc_id == "ruc" and _has_ruc(profile):
                completed = True

            docs.append(RequiredDocumentResponse(id=doc_id, title=doc_title, completed=completed))

        for doc_id, doc_title in self.STANDARD_DOCUMENTS:
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                docs.append(RequiredDocumentResponse(id=doc_id, title=doc_title, completed=False))

        if _receives_foreign_funds(profile) and not _has_apci(profile):
            docs.append(RequiredDocumentResponse(
                id="apci_cert",
                title="Certificado de inscripción en APCI (o constancia de trámite)",
                completed=False,
            ))

        return docs[:10]

    def _build_internal_decisions(self, org: OrganizationProfile) -> list[InternalDecisionResponse]:
        decisions: list[InternalDecisionResponse] = []
        profile = org.legal_profile

        # A: Legal figure (if not formalized)
        if not _has_legal_status(profile):
            options_a = [
                InternalDecisionOptionResponse(id="a1", label="Opción A: Asociación Civil (sin fines de lucro)"),
                InternalDecisionOptionResponse(id="a2", label="Opción B: Fundación (patrimonio afectado a fin altruista)"),
            ]
            if _seeks_profits(profile):
                options_a.append(InternalDecisionOptionResponse(id="a3", label="Opción C: Empresa (SAC o SRL)"))
            else:
                options_a.append(InternalDecisionOptionResponse(id="a3", label="Opción C: Continuar como colectivo informal"))
            decisions.append(InternalDecisionResponse(
                id="decision_a",
                scenario="Escenario A: ¿Qué figura jurídica adoptar?",
                options=options_a,
            ))

        # B: Hiring modality
        hiring = profile.human_resources.hiring_v2
        has_hiring_needs = bool(hiring) and not any("Solo gestión" in h for h in hiring)
        if has_hiring_needs or not hiring:
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
        if _receives_foreign_funds(profile):
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
