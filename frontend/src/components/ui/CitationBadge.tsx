import { useState, useRef, useEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
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
    const [coords, setCoords] = useState({ top: 0, left: 0 })
    const [tooltipMaxWidth, setTooltipMaxWidth] = useState(320)
    const badgeRef = useRef<HTMLButtonElement>(null)
    const tooltipRef = useRef<HTMLSpanElement>(null)
    const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

    const citationText = citations[index]
    if (!citationText) return <span className="citation-badge-missing">[{index}]</span>

    const show = useCallback(() => {
        if (hideTimer.current) clearTimeout(hideTimer.current)
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

    // Position the portal tooltip against viewport so it never gets clipped by overflow containers.
    useEffect(() => {
        if (!visible) return

        const updatePosition = () => {
            const badge = badgeRef.current
            const tooltip = tooltipRef.current
            if (!badge || !tooltip) return

            const vv = window.visualViewport
            const viewportWidth = vv?.width ?? document.documentElement.clientWidth ?? window.innerWidth
            const viewportHeight = vv?.height ?? document.documentElement.clientHeight ?? window.innerHeight
            const rect = badge.getBoundingClientRect()
            const tooltipWidth = tooltip.offsetWidth
            const tooltipHeight = tooltip.offsetHeight
            const margin = 8
            const gap = 8

            // On narrow screens (mobile Safari included), enforce a safe width inside viewport.
            const maxAllowedWidth = Math.max(180, Math.floor(viewportWidth - margin * 2))
            setTooltipMaxWidth(maxAllowedWidth)

            let nextPosition: 'top' | 'bottom' = rect.top > tooltipHeight + 24 ? 'top' : 'bottom'

            let left = rect.left + rect.width / 2 - tooltipWidth / 2
            left = Math.max(margin, Math.min(left, viewportWidth - tooltipWidth - margin))

            let top = nextPosition === 'top'
                ? rect.top - tooltipHeight - gap
                : rect.bottom + gap

            // Flip if the selected side overflows vertically.
            if (nextPosition === 'top' && top < margin) {
                nextPosition = 'bottom'
                top = rect.bottom + gap
            } else if (nextPosition === 'bottom' && top + tooltipHeight > viewportHeight - margin) {
                nextPosition = 'top'
                top = rect.top - tooltipHeight - gap
            }

            top = Math.max(margin, Math.min(top, viewportHeight - tooltipHeight - margin))

            setPosition(nextPosition)
            setCoords({ top, left })
        }

        // Run twice to stabilize position after first paint/font metrics in mobile browsers.
        const raf = requestAnimationFrame(() => {
            updatePosition()
            requestAnimationFrame(updatePosition)
        })

        window.addEventListener('resize', updatePosition)
        window.addEventListener('scroll', updatePosition, true)
        window.visualViewport?.addEventListener('resize', updatePosition)
        window.visualViewport?.addEventListener('scroll', updatePosition)

        return () => {
            cancelAnimationFrame(raf)
            window.removeEventListener('resize', updatePosition)
            window.removeEventListener('scroll', updatePosition, true)
            window.visualViewport?.removeEventListener('resize', updatePosition)
            window.visualViewport?.removeEventListener('scroll', updatePosition)
        }
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
            {visible && createPortal(
                <span
                    ref={tooltipRef}
                    role="tooltip"
                    onMouseEnter={keepOpen}
                    onMouseLeave={hide}
                    className={`
            citation-tooltip
            fixed z-[9999]
            max-w-xs w-max
            bg-gray-900 text-gray-100
            text-xs leading-snug
            px-3 py-2 rounded-lg shadow-xl
            pointer-events-auto
            border border-gray-700
            before:content-['']
            before:absolute before:left-1/2 before:-translate-x-1/2
            ${position === 'top'
                            ? "before:top-full before:border-[5px] before:border-transparent before:border-t-gray-900"
                            : "before:bottom-full before:border-[5px] before:border-transparent before:border-b-gray-900"
                        }
            animate-fade-in
          `}
                    style={{
                        whiteSpace: 'normal',
                        maxWidth: `${tooltipMaxWidth}px`,
                        top: `${coords.top}px`,
                        left: `${coords.left}px`,
                    }}
                >
                    <span className="font-bold text-amber-400 mr-1">[{index}]</span>
                    {citationText}
                </span>,
                document.body
            )}
        </span>
    )
}
