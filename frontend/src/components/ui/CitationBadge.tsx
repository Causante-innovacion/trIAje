import { useState, useRef, useEffect, useCallback } from 'react'
import { CitationMap } from '../../hooks/useCitations'

interface CitationBadgeProps {
    index: number
    citations: CitationMap
}

/**
 * CitationBadge — small numbered circle that shows a tooltip with the full
 * citation text when the user hovers over or focuses it.
 *
 * Example marker in text: [1]  →  renders as  ①  with a floating tooltip.
 */
export function CitationBadge({ index, citations }: CitationBadgeProps) {
    const [visible, setVisible] = useState(false)
    const [position, setPosition] = useState<'top' | 'bottom'>('top')
    const badgeRef = useRef<HTMLButtonElement>(null)
    const tooltipRef = useRef<HTMLDivElement>(null)
    const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

    const citationText = citations[index]
    if (!citationText) return <span className="citation-badge-missing">[{index}]</span>

    const show = useCallback(() => {
        if (hideTimer.current) clearTimeout(hideTimer.current)
        // Decide whether to open upward or downward based on space
        if (badgeRef.current) {
            const rect = badgeRef.current.getBoundingClientRect()
            setPosition(rect.top > 160 ? 'top' : 'bottom')
        }
        setVisible(true)
    }, [])

    const hide = useCallback(() => {
        hideTimer.current = setTimeout(() => setVisible(false), 120)
    }, [])

    const keepOpen = useCallback(() => {
        if (hideTimer.current) clearTimeout(hideTimer.current)
    }, [])

    // Close on Escape
    useEffect(() => {
        if (!visible) return
        const handler = (e: KeyboardEvent) => {
            if (e.key === 'Escape') setVisible(false)
        }
        window.addEventListener('keydown', handler)
        return () => window.removeEventListener('keydown', handler)
    }, [visible])

    return (
        <span className="citation-badge-wrapper">
            {/* The numbered circle */}
            <button
                ref={badgeRef}
                type="button"
                aria-label={`Ver cita ${index}`}
                aria-expanded={visible}
                onMouseEnter={show}
                onMouseLeave={hide}
                onFocus={show}
                onBlur={hide}
                onClick={() => setVisible(v => !v)}
                className={`
          citation-badge
          inline-flex items-center justify-center
          w-[1.15em] h-[1.15em] min-w-[1.15em]
          text-[0.65em] font-bold leading-none
          rounded-full
          border border-amber-400
          bg-amber-50 text-amber-700
          cursor-pointer select-none
          align-super
          mx-[0.15em]
          transition-all duration-150
          hover:bg-amber-400 hover:text-white hover:border-amber-500
          hover:scale-110
          focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:ring-offset-1
        `}
            >
                {index}
            </button>

            {/* Floating tooltip */}
            {visible && (
                <span
                    ref={tooltipRef as React.RefObject<HTMLSpanElement>}
                    role="tooltip"
                    onMouseEnter={keepOpen}
                    onMouseLeave={hide}
                    className={`
            citation-tooltip
            absolute z-50
            max-w-xs w-max
            bg-gray-900 text-gray-100
            text-xs leading-snug
            px-3 py-2 rounded-lg shadow-xl
            pointer-events-auto
            border border-gray-700
            ${position === 'top'
                            ? 'bottom-[calc(100%+6px)] left-1/2 -translate-x-1/2'
                            : 'top-[calc(100%+6px)] left-1/2 -translate-x-1/2'
                        }
            before:content-['']
            before:absolute before:left-1/2 before:-translate-x-1/2
            ${position === 'top'
                            ? "before:top-full before:border-[5px] before:border-transparent before:border-t-gray-900"
                            : "before:bottom-full before:border-[5px] before:border-transparent before:border-b-gray-900"
                        }
            animate-fade-in
          `}
                    style={{ whiteSpace: 'normal', maxWidth: '20rem' }}
                >
                    <span className="font-bold text-amber-400 mr-1">[{index}]</span>
                    {citationText}
                </span>
            )}
        </span>
    )
}
