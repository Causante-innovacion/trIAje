import { useState } from 'react';
import type { ProjectOutput } from '../../../shared/types';
import {
    Mic,
    Copy,
    CheckCircle,
    AlertTriangle,
    RotateCcw,
    Download,
    UserCheck,
    AlertOctagon,
    ShieldAlert,
    Search,
    Megaphone
} from 'lucide-react';

interface ResultsProps {
    data: ProjectOutput;
    onReset: () => void;
    onBack?: () => void;  // Volver al selector de ideas
}

export default function Results({ data, onReset, onBack }: ResultsProps) {
    const [copied, setCopied] = useState(false);

    const handleCopyPitch = () => {
        navigator.clipboard.writeText(data.tactical.pitch);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    // Generar documento DOCX editable
    const handleExport = async () => {
        try {
            // Import dinámico de librerías para DOCX
            const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType } = await import('docx');
            const { saveAs } = await import('file-saver');

            // --- SECCIONES DEL DOCUMENTO ---

            // 1. HEADER & TITULO
            const headerSection = [
                new Paragraph({
                    text: "PLAN ESTRATÉGICO CAUSANTE",
                    heading: HeadingLevel.HEADING_1,
                    alignment: "center",
                }),
                new Paragraph({ text: "" }), // Espacio
                new Paragraph({
                    children: [
                        new TextRun({
                            text: data.projectTitle.toUpperCase(),
                            size: 32,
                            bold: true,
                            font: "Space Grotesk",
                            color: "D7D100" // Causante Yellow
                        }),
                    ],
                    alignment: "center",
                }),
                new Paragraph({ text: "" }),
            ];

            // 2. PITCH
            const pitchSection = [
                new Paragraph({
                    text: "1. PROPUESTA DE VALOR (PITCH)",
                    heading: HeadingLevel.HEADING_2,
                }),
                new Paragraph({
                    children: [
                        new TextRun({
                            text: `"${data.tactical.pitch}"`,
                            italics: true,
                            size: 24,
                            color: "333333"
                        }),
                    ],
                    spacing: { after: 200 },
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "Impacto Esperado: ", bold: true }),
                        new TextRun({ text: data.tactical.conceptNote.impact }),
                    ],
                    spacing: { after: 400 },
                }),
            ];

            // 3. CONCEPTO
            const conceptSection = [
                new Paragraph({
                    text: "2. CONCEPTO ESTRATÉGICO",
                    heading: HeadingLevel.HEADING_2,
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "EL PROBLEMA:", bold: true, color: "DC2626" }), // Red
                    ],
                }),
                new Paragraph({
                    children: [new TextRun({ text: data.tactical.conceptNote.problem })],
                    spacing: { after: 200 },
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "LA SOLUCIÓN:", bold: true, color: "059669" }), // Green
                    ],
                }),
                new Paragraph({
                    children: [new TextRun({ text: data.tactical.conceptNote.solution })],
                    spacing: { after: 400 },
                }),
            ];

            // 4. EQUIPO (Tabla simple)
            const teamRows = [
                new TableRow({
                    children: [
                        new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "ORGANIZACIÓN", bold: true, color: "FFFFFF" })] })], shading: { fill: "000000" } }),
                        new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "ROL ASIGNADO", bold: true, color: "FFFFFF" })] })], shading: { fill: "000000" } }),
                        new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "TAREAS CLAVE", bold: true, color: "FFFFFF" })] })], shading: { fill: "000000" } }),
                    ],
                }),
                ...data.tactical.team.map(t => new TableRow({
                    children: [
                        new TableCell({ children: [new Paragraph(t.assignedTo)] }),
                        new TableCell({ children: [new Paragraph(t.roleName)] }),
                        new TableCell({
                            children: t.keyTasks.map(task => new Paragraph({
                                children: [new TextRun({ text: `• ${task}` })],
                            }))
                        }),
                    ],
                }))
            ];

            const teamSection = [
                new Paragraph({
                    text: `3. EQUIPO Y ROLES (Dep. Externa: ${data.dependency_index}%)`,
                    heading: HeadingLevel.HEADING_2,
                }),
                new Table({
                    rows: teamRows,
                    width: { size: 100, type: WidthType.PERCENTAGE },
                }),
                new Paragraph({ text: "", spacing: { after: 400 } }),
            ];

            // 5. GAPS
            const gapsRows = [
                new TableRow({
                    children: [
                        new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "NOS FALTA...", bold: true })] })], shading: { fill: "FEF3C7" } }), // Amber-50 equivalent
                        new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "BUSCAR ALIADO TIPO...", bold: true })] })], shading: { fill: "FEF3C7" } }),
                        new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "ESTRATEGIA", bold: true })] })], shading: { fill: "FEF3C7" } }),
                    ],
                }),
                ...data.strategic.gaps.map(g => new TableRow({
                    children: [
                        new TableCell({ children: [new Paragraph(g.missing_capability)] }),
                        new TableCell({ children: [new Paragraph(g.suggested_ally_type)] }),
                        new TableCell({ children: [new Paragraph(g.mitigation_plan)] }),
                    ],
                }))
            ];

            const gapsSection = [
                new Paragraph({
                    text: "4. ANÁLISIS DE BRECHAS",
                    heading: HeadingLevel.HEADING_2,
                }),
                new Table({
                    rows: gapsRows,
                    width: { size: 100, type: WidthType.PERCENTAGE },
                }),
                new Paragraph({ text: "", spacing: { after: 400 } }),
            ];

            // 6. FINANCIAMIENTO
            const fundingSection = [
                new Paragraph({
                    text: "5. ESTRATEGIA DE FINANCIAMIENTO",
                    heading: HeadingLevel.HEADING_2,
                }),
                new Paragraph({ children: [new TextRun({ text: "FASE 1: ARRANQUE", bold: true, color: "059669" })] }),
                new Paragraph({ children: [new TextRun({ text: `Tipo: ${data.strategic.roadmap.funding.immediate.type}` })] }),
                new Paragraph({ children: [new TextRun({ text: `Fuentes Sugeridas: ${data.strategic.roadmap.funding.immediate.suggestedInvestors.join(", ")}` })] }),
                new Paragraph({ children: [new TextRun({ text: `Perfil Inversor: ${data.strategic.roadmap.funding.immediate.investorProfile}` })], spacing: { after: 200 } }),

                new Paragraph({ children: [new TextRun({ text: "FASE 2: ESCALAMIENTO", bold: true, color: "D97706" })] }),
                new Paragraph({ children: [new TextRun({ text: `Disparador: ${data.strategic.roadmap.funding.scaling.trigger}` })] }),
                new Paragraph({ children: [new TextRun({ text: `Pitch de Escala: "${data.strategic.roadmap.funding.scaling.scalingPitch}"` })] }),
                new Paragraph({ children: [new TextRun({ text: `Futuros Aliados: ${data.strategic.roadmap.funding.scaling.suggestedInvestors.join(", ")}` })], spacing: { after: 200 } }),

                new Paragraph({
                    children: [
                        new TextRun({
                            text: `Nota legal: ${data.strategic.roadmap.funding.disclaimer}`,
                            italics: true,
                            size: 16,
                            color: "666666"
                        })
                    ],
                }),
                new Paragraph({ text: "", spacing: { after: 400 } }),
            ];

            // 7. CASOS DE REFERENCIA
            const casesSection = [
                new Paragraph({
                    text: "6. CASOS DE REFERENCIA",
                    heading: HeadingLevel.HEADING_2,
                }),
                ...data.strategic.cases.map(cs => [
                    new Paragraph({ children: [new TextRun({ text: `${cs.name} (${cs.country})`, bold: true })] }),
                    new Paragraph({ children: [new TextRun({ text: cs.description })] }),
                    new Paragraph({ children: [new TextRun({ text: `Financiado por: ${cs.funder}`, size: 18, italics: true })] }),
                    new Paragraph({ children: [new TextRun({ text: `Link: ${cs.url}`, color: "2563EB", size: 18 })], spacing: { after: 200 } }),
                ]).flat()
            ];


            // CONTRUIR DOC
            const docData = new Document({
                styles: {
                    default: {
                        heading1: {
                            run: {
                                font: "Space Grotesk",
                                size: 36,
                                bold: true,
                                color: "000000",
                            },
                            paragraph: {
                                spacing: { after: 240 },
                            },
                        },
                        heading2: {
                            run: {
                                font: "Space Grotesk",
                                size: 28,
                                bold: true,
                                color: "000000",
                            },
                            paragraph: {
                                spacing: { before: 240, after: 120 },
                            },
                        },
                        document: {
                            run: {
                                font: "Inter", // Main font requested by user
                                size: 22, // 11pt
                            },
                        },
                    },
                },
                sections: [{
                    properties: {},
                    children: [
                        ...headerSection,
                        ...pitchSection,
                        ...conceptSection,
                        ...teamSection,
                        ...gapsSection,
                        ...fundingSection,
                        ...casesSection
                    ],
                }],
            });

            // GENERAR BLOB Y DESCARGAR
            const blob = await Packer.toBlob(docData);

            // Construir nombre del archivo: [Organizaciones]_[Proyecto]
            const distinctOrgs = Array.from(new Set(data.tactical.team.map(t => t.assignedTo)));

            const orgString = distinctOrgs.join('_')
                .replace(/\s+/g, '_')
                .replace(/[^a-zA-Z0-9_]/g, '')
                .substring(0, 50);

            const titleString = data.projectTitle
                .replace(/\s+/g, '_')
                .replace(/[^a-zA-Z0-9_]/g, '')
                .substring(0, 30);

            const filename = `${orgString || 'Causante'}_${titleString}.docx`;

            saveAs(blob, filename);

        } catch (error) {
            console.error("Error generating DOCX:", error);
            alert("Hubo un error al generar el documento editable. Por favor intenta de nuevo.");
        }
    };

    // Dependency Index Color
    const getDependencyColor = (idx: number) => {
        if (idx > 60) return 'text-red-700 bg-red-100 border-red-200';
        if (idx > 30) return 'text-amber-700 bg-amber-100 border-amber-200';
        return 'text-green-700 bg-green-100 border-green-200';
    };

    return (
        <div className="max-w-6xl mx-auto pb-32 animate-fade-in print:p-0 px-6 font-sans">

            {/* HEADER */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-4 print:hidden pt-8">
                <div>
                    <span className="inline-block py-1 px-3 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold tracking-widest uppercase mb-4 border border-emerald-200">
                        Plan Estratégico Generado
                    </span>
                </div>
                <div className="flex gap-3 flex-wrap">
                    {/* Botón para elegir otra idea (si aplica) */}
                    {onBack && (
                        <button
                            onClick={onBack}
                            className="flex items-center gap-2 px-5 py-2.5 text-sm font-bold text-slate-600 hover:text-black bg-white border border-slate-200 hover:border-black rounded-full transition-all"
                        >
                            ← Elegir Otra Idea
                        </button>
                    )}
                    <button onClick={onReset} className="flex items-center gap-2 px-5 py-2.5 text-sm font-bold text-slate-500 hover:text-black bg-transparent hover:bg-slate-50 rounded-full transition-all">
                        <RotateCcw size={16} /> Volver a Empezar
                    </button>
                    <button onClick={handleExport} className="flex items-center gap-2 px-6 py-2.5 text-sm font-bold text-white bg-black hover:bg-slate-800 rounded-full shadow-lg transition-all hover:-translate-y-0.5">
                        <Download size={16} /> Descargar DOCX
                    </button>
                </div>
            </div>

            <div className="space-y-16">

                {/* 1. PROPUESTA DE VALOR - Pitch de 20 segundos */}
                <section className="bg-black text-white rounded-[2.5rem] p-10 md:p-16 relative overflow-hidden print:bg-white print:text-black print:border-b shadow-2xl shadow-slate-200">
                    <div className="absolute top-0 right-0 p-10 opacity-10 text-yellow-500">
                        <Mic size={120} />
                    </div>
                    {/* Background Pattern Hint */}
                    <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-black to-black opacity-50 pointer-events-none"></div>

                    <div className="relative z-10">
                        <div className="flex items-center gap-3 mb-8">
                            <span className="inline-block py-1 px-3 rounded-md bg-yellow-400 text-black text-[10px] font-bold tracking-widest uppercase">
                                Paso 1
                            </span>
                            <span className="uppercase tracking-widest text-xs font-bold text-slate-300">
                                Tu Norte Estratégico
                            </span>
                        </div>

                        <div className="max-w-4xl">
                            <h1 className="text-3xl md:text-5xl font-bold mb-10 leading-tight font-display tracking-tight text-white">
                                "{data.tactical.pitch}"
                            </h1>
                        </div>

                        {/* Variaciones del pitch */}
                        {data.tactical.pitch_variations && data.tactical.pitch_variations.length > 0 && (
                            <div className="mb-12 print:hidden bg-white/5 p-6 rounded-2xl border border-white/10 backdrop-blur-sm">
                                <p className="text-slate-300 text-xs font-bold uppercase tracking-widest mb-4">Otras formas de contarlo:</p>
                                <div className="space-y-3">
                                    {data.tactical.pitch_variations.slice(1).map((variation, idx) => (
                                        <div
                                            key={idx}
                                            className="flex gap-3 items-start group cursor-pointer hover:bg-white/5 p-2 rounded-lg transition-colors"
                                            onClick={() => navigator.clipboard.writeText(variation)}
                                        >
                                            <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-yellow-500 shrink-0 group-hover:scale-125 transition-transform" />
                                            <p className="text-sm text-slate-200 group-hover:text-white transition-colors leading-relaxed font-light">
                                                "{variation}"
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="flex flex-col md:flex-row gap-8 justify-between items-end border-t border-white/20 pt-8">
                            <div>
                                <h2 className="text-xl font-bold text-white mb-2 font-display">{data.projectTitle}</h2>
                                <p className="text-emerald-300 text-sm max-w-xl leading-relaxed font-medium bg-emerald-900/30 px-3 py-1 rounded-lg border border-emerald-800/50 inline-block">
                                    {data.tactical.conceptNote.impact}
                                </p>
                            </div>
                            <button onClick={handleCopyPitch} className="px-6 py-3 bg-white text-black hover:bg-yellow-400 rounded-full text-sm font-bold flex items-center gap-2 print:hidden transition-colors shadow-lg">
                                {copied ? <CheckCircle size={16} className="text-green-600" /> : <Copy size={16} />}
                                {copied ? '¡Listo!' : 'Copiar Pitch'}
                            </button>
                        </div>
                    </div>
                </section>

                {/* 2. CONCEPT */}
                <section className="grid md:grid-cols-2 gap-8">
                    {/* Problem Card - Red Tint */}
                    <div className="bg-white p-10 rounded-[2rem] border border-rose-100 shadow-sm relative group hover:border-black transition-colors hover:shadow-md overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-rose-400 to-rose-200"></div>
                        <div className="bg-rose-50 w-12 h-12 rounded-full flex items-center justify-center mb-6 text-rose-600 border border-rose-100">
                            <AlertTriangle size={24} />
                        </div>
                        <h3 className="font-display text-2xl font-bold mb-4 text-black">El Problema</h3>
                        <p className="text-slate-600 text-lg leading-relaxed">{data.tactical.conceptNote.problem}</p>
                    </div>

                    {/* Solution Card - Green Tint */}
                    <div className="bg-white p-10 rounded-[2rem] border border-emerald-100 shadow-sm relative group hover:border-black transition-colors hover:shadow-md overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-emerald-400 to-emerald-200"></div>
                        <div className="bg-emerald-50 w-12 h-12 rounded-full flex items-center justify-center mb-6 text-emerald-600 border border-emerald-100">
                            <CheckCircle size={24} />
                        </div>
                        <h3 className="font-display text-2xl font-bold mb-4 text-black">La Solución</h3>
                        <p className="text-slate-600 text-lg leading-relaxed">{data.tactical.conceptNote.solution}</p>
                    </div>
                </section>

                {/* 3. TEAM ROLES - Distribución por Organización */}
                <section className="bg-slate-50 rounded-[2.5rem] p-8 md:p-12 border border-slate-100">
                    <div className="flex items-end justify-between mb-8">
                        <div>
                            <span className="inline-block py-1 px-3 rounded-md bg-white border border-slate-200 text-slate-800 text-[10px] font-bold tracking-widest uppercase mb-3 shadow-sm">
                                Paso 2
                            </span>
                            <h2 className="text-3xl font-bold text-black font-display">Equipo y Responsabilidades</h2>
                        </div>
                        <div className={`px-4 py-2 rounded-full border font-bold text-xs flex items-center gap-2 bg-white shadow-sm ${getDependencyColor(data.dependency_index)}`}>
                            <AlertOctagon size={14} />
                            <span>Dependencia Externa: {data.dependency_index}%</span>
                        </div>
                    </div>

                    {/* Card por cada organización/rol */}
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {data.tactical.team.map((role, i) => (
                            <div key={i} className={`bg-white rounded-3xl p-8 border hover:shadow-lg transition-all relative overflow-hidden ${role.isOverloaded ? 'border-red-200 bg-red-50/20' : 'border-slate-200 hover:border-indigo-400'}`}>
                                {role.isOverloaded && (
                                    <div className="mb-4 text-[10px] font-bold uppercase text-red-600 bg-red-100 w-fit px-3 py-1 rounded-full flex items-center gap-1 border border-red-200">
                                        <AlertTriangle size={12} /> Alta carga
                                    </div>
                                )}
                                <div className="mb-6">
                                    <span className="inline-block py-1 px-2 rounded bg-slate-100 text-slate-500 text-[10px] font-bold tracking-widest uppercase mb-2">
                                        {role.assignedTo}
                                    </span>
                                    <h3 className="text-xl font-bold text-black leading-tight font-display">{role.roleName}</h3>
                                </div>

                                <div className="space-y-3">
                                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 pb-2">Tareas Clave</p>
                                    <ul className="space-y-3 pt-1">
                                        {role.keyTasks.map((task, j) => (
                                            <li key={j} className="flex items-start gap-3 text-sm text-slate-600 leading-snug">
                                                <div className="min-w-[6px] h-[6px] bg-slate-300 rounded-full mt-1.5 shrink-0 group-hover:bg-indigo-500 transition-colors"></div>
                                                <span>{task}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* 4. GAPS - What we're missing */}
                <section>
                    <div className="mb-8">
                        <span className="inline-block py-1 px-3 rounded-md bg-purple-100 text-purple-800 text-[10px] font-bold tracking-widest uppercase mb-3 border border-purple-200">
                            Paso 3
                        </span>
                        <h2 className="text-3xl font-bold text-black font-display">Análisis de Brechas</h2>
                    </div>

                    {/* GAPS TABLE */}
                    <div className="bg-white rounded-[2rem] border border-purple-100 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-purple-50 text-xs font-bold uppercase text-purple-900 tracking-wider">
                                        <th className="px-8 py-6 border-b border-purple-100">Lo que falta</th>
                                        <th className="px-8 py-6 border-b border-purple-100">Aliado Ideal</th>
                                        <th className="px-8 py-6 w-1/3 border-b border-purple-100">Estrategia de Mitigación</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-purple-50">
                                    {data.strategic.gaps.map((gap, i) => (
                                        <tr key={i} className="hover:bg-purple-50/30 transition-colors group">
                                            <td className="px-8 py-6 font-bold text-slate-800 group-hover:text-purple-900 transition-colors">{gap.missing_capability}</td>
                                            <td className="px-8 py-6">
                                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-white text-purple-700 border border-purple-200 shadow-sm">
                                                    {gap.suggested_ally_type}
                                                </span>
                                            </td>
                                            <td className="px-8 py-6 text-slate-600 text-sm leading-relaxed">{gap.mitigation_plan}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </section>

                {/* 5. FUNDING JOURNEY */}
                <section>
                    <div className="mb-8">
                        <span className="inline-block py-1 px-3 rounded-md bg-blue-100 text-blue-800 text-[10px] font-bold tracking-widest uppercase mb-3 border border-blue-200">
                            Paso 4
                        </span>
                        <h2 className="text-3xl font-bold text-black font-display">Ruta de Recursos</h2>
                    </div>

                    <div className="grid md:grid-cols-2 gap-8">
                        {/* INITIAL FUNDING */}
                        <div className="bg-gradient-to-b from-white to-blue-50/30 rounded-[2.5rem] p-10 border border-blue-100 shadow-sm relative flex flex-col hover:border-blue-300 transition-colors group">
                            <div className="mb-8">
                                <span className="inline-block py-1.5 px-3 rounded-full bg-blue-100 text-blue-800 text-[10px] font-bold tracking-widest uppercase mb-4">
                                    Fase 1: Arranque
                                </span>
                                <h3 className="text-2xl font-bold text-black font-display mb-2">{data.strategic.roadmap.funding.immediate.type}</h3>
                            </div>

                            <div className="mb-8 p-6 bg-white rounded-2xl border border-blue-100 shadow-sm">
                                <div className="flex items-center gap-2 mb-3">
                                    <UserCheck size={16} className="text-blue-600" />
                                    <span className="text-xs font-bold uppercase text-slate-900">Perfil del Inversor</span>
                                </div>
                                <p className="text-sm text-slate-600 leading-relaxed">{data.strategic.roadmap.funding.immediate.investorProfile}</p>
                            </div>

                            <div className="mt-auto pt-6 border-t border-blue-100/50">
                                <span className="text-[10px] font-bold uppercase text-blue-400 block mb-3 tracking-wider">A quién tocar la puerta:</span>
                                <div className="flex flex-wrap gap-2">
                                    {data.strategic.roadmap.funding.immediate.suggestedInvestors.map((inv, idx) => (
                                        <span key={idx} className="bg-white border-2 border-blue-100 text-blue-700 px-4 py-1.5 rounded-full text-xs font-bold hover:border-blue-400 transition-colors cursor-default">
                                            {inv}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* SCALING */}
                        <div className="bg-slate-900 rounded-[2.5rem] p-10 border border-slate-800 shadow-xl text-white relative flex flex-col overflow-hidden">
                            {/* Abstract Decoration */}
                            <div className="absolute -top-10 -right-10 w-40 h-40 bg-yellow-500 rounded-full blur-[80px] opacity-20"></div>

                            <div className="mb-8 relative z-10">
                                <span className="inline-block py-1.5 px-3 rounded-full bg-white/10 text-white text-[10px] font-bold tracking-widest uppercase mb-4 border border-white/20">
                                    Fase 2: Escalamiento
                                </span>
                                <h3 className="text-2xl font-bold text-white font-display mb-2">{data.strategic.roadmap.funding.scaling.trigger}</h3>
                            </div>

                            <div className="mb-8 p-6 bg-white/5 rounded-2xl border border-white/10 relative z-10 backdrop-blur-sm">
                                <div className="flex items-center gap-2 mb-3">
                                    <Megaphone size={16} className="text-yellow-400" />
                                    <span className="text-xs font-bold uppercase text-slate-200">Discurso de Escala</span>
                                </div>
                                <p className="text-sm text-slate-300 italic leading-relaxed">"{data.strategic.roadmap.funding.scaling.scalingPitch}"</p>
                            </div>

                            <div className="mt-auto pt-6 border-t border-white/10 relative z-10">
                                <span className="text-[10px] font-bold uppercase text-slate-400 block mb-3 tracking-wider">Futuros Aliados:</span>
                                <div className="flex flex-wrap gap-2">
                                    {data.strategic.roadmap.funding.scaling.suggestedInvestors.map((inv, idx) => (
                                        <span key={idx} className="bg-white/10 text-white px-4 py-1.5 rounded-full text-xs font-bold border border-white/5 hover:bg-white/20 transition-colors cursor-default">
                                            {inv}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 6. DISCLAIMER */}
                <div className="bg-amber-50 rounded-2xl p-6 flex gap-4 border border-amber-100 items-start">
                    <ShieldAlert size={20} className="text-amber-500 shrink-0 mt-0.5" />
                    <div className="space-y-1">
                        <h4 className="text-xs font-bold uppercase text-amber-700 tracking-wider">Aviso Legal</h4>
                        <p className="text-sm text-amber-600/80 leading-relaxed">{data.strategic.roadmap.funding.disclaimer}</p>
                    </div>
                </div>

                {/* 7. REAL CASES */}
                <section>
                    <div className="mb-8 flex items-end gap-4">
                        <div>
                            <span className="inline-block py-1 px-3 rounded-md bg-slate-100 text-slate-600 text-[10px] font-bold tracking-widest uppercase mb-3 border border-slate-200">
                                Inspiración
                            </span>
                            <h2 className="text-3xl font-bold text-black font-display">Casos de Referencia</h2>
                        </div>
                        <div className="hidden md:flex items-center gap-2 bg-yellow-50 px-3 py-1.5 rounded-full border border-yellow-100 shadow-sm">
                            <AlertTriangle size={14} className="text-yellow-600" />
                            <span className="text-[10px] font-bold text-yellow-800 uppercase">Solo referencias</span>
                        </div>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6">
                        {data.strategic.cases.map((cs, i) => (
                            <div key={i} className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm flex flex-col hover:border-black transition-colors group hover:shadow-lg">
                                <div className="flex justify-between items-start mb-6">
                                    <span className="text-[10px] font-bold uppercase tracking-widest bg-black text-white px-2 py-1 rounded">
                                        {cs.country}
                                    </span>
                                </div>
                                <h4 className="font-bold text-black mb-4 text-xl font-display leading-tight group-hover:text-slate-700 transition-colors">{cs.name}</h4>
                                <p className="text-sm text-slate-600 leading-relaxed mb-6 flex-grow">{cs.description}</p>
                                <div className="pt-6 border-t border-slate-100 mt-auto text-xs space-y-2">
                                    <div>
                                        <span className="font-bold text-slate-900 block mb-1 uppercase tracking-wide text-[10px]">Financiado por:</span>
                                        <span className="text-slate-600 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">{cs.funder}</span>
                                    </div>
                                    {cs.url && cs.url !== 'No público' && (() => {
                                        const rawUrl = cs.url || '';
                                        const parts = rawUrl.split(';');
                                        const candidate = parts[0].trim();
                                        const isUrl = candidate.startsWith('http') || candidate.startsWith('https') || candidate.startsWith('www');
                                        const href = candidate.startsWith('www') ? `https://${candidate}` : candidate;

                                        if (isUrl) {
                                            return (
                                                <a href={href} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-black font-bold hover:underline mt-4 hover:text-blue-600 transition-colors text-[10px] uppercase tracking-wide">
                                                    Ver Fuente <Search size={10} />
                                                </a>
                                            );
                                        }

                                        return (
                                            <span className="block mt-4 text-[10px] font-medium text-slate-400 truncate w-full" title={candidate}>
                                                Ref: {candidate}
                                            </span>
                                        );
                                    })()}
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

            </div>
        </div>
    );
}
