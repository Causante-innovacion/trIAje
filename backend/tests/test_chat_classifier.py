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

    # ------ PDF FASE 2: Tests adicionales de keywords por intención ------

    def test_formalizacion_reserva_nombre_keywords(self):
        """'Reserva de nombre SUNARP' → FORMALIZACION."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo pido la reserva de nombre en SUNARP antes de constituir?"
        )
        assert intention == Intention.FORMALIZACION
        assert conf > 0.0

    def test_ruc_domicilio_fiscal_keywords(self):
        """'Domicilio fiscal SUNAT' → IDENTIDAD_RUC."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cuál es el plazo para actualizar el domicilio fiscal ante SUNAT?"
        )
        assert intention == Intention.IDENTIDAD_RUC
        assert conf > 0.0

    def test_donaciones_certificado_keywords(self):
        """'Certificado de donación APCI' → DONACIONES."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo emito un certificado de donación para el donante internacional de nuestra ONGD?"
        )
        assert intention == Intention.DONACIONES
        assert conf > 0.0

    def test_tributacion_exoneracion_vigencia_keywords(self):
        """'Exoneración impuesto renta UIT' → TRIBUTACION."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Hasta cuándo tiene vigencia la exoneración del impuesto a la renta para OSAL?"
        )
        assert intention == Intention.TRIBUTACION
        assert conf > 0.0

    def test_contratacion_pasantia_keywords(self):
        """'Convenio pasantía practicante' → CONTRATACION."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Podemos firmar un convenio de pasantía para practicantes pre-profesionales?"
        )
        assert intention == Intention.CONTRATACION
        assert conf > 0.0

    def test_propiedad_intelectual_derechos_morales_keywords(self):
        """'Derechos de autor obra' → PROPIEDAD_INTELECTUAL."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Qué son los derechos morales de autor en una obra periodística?"
        )
        assert intention == Intention.PROPIEDAD_INTELECTUAL
        assert conf > 0.0

    def test_datos_personales_oficial_keywords(self):
        """'Oficial de datos protección' → DATOS_PERSONALES."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Qué es un oficial de datos y cuándo es obligatorio nombrarlo?"
        )
        assert intention == Intention.DATOS_PERSONALES
        assert conf > 0.0

    def test_preparacion_asesoria_keywords(self):
        """'Abogado documentos preparar caso' → PREPARACION_ASESORIA."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Qué documentos debo ordenar para consultar a un abogado y preparar mi caso?"
        )
        assert intention == Intention.PREPARACION_ASESORIA
        assert conf > 0.0

    def test_gobernanza_exclusion_keywords(self):
        """'Exclusión de socio estatuto' → GOBERNANZA."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Cómo se realiza la exclusión de un socio según el estatuto de la asociación?"
        )
        assert intention == Intention.GOBERNANZA
        assert conf > 0.0

    def test_marca_nombre_comercial_keywords(self):
        """'Nombre comercial INDECOPI' → MARCA_IDENTIDAD."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Qué es el nombre comercial y cómo lo registro en INDECOPI?"
        )
        assert intention == Intention.MARCA_IDENTIDAD
        assert conf > 0.0

    def test_permisos_espectaculo_publico_keywords(self):
        """'Espectáculo público autorización municipalidad' → PERMISOS."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Qué es un espectáculo público y qué autorización necesito de la municipalidad?"
        )
        assert intention == Intention.PERMISOS
        assert conf > 0.0

    def test_seguridad_secreto_profesional_keywords(self):
        """'Secreto profesional protección fuentes' → SEGURIDAD_INFORMACION."""
        intention, conf = IntentionClassifier.classify_by_keywords(
            "¿Qué es el secreto profesional y cómo protejo mis fuentes periodísticas?"
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

    # ==========================================================================
    # PDF FASE 2 — VERDE: Preguntas informativas generales por intención
    # Fuente: Matrices "Pregunta / Escenario → Fuente Exacta" del Entregable 2
    # ==========================================================================

    def test_formalizacion_estatuto_verde(self):
        """PDF Fase 2 §1 — '¿Qué debe incluir el estatuto?' → VERDE (Cód. Civil Art. 82)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué debe incluir el estatuto de una asociación civil?",
            Intention.FORMALIZACION,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_formalizacion_reserva_nombre_verde(self):
        """PDF Fase 2 §1 — '¿Cómo pido reserva de nombre?' → VERDE (Res. 038-2013-SUNARP Art. 32)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Cómo pido la reserva de nombre en SUNARP?",
            Intention.FORMALIZACION,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_ruc_documentos_verde(self):
        """PDF Fase 2 §2 — '¿Qué documentos para el RUC?' → VERDE (RS 210-2004/SUNAT Art. 7)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué documentos necesito para obtener el RUC de persona jurídica?",
            Intention.IDENTIDAD_RUC,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_ruc_diferencia_10_20_verde(self):
        """PDF Fase 2 §2 — 'Diferencia RUC 10 vs RUC 20' → VERDE (guías SUNAT)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Cuál es la diferencia entre el RUC 10 y el RUC 20?",
            Intention.IDENTIDAD_RUC,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_donaciones_ongd_verde(self):
        """PDF Fase 2 §3 — '¿Qué es una ONGD?' → VERDE (DS 032-2025-RE Art. 29)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué es una ONGD y cuáles son sus fines?",
            Intention.DONACIONES,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_donaciones_ipreda_eniex_verde(self):
        """PDF Fase 2 §3 — 'Diferencia IPREDA y ENIEX' → VERDE (Portal APCI)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Cuál es la diferencia entre una IPREDA y una ENIEX?",
            Intention.DONACIONES,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_tributacion_exoneracion_ir_verde(self):
        """PDF Fase 2 §4 — '¿Qué es el beneficio de exoneración?' → VERDE (Art. 19 LIR)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué es el beneficio de exoneración del impuesto a la renta para organizaciones?",
            Intention.TRIBUTACION,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_tributacion_vigencia_exoneracion_verde(self):
        """PDF Fase 2 §4 — '¿Vigencia de la exoneración?' → VERDE (DL 1549 hasta 31/12/2026)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Hasta cuándo tiene vigencia la exoneración del IR según el DL 1549?",
            Intention.TRIBUTACION,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_contratacion_que_es_voluntariado_verde(self):
        """PDF Fase 2 §5 — '¿Qué es el voluntariado?' → VERDE (Ley 28238 Art. 2)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué es el voluntariado según la ley peruana?",
            Intention.CONTRATACION,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_contratacion_edad_minima_verde(self):
        """PDF Fase 2 §5 — '¿Edad para ser voluntario?' → VERDE (Ley 28238 Art. 4: 14 años)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Cuál es la edad mínima para ser voluntario en una organización?",
            Intention.CONTRATACION,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_propiedad_derechos_morales_verde(self):
        """PDF Fase 2 §6 — '¿Qué son derechos morales?' → VERDE (DL 822 Art. 22)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué son los derechos morales de autor y qué protegen?",
            Intention.PROPIEDAD_INTELECTUAL,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_propiedad_duracion_derechos_verde(self):
        """PDF Fase 2 §6 — '¿Límite de protección derechos autor?' → VERDE (DL 822 Art. 52: vida + 70 años)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Cuánto dura la protección de los derechos de autor en Perú?",
            Intention.PROPIEDAD_INTELECTUAL,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_datos_consentimiento_verde(self):
        """PDF Fase 2 §7 — '¿Qué es el consentimiento informado?' → VERDE (Ley 29733 Art. 5)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué es el consentimiento informado en el tratamiento de datos personales?",
            Intention.DATOS_PERSONALES,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_datos_sensibles_verde(self):
        """PDF Fase 2 §7 — '¿Qué son datos sensibles?' → VERDE (Ley 29733 Glosario)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué son los datos sensibles según la ley 29733?",
            Intention.DATOS_PERSONALES,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_preparacion_asesoria_documentos_verde(self):
        """PDF Fase 2 §8 — '¿Qué documentos debo ordenar?' → VERDE (Guía ACE Metodología)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué documentos debo ordenar antes de consultar a un abogado?",
            Intention.PREPARACION_ASESORIA,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_gobernanza_asamblea_virtual_verde(self):
        """PDF Fase 2 §9 — 'Sesión de asamblea virtual' → VERDE (Res. 038-2013-SUNARP Art. 13)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Cómo se puede realizar una sesión de asamblea general virtual?",
            Intention.GOBERNANZA,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_alianzas_consorcio_verde(self):
        """PDF Fase 2 §10 — '¿Qué es un consorcio?' → VERDE (LGS Art. 445)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué es un consorcio entre organizaciones civiles?",
            Intention.ALIANZAS,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_permisos_espectaculo_publico_verde(self):
        """PDF Fase 2 §11 — '¿Qué es espectáculo público?' → VERDE (plataforma Gob.pe)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué es un espectáculo público según la normativa vigente?",
            Intention.PERMISOS,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_marca_nombre_comercial_verde(self):
        """PDF Fase 2 §12 — '¿Qué es nombre comercial?' → VERDE (DL 823 / Guía INDECOPI)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué es un nombre comercial en propiedad industrial?",
            Intention.MARCA_IDENTIDAD,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    def test_seguridad_secreto_profesional_verde(self):
        """PDF Fase 2 §13 — '¿Qué es el secreto profesional?' → VERDE (Constitución Art. 2 inc. 18)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "¿Qué es el secreto profesional del periodismo y cómo me protege?",
            Intention.SEGURIDAD_INFORMACION,
        )
        assert semaphore == Semaphore.VERDE
        assert len(gatillos) == 0

    # ==========================================================================
    # PDF FASE 2 — AMARILLO: Casos específicos que requieren contexto mínimo
    # El usuario habla de SU situación; el sistema solicita dato mínimo.
    # ==========================================================================

    def test_formalizacion_error_escritura_amarillo(self):
        """PDF Fase 2 §1 — Error en escritura pública → AMARILLO (dato: tipo error)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Tenemos un error en nuestra escritura pública de constitución",
            Intention.FORMALIZACION,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_formalizacion_fundador_ausente_amarillo(self):
        """PDF Fase 2 §1 — Fundador ausente para firmar → AMARILLO (dato: tiempo ausencia)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Uno de nuestros fundadores está ausente y no puede firmar la escritura",
            Intention.FORMALIZACION,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_ruc_representante_cambio_amarillo(self):
        """PDF Fase 2 §2 — Cambio de representante legal → AMARILLO (dato: etapa trámite RUC)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Cambió nuestro representante legal y necesitamos actualizar el RUC en SUNAT",
            Intention.IDENTIDAD_RUC,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_donaciones_bienes_extranjero_amarillo(self):
        """PDF Fase 2 §3 — Recepción de bienes del extranjero → AMARILLO (dato: tipo bien)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Recibimos equipos del extranjero como donación y no sabemos cómo registrarlos",
            Intention.DONACIONES,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_tributacion_venta_servicios_amarillo(self):
        """PDF Fase 2 §4 — Venta de servicios manteniendo exoneración → AMARILLO (dato: actividad comercial)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Nuestro colectivo vende polos para financiar sus actividades sociales",
            Intention.TRIBUTACION,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_tributacion_igv_consultorias_amarillo(self):
        """PDF Fase 2 §4 — IGV por consultorías → AMARILLO (dato: monto operación)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Tenemos una consultoría pendiente y no sabemos si debemos pagar IGV",
            Intention.TRIBUTACION,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_contratacion_registro_voluntarios_amarillo(self):
        """PDF Fase 2 §5 — Registro de voluntarios → AMARILLO (dato: cantidad voluntarios)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Tenemos 50 voluntarios activos y queremos saber si debemos registrarlos ante el MIMP",
            Intention.CONTRATACION,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_propiedad_fotos_internet_amarillo(self):
        """PDF Fase 2 §6 — Uso de fotos de internet → AMARILLO (dato: tipo licencia)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Descargamos imágenes de internet para nuestros materiales sin pedir autorización de los autores",
            Intention.PROPIEDAD_INTELECTUAL,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_datos_base_datos_amarillo(self):
        """PDF Fase 2 §7 — Registro de base de datos → AMARILLO (dato: volumen)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Tenemos una base de datos con cientos de registros de nuestros beneficiarios",
            Intention.DATOS_PERSONALES,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_datos_transferencia_ong_amarillo(self):
        """PDF Fase 2 §7 — Transferencia de datos a ONG socia → AMARILLO (dato: país destino)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Tenemos que transferir datos de socios a una ONG socia en el extranjero",
            Intention.DATOS_PERSONALES,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_gobernanza_excluir_socio_amarillo(self):
        """PDF Fase 2 §9 — Exclusión de socio → AMARILLO (dato: motivo exclusión, Cód. Civil Art. 95)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Tenemos un socio que cometió una falta grave y queremos excluirlo de la asociación",
            Intention.GOBERNANZA,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_alianzas_responsabilidad_amarillo(self):
        """PDF Fase 2 §10 — Responsabilidad en consorcio → AMARILLO (dato: tipo de aportes, LGS Art. 447)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Nuestro consorcio tiene dudas sobre la responsabilidad ante terceros",
            Intention.ALIANZAS,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    def test_permisos_evento_calle_amarillo(self):
        """PDF Fase 2 §11 — Permiso para evento en calle → AMARILLO (dato: distrito, TUPA municipal)."""
        semaphore, gatillos, context = SemaphoreClassifier.classify(
            "Necesitamos un permiso para nuestro evento cultural en la calle",
            Intention.PERMISOS,
        )
        assert semaphore == Semaphore.AMARILLO
        assert len(gatillos) == 0
        assert len(context) > 0

    # ==========================================================================
    # PDF FASE 2 — ROJO: Gatillos de derivación obligatoria a abogado
    # ==========================================================================

    def test_formalizacion_conflicto_fundadores_rojo(self):
        """PDF Fase 2 §1 — Conflicto entre fundadores → ROJO (crisis de gobernanza)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Hay un conflicto interno entre nuestros fundadores y no podemos avanzar",
            Intention.FORMALIZACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_ruc_operamos_sin_ruc_rojo(self):
        """PDF Fase 2 §2 — Operar sin RUC con ingresos → ROJO (Art. 173 Cód. Tributario)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Operamos sin RUC durante varios meses y tuvimos ingresos por actividades",
            Intention.IDENTIDAD_RUC,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_ruc_cancelado_oficio_rojo(self):
        """PDF Fase 2 §2 — RUC cancelado por SUNAT → ROJO (baja de oficio, RS 210-2004/SUNAT)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Nos avisaron que el RUC cancelado de nuestra asociación no puede operar",
            Intention.IDENTIDAD_RUC,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_donaciones_auditoria_apci_rojo(self):
        """PDF Fase 2 §3 — Auditoría de APCI en curso → ROJO (DS 032-2025-RE Art. 19)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Estamos en una auditoría de APCI por nuestros proyectos de cooperación",
            Intention.DONACIONES,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_donaciones_multa_500_uit_rojo(self):
        """PDF Fase 2 §3 — Multa de 500 UIT por APCI → ROJO (Ley 32301 régimen sancionador)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Recibimos una multa de 500 UIT de APCI por el reporte tardío de proyectos",
            Intention.DONACIONES,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_tributacion_reparto_excedentes_rojo(self):
        """PDF Fase 2 §4 — Reparto de excedentes entre socios → ROJO (pérdida beneficio Art. 19 LIR)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Queremos hacer el reparto de excedentes entre socios al cierre del año",
            Intention.TRIBUTACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_tributacion_reparo_tributario_rojo(self):
        """PDF Fase 2 §4 — Notificación de reparo tributario → ROJO (Cód. Tributario)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Recibimos una notificación de reparo tributario de SUNAT por el ejercicio anterior",
            Intention.TRIBUTACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_contratacion_locador_horario_fijo_rojo(self):
        """PDF Fase 2 §5 — Locador de servicios con horario fijo → ROJO (desnaturalización, DL 728)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Tenemos un locador con horario fijo de 9 a 5 en nuestra oficina",
            Intention.CONTRATACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_contratacion_accidente_voluntario_rojo(self):
        """PDF Fase 2 §5 — Accidente de un voluntario → ROJO (responsabilidad PJ, Ley 28238 Art. 5)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Tuvimos un accidente de voluntario durante el último evento solidario",
            Intention.CONTRATACION,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_datos_hackeo_base_datos_rojo(self):
        """PDF Fase 2 §7 — Hackeo de base de datos → ROJO (reportar en 48h a ANPDP, Reg. 2025)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Sufrimos un hackeo de base de datos con información de nuestros beneficiarios",
            Intention.DATOS_PERSONALES,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_gobernanza_conflicto_directores_rojo(self):
        """PDF Fase 2 §9 — Conflicto grave entre directores → ROJO (crisis institucional)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Existe un conflicto grave entre directores que paraliza las decisiones de la institución",
            Intention.GOBERNANZA,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_alianzas_incumplimiento_rojo(self):
        """PDF Fase 2 §10 — Incumplimiento de aliado → ROJO (Cód. Civil Art. 1428, daños y perjuicios)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Hay un incumplimiento de aliado en nuestro consorcio y perdimos el fondo",
            Intention.ALIANZAS,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_permisos_ninos_huerfanos_rojo(self):
        """PDF Fase 2 §11 — Trabajo con niños huérfanos → ROJO (riesgo extremo, Cód. Niños)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Vamos a realizar trabajo con niños huérfanos de la comunidad",
            Intention.PERMISOS,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_marca_logo_sin_permiso_rojo(self):
        """PDF Fase 2 §12 — Alguien usa el logo sin permiso → ROJO (infracción DL 823, INDECOPI)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Alguien usa mi logo sin permiso en sus publicaciones comerciales",
            Intention.MARCA_IDENTIDAD,
        )
        assert semaphore == Semaphore.ROJO
        assert len(gatillos) > 0

    def test_seguridad_borrado_base_datos_rojo(self):
        """PDF Fase 2 §13 — Ex-miembro borra base de datos → ROJO (sabotaje, Ley 30096)."""
        semaphore, gatillos, _ = SemaphoreClassifier.classify(
            "Nos borraron nuestra base de datos del servidor la semana pasada",
            Intention.SEGURIDAD_INFORMACION,
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
    async def test_autodescripcion_asistente(self, mock_ai_router, mock_rag):
        """Preguntas sobre el asistente devuelven su descripción y capacidades."""
        from app.features.chat.service import ChatService

        service = ChatService()
        request = ChatRequest(message="¿Cómo te defines y qué capacidades tienes?")
        response = await service.process_message(request)

        assert response.classification.intention == Intention.FUERA_DE_ALCANCE
        assert "soy **justo**" in response.message.lower()
        assert "puedo ayudarte" in response.message.lower()
        assert "no puedo responder" not in response.message.lower()

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
