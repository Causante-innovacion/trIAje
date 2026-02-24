import { ProjectEvaluation } from '../../types/evaluation.types'

const STATUS_LABEL: Record<string, string> = {
    green: '✅ CONFORME',
    yellow: '⚠️ PENDIENTE',
    red: '🔴 CRÍTICO',
}

/**
 * Genera y descarga un documento .docx con la evaluación legal del proyecto.
 * Sigue el mismo patrón de import dinámico de Results.tsx.
 */
export async function exportEvaluationToDocx(data: ProjectEvaluation): Promise<void> {
    const {
        Document,
        Packer,
        Paragraph,
        TextRun,
        HeadingLevel,
        Table,
        TableRow,
        TableCell,
        WidthType,
        AlignmentType,
        BorderStyle,
    } = await import('docx')
    const { saveAs } = await import('file-saver')

    // ─── Brand colours ─────────────────────────────────────────────────────────
    const GOLD = 'B3994C'       // causante-ocre
    const BLACK = '111111'
    const MID_GRAY = '888888'

    // ─── Helpers ──────────────────────────────────────────────────────────────

    const headerCell = (text: string) =>
        new TableCell({
            children: [
                new Paragraph({
                    children: [new TextRun({ text, bold: true, color: 'FFFFFF', size: 20, font: 'Calibri' })],
                }),
            ],
            shading: { fill: BLACK },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
        })

    const cell = (text: string, color?: string) =>
        new TableCell({
            children: [
                new Paragraph({
                    children: [new TextRun({ text, size: 20, color: color ?? '333333', font: 'Calibri' })],
                }),
            ],
            margins: { top: 60, bottom: 60, left: 120, right: 120 },
        })

    const spacer = () => new Paragraph({ text: '' })

    const sectionHeading = (text: string, level = HeadingLevel.HEADING_2) =>
        new Paragraph({
            children: [
                new TextRun({ text, bold: true, size: 28, color: GOLD, font: 'Calibri' }),
            ],
            heading: level,
            spacing: { before: 300, after: 120 },
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: GOLD } },
        })

    // ─── 1. ENCABEZADO ────────────────────────────────────────────────────────

    const headerSection = [
        // Gold bar
        new Paragraph({
            children: [
                new TextRun({ text: '\u00A0', size: 8 }),
            ],
            shading: { fill: GOLD },
            spacing: { after: 0 },
        }),
        spacer(),
        new Paragraph({
            children: [
                new TextRun({
                    text: 'EVALUACIÓN LEGAL DE PROYECTO',
                    bold: true,
                    size: 44,
                    color: BLACK,
                    font: 'Calibri',
                }),
            ],
            alignment: AlignmentType.LEFT,
            spacing: { after: 80 },
        }),
        new Paragraph({
            children: [
                new TextRun({
                    text: data.projectTitle,
                    bold: true,
                    size: 34,
                    color: GOLD,
                    font: 'Calibri',
                }),
            ],
            alignment: AlignmentType.LEFT,
            spacing: { after: 80 },
        }),
        new Paragraph({
            children: [
                new TextRun({ text: `ID: ${data.projectId}  ·  Líder: ${data.projectLeader}`, size: 20, color: MID_GRAY, font: 'Calibri' }),
            ],
            alignment: AlignmentType.LEFT,
            spacing: { after: 400 },
        }),
    ]

    // ─── 2. DIAGNÓSTICO POR ORGANIZACIÓN ──────────────────────────────────────

    const orgRows = [
        new TableRow({
            children: [
                headerCell('ORGANIZACIÓN'),
                headerCell('ESTADO'),
                headerCell('SITUACIÓN'),
            ],
        }),
        ...data.organizations.map(
            org =>
                new TableRow({
                    children: [
                        cell(org.name),
                        cell(STATUS_LABEL[org.status] ?? org.status),
                        cell(org.message),
                    ],
                }),
        ),
    ]

    const orgSection = [
        sectionHeading('1. Diagnóstico por Organización'),
        new Table({
            rows: orgRows,
            width: { size: 100, type: WidthType.PERCENTAGE },
            borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
                left: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
                right: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
            },
        }),
        spacer(),
    ]

    // ─── 3. ESTADO LEGAL ACTUAL ───────────────────────────────────────────────

    const PRIORITY_COLOR: Record<string, string> = {
        'CRÍTICA': 'DC2626',
        'ALTA': 'D97706',
        'BAJA': '059669',
    }

    const legalRows = [
        new TableRow({
            children: [
                headerCell('ENTIDAD'),
                headerCell('ESTADO'),
                headerCell('PRIORIDAD'),
                headerCell('ACCIÓN RECOMENDADA'),
            ],
        }),
        ...data.legalEntities.map(
            entity =>
                new TableRow({
                    children: [
                        cell(entity.entity),
                        cell(`${STATUS_LABEL[entity.status] ?? entity.status}  ${entity.statusText}`),
                        cell(entity.priority, PRIORITY_COLOR[entity.priority]),
                        cell(entity.action),
                    ],
                }),
        ),
    ]

    const legalSection = [
        sectionHeading('2. Estado Legal Actual'),
        new Table({
            rows: legalRows,
            width: { size: 100, type: WidthType.PERCENTAGE },
            borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
                left: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
                right: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
            },
        }),
        spacer(),
    ]

    // ─── 4. PASOS A SEGUIR (solo si hay actionSteps) ─────────────────────────

    const actionSection =
        data.actionSteps && data.actionSteps.length > 0
            ? [
                  sectionHeading('3. Pasos a Seguir'),
                  ...data.actionSteps.map(
                      (step, i) =>
                          new Paragraph({
                              children: [
                                  new TextRun({ text: `${i + 1}. `, bold: true }),
                                  new TextRun({ text: step, size: 22 }),
                              ],
                              spacing: { after: 80 },
                          }),
                  ),
                  spacer(),
              ]
            : []

    // ─── 5. CONDICIONES DE VIABILIDAD (CRÍTICA y ALTA) ───────────────────────

    const criticalConditions = data.viabilityConditions.filter(
        c => c.severity === 'CRÍTICA' || c.severity === 'ALTA',
    )

    const viabilitySection =
        criticalConditions.length > 0
            ? [
                  sectionHeading('4. Condiciones de Viabilidad (Plan de Acción)'),
                  ...criticalConditions.flatMap(condition => [
                      new Paragraph({
                          children: [
                              new TextRun({ text: condition.title, bold: true, size: 24 }),
                              new TextRun({
                                  text: `  [${condition.severity}]`,
                                  bold: true,
                                  color: condition.severity === 'CRÍTICA' ? 'DC2626' : 'D97706',
                                  size: 20,
                              }),
                          ],
                          spacing: { before: 160, after: 60 },
                      }),
                      new Paragraph({
                          children: [new TextRun({ text: condition.reason, size: 20, color: '555555' })],
                          spacing: { after: 60 },
                      }),
                      ...(condition.requirements.length > 0
                          ? condition.requirements.map(
                                req =>
                                    new Paragraph({
                                        children: [new TextRun({ text: `• ${req}`, size: 20 })],
                                        spacing: { after: 40 },
                                    }),
                            )
                          : []),
                      spacer(),
                  ]),
              ]
            : []

    // ─── 6. RUTA DE IMPLEMENTACIÓN ────────────────────────────────────────────

    const PHASE_STATUS: Record<string, string> = {
        completed: '✅',
        current: '▶️',
        upcoming: '⏳',
    }

    const implementationSection = [
        sectionHeading('5. Ruta de Implementación'),
        // Phases row
        new Paragraph({
            children: data.implementationPhases.map(
                phase =>
                    new TextRun({
                        text: `${PHASE_STATUS[phase.status] ?? ''} ${phase.name}    `,
                        bold: phase.status === 'current',
                        size: 22,
                        color: phase.status === 'current' ? 'B45309' : '555555',
                    }),
            ),
            spacing: { after: 160 },
        }),
        // Actions
        ...data.implementationActions.map(
            action =>
                new Paragraph({
                    children: [
                        new TextRun({ text: action.completed ? '☑ ' : '☐ ', size: 20 }),
                        new TextRun({ text: action.text, size: 20 }),
                    ],
                    spacing: { after: 60 },
                }),
        ),
        spacer(),
    ]

    // ─── 7. ALTERNATIVAS ──────────────────────────────────────────────────────

    const alternativesSection =
        data.alternatives.length > 0
            ? [
                  sectionHeading('6. Alternativas'),
                  ...data.alternatives.flatMap(alt => [
                      new Paragraph({
                          children: [new TextRun({ text: alt.title, bold: true, size: 22 })],
                          spacing: { after: 60 },
                      }),
                      new Paragraph({
                          children: [new TextRun({ text: alt.description, size: 20, color: '555555' })],
                          spacing: { after: 120 },
                      }),
                  ]),
                  spacer(),
              ]
            : []

    // ─── 8. AVISO LEGAL ───────────────────────────────────────────────────────

    const disclaimerSection = [
        sectionHeading('Aviso Legal'),
        new Paragraph({
            children: [
                new TextRun({
                    text: data.disclaimer,
                    italics: true,
                    size: 18,
                    color: MID_GRAY,
                    font: 'Calibri',
                }),
            ],
        }),
    ]

    // ─── CONSTRUIR DOCUMENTO ──────────────────────────────────────────────────

    const doc = new Document({
        styles: {
            default: {
                heading1: {
                    run: { font: 'Calibri', size: 44, bold: true, color: BLACK },
                    paragraph: { spacing: { after: 200 } },
                },
                heading2: {
                    run: { font: 'Calibri', size: 28, bold: true, color: GOLD },
                    paragraph: { spacing: { before: 300, after: 120 } },
                },
                document: {
                    run: { font: 'Calibri', size: 22, color: '222222' },
                },
            },
        },
        sections: [
            {
                properties: {},
                children: [
                    ...headerSection,
                    ...orgSection,
                    ...legalSection,
                    ...actionSection,
                    ...viabilitySection,
                    ...implementationSection,
                    ...alternativesSection,
                    ...disclaimerSection,
                ],
            },
        ],
    })

    const blob = await Packer.toBlob(doc)

    const titleSlug = data.projectTitle
        .replace(/\s+/g, '_')
        .replace(/[^a-zA-Z0-9_]/g, '')
        .substring(0, 40)

    saveAs(blob, `Evaluacion_Legal_${titleSlug || 'Proyecto'}.docx`)
}
