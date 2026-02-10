# 🎯 Estrategia de Contenido: Verdes, Amarillas y Rojas

## Tu Pregunta Clave

> "¿Lo ideal es tener TODAS las respuestas a preguntas verdes/amarillas?  
> ¿Las rojas se dejan sin respuesta y se mandan directo al asesor?"

**Respuesta corta**:
- ✅ **Sistema ideal**: Sí, todas las ~400 preguntas verdes/amarillas con respuestas modelo
- ✅ **MVP esta semana**: No, con 15-20 bien hechas pruebas todo el flujo
- ⚠️ **Preguntas rojas**: NO necesitan respuesta detallada, pero SÍ necesitan manejo especial

---

## 📊 Los 3 Tipos de Preguntas y Su Manejo

### 🟢 PREGUNTAS VERDES (Autoservicio)

**Características**:
- Respuesta estándar clara
- Procedimientos establecidos
- Bajo riesgo legal
- Usuario puede resolverlo solo

**Ejemplos**:
- "¿Cómo obtener el RUC?"
- "¿Cuántos socios mínimos necesito?"
- "¿Dónde descargar formularios de SUNARP?"

**Qué necesitas crear**:
✅ **Respuesta modelo completa** (como las que ya hiciste)
- Paso a paso
- Costos y tiempos
- Enlaces a recursos
- Normativa aplicable

**Flujo en el RAG**:
```
Usuario: "¿Cómo obtener RUC?"
    ↓
Clasificador: Verde + Intención: Formalización
    ↓
RAG recupera: respuesta_ruc.md + Arts. Código Tributario
    ↓
LLM genera: Respuesta completa paso a paso
    ↓
Usuario: Resuelve solo ✅
```

---

### 🟡 PREGUNTAS AMARILLAS (Asesoría Recomendada)

**Características**:
- Respuesta compleja pero documentable
- Requiere análisis de contexto
- Riesgo medio si se hace mal
- Usuario puede intentarlo con guía

**Ejemplos**:
- "¿Qué retenciones aplicar a servicios profesionales?"
- "¿Cómo manejar ingresos afectos y exonerados juntos?"
- "¿Puedo contratar extranjeros como voluntarios?"

**Qué necesitas crear**:
✅ **Respuesta modelo con advertencias**
- Explicación del tema
- Pasos generales
- ⚠️ **Alertas de cuándo consultar abogado**
- Casos especiales que requieren asesoría

**Flujo en el RAG**:
```
Usuario: "¿Qué retención aplico a honorarios?"
    ↓
Clasificador: Amarillo + Intención: Tributación
    ↓
RAG recupera: retenciones.md + Ley IR Art. 71
    ↓
LLM genera: 
  - Respuesta general (8% en caso estándar)
  - ⚠️ "Si el monto supera X, consulta abogado"
  - ⚠️ "Si es extranjero, hay reglas especiales"
    ↓
Usuario: Decide si continúa solo o consulta 🤔
```

**Ejemplo de respuesta amarilla**:
```markdown
# ¿Qué retención aplico a recibos por honorarios?

## Respuesta

En el caso **estándar**, la retención es del **8%** sobre el monto bruto.

### Cálculo Simple
- Recibo por honorarios: S/. 1,000
- Retención (8%): S/. 80
- Neto a pagar: S/. 920

---

## ⚠️ Consulta a un Abogado Si:

- El proveedor es **extranjero no domiciliado** (retención puede ser 30%)
- El monto anual supera **S/. 50,000** (requiere análisis tributario)
- El servicio incluye **cesión de derechos** (puede tener tratamiento especial)
- Tienes **múltiples contratos** con la misma persona (puede reclasificarse como planilla)

---

## Normativa
- Ley IR Art. 71
```

---

### 🔴 PREGUNTAS ROJAS (Derivación Obligatoria)

**Características**:
- Requiere análisis legal específico
- Alto riesgo si se hace mal
- Puede tener consecuencias legales graves
- Contexto único de cada caso

