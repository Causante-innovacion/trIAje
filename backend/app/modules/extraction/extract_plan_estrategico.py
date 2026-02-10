#!/usr/bin/env python3
"""
extract_plan_estrategico.py
───────────────────────────────
Extrae datos estructurados de un Plan Estratégico CAUSANTE (.docx)
y genera un JSON con la información extraída.

Se han eliminado las inferencias automáticas y la estructura de formulario
ya que esta última se maneja en el frontend/backend de la aplicación.
"""

import json
import re
from pathlib import Path
from typing import BinaryIO, Union
from docx import Document


# ─────────────────────────────────────────────
# 1. LECTURA DEL DOCUMENTO
# ─────────────────────────────────────────────

def read_docx(file_input: Union[str, BinaryIO]) -> dict:
    """Lee el .docx y devuelve texto por secciones + tablas crudas."""
    doc = Document(file_input)

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
# 2. SEGMENTACIÓN POR SECCIONES
# ─────────────────────────────────────────────

SECTION_PATTERNS = {
    "pitch":           r"(?:1\.?\s*)?PROPUESTA\s+DE\s+VALOR",
    "concepto":        r"(?:2\.?\s*)?CONCEPTO\s+ESTRAT[ÉE]GICO",
    "equipo":          r"(?:3\.?\s*)?EQUIPO\s+Y\s+ROLES",
    "brechas":         r"(?:4\.?\s*)?AN[ÁA]LISIS\s+DE\s+BRECHAS",
    "financiamiento":  r"(?:5\.?\s*)?ESTRATEGIA\s+DE\s+FINANCIAMIENTO",
    "referencias":     r"(?:6\.?\s*)?CASOS\s+DE\s+REFERENCIA",
}


def split_sections(full_text: str) -> dict:
    """Divide el texto completo en secciones usando los encabezados."""
    positions = {}
    for key, pattern in SECTION_PATTERNS.items():
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            positions[key] = match.start()

    # Ordenar por posición
    ordered = sorted(positions.items(), key=lambda x: x[1])

    sections = {}
    for i, (key, start) in enumerate(ordered):
        end = ordered[i + 1][1] if i + 1 < len(ordered) else len(full_text)
        sections[key] = full_text[start:end].strip()

    return sections


# ─────────────────────────────────────────────
# 3. EXTRACCIÓN DE DATOS CRUDOS (Sin inferencias)
# ─────────────────────────────────────────────

def extract_project_metadata(sections: dict, paragraphs: list, full_text: str) -> dict:
    """Extrae metadatos básicos del proyecto (nombre, descripción, problema, solución)."""
    # Nombre del proyecto: usualmente el segundo párrafo
    name = paragraphs[1] if len(paragraphs) > 1 else "Sin nombre"

    # Descripción: texto entre comillas en la sección Pitch
    pitch_text = sections.get("pitch", "")
    description = ""
    desc_match = re.search(r'"(.*?)"', pitch_text, re.DOTALL)
    if desc_match:
        description = desc_match.group(1).strip()

    # Problema y solución
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

    # Dependencia externa (Dato numérico explícito)
    dep_match = re.search(r"Dep\.?\s*Externa[:\s]*(\d+)%", full_text, re.IGNORECASE)
    ext_dep = int(dep_match.group(1)) if dep_match else None

    return {
        "name": name,
        "description": description,
        "problem": problema,
        "solution": solucion,
        "external_dependency_pct": ext_dep,
    }


def extract_organizations_raw(tables: list) -> list:
    """Extrae lista de organizaciones/personas del equipo sin inferir roles ni perfiles."""
    organizations = []

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
                t.strip().lstrip("•-–").strip()
                for t in re.split(r"[•\n\-–]", tasks_raw)
                if t.strip()
            ]

            organizations.append({
                "name": name,
                "role_raw": role_raw,
                "tasks": tasks
            })

    return organizations


def extract_gaps_raw(tables: list, section_text: str) -> list:
    """Extrae brechas explícitas."""
    gaps = []

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
                "ally_needed": "Extraer manualmente",
                "strategy": "Extraer manualmente",
            })

    return gaps


