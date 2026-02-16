import ReactMarkdown from 'react-markdown'

interface MarkdownRendererProps {
    content: string
    className?: string
}

/**
 * Renders Markdown content with styled typography.
 * Supports: bold, italic, lists, links, headings, code, blockquotes.
 */
export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
    return (
        <div className={`markdown-content ${className}`}>
            <ReactMarkdown
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
                            className="text-gold hover:text-yellow-600 underline underline-offset-2 transition-colors"
                        >
                            {children}
                        </a>
                    ),
                    // Unordered lists
                    ul: ({ children }) => (
                        <ul className="list-disc list-inside space-y-1 mb-2 ml-1">{children}</ul>
                    ),
                    // Ordered lists
                    ol: ({ children }) => (
                        <ol className="list-decimal list-inside space-y-1 mb-2 ml-1">{children}</ol>
                    ),
                    // List items
                    li: ({ children }) => (
                        <li className="text-gray-700 leading-relaxed">{children}</li>
                    ),
                    // Inline code
                    code: ({ children, className: codeClassName }) => {
                        // Block code (has language class)
                        if (codeClassName) {
                            return (
                                <code className="block bg-gray-100 rounded-lg p-3 text-sm font-mono text-gray-800 overflow-x-auto my-2">
                                    {children}
                                </code>
                            )
                        }
                        // Inline code
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
                        <blockquote className="border-l-3 border-gold bg-cream/50 pl-3 py-1 my-2 text-gray-700 italic rounded-r">
                            {children}
                        </blockquote>
                    ),
                    // Horizontal rule
                    hr: () => (
                        <hr className="border-gray-200 my-3" />
                    ),
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    )
}
