"""
Extracción de datos de Plan Estratégico CAUSANTE (.docx)
Adaptado de extract_plan_estrategico.py para funcionar como módulo del backend.
"""

import io
import re
from typing import Any

from docx import Document


# ─────────────────────────────────────────────
# LECTURA DEL DOCUMENTO
# ─────────────────────────────────────────────

def _read_docx_bytes(file_bytes: bytes) -> dict:
    """Lee un .docx desde bytes y devuelve texto + tablas."""
    doc = Document(io.BytesIO(file_bytes))

    full_text = []
    tables_raw = []

    for para in doc.paragraphs:
        full_text.append(para.text.strip())

    for table in doc.tables:
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            rows.append(cells)
        tables_raw.append(rows)

    return {
        "full_text": "\n".join(full_text),
        "paragraphs": [p.text.strip() for p in doc.paragraphs if p.text.strip()],
        "tables": tables_raw,
    }


# ─────────────────────────────────────────────
# SEGMENTACIÓN POR SECCIONES
# ─────────────────────────────────────────────

SECTION_PATTERNS = {
    "pitch": r"(?:1\.?\s*)?PROPUESTA\s+DE\s+VALOR",
    "concepto": r"(?:2\.?\s*)?CONCEPTO\s+ESTRAT[ÉE]GICO",
    "equipo": r"(?:3\.?\s*)?EQUIPO\s+Y\s+ROLES",
    "brechas": r"(?:4\.?\s*)?AN[ÁA]LISIS\s+DE\s+BRECHAS",
    "financiamiento": r"(?:5\.?\s*)?ESTRATEGIA\s+DE\s+FINANCIAMIENTO",
    "referencias": r"(?:6\.?\s*)?CASOS\s+DE\s+REFERENCIA",
}


def _split_sections(full_text: str) -> dict:
    """Divide el texto completo en secciones usando los encabezados."""
    positions = {}
    for key, pattern in SECTION_PATTERNS.items():
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            positions[key] = match.start()

    ordered = sorted(positions.items(), key=lambda x: x[1])

    sections = {}
    for i, (key, start) in enumerate(ordered):
        end = ordered[i + 1][1] if i + 1 < len(ordered) else len(full_text)
        sections[key] = full_text[start:end].strip()

    return sections


# ─────────────────────────────────────────────
# EXTRACCIÓN DE DATOS
# ─────────────────────────────────────────────

def _extract_project_metadata(
    sections: dict, paragraphs: list, full_text: str
) -> dict:
    """Extrae metadatos del proyecto."""
    name = paragraphs[1] if len(paragraphs) > 1 else "Sin nombre"

    pitch_text = sections.get("pitch", "")
    description = ""
    desc_match = re.search(r'"(.*?)"', pitch_text, re.DOTALL)
    if desc_match:
        description = desc_match.group(1).strip()

    concepto = sections.get("concepto", "")
    problema = ""
    solucion = ""

    prob_match = re.search(
        r"EL\s+PROBLEMA[:\s]*(.*?)(?=LA\s+SOLUCI[ÓO]N|$)",
        concepto,
        re.IGNORECASE | re.DOTALL,
    )
    if prob_match:
        problema = prob_match.group(1).strip()

    sol_match = re.search(
        r"LA\s+SOLUCI[ÓO]N[:\s]*(.*?)(?=\d+\.\s|$)",
        concepto,
        re.IGNORECASE | re.DOTALL,
    )
    if sol_match:
        solucion = sol_match.group(1).strip()

    dep_match = re.search(r"Dep\.?\s*Externa[:\s]*(\d+)%", full_text, re.IGNORECASE)
    ext_dep = int(dep_match.group(1)) if dep_match else None

    return {
        "project_name": name,
        "description": description,
        "problem_summary": problema,
        "solution_summary": solucion,
        "external_dependency": ext_dep,
    }


def _extract_organizations(tables: list) -> list[dict]:
    """Extrae organizaciones de la tabla de equipo."""
    organizations: list[dict] = []

    for table in tables:
        if not table:
            continue

        header = " ".join(table[0]).lower()
        if "organización" not in header and "rol" not in header:
            continue

        for row in table[1:]:
            if len(row) < 3:
                continue

            name = row[0].strip()
            role_raw = row[1].strip()
            tasks_raw = row[2].strip()

            if not name or name.lower() == "organización":
                continue

            tasks = [
                t.strip().lstrip("•-\u2013").strip()
                for t in re.split(r"[•\n\-\u2013]", tasks_raw)
                if t.strip()
            ]

            organizations.append({
                "name": name,
                "role_raw": role_raw,
                "tasks": tasks,
            })

    return organizations


