import { FormalizationPackage } from './mockFormalizationData'

/**
 * Genera y descarga un documento .docx con la ruta de formalización completa.
 * Mismo patrón de import dinámico que evaluationExport.ts.
 */
export async function exportFormalizationToDocx(data: FormalizationPackage): Promise<void> {
    const {
        Document,
        Packer,
        Paragraph,
        TextRun,
        HeadingLevel,
        AlignmentType,
        BorderStyle,
    } = await import('docx')
    const { saveAs } = await import('file-saver')

    const spacer = () => new Paragraph({ text: '' })

    // ─── ENCABEZADO ───────────────────────────────────────────────────────────

    const headerSection = [
        new Paragraph({
            children: [
                new TextRun({
                    text: 'RUTA DE FORMALIZACIÓN',
                    bold: true,
                    size: 40,
                    color: 'B45309',
                }),
            ],
            alignment: AlignmentType.CENTER,
            heading: HeadingLevel.HEADING_1,
            spacing: { after: 120 },
        }),
        new Paragraph({
            children: [
                new TextRun({ text: data.organizationName, bold: true, size: 28 }),
            ],
            alignment: AlignmentType.CENTER,
            spacing: { after: 80 },
        }),
        new Paragraph({
            children: [
                new TextRun({ text: data.subtitle, size: 20, color: '666666', italics: true }),
            ],
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 },
        }),
    ]

    // ─── RUTAS Y ETAPAS ───────────────────────────────────────────────────────

    const routeSections = data.routes.flatMap(route => [
        // Route title
        new Paragraph({
            children: [
                new TextRun({
                    text: `${route.number}. ${route.title}`,
                    bold: true,
                    size: 28,
                    color: 'B45309',
                }),
            ],
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 360, after: 120 },
            border: {
                bottom: { style: BorderStyle.SINGLE, size: 1, color: 'E5E0D8' },
            },
        }),
        new Paragraph({
            children: [new TextRun({ text: route.description, size: 20, color: '555555', italics: true })],
            spacing: { after: 200 },
        }),

        // Each stage
        ...route.stages.flatMap(stage => [
            new Paragraph({
                children: [
                    new TextRun({
                        text: `ETAPA ${stage.number}: `,
                        bold: true,
                        size: 22,
                        color: 'B45309',
                        allCaps: true,
                    }),
                    new TextRun({
                        text: stage.title,
                        bold: true,
                        size: 22,
                        color: '111111',
                    }),
                ],
                spacing: { before: 200, after: 80 },
            }),
            ...stage.items.map(
                item =>
                    new Paragraph({
                        children: [
                            new TextRun({ text: `• ${item.title}: `, bold: true, size: 20 }),
                            new TextRun({ text: item.detail, size: 20, color: '444444' }),
                        ],
                        spacing: { after: 60 },
                        indent: { left: 360 },
                    }),
            ),
            spacer(),
        ]),
    ])

    // ─── PIE ──────────────────────────────────────────────────────────────────

    const footerSection = [
        new Paragraph({
            children: [
                new TextRun({
                    text: '© 2024 GPT Legal — Guía Informativa de Cumplimiento. Esta guía es de carácter informativo. Los requisitos pueden variar según las normativas vigentes.',
                    size: 16,
                    color: '888888',
                    italics: true,
                }),
            ],
            alignment: AlignmentType.CENTER,
            spacing: { before: 480 },
        }),
    ]

    // ─── CONSTRUIR DOCUMENTO ──────────────────────────────────────────────────

    const doc = new Document({
        styles: {
            default: {
                heading1: {
                    run: { font: 'Arial', size: 40, bold: true, color: 'B45309' },
                    paragraph: { spacing: { after: 200 } },
                },
                heading2: {
                    run: { font: 'Arial', size: 28, bold: true, color: '111111' },
                    paragraph: { spacing: { before: 240, after: 120 } },
                },
                document: {
                    run: { font: 'Arial', size: 22 },
                },
            },
        },
        sections: [
            {
                properties: {},
                children: [
                    ...headerSection,
                    ...routeSections,
                    ...footerSection,
                ],
            },
        ],
    })

    const blob = await Packer.toBlob(doc)

    const orgSlug = data.organizationName
        .replace(/\s+/g, '_')
        .replace(/[^a-zA-Z0-9_]/g, '')
        .substring(0, 40)

    saveAs(blob, `Ruta_Formalizacion_${orgSlug || 'Organizacion'}.docx`)
}
