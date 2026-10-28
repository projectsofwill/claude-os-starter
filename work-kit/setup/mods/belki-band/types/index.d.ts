export type Counts = { overdue: number; today: number; chase: number; first: string | null }

declare module 'claude-code' {
  interface PluginState {
    'belki-band': { counts: Counts | null; isHidden: boolean }
  }
}