def extract_financing_raw(section_text: str) -> dict:
    """Extrae datos crudos de financiamiento."""
    sources_raw = []
    sources_match = re.search(
        r"Fuentes\s+Sugeridas[:\s]*(.*?)(?=Perfil|FASE|\n\n|$)",
        section_text,
        re.IGNORECASE | re.DOTALL,
    )
    if sources_match:
        raw = sources_match.group(1).strip()
        sources_raw = [s.strip() for s in re.split(r"[,;]", raw) if s.strip()]

    future_allies = []
    future_match = re.search(
        r"Futuros\s+Aliados[:\s]*(.*?)(?=Nota|$)",
        section_text,
        re.IGNORECASE | re.DOTALL,
    )
    if future_match:
        raw = future_match.group(1).strip()
        future_allies = [s.strip() for s in re.split(r"[,;]", raw) if s.strip()]

    # Fases
    phases = []
    phase_matches = re.finditer(
        r"FASE\s+(\d+)[:\s]*([A-ZÁÉÍÓÚÑ\s]+)",
        section_text,
        re.IGNORECASE,
    )
    for match in phase_matches:
        phases.append({
            "phase": int(match.group(1)),
            "name": match.group(2).strip()
        })

    return {
        "sources_suggested_raw": sources_raw,
        "future_allies_raw": future_allies,
        "phases_raw": phases
    }


# ─────────────────────────────────────────────
# 4. ORQUESTADOR PRINCIPAL
# ─────────────────────────────────────────────

def extract_plan(file_input: Union[str, BinaryIO], filename: str = "document.docx") -> dict:
    """Función principal: extrae datos crudos."""

    doc_data = read_docx(file_input)
    sections = split_sections(doc_data["full_text"])

    project_metadata = extract_project_metadata(sections, doc_data["paragraphs"], doc_data["full_text"])
    organizations_raw = extract_organizations_raw(doc_data["tables"])
    gaps_raw = extract_gaps_raw(doc_data["tables"], sections.get("brechas", ""))
    financing_raw = extract_financing_raw(sections.get("financiamiento", ""))

    # Construir JSON final (solo datos extraídos)
    result = {
        "source_metadata": {
            "project_name": project_metadata["name"],
            "description": project_metadata["description"],
            "problem_summary": project_metadata["problem"],
            "solution_summary": project_metadata["solution"],
            "external_dependency": project_metadata["external_dependency_pct"],
        },
        "raw_extractions": {
            "team_and_partners": organizations_raw,
            "financing_sources_raw": financing_raw,
            "gaps_identified": gaps_raw,
        },
        "_metadata": {
            "source_file": filename,
            "sections_found": list(sections.keys()),
            "num_organizations": len(organizations_raw),
        },
    }

    return result


# ─────────────────────────────────────────────
# CLI (para pruebas locales)
# ─────────────────────────────────────────────

def main():
    import sys
    
    if len(sys.argv) < 2:
        # Default: buscar en uploads o usar path hardcodeado para pruebas
        docx_path = r"C:\Users\Salva\Desktop\Prep Pasantia\PRUEBAS\CAUSANTE_Plan_Memoria_Viva__E.docx"
    else:
        docx_path = sys.argv[1]

    if not Path(docx_path).exists():
        print(f"❌ Archivo no encontrado: {docx_path}")
        sys.exit(1)

    result = extract_plan(docx_path, Path(docx_path).name)

    # Guardar JSON
    output_path = Path(docx_path).stem + "_extracted_data.json"
    output_full = Path(docx_path).parent / output_path

    with open(output_full, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ JSON generado: {output_full}")
    print(f"   Datos crudos extraídos correctamente.")

    # Imprimir JSON (Primeros 2000 caracteres para verificación rápida)
    print("\n" + "=" * 60)
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    print(json_str[:2000] + "\n... (truncated)")


if __name__ == "__main__":
    main()
