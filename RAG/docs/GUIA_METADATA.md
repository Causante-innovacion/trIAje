# 📋 Cómo Crear Metadata para PDFs - Paso a Paso

## ¿Qué es la Metadata?

La **metadata** es información SOBRE el documento legal que ayuda al RAG a:
1. Entender qué contiene el PDF sin leerlo completo
2. Mapear artículos específicos a preguntas frecuentes
3. Clasificar por intención y nivel de riesgo
4. Relacionar con campos de la Ficha Legal Mínima

---

## 🎯 Ejemplo Completo: Ley del Impuesto a la Renta

### Paso 1: Revisar el PDF Rápidamente (30 min)

**Objetivo**: Entender la estructura del documento

#### Preguntas a responder:
- ¿Cuántos artículos tiene?
- ¿Qué artículos son relevantes para ONGs?
- ¿Qué temas cubre? (exoneraciones, retenciones, etc.)
- ¿Hay tablas o anexos importantes?

#### Para Ley IR:
```
✅ Documento: TUO Ley del Impuesto a la Renta
✅ Artículos totales: ~157
✅ Artículos clave para ONGs:
    - Art. 19: Ingresos inafectos (exoneraciones)
    - Art. 28: Rentas de tercera categoría
    - Art. 71: Retenciones
✅ Temas principales: Exoneraciones, tributación de ingresos, retenciones
```

---

### Paso 2: Identificar Artículos Clave (30 min)

**Objetivo**: ¿Qué artículos se citan en tus respuestas modelo?

#### Busca en tus respuestas modelo:

Abre las respuestas que ya creaste y busca menciones a esta ley:
```bash
# En Windows PowerShell
Select-String -Path "knowledge_base\intenciones\**\*.md" -Pattern "Impuesto.*Renta|Art.*19"
```

O manualmente revisa qué artículos mencionaste en tus respuestas de **Tributación**.

#### Ejemplo:
Si en tus respuestas mencionaste:
- "Según Art. 19 de la Ley IR, las asociaciones están exoneradas si..."
- "El Art. 71 establece retenciones del 8%..."

Entonces esos son tus **artículos clave**.

---

### Paso 3: Mapear a Intenciones (15 min)

**Objetivo**: ¿Qué intenciones usan este documento?

#### Para Ley IR:
```
✅ Intenciones aplicables:
    - tributacion (principal)
    - registro_donaciones (secundario)
    - cooperacion (menciona ingresos de donaciones)
```

**Cómo saber**: Revisa tus 10 intenciones y pregúntate si alguna pregunta de esa intención necesita citar esta ley.

---

### Paso 4: Clasificar Temas por Nivel de Riesgo (15 min)

**Objetivo**: Algunos temas del PDF son más complejos que otros

#### Para Ley IR:

**🟢 Verde (Autoservicio)**:
- Consultar si están exonerados
- Conocer qué ingresos están afectos/inafectos

**🟡 Amarillo (Asesoría recomendada)**:
- Calcular retenciones
- Declaración anual de IR
- Combinación de ingresos afectos + exonerados

**🔴 Rojo (Requiere abogado)**:
- Fiscalización de SUNAT
- Pérdida de exoneración
- Conflictos tributarios

---

### Paso 5: Llenar el Template JSON (30 min)

Ahora con toda esa información, llena el archivo JSON:

#### `knowledge_base/metadata/SUNAT_LIR_2023.json`