**Ejemplos**:
- "Recibí notificación de fiscalización de SUNAT"
- "Un trabajador demandó por despido arbitrario"
- "Tenemos conflicto con un donante internacional"
- "Descubrimos fraude interno en la organización"

**Qué necesitas crear**:
❌ **NO necesitas respuesta detallada**
✅ **SÍ necesitas**:
1. Plantilla de respuesta estándar
2. Sistema de recopilación de contexto
3. Formulario para derivar al abogado

**Flujo en el RAG**:
```
Usuario: "Recibí notificación de SUNAT por fiscalización"
    ↓
Clasificador: ROJO + Intención: Tributación
    ↓
RAG NO recupera respuesta detallada
    ↓
LLM genera con prompt especial ROJO:
  - "Este caso requiere asesoría legal urgente"
  - "Tienes [X días] para responder"
  - Recopila contexto: ¿Qué tipo de notificación? ¿Qué periodo?
    ↓
Sistema deriva a abogado con contexto 🚨
```

---

## 📝 Respuestas Modelo para Preguntas Rojas

### Opción 1: Sin Respuesta Detallada (RECOMENDADO para MVP)

**Archivo**: `knowledge_base/intenciones/10_casos_grises/template_derivacion.md`

```markdown
# [Pregunta Roja]

## ⚠️ Este Caso Requiere Asesoría Legal Urgente

Esta situación tiene **alto riesgo legal** y requiere análisis específico de un abogado especializado.

### ¿Por qué no podemos dar una respuesta estándar?

- Cada caso tiene particularidades únicas
- Las consecuencias de un error pueden ser graves
- Requiere revisión de documentos específicos
- Puede haber plazos legales que cumplir

### Próximos Pasos

1. **Recopila la siguiente información**:
   - [Lista específica según el tipo de caso]
   - Documentos relacionados
   - Fechas importantes
   - Comunicaciones previas

2. **Contacta a un abogado especializado**:
   - Tributario: [contacto]
   - Laboral: [contacto]
   - Civil: [contacto]

3. **Urgencia**: 
   - Si tienes un plazo legal: Contacta HOY
   - Si no hay plazo: Contacta dentro de 48 horas

---

## ⏰ ¿Tienes un Plazo para Responder?

Si la notificación o situación tiene un **plazo legal**, actúa INMEDIATAMENTE.
No esperes. Los plazos en derecho son fatales.

---

## 💼 Mientras Tanto

- NO tomes decisiones sin asesoría
- NO respondas oficialmente sin revisión legal
- SÍ recopila todos los documentos relacionados
- SÍ anota una cronología de los hechos
```

---

### Opción 2: Contexto + Checklist (MEJOR para Sistema Final)

```markdown
# Recibí Notificación de Fiscalización de SUNAT

## 🚨 Derivación Inmediata a Abogado Tributario

### Contexto General

Una fiscalización de SUNAT es un procedimiento formal donde la autoridad tributaria revisa si cumpliste correctamente tus obligaciones.

**Riesgos**:
- Multas significativas (hasta 100% del tributo omitido)
- Cierre temporal de actividades
- Responsabilidad solidaria de directivos

**Por esto requieres abogado**: Los plazos son fatales y las respuestas inadecuadas agravan la situación.

---

## 📋 Información a Recopilar AHORA

Antes de contactar al abogado, reúne:

### Documentos de la Notificación
- [ ] Carta de presentación del fiscalizador
- [ ] Requerimiento de información
- [ ] Actas de inicio de fiscalización
- [ ] **Fecha de notificación** (importante para calcular plazos)

### Documentación de Tu Organización
- [ ] RUC y ficha RUC actualizada
- [ ] Declaraciones mensuales/anuales del periodo fiscalizado
- [ ] Comprobantes de pago (facturas, recibos)
- [ ] Contratos relevantes
- [ ] Estatuto y partida registral

### Información Contextual
- [ ] ¿Qué periodo están fiscalizando? (mes/año)
- [ ] ¿Qué tributo? (IR, IGV, retenciones)
- [ ] ¿Cuántos días tienes para responder?
- [ ] ¿Ya tuviste alguna comunicación previa con SUNAT?

---

## ⏰ Plazo Crítico

Usualmente tienes **3-7 días hábiles** para presentar la documentación requerida.

**Acción inmediata**: Contacta abogado HOY, no mañana.

---

## 🔗 Derivación

[Formulario automático para enviar al abogado con el contexto recopilado]

**Abogados Tributarios Recomendados**:
- Estudio A: [contacto] - Especializado en fiscalizaciones ONGs
- Estudio B: [contacto] - Experiencia con SUNAT

---

## ❌ Qué NO Hacer

- ❌ Ignorar la notificación
- ❌ Responder sin asesoría
- ❌ Presentar documentos incompletos
- ❌ Discutir con el fiscalizador sin preparación

## ✅ Qué SÍ Hacer

- ✅ Atender al fiscalizador cortésmente
- ✅ Pedir prórroga si necesitas tiempo (a través de abogado)
- ✅ Llevar registro de todas las comunicaciones
- ✅ Guardar copias de todo lo que entregues
```

