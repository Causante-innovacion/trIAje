import { useState, useLayoutEffect, useRef } from 'react'

interface UseTypewriterOptions {
    /** Words per batch to reveal at once (default: 2) */
    wordsPerTick?: number
    /** Milliseconds between each batch reveal (default: 30) */
    speed?: number
    /** Whether the effect is enabled (default: true) */
    enabled?: boolean
}

/**
 * Hook that reveals text word-by-word, creating a typewriter effect.
 * Returns the currently visible portion of the text and whether it's still animating.
 *
 * Uses useLayoutEffect so that `setVisibleText('')` runs synchronously
 * before the browser paints. This prevents the one-frame flash of full
 * text that would otherwise appear when `enabled` transitions to true.
 */
export function useTypewriter(
    fullText: string,
    options: UseTypewriterOptions = {}
) {
    const { wordsPerTick = 2, speed = 30, enabled = true } = options

    const [visibleText, setVisibleText] = useState(enabled ? '' : fullText)
    const [isAnimating, setIsAnimating] = useState(enabled && fullText.length > 0)
    const wordsRef = useRef<string[]>([])
    const indexRef = useRef(0)
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

    // useLayoutEffect fires synchronously after DOM mutations but BEFORE
    // the browser paints, so the user never sees the stale visibleText value.
    useLayoutEffect(() => {
        if (!enabled || !fullText) {
            setVisibleText(fullText)
            setIsAnimating(false)
            return
        }

        // Split into words, preserving whitespace/newlines
        wordsRef.current = fullText.match(/\S+|\s+/g) || []
        indexRef.current = 0
        setVisibleText('')
        setIsAnimating(true)

        timerRef.current = setInterval(() => {
            const words = wordsRef.current
            const nextIndex = Math.min(
                indexRef.current + wordsPerTick,
                words.length
            )

            if (nextIndex >= words.length) {
                // Done - show full text to avoid any rounding issues
                setVisibleText(fullText)
                setIsAnimating(false)
                if (timerRef.current) clearInterval(timerRef.current)
                return
            }

            indexRef.current = nextIndex
            setVisibleText(words.slice(0, nextIndex).join(''))
        }, speed)

        return () => {
            if (timerRef.current) clearInterval(timerRef.current)
        }
    }, [fullText, enabled, wordsPerTick, speed])

    return { visibleText, isAnimating }
}