```json
{
  "doc_id": "SUNAT_LIR_2023",
  "titulo": "Texto Único Ordenado de la Ley del Impuesto a la Renta",
  "tipo": "norma",
  "categoria": "tributario",
  "subcategoria": "impuesto_renta",
  
  "intenciones_aplicables": [
    "tributacion",
    "registro_donaciones",
    "cooperacion"
  ],
  
  "nivel_riesgo_temas": {
    "exoneraciones_asociaciones": "verde",
    "declaracion_anual_ir": "amarillo",
    "retenciones_servicios": "amarillo",
    "perdida_exoneracion": "rojo",
    "fiscalizacion_sunat": "rojo"
  },
  
  "articulos_clave": [
    {
      "numero": "19",
      "descripcion": "Ingresos inafectos - Exoneraciones para asociaciones sin fines de lucro",
      "relevancia": "critica",
      "preguntas_frecuentes": [
        "¿Mi asociación está exonerada del Impuesto a la Renta?",
        "¿Podemos cobrar por talleres y seguir exonerados?",
        "¿Qué condiciones debo cumplir para mantener la exoneración?"
      ]
    },
    {
      "numero": "28",
      "descripcion": "Rentas de tercera categoría - Actividades empresariales",
      "relevancia": "alta",
      "preguntas_frecuentes": [
        "¿Qué ingresos se consideran renta de tercera categoría?",
        "¿Debo pagar IR si vendo productos?"
      ]
    },
    {
      "numero": "71",
      "descripcion": "Retenciones del Impuesto a la Renta",
      "relevancia": "alta",
      "preguntas_frecuentes": [
        "¿Qué retención aplica a recibos por honorarios?",
        "¿Debo retener IR cuando pago a proveedores?"
      ]
    },
    {
      "numero": "55",
      "descripcion": "Declaración anual de impuesto a la renta",
      "relevancia": "media"
    }
  ],
  
  "campos_ficha_legal": [
    "fuentes_ingreso",
    "estado_tributario",
    "info_contable",
    "personal"
  ],
  
  "keywords": [
    "impuesto a la renta",
    "exoneraciones",
    "asociaciones sin fines de lucro",
    "ingresos inafectos",
    "retenciones",
    "declaración anual",
    "tercera categoría",
    "SUNAT"
  ],
  
  "entidad": "SUNAT",
  "nivel_autoridad": "ley",
  
  "url_oficial": "https://www.sunat.gob.pe/legislacion/renta/ley/fdetalle.htm",
  "archivo_local": "knowledge_base/normas/tributario/ley_impuesto_renta.pdf",
  
  "vigencia_desde": "2004-01-01",
  "vigencia_hasta": null,
  "ultima_verificacion": "2026-02-04",
  
  "notas": "Especial atención al Art. 19 inciso b) para consultas sobre generación de ingresos por ONGs. Si la ONG combina actividades exoneradas y gravadas, derivar a amarillo. Si hay fiscalización activa, derivar a rojo.",
  
  "version": 1,
  "idioma": "es"
}
```

---

## 📝 Checklist para Cada Campo

### ✅ Campos Obligatorios Mínimos

- [ ] `doc_id`: Identificador único (mayúsculas, guiones bajos)
- [ ] `titulo`: Nombre completo oficial del documento
- [ ] `tipo`: norma | procedimiento | respuesta_modelo
- [ ] `categoria`: tributario | civil | laboral | cooperacion | propiedad_intelectual
- [ ] `intenciones_aplicables`: Array con las intenciones relevantes
- [ ] `archivo_local`: Ruta al PDF

### ✅ Campos Importantes (Recomendados)

- [ ] `nivel_riesgo_temas`: Objeto con temas y su color
- [ ] `articulos_clave`: Array con mínimo 3-5 artículos principales
- [ ] `keywords`: Lista de palabras clave para búsqueda
- [ ] `url_oficial`: Link a la fuente oficial
- [ ] `notas`: Guía para el RAG sobre cuándo usar este documento

### ✅ Campos Opcionales

- [ ] `subcategoria`: Clasificación más específica
- [ ] `campos_ficha_legal`: Qué preguntar al usuario
- [ ] `entidad`: Organismo emisor
- [ ] `vigencia_desde/hasta`: Fechas de vigencia

---

## 🎯 Atajos para Identificar Artículos Clave

### Método 1: Usa ChatGPT o Claude

```
Prompt:
"Dame los 5 artículos más importantes de la Ley del Impuesto a la Renta 
de Perú para asociaciones civiles sin fines de lucro. 
Para cada artículo indica:
- Número
- Descripción breve
- Por qué es relevante para ONGs"
```

