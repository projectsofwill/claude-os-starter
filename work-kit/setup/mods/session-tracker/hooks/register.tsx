// Session Tracker: which other sessions are working in this repo, and on what.
//   Each session keeps one store key of its own (s:<session id>), so two sessions never
//   write the same value. Every session polls the store and draws the others above the prompt.
//   Display only: no model calls, nothing blocked.
import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Seen } from '../types'

const others = atom({ plugin: 'session-tracker', key: 'others' } as const, [])

/** A session quiet this long is hidden from the band (still listed by /sessions). */
export const IDLE_MS = 30 * 60_000
/** A record this old is removed from the store altogether. */
export const PRUNE_MS = 6 * 60 * 60_000
const POLL_MS = 15_000
/** A working session refreshes its record at most this often from tool calls. */
const BEAT_MS = 60_000
const BAND_ROWS = 3
const TASK_CHARS = 70

let lastBeat = 0

const keyOf = (id: string) => `s:${id}`

/** First line of a prompt, trimmed to fit one band row. */
export function taskOf(text: string) {
  const line = text.trim().split('\n')[0]?.trim() ?? ''
  return line.length > TASK_CHARS ? `${line.slice(0, TASK_CHARS - 1)}…` : line
}

export function ago(ms: number) {
  const m = Math.floor(ms / 60_000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  return `${Math.floor(m / 60)}h ${m % 60}m ago`
}

/** Others in this root, newest first; `all` keeps the idle ones too. */
export function visible(list: Seen[], self: string, root: string, now: number, all = false) {
  return list
    .filter(s => s.id !== self && s.root === root && (all || now - s.at < IDLE_MS))
    .sort((a, b) => b.at - a.at)
}

export function line(s: Seen, now: number) {
  const task = s.task === '' ? '(no prompt yet)' : `"${s.task}"`
  return `${s.state === 'working' ? '●' : '○'} ${s.state} · ${task} · ${ago(now - s.at)}`
}

async function write($: EngineInterface, patch: Partial<Seen>) {
  const id = await $.session.id()
  const prev = (await $.store.get(keyOf(id))) as Seen | undefined
  const seen: Seen = {
    id,
    root: await $.session.root(),
    state: 'waiting',
    task: '',
    ...prev,
    ...patch,
    at: await $.clock.now(),
  }
  await $.store.set(keyOf(id), seen)
}

/** Every record in the store; removes the long-dead ones as it goes. */
async function all($: EngineInterface, now: number) {
  const out: Seen[] = []
  for (const key of await $.store.keys()) {
    if (!key.startsWith('s:')) continue
    const s = (await $.store.get(key)) as Seen | undefined
    if (s === undefined || now - s.at > PRUNE_MS) await $.store.delete(key)
    else out.push(s)
  }
  return out
}

async function refresh($: EngineInterface) {
  const now = await $.clock.now()
  const list = visible(await all($, now), await $.session.id(), await $.session.root(), now)
  await update($, others, () => list)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const r = await next(e)
    await $.command.register({ name: 'sessions', description: 'List the Claude Code sessions in this repo and what each is on' })
    await write($, {})
    await refresh($)
    $.clock.every(POLL_MS, () => void refresh($).catch(() => undefined))
    return r
  })

  on('prompt.submit', async ($, e, next) => {
    const text = e.text.trim()
    // A slash command keeps the last real task as the label.
    await write($, text.startsWith('/') ? { state: 'working' } : { state: 'working', task: taskOf(text) }).catch(() => undefined)
    return next(e)
  })

  // A long turn keeps its record fresh, so it is not hidden as idle.
  on('tool.call', async ($, e, next) => {
    const now = await $.clock.now()
    if (now - lastBeat > BEAT_MS) {
      lastBeat = now
      await write($, { state: 'working' }).catch(() => undefined)
    }
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId === undefined) {
      await write($, { state: 'waiting' }).catch(() => undefined)
      await refresh($).catch(() => undefined)
    }
    return next(e)
  })

  // Exit and /clear both end this session id: drop its record.
  on('session.end', async ($, e, next) => {
    await $.store.delete(keyOf(e.sessionId)).catch(() => undefined)
    return next(e)
  })

  on('command.run', { command: 'sessions' }, async $ => {
    const now = await $.clock.now()
    const root = await $.session.root()
    const list = visible(await all($, now), await $.session.id(), root, now, true)
    if (list.length === 0) return { text: `No other sessions in ${root}.` }
    return { text: [`${list.length} other session(s) in ${root}:`, ...list.map(s => `  ${line(s, now)}`)].join('\n') }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const list = await read($, others)
    if (list.length === 0) return next(e)
    const now = Date.now()
    const { Box, Text } = $.ui.resolve(e)
    const below = await next(e)
    return (
      <Box flexDirection="column">
        {list.slice(0, BAND_ROWS).map(s => (
          <Text key={`s:${s.id}`} dimColor={s.state === 'waiting'} color={s.state === 'working' ? 'yellow' : undefined} wrap="truncate-end">
            {`other session here · ${line(s, now)}`}
          </Text>
        ))}
        {list.length > BAND_ROWS && <Text dimColor>{`+${list.length - BAND_ROWS} more · /sessions`}</Text>}
        {below}
      </Box>
    )
  })
}
