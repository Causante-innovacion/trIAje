/**
 * buildAdviserConversation
 *
 * Builds a clean conversation array for the adviser-prep API call.
 * - Strips internal UI messages (e.g. 'project_info_card' literal)
 * - Prepends structured project context from the extracted plan so the LLM
 *   has full information about organizations, financing and gaps — not just
 *   what the user typed in the chat.
 */

import type { Message } from '../../types/chat'
import type { PlanExtractionResponse } from '../../types/extraction.types'

interface ConvTurn {
  role: 'user' | 'assistant' | 'context'
  content: string
}

// Short confirmations that add no legal context — excluded from conversation
const FILLER_PHRASES = [
  'sí, la información es correcta',
  'si, la información es correcta',
  'sí, es correcto',
  'si, es correcto',
  'correcto',
  'ok',
  'okay',
  'de acuerdo',
  'entendido',
]

function isFiller(text: string): boolean {
  return FILLER_PHRASES.includes(text.trim().toLowerCase())
}

function buildProjectContextMessage(plan: PlanExtractionResponse): string {
  const meta = plan.source_metadata
  const raw = plan.raw_extractions

  const lines: string[] = [
    '=== CONTEXTO DEL PROYECTO (datos extraídos del Plan Estratégico) ===',
    `Nombre del proyecto: ${meta.project_name || 'Sin nombre'}`,
  ]

  if (meta.description) lines.push(`Descripción: ${meta.description}`)
  if (meta.problem_summary) lines.push(`Problema que resuelve: ${meta.problem_summary}`)
  if (meta.solution_summary) lines.push(`Solución propuesta: ${meta.solution_summary}`)
  if (meta.external_dependency != null)
    lines.push(`Dependencia externa: ${meta.external_dependency}%`)

  // Organizations / team
  if (raw.team_and_partners?.length) {
    lines.push('\nOrganizaciones del equipo:')
    raw.team_and_partners.forEach(org => {
      lines.push(`  - ${org.name} (${org.role_raw}): ${org.tasks?.join(', ') || ''}`)
    })
  }

  // Financing
  const fin = raw.financing_sources_raw
  if (fin) {
    if (fin.sources_suggested_raw?.length) {
      lines.push('\nFuentes de financiamiento sugeridas:')
      fin.sources_suggested_raw.forEach((s: string) => lines.push(`  - ${s}`))
    }
    if (fin.future_allies_raw?.length) {
      lines.push('Aliados futuros identificados:')
      fin.future_allies_raw.forEach((a: string) => lines.push(`  - ${a}`))
    }
  }

  // Gaps
  if (raw.gaps_identified?.length) {
    lines.push('\nBrechas identificadas:')
    raw.gaps_identified.forEach(g => {
      const parts = [g.description]
      if (g.ally_needed) parts.push(`aliado necesario: ${g.ally_needed}`)
      if (g.strategy) parts.push(`estrategia: ${g.strategy}`)
      lines.push(`  - ${parts.join(' | ')}`)
    })
  }

  lines.push('=== FIN CONTEXTO DEL PROYECTO ===')
  return lines.join('\n')
}

export function buildAdviserConversation(
  messages: Message[],
  extractedPlan: PlanExtractionResponse | null
): ConvTurn[] {
  // Filter to meaningful turns only
  const turns: ConvTurn[] = messages
    .filter(m => {
      if (m.sender === 'user') {
        return (
          m.contentType === 'text' &&
          m.content?.trim() &&
          !isFiller(m.content)
        )
      }
      if (m.sender === 'justo') {
        return (
          (m.contentType === 'semaphore_response' || m.contentType === 'text') &&
          m.content?.trim() &&
          m.content !== 'project_info_card' &&
          !m.isStreaming
        )
      }
      return false
    })
    .map(m => ({
      role: (m.sender === 'user' ? 'user' : 'assistant') as 'user' | 'assistant',
      content: m.content!,
    }))

  // Prepend structured project context as a background-context block (not a user turn)
  if (extractedPlan) {
    turns.unshift({
      role: 'context',
      content: buildProjectContextMessage(extractedPlan),
    })
  }

  return turns
}
