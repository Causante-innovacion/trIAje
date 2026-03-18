# 🤝 Contratos de Datos y APIs

Este documento (mantenido por *The Scribe*) define exactamente cómo el Frontend debe comunicarse con el Backend (FastAPI). Nuestro objetivo es que no necesites leer el código Python para saber qué JSON enviar o qué esperar de vuelta.

La arquitectura de la API está basada en **REST** y todas las validaciones corren bajo **Pydantic v2**. 

*URL Base:* `http://localhost:8000/api/v1`

---

## 1. Módulo: Evaluación de Proyecto (El Semáforo)

El flujo de evaluación recibe los datos de una ONG y calcula riesgos, viabilidad, semáforos y requerimientos, devolviendo un análisis estructurado.

### A. Ejecutar Evaluación
**Endpoint:** `POST /evaluation/`
**Descripción:** Recibe un `NormalizedProjectIntake` (datos de la organización y el usuario) y retorna un análisis profundo cruzando reglas de negocio y RAG (si está habilitado).

#### Request Esperado (Ejemplo Simplificado)
```json
{
  "intake": {
    "organizations": [
      {
        "id": "org_1",
        "name": "Mi ONG",
        "type": "asociacion",
        "has_legal_entity": false,
        "is_active": true
      }
    ],
    "project_intentions": ["formalizacion", "tributacion"],
    "funding_source": "cooperacion_internacional"
  },
  "include_rag_justification": true,
  "max_rag_queries": 5
}
```

#### Response Esperado (Objeto Completo)
FastAPI devolverá el objeto `EvaluationResponse`. Elementos clave del JSON:

| Campo | Tipo | Valores Posibles (Enums) | Descripción |
| :--- | :--- | :--- | :--- |
| `viability` | String | `viable`, `viable_with_conditions`, `not_viable`, `requires_review` | Estado legal general. |
| `traffic_light` | String | `green`, `yellow`, `red` | Elemento visual para el UI. Verde=Bajo riesgo, Rojo=No viable. |
| `organizations` | Array | Lista de Objetos | Resultados detallados divididos por cada organización participante. |
| `risk_summary` | Objeto | Múltiples factores | Resumen agregado del riesgo, nivel y si requiere asesoría profesional urgente. |
| `next_steps` | Array | Strings | Acciones concretas a tomar por el usuario en orden de prioridad. |
| `evidence_sources` | Array | Lista de Objetos | Si RAG estaba encendido, aquí vienen los artículos legales (PDFs) usados para justificar la respuesta. |

---

## 2. Módulo: Ruta de Cumplimiento (Compliance)

Si una evaluación arroja un semáforo *amarillo* o *verde*, el usuario suele necesitar el "paso a paso". Este endpoint desgrana qué tiene que hacer.

### A. Generar Ruta
**Endpoint:** `POST /compliance/`

#### Request Esperado (`ComplianceRequest`)
```json
{
  "compliance_goal": "formalizar_asociacion",
  "current_status": "idea_inicial",
  "organization_type": "asociacion",
  "timeline": "3_meses"
}
```

#### Response Esperado (`ComplianceResponse`)
Devuelve un JSON con la matriz de progreso y los hitos (milestones) ordenados por fase.

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `progress_percentage` | Float | Porcentaje actual del cumplimiento total (ej. 0.0 a 1.0). |
| `phases` | Array | Lista de las fases a ejecutar (Ej. 1. Estatutos, 2. Notaría). |
| `next_milestones` | Array | Los "Milestones" desbloqueados (pasos concretos que puede hacer ahora). |
| `blocked_milestones` | Array | Pasos que aún dependen de requisitos previos. |

**Estructura de un `Milestone`:**
```json
{
  "id": "redaccion_estatutos",
  "name": "Redactar Estatutos de Asociación",
  "status": "pending",
  "documents_required": ["minuta_base.pdf"],
  "estimated_duration": "1_semana",
  "prerequisites": []
}
```

---

## 💡 Notas para Desarrolladores (Frontend)

1. **Tipado Automático:** Si estás usando TypeScript (que es lo ideal por el stack actual), considera usar herramientas como `Orval` u `OpenAPI-TS` apuntando a `http://localhost:8000/openapi.json` para auto-generar los tipos TS desde estos esquemas de Pydantic. ¡Cero esfuerzo manual!
2. **Errores de Validación (422):** Si envías un JSON mal formado (ej. faltan campos de `intake`), FastAPI no ejecutará lógica; retornará inmediatamente un `422 Unprocessable Entity` diciendo qué campo exacto falló.
