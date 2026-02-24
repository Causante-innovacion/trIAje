"""
Legal Adviser Feature - Service
Business logic para generar paquete de asesor legal.
"""

from app.modules.intake.schemas import NormalizedProjectIntake

from .schemas import LegalAdviserResponse
from .pipeline import LegalAdviserPipeline, get_legal_adviser_pipeline


class LegalAdviserService:
    """
    Servicio para generar paquetes de preparación para asesor legal.
    """

    def __init__(self):
        self.pipeline = get_legal_adviser_pipeline()

    async def generate_from_intake(self, intake: NormalizedProjectIntake) -> LegalAdviserResponse:
        """
        Genera el paquete de asesor legal con evidencia normativa (RAG).

        Args:
            intake: NormalizedProjectIntake con 1-3 organizaciones

        Returns:
            LegalAdviserResponse con perfil, tópicos, preguntas, documentos, decisiones y evidencia
        """
        return await self.pipeline.generate_async(intake)


# Singleton
_service: LegalAdviserService | None = None


def get_legal_adviser_service() -> LegalAdviserService:
    """Obtiene el servicio de asesor legal"""
    global _service
    if _service is None:
        _service = LegalAdviserService()
    return _service
