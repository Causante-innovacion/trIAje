"""
Tests para el clasificador de Chat (intenciones, semáforo, gatillos).
Todos los tests son unitarios y no requieren API keys ni servicios externos.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.features.chat.config import Intention, Semaphore, INTENTIONS, GATILLOS
from app.features.chat.classifier import (
    IntentionClassifier,
    SemaphoreClassifier,
    ProjectAnalysisDetector,
)
from app.features.chat.schemas import (
    ChatRequest,
    ChatResponse,
    ChatClassification,
    ActionType,
)


# =============================================================================
# TESTS: Clasificación de Intenciones por Keywords
# =============================================================================


class TestIntentionClassifierKeywords:
    """Tests para la clasificación de intenciones por keywords."""

    def test_formalizacion_keywords(self):
        """Detecta intención de formalización."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo constituyo una asociación civil en SUNARP?"
        )
        assert intention == Intention.FORMALIZACION
        assert conf > 0.0

    def test_identidad_ruc_keywords(self):
        """Detecta intención de RUC."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "Necesito sacar mi RUC en SUNAT"
        )
        assert intention == Intention.IDENTIDAD_RUC
        assert conf > 0.0

    def test_baja_provisional_keywords(self):
        """'Me dieron de baja provisional' → IDENTIDAD_RUC (no fuera de alcance)."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "me dieron de baja provisional"
        )
        assert intention == Intention.IDENTIDAD_RUC
        assert conf > 0.0

    def test_baja_provisional_que_es_keywords(self):
        """'Qué es una baja provisional' → IDENTIDAD_RUC (no fuera de alcance)."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "qué es una baja provisional"
        )
        assert intention == Intention.IDENTIDAD_RUC
        assert conf > 0.0

    def test_dar_de_baja_ruc_keywords(self):
        """'Quiero dar de baja mi RUC' → IDENTIDAD_RUC."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "Quiero dar de baja mi RUC en SUNAT"
        )
        assert intention == Intention.IDENTIDAD_RUC
        assert conf > 0.0

    def test_reactivar_ruc_keywords(self):
        """'Reactivar RUC' → IDENTIDAD_RUC."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo puedo reactivar mi RUC?"
        )
        assert intention == Intention.IDENTIDAD_RUC
        assert conf > 0.0

    def test_donaciones_keywords(self):
        """Detecta intención de donaciones."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo registro mi ONGD en APCI para recibir cooperación internacional?"
        )
        assert intention == Intention.DONACIONES
        assert conf > 0.0

    def test_tributacion_keywords(self):
        """Detecta intención de tributación."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo pido la exoneración del impuesto a la renta?"
        )
        assert intention == Intention.TRIBUTACION
        assert conf > 0.0

    def test_contratacion_keywords(self):
        """Detecta intención de contratación."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Qué derechos tiene un voluntario en mi organización?"
        )
        assert intention == Intention.CONTRATACION
        assert conf > 0.0

    def test_propiedad_intelectual_keywords(self):
        """Detecta intención de propiedad intelectual."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo protejo los derechos de autor de mi obra?"
        )
        assert intention == Intention.PROPIEDAD_INTELECTUAL
        assert conf > 0.0

    def test_datos_personales_keywords(self):
        """Detecta intención de datos personales."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Necesito consentimiento para tratar datos personales?"
        )
        assert intention == Intention.DATOS_PERSONALES
        assert conf > 0.0

    def test_gobernanza_keywords(self):
        """Detecta intención de gobernanza."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cuál es el quórum para la asamblea de la directiva?"
        )
        assert intention == Intention.GOBERNANZA
        assert conf > 0.0

    def test_alianzas_keywords(self):
        """Detecta intención de alianzas."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Qué es un consorcio y cómo lo registro?"
        )
        assert intention == Intention.ALIANZAS
        assert conf > 0.0

    def test_permisos_keywords(self):
        """Detecta intención de permisos."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Necesito permiso de la municipalidad para un evento?"
        )
        assert intention == Intention.PERMISOS
        assert conf > 0.0

    def test_marca_identidad_keywords(self):
        """Detecta intención de marca."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Requisitos para el registro de marca y nombre comercial?"
        )
        assert intention == Intention.MARCA_IDENTIDAD
        assert conf > 0.0

    def test_seguridad_keywords(self):
        """Detecta intención de seguridad de la información."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo protejo mis archivos contra hackeo y ciberseguridad?"
        )
        assert intention == Intention.SEGURIDAD_INFORMACION
        assert conf > 0.0

    def test_no_match_returns_none(self):
        """Si no hay match, retorna None."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo hago una pizza margarita?"
        )
        assert intention is None
        assert conf == 0.0

    def test_empty_message(self):
        """Mensaje vacío retorna None."""
        intention, conf = IntentionClassifier.classify_by_keywords("")
        assert intention is None
        assert conf == 0.0


# =============================================================================
# TESTS: Clasificación de Semáforo (Gatillos)
# =============================================================================


