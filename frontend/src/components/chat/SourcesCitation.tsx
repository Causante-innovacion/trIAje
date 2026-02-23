import { useState } from 'react'
import { BookOpen, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import type { LegalSource } from '../../types/chat'

interface SourcesCitationProps {
    sources: LegalSource[]
}

/** Extrae el dominio legible de una URL, e.g. "congreso.gob.pe" */
function extractDomain(url: string): string {
    try {
        return new URL(url).hostname.replace(/^www\./, '')
    } catch {
        return ''
    }
}

export function SourcesCitation({ sources }: SourcesCitationProps) {
    const [isExpanded, setIsExpanded] = useState(false)

    if (!sources || sources.length === 0) return null

    const withUrl = sources.filter(s => s.url).length

    return (
        <div className="mt-3 animate-fade-in">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-600 transition-colors group"
            >
                <BookOpen className="w-3.5 h-3.5" />
                <span className="font-medium">
                    {sources.length} {sources.length === 1 ? 'fuente' : 'fuentes'}
                    {withUrl > 0 && <span className="text-gray-300 ml-1">· verificables</span>}
                </span>
                {isExpanded
                    ? <ChevronUp className="w-3 h-3 text-gray-300" />
                    : <ChevronDown className="w-3 h-3 text-gray-300" />
                }
            </button>

            {isExpanded && (
                <div className="mt-2 space-y-1.5 pl-1 border-l-2 border-gray-100">
                    {sources.map((source, index) => (
                        <div
                            key={index}
                            className="pl-3 py-1.5 animate-slide-in"
                            style={{ animationDelay: `${index * 40}ms` }}
                        >
                            {/* Title — clickable link if URL available */}
                            {source.url ? (
                                <a
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="group/link inline-flex items-baseline gap-1 text-xs font-medium text-gray-700 hover:text-causante-ocre transition-colors leading-snug"
                                >
                                    <span>{source.title}</span>
                                    <ExternalLink className="w-2.5 h-2.5 opacity-0 group-hover/link:opacity-60 transition-opacity flex-shrink-0 self-center" />
                                </a>
                            ) : (
                                <p className="text-xs font-medium text-gray-700 leading-snug">{source.title}</p>
                            )}

                            {/* Metadata row */}
                            <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 mt-0.5">
                                {source.article && (
                                    <span className="text-[11px] text-gray-500">{source.article}</span>
                                )}
                                {source.authority && (
                                    <span className="text-[11px] text-gray-400">{source.authority}</span>
                                )}
                                {source.url && (
                                    <span className="text-[10px] text-gray-300 font-mono">
                                        {extractDomain(source.url)}
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
