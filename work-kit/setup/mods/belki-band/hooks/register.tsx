import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Counts, Task } from '../types'

const counts = atom({ plugin: 'belki-band', key: 'counts' } as const, null)
const isHidden = atom({ plugin: 'belki-band', key: 'isHidden' } as const, false)
// The side pane: every open task, fetched only once the pane has been opened.
const PANE = 'belki'
const tasks = atom({ plugin: 'belki-band', key: 'tasks' } as const, null)
const listWanted = atom({ plugin: 'belki-band', key: 'listWanted' } as const, false)

type Item = { title: string; due: string; project: string; repeat?: string }
type Waiting = { title: string; who: string; due: string; stale: boolean }

// belki.py summary --days 0: due_soon holds tasks due today. A recurring task
// keeps its checkbox open by design, so a past due date on it is not overdue.
// waiting holds items someone else owes; stale ones are the chase list.
export function summarize(json: string): Counts {
  const { overdue, due_soon, waiting = [] } = JSON.parse(json) as { overdue: Item[]; due_soon: Item[]; waiting?: Waiting[] }
  const late = overdue.filter(t => !t.repeat)
  const chase = waiting.filter(t => t.stale).length
  return { overdue: late.length, today: due_soon.length, chase, first: (late[0] ?? due_soon[0])?.title ?? null }
}

// One line of `belki.py list`: [ ] (project) title  due:YYYY-MM-DD  waiting:who !OVERDUE  id=task-...
const LIST_LINE = /^\[ \] \(([^)]*)\) (.*?)(?:  due:(\S+))?(?:  waiting:(.*?))?( !OVERDUE)?(?:  !DUPKEY\([^)]*\))?  id=(\S+)$/

// Overdue first, then by due date, undated last.
export function parseList(stdout: string): Task[] {
  const out: Task[] = []
  for (const line of stdout.split(/\r?\n/)) {
    const m = LIST_LINE.exec(line.trim())
    if (!m || m[6] === '?') continue // no id:: means belki.py done can't complete it
    out.push({
      project: m[1] ?? '',
      title: m[2] ?? '',
      due: m[3] ?? null,
      waiting: m[4] ?? null,
      isOverdue: Boolean(m[5]),
      id: m[6] ?? '',
    })
  }
  const rank = (t: Task) => (t.isOverdue ? 0 : t.due ? 1 : 2)
  return out.sort((a, b) => rank(a) - rank(b) || (a.due ?? '').localeCompare(b.due ?? ''))
}

// Groups keep parseList's order, so the project holding the most urgent task leads.
export function groupByProject(list: Task[]): [string, Task[]][] {
  const groups = new Map<string, Task[]>()
  for (const t of list) groups.set(t.project, [...(groups.get(t.project) ?? []), t])
  return [...groups]
}

// Windows may have only python or the py launcher, so probe once per session.
let PY: string[] = ['python3']
async function findPython($: EngineInterface) {
  PY = ['python3']
  for (const cand of [['python3'], ['python'], ['py', '-3']]) {
    try {
      const r = await $.process.run([...cand, '--version'], { timeoutMs: 5000 })
      if (r.exitCode === 0) {
        PY = cand
        return
      }
    } catch {
      // A missing executable can throw instead of returning a nonzero exit.
    }
  }
}

// The BELKI_DIR the summary worked with (undefined: the cwd walk), reused by list.
let belkiEnv: Record<string, string> | undefined

// BELKI_HELPER points at the work brain's project-scoped helper (set by setup/install-mac.sh).
async function script($: EngineInterface) {
  const home = (await $.env.get('HOME')) || (await $.env.get('USERPROFILE'))
  return { home, path: (await $.env.get('BELKI_HELPER')) || `${home}/.claude/skills/todo/scripts/belki.py` }
}

