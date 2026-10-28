export type Seen = {
  id: string
  root: string
  state: 'working' | 'waiting'
  task: string
  at: number
}

declare module 'claude-code' {
  interface PluginState {
    'session-tracker': { others: Seen[] }
  }
}
