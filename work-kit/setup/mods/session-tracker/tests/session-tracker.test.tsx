import { describe, expect, mock, test } from 'claude-code/testing'

import { ago, IDLE_MS, line, taskOf, visible } from '../hooks/register'

const BAND = { component: 'AbovePrompt', props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 140 } }
const NOW = 1_000_000_000

const seen = (id: string, root: string, at: number, state: 'working' | 'waiting' = 'working', task = 'fix the sync bug') => ({ id, root, state, task, at })

// The plugin's store, in memory and readable by the test.
function store(on: any, entries: Record<string, unknown> = {}) {
  const m = new Map<string, unknown>(Object.entries(entries))
  on('store.get', (_$: any, e: any) => ({ value: m.get(e.key) }))
  on('store.set', (_$: any, e: any) => (m.set(e.key, e.value), { value: undefined }))
  on('store.delete', (_$: any, e: any) => (m.delete(e.key), { value: undefined }))
  on('store.keys', () => ({ value: [...m.keys()] }))
  return m
}

// Stands for the engine beneath the mod: this session is "me" in /repo.
function engine(on: any) {
  on('session.start', (_$: any, e: any) => ({ sessionId: 'me', cwd: e.cwd }))
  on('session.id', () => ({ value: 'me' }))
  on('session.root', () => ({ value: '/repo' }))
  on('command.register', () => ({ value: undefined }))
  on('turn.complete', () => ({ text: '' }))
  on('ui.render', ($: any, e: any) => $.ui.resolve(e).Text({ children: 'band below' }))
}

describe('session-tracker', () => {
  test('helpers', () => {
    expect(taskOf('  audit starting context\nsecond line')).toBe('audit starting context')
    expect(taskOf('x'.repeat(100)).length).toBe(70)
    expect(ago(30_000)).toBe('just now')
    expect(ago(4 * 60_000)).toBe('4m ago')
    expect(ago(125 * 60_000)).toBe('2h 5m ago')
    const list = [seen('me', '/repo', NOW), seen('a', '/repo', NOW - 60_000), seen('b', '/other', NOW), seen('c', '/repo', NOW - IDLE_MS - 1)]
    expect(visible(list, 'me', '/repo', NOW).map(s => s.id)).toEqual(['a'])
    expect(visible(list, 'me', '/repo', NOW, true).map(s => s.id)).toEqual(['a', 'c'])
    expect(line(seen('a', '/repo', NOW - 120_000, 'waiting', ''), NOW)).toBe('○ waiting · (no prompt yet) · 2m ago')
  })

  test('another session in this repo shows in the band and in /sessions; other repos do not', async ($, on) => {
    engine(on)
    const clock = mock.clock(on, { now: NOW })
    const m = store(on, {
      's:a': seen('a', '/repo', NOW - 4 * 60_000),
      's:b': seen('b', '/elsewhere', NOW),
      's:old': seen('old', '/repo', NOW - 7 * 60 * 60_000),
    })
    await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/repo' } as any)

    const band = await $.ui.mount({ plugin: 'session-tracker', surface: 'terminal', ...BAND } as any)
    expect(await band.find({ type: 'Text', text: /other session here · ● working · "fix the sync bug"/ })).toBeDefined()
    expect(await band.find({ type: 'Text', text: /band below/ })).toBeDefined()

    const r = await $.command.run({ command: 'sessions', args: '' } as any)
    expect(r.text).toMatch(/^1 other session\(s\) in \/repo:/)
    expect(r.text).not.toMatch(/elsewhere/)

    // This session's own record exists; the 7-hour-old one was pruned.
    expect(m.get('s:me')).toBeDefined()
    expect(m.has('s:old')).toBe(false)
    void clock
    await band.unmount()
  })

  test('a prompt marks this session working with its first line as the task', async ($, on) => {
    engine(on)
    mock.clock(on, { now: NOW })
    const m = store(on)
    on('prompt.submit', (_$: any, e: any) => ({ text: e.text }))
    await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/repo' } as any)
    await $.prompt.submit({ text: 'port reflect to memory\nmore detail', origin: { kind: 'composer' } } as any)
    const me = m.get('s:me') as any
    expect(me.state).toBe('working')
    expect(me.task).toBe('port reflect to memory')
    await $.turn.complete({ reason: 'answer', answer: 'ok', durationMs: 1 } as any)
    expect((m.get('s:me') as any).state).toBe('waiting')
  })
})
