/**
 * useCitations
 * -----------
 * Parses a Markdown string that may contain inline citation markers `[1]`, `[2]`, …
 * and a trailing references block like:
 *
 *   ## Referencias
 *   [1] Ley General de Sociedades — Art. 82, Ley N.º 26887.
 *   [2] Código Tributario — Art. 11, D.S. N.º 133-2013-EF.
 *
 * Returns:
 *   - `cleanContent`  : the Markdown without the references block
 *   - `citations`     : map of { index → citation text }
 *   - `hasCitations`  : whether any citations were found
 */
export interface CitationMap {
    [key: number]: string
}

export interface UseCitationsResult {
    cleanContent: string
    citations: CitationMap
    hasCitations: boolean
}

// Headings that mark the start of the references block (case-insensitive, no accents)
const REF_HEADING_PATTERN = /^#{1,3}\s*(referencias|fuentes|notas|fuentes\s+legales|notas\s+al\s+pie)/im

// Individual citation line: [N] Some text…
const CITATION_LINE_PATTERN = /^\[(\d+)\]\s+(.+)$/

export function useCitations(content: string): UseCitationsResult {
    const lines = content.split('\n')

    // Find where the references block starts
    let refStartIdx = -1
    for (let i = 0; i < lines.length; i++) {
        if (REF_HEADING_PATTERN.test(lines[i].trim())) {
            refStartIdx = i
            break
        }
    }

    if (refStartIdx === -1) {
        // No references block found — still parse inline [N] for any stray markers
        return { cleanContent: content, citations: {}, hasCitations: false }
    }

    // Split content into body + references block
    const bodyLines = lines.slice(0, refStartIdx)
    const refLines = lines.slice(refStartIdx + 1) // skip the heading line itself

    // Parse individual citations
    const citations: CitationMap = {}
    for (const line of refLines) {
        const trimmed = line.trim()
        if (!trimmed) continue
        const match = CITATION_LINE_PATTERN.exec(trimmed)
        if (match) {
            const index = parseInt(match[1], 10)
            citations[index] = match[2].trim()
        }
    }

    const hasCitations = Object.keys(citations).length > 0

    // Remove any trailing blank lines from body
    while (bodyLines.length > 0 && bodyLines[bodyLines.length - 1].trim() === '') {
        bodyLines.pop()
    }

    return {
        cleanContent: bodyLines.join('\n'),
        citations,
        hasCitations,
    }
}
