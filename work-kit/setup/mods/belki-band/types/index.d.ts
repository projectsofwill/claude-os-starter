export type Counts = { overdue: number; today: number; chase: number; first: string | null }
export type Task = { id: string; title: string; project: string; due: string | null; waiting: string | null; isOverdue: boolean }

declare module 'claude-code' {
  interface PluginState {
    'belki-band': {
      counts: Counts | null
      isHidden: boolean
      tasks: Task[] | null
      listWanted: boolean
    }
  }
}
