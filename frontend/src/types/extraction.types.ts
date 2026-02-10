// Types for Plan Estratégico CAUSANTE extraction

export interface OrganizationExtracted {
  name: string
  role_raw: string
  tasks: string[]
}

export interface GapExtracted {
  description: string
  ally_needed: string
  strategy: string
}

export interface FinancingPhase {
  phase: number
  name: string
}

export interface FinancingExtracted {
  sources_suggested_raw: string[]
  future_allies_raw: string[]
  phases_raw: FinancingPhase[]
}

export interface SourceMetadata {
  project_name: string
  description: string
  problem_summary: string
  solution_summary: string
  external_dependency: number | null
}

export interface RawExtractions {
  team_and_partners: OrganizationExtracted[]
  financing_sources_raw: FinancingExtracted
  gaps_identified: GapExtracted[]
}

export interface PlanExtractionResponse {
  source_metadata: SourceMetadata
  raw_extractions: RawExtractions
}
