"""
Model: Assessment
Evaluaciones guardadas
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Assessment(Base):
    """Evaluación guardada"""
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Tipo
    assessment_type: Mapped[str] = mapped_column(String(50))  # evaluation, compliance

    # Resultado
    viability: Mapped[str] = mapped_column(String(50))
    risk_level: Mapped[str] = mapped_column(String(20))
    gaps_count: Mapped[int] = mapped_column(Integer, default=0)

    # Contenido
    summary: Mapped[str] = mapped_column(Text)
    full_result: Mapped[dict] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