class TestSemaphoreClassifier:
    """Tests para la clasificación de semáforo."""

    # ------ GATILLOS ROJO ------

    def test_formalizacion_gatillo_rojo(self):
        """Esquela de observación → ROJO."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Recibimos una esquela de observación de SUNARP",
            Intention.FORMALIZACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0
        assert "esquela de observación" in gatillos

    def test_ruc_gatillo_rojo_fiscalizacion(self):
        """Fiscalización de SUNAT → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Nos llegó una fiscalización de SUNAT",
            Intention.IDENTIDAD_RUC,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_donaciones_gatillo_rojo(self):
        """Fondos extranjeros para marchas → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Recibimos fondos extranjeros para marchas",
            Intention.DONACIONES,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_tributacion_gatillo_rojo(self):
        """Dividendo entre socios → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Queremos repartir un dividendo entre socios",
            Intention.TRIBUTACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_contratacion_gatillo_rojo(self):
        """SUNAFIL → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Recibimos una inspección de SUNAFIL",
            Intention.CONTRATACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_propiedad_intelectual_gatillo_rojo(self):
        """Notificación de INDECOPI → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Recibimos una notificación de INDECOPI por infracción",
            Intention.PROPIEDAD_INTELECTUAL,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_datos_personales_gatillo_rojo(self):
        """Filtración de datos → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Hubo una filtración de datos de víctimas",
            Intention.DATOS_PERSONALES,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_gobernanza_gatillo_rojo(self):
        """Presidente actúa sin poderes → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "El presidente actúa sin poderes legales",
            Intention.GOBERNANZA,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_seguridad_gatillo_rojo(self):
        """Sabotaje informático → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Sufrimos un sabotaje informático",
            Intention.SEGURIDAD_INFORMACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_marca_gatillo_rojo(self):
        """Oposición de tercero → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Hay una oposición de tercero contra nuestra marca",
            Intention.MARCA_IDENTIDAD,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_permisos_gatillo_rojo(self):
        """Evento > 3000 personas → ROJO."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Vamos a hacer un evento de más de 3000 personas",
            Intention.PERMISOS,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    # ------ VERDE ------

    def test_baja_provisional_especifico_amarillo(self):
        """'Me dieron de baja provisional' es caso específico → AMARILLO, no VERDE."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "me dieron de baja provisional",
            Intention.IDENTIDAD_RUC,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_pregunta_mixta_especifica_amarillo(self):
        """Pregunta informativa + caso concreto → AMARILLO (no bypass a VERDE)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Cómo reactivo mi RUC si me dieron de baja provisional?",
            Intention.IDENTIDAD_RUC,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0

    def test_pregunta_informativa_verde(self):
        """Pregunta informativa pura → VERDE."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué es una asociación civil?",
            Intention.FORMALIZACION,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_pregunta_requisitos_verde(self):
        """Pregunta de requisitos → VERDE."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "¿Qué requisitos necesito para constituir una fundación?",
            Intention.FORMALIZACION,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_sin_gatillos_verde(self):
        """Sin gatillos ni contexto faltante → VERDE."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "¿Cuál es el plazo para registrar una marca?",
            Intention.MARCA_IDENTIDAD,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    # ------ CROSS-INTENTION GATILLOS ------

    def test_cross_intention_gatillo(self):
        """Gatillo detectado de otra intención (cruzado)."""
        # Fiscalización SUNAT es gatillo de IDENTIDAD_RUC,
        # pero si el usuario pregunta sobre tributación mencionando "fiscalización de sunat"
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Nos llegó una fiscalización de sunat por el tema de impuestos",
            Intention.TRIBUTACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0


# =============================================================================
# TESTS: Detección de Análisis de Proyecto
# =============================================================================


class TestProjectAnalysisDetector:
    """Tests para detección de análisis de proyecto."""

    def test_analizar_proyecto(self):
        assert ProjectAnalysisDetector.is_project_analysis(
            "Quiero analizar mi proyecto"
        )

    def test_evaluar_viabilidad(self):
        assert ProjectAnalysisDetector.is_project_analysis(
            "¿Mi proyecto es viable legalmente?"
        )

    def test_proyecto_emprender(self):
        assert ProjectAnalysisDetector.is_project_analysis(
            "Quiero emprender, ¿qué necesito?"
        )

    def test_no_analisis(self):
        assert not ProjectAnalysisDetector.is_project_analysis(
            "¿Cómo constituyo una asociación civil?"
        )

    def test_no_analisis_pizza(self):
        assert not ProjectAnalysisDetector.is_project_analysis(
            "¿Cómo hago una pizza?"
        )


# =============================================================================
# TESTS: ChatService (con mocks)
# =============================================================================


