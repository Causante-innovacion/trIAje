"""
Model: Consultation
Historial de consultas
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Consultation(Base):
    """Registro de consulta"""
    __tablename__ = "consultations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Tipo de consulta
    tool_id: Mapped[int] = mapped_column(Integer)  # 1-4
    tool_name: Mapped[str] = mapped_column(String(100))

    # Datos de entrada (anonimizados)
    input_summary: Mapped[str] = mapped_column(Text, nullable=True)
    organization_type: Mapped[str] = mapped_column(String(100), nullable=True)

    # Resultado
    viability: Mapped[str] = mapped_column(String(50), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=True)
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=True)

    # Metadata
    rag_confidence: Mapped[float] = mapped_column(nullable=True)
    escalation_triggered: Mapped[bool] = mapped_column(default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Datos adicionales (JSON)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
