/** One learning the check found: a rule and what happened to it. */
export type Learning = {
  id: string
  /** The rule, one imperative line in English. */
  rule: string
  /** The session root it was said in. */
  project: string
  /** The memory folder it would be saved in: only sessions resolving to this folder show it. */
  memDir: string
  /** How many times it was said (the check merges repeats). */
  count: number
  firstAt: number
  lastAt: number
  status: 'pending' | 'saved' | 'skipped'
  confidence: number
}

declare module 'claude-code' {
  interface PluginState {
    reflect: {
      /** Learnings waiting for a decision, as the band draws them. */
      pending: Learning[]
      /** Rules saved in this session: the system prompt carries them until MEMORY.md is read again. */
      savedThisSession: string[]
    }
  }
}