---

## 🎯 Estrategia de Contenido por Etapa

### MVP (Esta Semana) - Mínimo Funcional

**Verdes**: 8-10 respuestas modelo completas
**Amarillas**: 5-7 respuestas modelo con advertencias
**Rojas**: 1 template genérico de derivación

**Total**: ~15 archivos

---

### Sistema V1 (1-2 Meses) - Producción Básica

**Verdes**: 50-80 respuestas modelo (~20% del entregable)
**Amarillas**: 30-50 respuestas modelo
**Rojas**: 5-10 templates específicos por tipo de caso

**Total**: ~90-140 archivos

---

### Sistema Final (3-6 Meses) - Cobertura Completa

**Verdes**: ~250 respuestas modelo (todas las verdes del entregable)
**Amarillas**: ~150 respuestas modelo (todas las amarillas)
**Rojas**: 20+ templates + sistema de derivación automática

**Total**: ~420 archivos + sistema de gestión de casos

---

## 💡 Priorización Inteligente

### ¿Cuáles respuestas crear primero?

**Método 1: Por Frecuencia**
Usa las estadísticas del entregable de Miguel Alor:
- Preguntas que se repiten más → Prioridad alta
- Preguntas que aparecen en múltiples secciones → Prioridad alta

**Método 2: Por Dependencia**
- Preguntas que otras preguntas referencian → Primero
- Ejemplo: "¿Qué es una asociación?" se menciona en 10 otras preguntas → Crear primero

**Método 3: Por Impacto**
- Procedimientos completos (constitución, obtención RUC) → Prioridad alta
- Preguntas muy específicas (formato de un formulario) → Prioridad baja

---

## 📊 Resumen de Tu Pregunta

| Aspecto | MVP (Semana 1) | Sistema Final |
|---------|----------------|---------------|
| **Respuestas Verdes** | 8-10 | ~250 (todas) |
| **Respuestas Amarillas** | 5-7 | ~150 (todas) |
| **Respuestas Rojas** | 1 template | 20+ templates |
| **¿Necesitas todas ahora?** | ❌ NO | ✅ Sí eventualmente |
| **Suficiente para probar RAG** | ✅ SÍ | ✅ SÍ |

---

## 🚀 Recomendación Final

**Para esta semana (MVP)**:
1. Crea **10 verdes + 5 amarillas** = 15 respuestas
2. Crea **1 template rojo** genérico
3. Enfócate en **2 intenciones** (Formalización + Tributación)
4. **Luego** agrega el resto incrementalmente

**No necesitas las 400 respuestas para que el RAG funcione.**

Con 15-20 respuestas bien hechas + 3 PDFs procesados, ya tienes un sistema funcional que demuestra todo el valor.

**Después del MVP**:
- Agrega 5-10 respuestas por semana
- En 2-3 meses tendrás cobertura completa
- El sistema sigue funcionando mientras tanto

---

**¿Te queda claro? ¿Seguimos con el plan de crear 15-17 respuestas esta semana o prefieres ir por la cobertura completa desde el inicio?**