### Método 2: Busca en el PDF

Palabras clave a buscar (Ctrl+F):
- "asociación"
- "sin fines de lucro"
- "inafecto"
- "exonerado"
- "donación"

Los artículos que contengan estas palabras probablemente sean clave.

### Método 3: Revisa Tus Respuestas Modelo

Los artículos que YA citaste en las respuestas que escribiste son automáticamente artículos clave.

---

## 🚀 Flujo Rápido (1.5 hrs por PDF)

### CÓDIGO CIVIL (90 min)

**1. Revisar** (20 min):
- Enfócate en Libro I, Título II (Asociaciones, Arts. 80-98)
- Son solo ~20 artículos

**2. Artículos clave** (20 min):
```json
articulos_clave: [
  {"numero": "80", "descripcion": "Definición de asociación"},
  {"numero": "82", "descripcion": "Número mínimo de asociados"},
  {"numero": "84", "descripcion": "Contenido del estatuto"},
  {"numero": "77", "descripcion": "Constitución e inscripción"}
]
```

**3. Llenar JSON** (50 min):
```json
{
  "doc_id": "CODIGO_CIVIL_2023",
  "intenciones_aplicables": ["formalizacion", "viabilidad"],
  "nivel_riesgo_temas": {
    "constitucion_asociacion": "verde",
    "modificacion_estatuto": "amarillo",
    "disolucion": "amarillo"
  }
}
```

---

### LEY IGV (90 min)

**1. Revisar** (20 min):
- Busca artículos sobre "servicios"
- Exoneraciones

**2. Artículos clave** (20 min):
```json
articulos_clave: [
  {"numero": "1", "descripcion": "Operaciones gravadas"},
  {"numero": "2", "descripcion": "Servicios gravados"},
  {"numero": "5", "descripcion": "Exoneraciones"}
]
```

**3. Llenar JSON** (50 min)

---

## 💡 Tips para Ahorrar Tiempo

### 1. Copia y Adapta
- Usa `TEMPLATE.json` como base
- Copia `SUNAT_LIR_2023.json` para otros docs de SUNAT
- Solo cambia lo específico

### 2. No Busques Perfección
- Con 3-5 artículos clave es suficiente para MVP
- Puedes agregar más después

### 3. Prioriza
- Si un campo opcional no lo sabes, déjalo en `null` o `[]`
- Los campos críticos son: `doc_id`, `titulo`, `intenciones_aplicables`, `articulos_clave`

---

## ✅ Resultado Final

Al terminar Día 3 deberías tener:

```
knowledge_base/metadata/
├── TEMPLATE.json                    (ya existe)
├── CODIGO_CIVIL_2023.json          ⬜ CREAR
├── SUNAT_LIR_2023.json              ⬜ CREAR
└── SUNAT_IGV_2023.json              ⬜ CREAR
```

Y los PDFs en:
```
knowledge_base/normas/
├── civil/
│   └── codigo_civil_libro_I.pdf     ⬜ DESCARGAR
└── tributario/
    ├── ley_impuesto_renta.pdf       ⬜ DESCARGAR
    └── ley_igv.pdf                  ⬜ DESCARGAR
```

---

## 🆘 Si Te Atascas

### "No encuentro el PDF"
- Googlea: `nombre_ley filetype:pdf site:.gob.pe`
- Si no hay PDF oficial, usa versiones de repositorios legales (LP Pasión por el Derecho)

### "No sé qué poner en 'articulos_clave'"
- Usa ChatGPT con el prompt de arriba
- O simplemente pon los 5 primeros artículos del documento

### "No sé qué intenciones aplican"
- Pregúntate: ¿Alguna pregunta de mis 10 intenciones necesita citar esta ley?
- En duda, pon solo la intención principal (ej: Código Civil → solo "formalizacion")

---

**¿Listo para empezar? ¿Quieres que te ayude a crear el primer metadata ahora?**