// Reuses the /todo skill's parser (date math, repeat handling). Walks up from the
// session's cwd first; outside the brain, uses WORK_BRAIN_DIR (default ~/work-brain).
async function refresh($: EngineInterface) {
  const { home, path } = await script($)
  const argv = [...PY, path, 'summary', '--days', '0']
  try {
    belkiEnv = undefined
    let r = await $.process.run(argv, { timeoutMs: 10_000 })
    if (r.exitCode !== 0) {
      const root = (await $.env.get('WORK_BRAIN_DIR')) || `${home}/work-brain`
      belkiEnv = { BELKI_DIR: `${root}/_belki_files` }
      r = await $.process.run(argv, { timeoutMs: 10_000, env: belkiEnv })
    }
    const next = r.exitCode === 0 ? summarize(r.stdout) : null
    await update($, counts, () => next)
  } catch {
    await update($, counts, () => null)
  }
  if (await read($, listWanted)) await refreshList($)
}

async function refreshList($: EngineInterface) {
  const { path } = await script($)
  try {
    const r = await $.process.run([...PY, path, 'list'], { timeoutMs: 10_000, ...(belkiEnv ? { env: belkiEnv } : {}) })
    const next = r.exitCode === 0 ? parseList(r.stdout) : null
    await update($, tasks, () => next)
  } catch {
    await update($, tasks, () => null)
  }
}

// Fetches the list first, then asks for the pane; `ui.open` resolves once the pane is placed.
async function openPane($: EngineInterface) {
  await update($, listWanted, () => true)
  await refreshList($)
  void $.ui.open({ id: PANE, title: 'Belki' }).catch(() => {})
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await $.command.register({ name: 'belki', description: 'Show open Belki tasks in a side pane, grouped by project' })
    await findPython($)
    await refresh($)
    // The Desktop app has room beside the chat; the terminal opens it on /belki.
    if (e.surface === 'desktop') await openPane($)
    return result
  })

  on('command.run', { command: 'belki' }, async $ => {
    await openPane($)
    return { text: 'Belki pane opened.' }
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    await refresh($)
    return result
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const c = await read($, counts)
    if (e.props.hasSurvey || c === null || (c.overdue === 0 && c.today === 0 && c.chase === 0) || (await read($, isHidden))) {
      return next(e)
    }

    const { Box, Button, Text } = $.ui.resolve(e)
    const parts = [
      c.overdue ? `${c.overdue} overdue` : '',
      c.today ? `${c.today} due today` : '',
      c.chase ? `${c.chase} to chase` : '',
    ].filter(Boolean)

    return (
      <Box>
        <Text color={c.overdue ? 'error' : 'warning'}>Belki: {parts.join(' · ')}</Text>
        {c.first ? <Text dimColor> · {c.first} </Text> : <Text> </Text>}
        <Button key="hide" label="Hide" onPress={() => update($, isHidden, () => true)} />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Text } = $.ui.resolve(e)
    const list = await read($, tasks)
    // Header and project lines count against the rows too.
    let room = Math.max(1, (e.viewport?.rows ?? 24) - 6)
    let shownCount = 0
    const groups: [string, Task[]][] = []
    for (const [project, items] of groupByProject(list ?? [])) {
      if (room < 2) break
      const fit = items.slice(0, room - 1)
      groups.push([project, fit])
      room -= fit.length + 1
      shownCount += fit.length
    }

    return (
      <Box flexDirection="column">
        <Box flexDirection="row">
          <Text dimColor>{list === null ? 'Belki unavailable ' : `${list.length} open `}</Text>
          <Button key="refresh" label="Refresh" onPress={() => refresh($)} />
        </Box>
        {list !== null && list.length === 0 && <Text dimColor>Nothing open.</Text>}
        {groups.map(([project, items]) => (
          <Box key={`p-${project}`} flexDirection="column">
            <Text bold wrap="truncate">{`${project || 'No project'} (${items.length})`}</Text>
            {items.map(t => (
              <Box key={t.id} flexDirection="row">
                <Text color={t.isOverdue ? 'error' : undefined} wrap="truncate">
                  {`  ${t.title} `}
                </Text>
                {t.waiting && <Text color="warning">{`waiting: ${t.waiting} `}</Text>}
                {t.due && <Text dimColor>{t.due}</Text>}
              </Box>
            ))}
          </Box>
        ))}
        {(list?.length ?? 0) > shownCount && <Text dimColor>+{(list?.length ?? 0) - shownCount} more</Text>}
      </Box>
    )
  })
}