class TestChatService:
    """Tests para el servicio de chat con mocks del LLM."""

    @pytest.fixture
    def mock_ai_router(self):
        """Mock del AIRouter."""
        with patch("app.features.chat.classifier.AIRouter") as mock:
            router_instance = MagicMock()
            router_instance.intake_json = AsyncMock(return_value={
                "intention": "formalizacion",
                "semaphore": "verde",
                "confidence": 0.9,
                "reasoning": "Test",
            })
            router_instance.reason = AsyncMock(return_value=MagicMock(
                content="Respuesta de prueba del LLM"
            ))
            mock.return_value = router_instance
            yield mock

    @pytest.fixture
    def mock_rag(self):
        """Mock del módulo RAG."""
        with patch("app.features.chat.service.get_rag_module") as mock:
            mock.return_value = None  # Sin RAG
            yield mock

    @pytest.mark.asyncio
    async def test_fuera_de_alcance(self, mock_ai_router, mock_rag):
        """Consulta fuera de alcance es rechazada."""
        from app.features.chat.service import ChatService

        # Mock classify para retornar fuera_de_alcance
        with patch.object(
            IntentionClassifier, "classify",
            new=AsyncMock(return_value=(Intention.FUERA_DE_ALCANCE, 0.0))
        ):
            service = ChatService()
            request = ChatRequest(message="¿Cómo hago una pizza?")
            response = await service.process_message(request)

            assert response.classification.intention == Intention.FUERA_DE_ALCANCE
            assert "no puedo responder" in response.message.lower() or "fuera" in response.message.lower() or "especializado" in response.message.lower()

    @pytest.mark.asyncio
    async def test_proyecto_analysis_sugiere_archivo(self, mock_ai_router, mock_rag):
        """Análisis de proyecto sugiere subir archivo."""
        from app.features.chat.service import ChatService

        service = ChatService()
        request = ChatRequest(message="Quiero analizar mi proyecto")
        response = await service.process_message(request)

        assert any(a.type == ActionType.UPLOAD_FILE for a in response.actions)
        assert "subir" in response.message.lower() or "archivo" in response.message.lower()

    @pytest.mark.asyncio
    async def test_gatillo_rojo_deriva_asesor(self, mock_ai_router, mock_rag):
        """Gatillo ROJO deriva a asesor automáticamente."""
        from app.features.chat.service import ChatService

        service = ChatService()
        request = ChatRequest(
            message="Recibimos una esquela de observación de SUNARP"
        )
        response = await service.process_message(request)

        assert response.classification.semaphore == Semaphore.ROJO
        assert len(response.classification.gatillos_detected) > 0
        assert any(a.type == ActionType.DERIVE_TO_ADVISOR for a in response.actions)
        assert "ALERTA" in response.message or "asesor" in response.message.lower()

    @pytest.mark.asyncio
    async def test_verde_genera_respuesta(self, mock_ai_router, mock_rag):
        """Consulta verde genera respuesta (básica sin RAG)."""
        from app.features.chat.service import ChatService

        # Mock the AI router at service level too
        with patch("app.features.chat.service.AIRouter") as svc_mock:
            router_instance = MagicMock()
            router_instance.reason = AsyncMock(return_value=MagicMock(
                content="Para constituir una asociación civil necesitas..."
            ))
            svc_mock.return_value = router_instance

            service = ChatService()
            request = ChatRequest(
                message="¿Qué es una asociación civil?"
            )
            response = await service.process_message(request)

            assert response.classification.semaphore == Semaphore.VERDE
            assert response.classification.intention == Intention.FORMALIZACION
            assert len(response.message) > 0


# =============================================================================
# TESTS: Configuración
# =============================================================================


class TestConfiguration:
    """Tests para verificar la integridad de la configuración."""

    def test_13_intenciones_plus_fuera(self):
        """Debe haber 13 intenciones + fuera_de_alcance = 14."""
        assert len(INTENTIONS) == 14

    def test_todas_intenciones_tienen_nombre(self):
        """Todas las intenciones deben tener nombre."""
        for intention, config in INTENTIONS.items():
            assert config.name, f"{intention} no tiene nombre"

    def test_todas_intenciones_tienen_descripcion(self):
        """Todas las intenciones deben tener descripción."""
        for intention, config in INTENTIONS.items():
            assert config.description, f"{intention} no tiene descripción"

    def test_gatillos_tienen_phrases(self):
        """Todos los gatillos deben tener al menos una frase."""
        for intention, gatillo_list in GATILLOS.items():
            for gatillo in gatillo_list:
                assert len(gatillo.trigger_phrases) > 0, \
                    f"Gatillo de {intention} no tiene frases"

    def test_gatillos_tienen_razon(self):
        """Todos los gatillos deben tener razón de derivación."""
        for intention, gatillo_list in GATILLOS.items():
            for gatillo in gatillo_list:
                assert gatillo.derivation_reason, \
                    f"Gatillo de {intention} no tiene razón de derivación"

    def test_intenciones_con_keywords(self):
        """Todas las intenciones (excepto fuera_de_alcance) deben tener keywords."""
        for intention, config in INTENTIONS.items():
            if intention != Intention.FUERA_DE_ALCANCE:
                assert len(config.keywords) > 0, \
                    f"{intention} no tiene keywords"
