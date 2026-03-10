import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { CitationMap } from '../../hooks/useCitations'
import { CitationBadge } from './CitationBadge'

interface MarkdownRendererProps {
    content: string
    className?: string
    /** When provided, inline [N] markers render as hoverable citation badge circles */
    citations?: CitationMap
    /**
     * When true, suppress raw [N] citation markers without replacing them with badges.
     * Use this during typewriter animation so markers don't flash as plain text before
     * the citations map is ready.
     */
    suppressCitationMarkers?: boolean
}

/** Regex that matches [N] citation markers in text */
const CITATION_MARKER_RE = /\[(\d+)\]/g

/**
 * Converts `[N]` markers in the content to inline-code sentinels `cite:N`
 * that the code renderer below will pick up and turn into CitationBadge elements.
 * Only markers whose index exists in `citations` are converted.
 */
function injectCitationSentinels(content: string, citations: CitationMap): string {
    return content.replace(CITATION_MARKER_RE, (original, numStr) => {
        const idx = parseInt(numStr, 10)
        return citations[idx] !== undefined ? `\`cite:${idx}\`` : original
    })
}

/** Strips [N] markers from text silently (used during typewriter animation). */
function stripCitationMarkers(content: string): string {
    return content.replace(CITATION_MARKER_RE, '')
}

/**
 * Renders Markdown content with styled typography.
 * When `citations` is provided, inline `[N]` markers are replaced with small
 * hoverable circle badges showing the full citation text on hover.
 *
 * Supports: bold, italic, lists, links, headings, code, blockquotes, tables (GFM).
 */
export function MarkdownRenderer({ content, className = '', citations, suppressCitationMarkers }: MarkdownRendererProps) {
    const hasCitations = !!citations && Object.keys(citations).length > 0

    // Prepare content:
    //  - If citations are ready: inject sentinels so code renderer turns them into badges.
    //  - If suppressing (during animation): strip markers so they never flash as [1],[2].
    //  - Otherwise: pass content unchanged.
    const processedContent = hasCitations
        ? injectCitationSentinels(content, citations!)
        : suppressCitationMarkers
            ? stripCitationMarkers(content)
            : content

    return (
        <div className={`markdown-content ${className}`}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    // Headings
                    h1: ({ children }) => (
                        <h1 className="text-lg font-bold text-gray-900 mt-4 mb-2 first:mt-0">{children}</h1>
                    ),
                    h2: ({ children }) => (
                        <h2 className="text-base font-bold text-gray-900 mt-3 mb-2 first:mt-0">{children}</h2>
                    ),
                    h3: ({ children }) => (
                        <h3 className="text-sm font-bold text-gray-800 mt-3 mb-1 first:mt-0">{children}</h3>
                    ),
                    // Paragraphs
                    p: ({ children }) => (
                        <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
                    ),
                    // Bold
                    strong: ({ children }) => (
                        <strong className="font-semibold text-gray-900">{children}</strong>
                    ),
                    // Italic
                    em: ({ children }) => (
                        <em className="italic text-gray-700">{children}</em>
                    ),
                    // Links
                    a: ({ href, children }) => (
                        <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-causante-ocre hover:text-causante-yellow underline underline-offset-2 transition-colors"
                        >
                            {children}
                        </a>
                    ),
                    // Unordered lists
                    ul: ({ children }) => (
                        <ul className="list-disc list-outside space-y-1.5 mb-2 pl-5">{children}</ul>
                    ),
                    // Ordered lists
                    ol: ({ children }) => (
                        <ol className="list-decimal list-outside space-y-1.5 mb-2 pl-5">{children}</ol>
                    ),
                    // List items
                    li: ({ children }) => (
                        <li className="text-gray-700 leading-relaxed pl-1 [&>p]:inline [&>p]:mb-0">{children}</li>
                    ),
                    // Code — intercepts citation sentinels `cite:N`, passes the rest through normally
                    code: ({ children, className: codeClassName }) => {
                        const raw = String(children ?? '')

                        // ── Citation badge ────────────────────────────────────────
                        if (!codeClassName && raw.startsWith('cite:') && hasCitations) {
                            const index = parseInt(raw.slice(5), 10)
                            if (!isNaN(index)) {
                                return <CitationBadge index={index} citations={citations!} />
                            }
                        }

                        // ── Block code (has language class) ───────────────────────
                        if (codeClassName) {
                            return (
                                <code className="block bg-gray-100 rounded-lg p-3 text-sm font-mono text-gray-800 overflow-x-auto my-2">
                                    {children}
                                </code>
                            )
                        }

                        // ── Inline code ───────────────────────────────────────────
                        return (
                            <code className="bg-gray-100 text-gray-800 text-sm font-mono px-1.5 py-0.5 rounded">
                                {children}
                            </code>
                        )
                    },
                    // Code blocks
                    pre: ({ children }) => (
                        <pre className="bg-gray-100 rounded-lg p-3 overflow-x-auto my-2 text-sm">
                            {children}
                        </pre>
                    ),
                    // Blockquotes
                    blockquote: ({ children }) => (
                        <blockquote className="border-l-3 border-causante-ocre bg-cream/50 pl-3 py-1 my-2 text-gray-700 italic rounded-r">
                            {children}
                        </blockquote>
                    ),
                    // Horizontal rule
                    hr: () => (
                        <hr className="border-gray-200 my-3" />
                    ),
                    // Tables (GFM)
                    table: ({ children }) => (
                        <div className="overflow-x-auto my-3 rounded-lg border border-gray-200">
                            <table className="w-full text-sm border-collapse">{children}</table>
                        </div>
                    ),
                    thead: ({ children }) => (
                        <thead className="bg-gray-50">{children}</thead>
                    ),
                    tbody: ({ children }) => (
                        <tbody className="divide-y divide-gray-100">{children}</tbody>
                    ),
                    tr: ({ children }) => (
                        <tr className="hover:bg-gray-50/60 transition-colors">{children}</tr>
                    ),
                    th: ({ children }) => (
                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide border-b border-gray-200 whitespace-nowrap">
                            {children}
                        </th>
                    ),
                    td: ({ children }) => (
                        <td className="px-3 py-2 text-gray-700 leading-relaxed align-top">
                            {children}
                        </td>
                    ),
                }}
            >
                {processedContent}
            </ReactMarkdown>
        </div>
    )
}
