// Re-export all types from the main types module
export * from '../../types/chat'

// Legacy types for backwards compatibility
export interface Question {
  id: string
  text: string
  type: 'boolean' | 'enum' | 'multi_select' | 'range'
  required: boolean
  options?: string[]
  help_text?: string
}

export interface QueryResult {
  answer: string
  answer_type: 'direct' | 'conditional' | 'orientation'
  conditions: string[]
  sources: Array<{
    title: string
    authority: string
    anchor?: string
  }>
  confidence_level: string
  escalation_recommended: boolean
  disclaimers: string[]
}
