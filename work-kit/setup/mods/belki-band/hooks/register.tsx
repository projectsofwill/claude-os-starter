import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Counts } from '../types'

const counts = atom({ plugin: 'belki-band', key: 'counts' } as const, null)
const isHidden = atom({ plugin: 'belki-band', key: 'isHidden' } as const, false)

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

// Reuses the /todo skill's parser (date math, repeat handling). BELKI_HELPER points at the
// work brain's project-scoped helper (set by setup/install-mac.sh). Walks up from the
// session's cwd first; outside the brain, uses WORK_BRAIN_DIR (default ~/work-brain).
async function refresh($: EngineInterface) {
  const home = (await $.env.get('HOME')) || (await $.env.get('USERPROFILE'))
  const helper = (await $.env.get('BELKI_HELPER')) || `${home}/.claude/skills/todo/scripts/belki.py`
  const argv = [...PY, helper, 'summary', '--days', '0']
  try {
    let r = await $.process.run(argv, { timeoutMs: 10_000 })
    if (r.exitCode !== 0) {
      const root = (await $.env.get('WORK_BRAIN_DIR')) || `${home}/work-brain`
      const belkiDir = `${root}/_belki_files`
      r = await $.process.run(argv, { timeoutMs: 10_000, env: { BELKI_DIR: belkiDir } })
    }
    const next = r.exitCode === 0 ? summarize(r.stdout) : null
    await update($, counts, () => next)
  } catch {
    await update($, counts, () => null)
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await findPython($)
    await refresh($)
    return result
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
}
