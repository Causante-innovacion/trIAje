import { LegalAdviserPackage } from '../../types/adviser.types'

const STATUS_LABEL: Record<string, string> = {
    green: '✅ CONFORME',
    yellow: '⚠️ PENDIENTE',
    red: '🔴 CRÍTICO',
}

const STAGE_LABEL: Record<string, string> = {
    prototipo: 'Prototipo',
    piloto: 'Piloto',
    escalamiento: 'Escalamiento',
    unknown: 'Por definir',
}

/**
 * Genera y descarga un .docx con el paquete de preparación para reunión con asesor legal.
 */
export async function exportAdviserToDocx(data: LegalAdviserPackage): Promise<void> {
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
    const GOLD = 'B3994C'
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
        new Paragraph({
            children: [new TextRun({ text: '\u00A0', size: 8 })],
            shading: { fill: GOLD },
            spacing: { after: 0 },
        }),
        spacer(),
        new Paragraph({
            children: [
                new TextRun({
                    text: 'PAQUETE DE PREPARACIÓN',
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
                    text: 'Reunión con Asesor Legal',
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
                new TextRun({
                    text: data.organizationProfile.entityName,
                    size: 22,
                    color: MID_GRAY,
                    font: 'Calibri',
                }),
            ],
            spacing: { after: 400 },
        }),
    ]

    // ─── 2. PERFIL DE LA ORGANIZACIÓN ─────────────────────────────────────────

    const profile = data.organizationProfile
    const profileRows = [
        new TableRow({
            children: [
                headerCell('CAMPO'),
                headerCell('VALOR'),
            ],
        }),
        new TableRow({
            children: [
                cell('Organización'),
                cell(profile.entityName),
            ],
        }),
        new TableRow({
            children: [
                cell('Estado legal'),
                cell(STATUS_LABEL[profile.legalStatus] ?? profile.legalStatus),
            ],
        }),
        new TableRow({
            children: [
                cell('Etapa'),
                cell(STAGE_LABEL[profile.stage] ?? profile.stage),
            ],
        }),
        new TableRow({
            children: [
                cell('Tipo de financiamiento'),
                cell(profile.fundingTypes.join(', ')),
            ],
        }),
        ...(data.fundingCritical ? [
            new TableRow({
                children: [
                    cell('Rango de fondos necesarios'),
                    cell(`${data.fundingCritical.min} – ${data.fundingCritical.max}`),
                ],
            }),
        ] : []),
        ...(data.incomeSources && data.incomeSources.length > 0 ? [
            new TableRow({
                children: [
                    cell('Fuentes de ingresos'),
                    cell(data.incomeSources.join(', ')),
                ],
            }),
        ] : []),
    ]

    const profileSection = [
        sectionHeading('1. Perfil de la Organización'),
        new Table({
            rows: profileRows,
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

    // ─── 3. REGISTRO LEGAL ────────────────────────────────────────────────────

    const legalRows = [
        new TableRow({
            children: [
                headerCell('ENTIDAD'),
                headerCell('ESTADO'),
            ],
        }),
        ...data.legalStatusCards.map(card =>
            new TableRow({
                children: [
                    cell(card.label),
                    cell(STATUS_LABEL[card.status] ?? card.status),
                ],
            }),
        ),
    ]

    const legalSection = [
        sectionHeading('2. Estado de Registros Legales'),
        new Table({
            rows: legalRows,
            width: { size: 60, type: WidthType.PERCENTAGE },
            borders: {
                top: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
                bottom: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
                left: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
                right: { style: BorderStyle.SINGLE, size: 1, color: 'DDDDDD' },
            },
        }),
        spacer(),
    ]

    // ─── 4. TEMAS CRÍTICOS ────────────────────────────────────────────────────

    const criticalSection = [
        sectionHeading('3. Temas Críticos a Tratar'),
        ...data.criticalTopics.flatMap((topic, i) => [
            new Paragraph({
                children: [
                    new TextRun({ text: `${i + 1}. ${topic.title}`, bold: true, size: 24, font: 'Calibri' }),
                    new TextRun({ text: `  [${topic.priority}]`, bold: true, color: 'DC2626', size: 20 }),
                ],
                spacing: { before: 180, after: 60 },
            }),
            new Paragraph({
                children: [new TextRun({ text: topic.description, size: 20, color: '555555', font: 'Calibri' })],
                spacing: { after: 80 },
            }),
        ]),
        spacer(),
    ]

    // ─── 5. PREGUNTAS PARA EL ASESOR ──────────────────────────────────────────

    const questionsSection = [
        sectionHeading('4. Preguntas Clave para el Asesor'),
        ...data.lawyerQuestions.map(q =>
            new Paragraph({
                children: [
                    new TextRun({ text: `${q.number}. `, bold: true, size: 22, font: 'Calibri' }),
                    new TextRun({ text: q.question, size: 22, font: 'Calibri' }),
                ],
                spacing: { after: 100 },
            }),
        ),
        spacer(),
    ]

    // ─── 6. DOCUMENTOS REQUERIDOS ─────────────────────────────────────────────

    const docsSection = [
        sectionHeading('5. Documentos a Presentar'),
        ...data.requiredDocuments.map(doc =>
            new Paragraph({
                children: [
                    new TextRun({ text: doc.completed ? '☑ ' : '☐ ', size: 22 }),
                    new TextRun({
                        text: doc.title,
                        size: 22,
                        font: 'Calibri',
                        color: doc.completed ? '059669' : '222222',
                    }),
                ],
                spacing: { after: 80 },
            }),
        ),
        spacer(),
    ]

    // ─── 7. DECISIONES INTERNAS ───────────────────────────────────────────────

    const decisionsSection = [
        sectionHeading('6. Decisiones Internas Previas'),
        ...data.internalDecisions.flatMap(decision => [
            new Paragraph({
                children: [new TextRun({ text: decision.scenario, bold: true, size: 22, font: 'Calibri' })],
                spacing: { before: 160, after: 60 },
            }),
            ...decision.options.map(opt =>
                new Paragraph({
                    children: [new TextRun({ text: `  • ${opt.label}`, size: 20, color: '555555', font: 'Calibri' })],
                    spacing: { after: 40 },
                }),
            ),
        ]),
        spacer(),
    ]

    // ─── CONSTRUIR DOCUMENTO ──────────────────────────────────────────────────

    const doc = new Document({
        styles: {
            default: {
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
                    ...profileSection,
                    ...legalSection,
                    ...criticalSection,
                    ...questionsSection,
                    ...docsSection,
                    ...decisionsSection,
                ],
            },
        ],
    })

    const blob = await Packer.toBlob(doc)
    const nameSlug = data.organizationProfile.entityName
        .replace(/\s+/g, '_')
        .replace(/[^a-zA-Z0-9_]/g, '')
        .substring(0, 40)

    saveAs(blob, `Paquete_Asesor_${nameSlug || 'Organizacion'}.docx`)
}
