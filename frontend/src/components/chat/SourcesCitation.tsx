import { useState } from 'react'
import { BookOpen, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react'
import type { LegalSource } from '../../types/chat'

interface SourcesCitationProps {
    sources: LegalSource[]
}

export function SourcesCitation({ sources }: SourcesCitationProps) {
    const [isExpanded, setIsExpanded] = useState(false)

    if (!sources || sources.length === 0) return null

    return (
        <div className="mt-4 animate-fade-in">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition-colors group"
            >
                <BookOpen className="w-4 h-4" />
                <span className="font-medium">Fuentes citadas ({sources.length})</span>
                {isExpanded ? (
                    <ChevronUp className="w-3.5 h-3.5 text-gray-400" />
                ) : (
                    <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
                )}
            </button>

            {isExpanded && (
                <div className="mt-3 space-y-2 pl-1 border-l-2 border-gray-100">
                    {sources.map((source, index) => (
                        <div
                            key={index}
                            className="pl-4 py-2 text-sm animate-slide-in"
                            style={{ animationDelay: `${index * 50}ms` }}
                        >
                            <div className="flex items-start gap-2">
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-gray-800 truncate">
                                        {source.title}
                                    </p>
                                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-0.5">
                                        {source.article && (
                                            <span className="text-xs text-gray-500">
                                                {source.article}
                                            </span>
                                        )}
                                        {source.authority && (
                                            <span className="text-xs text-gray-400">
                                                {source.authority}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                {source.url && (
                                    <a
                                        href={source.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex-shrink-0 text-gold hover:text-gold-dark p-1 rounded transition-colors"
                                        title="Abrir fuente"
                                    >
                                        <ExternalLink className="w-3.5 h-3.5" />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