def _extract_gaps(tables: list, section_text: str) -> list[dict]:
    """Extrae brechas identificadas."""
    gaps: list[dict] = []

    for table in tables:
        if not table:
            continue

        header = " ".join(table[0]).lower()
        if "nos falta" not in header and "buscar aliado" not in header:
            continue

        for row in table[1:]:
            if len(row) < 3:
                continue

            nos_falta = row[0].strip()
            aliado_tipo = row[1].strip()
            estrategia = row[2].strip()

            if not nos_falta or "nos falta" in nos_falta.lower():
                continue

            gaps.append({
                "description": nos_falta,
                "ally_needed": aliado_tipo,
                "strategy": estrategia,
            })

    if not gaps and section_text:
        nos_falta_match = re.search(
            r"NOS\s+FALTA[.\s:]*(.*?)(?=BUSCAR\s+ALIADO|$)",
            section_text,
            re.IGNORECASE | re.DOTALL,
        )
        if nos_falta_match:
            gaps.append({
                "description": nos_falta_match.group(1).strip(),
                "ally_needed": "",
                "strategy": "",
            })

    return gaps


def _extract_financing(section_text: str) -> dict:
    """Extrae datos de financiamiento."""
    sources_raw: list[str] = []
    sources_match = re.search(
        r"Fuentes\s+Sugeridas[:\s]*(.*?)(?=Perfil|FASE|\n\n|$)",
        section_text,
        re.IGNORECASE | re.DOTALL,
    )
    if sources_match:
        raw = sources_match.group(1).strip()
        sources_raw = [s.strip() for s in re.split(r"[,;]", raw) if s.strip()]

    future_allies: list[str] = []
    future_match = re.search(
        r"Futuros\s+Aliados[:\s]*(.*?)(?=Nota|$)",
        section_text,
        re.IGNORECASE | re.DOTALL,
    )
    if future_match:
        raw = future_match.group(1).strip()
        future_allies = [s.strip() for s in re.split(r"[,;]", raw) if s.strip()]

    phases: list[dict[str, Any]] = []
    phase_matches = re.finditer(
        r"FASE\s+(\d+)[:\s]*([A-ZÁÉÍÓÚÑ\s]+)",
        section_text,
        re.IGNORECASE,
    )
    for match in phase_matches:
        phases.append({
            "phase": int(match.group(1)),
            "name": match.group(2).strip(),
        })

    return {
        "sources_suggested_raw": sources_raw,
        "future_allies_raw": future_allies,
        "phases_raw": phases,
    }


# ─────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────

def extract_from_bytes(file_bytes: bytes, filename: str) -> dict:
    """
    Extrae datos estructurados de un Plan Estratégico CAUSANTE.

    Args:
        file_bytes: Contenido del archivo .docx en bytes
        filename: Nombre del archivo (para metadata)

    Returns:
        dict con source_metadata y raw_extractions

    Raises:
        ValueError: Si el documento no tiene el formato de Plan Estratégico CAUSANTE
    """
    doc_data = _read_docx_bytes(file_bytes)

    # Validar contenido mínimo
    if not doc_data["full_text"].strip():
        raise ValueError(
            "El archivo está vacío o no contiene texto legible. "
            "Asegúrate de que el documento no esté protegido o corrupto."
        )

    sections = _split_sections(doc_data["full_text"])

    # Validar que el documento tenga estructura CAUSANTE
    if not sections:
        raise ValueError(
            "El archivo no parece ser un Plan Estratégico CAUSANTE. "
            "El documento debe incluir las secciones: PROPUESTA DE VALOR, "
            "CONCEPTO ESTRATÉGICO, EQUIPO Y ROLES, ANÁLISIS DE BRECHAS y "
            "ESTRATEGIA DE FINANCIAMIENTO. Por favor usa la plantilla oficial."
        )

    metadata = _extract_project_metadata(
        sections, doc_data["paragraphs"], doc_data["full_text"]
    )
    organizations = _extract_organizations(doc_data["tables"])
    gaps = _extract_gaps(doc_data["tables"], sections.get("brechas", ""))
    financing = _extract_financing(sections.get("financiamiento", ""))

    return {
        "source_metadata": metadata,
        "raw_extractions": {
            "team_and_partners": organizations,
            "financing_sources_raw": financing,
            "gaps_identified": gaps,
        },
    }
