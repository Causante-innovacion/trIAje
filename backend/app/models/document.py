"""
Model: Legal Document
Documentos legales indexados para RAG
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class LegalDocument(Base):
    """Documento legal indexado"""
    __tablename__ = "legal_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Metadata
    title: Mapped[str] = mapped_column(String(500))
    source_type: Mapped[str] = mapped_column(String(50))  # normative_primary, etc.
    authority_level: Mapped[float] = mapped_column(Float, default=0.5)
    jurisdiction: Mapped[str] = mapped_column(String(10), default="PE")

    # Contenido
    content: Mapped[str] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Fechas
    validity_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    indexed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Estado
    is_active: Mapped[bool] = mapped_column(default=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
