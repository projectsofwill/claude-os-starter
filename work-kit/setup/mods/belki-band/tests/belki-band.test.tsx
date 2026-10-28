import { describe, expect, test } from 'claude-code/testing'

import { summarize } from '../hooks/register'

const BAND = { component: 'AbovePrompt', props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 120 } }
const SUMMARY = JSON.stringify({
  overdue: [
    { title: 'Weekly review', due: '2026-10-01', project: 'Inbox', repeat: 'every week' },
    { title: 'Email the vendor', due: '2026-10-05', project: 'Ops' },
  ],
  due_soon: [{ title: 'Prep QBR deck', due: '2026-10-07', project: 'Ops' }],
  waiting: [
    { title: 'Territory export', who: 'Sales Ops', due: '2026-10-02', stale: true },
    { title: 'Overage policy', who: 'Finance', due: '', stale: false },
  ],
})

type Call = { argv: string[]; init?: { env?: Record<string, string>; timeoutMs?: number } }
type Options = {
  env?: Record<string, string>
  probe?: (argv: string[]) => number
  fallback?: boolean
}

function engine(on: any, stdout: string, opts: Options = {}) {
  const calls: Call[] = []
  const env = opts.env ?? { HOME: '/home/test' }
  on('session.start', (_$: any, e: any) => ({ sessionId: 's', cwd: e.cwd }))
  on('env.get', (_$: any, e: any) => ({ value: env[e.name] }))
  on('process.run', (_$: any, e: Call) => {
    calls.push(e)
    if (e.argv.at(-1) === '--version') {
      return { value: { exitCode: opts.probe?.(e.argv) ?? 0, stdout: 'Python 3.13.2', stderr: '' } }
    }
    const exitCode = opts.fallback && !e.init?.env?.BELKI_DIR ? 1 : 0
    return { value: { exitCode, stdout, stderr: '' } }
  })
  on('turn.complete', () => ({ text: '' }))
  on('ui.render', ($: any, e: any) => $.ui.resolve(e).Text({ children: 'engine band' }))
  return calls
}

const START = { surface: 'terminal', isInteractive: true, cwd: '/work' } as any
const SCRIPT = '/home/test/.claude/skills/todo/scripts/belki.py'

describe('belki-band', () => {
  test('uses python when python3 exits nonzero, and probes only once per session', async ($, on) => {
    const calls = engine(on, SUMMARY, { probe: argv => argv[0] === 'python3' ? 1 : 0 })
    await $.session.start(START)
    await $.turn.complete({ reason: 'answer', answer: 'ok', durationMs: 1 } as any)
    expect(calls.map(c => c.argv)).toEqual([
      ['python3', '--version'],
      ['python', '--version'],
      ['python', SCRIPT, 'summary', '--days', '0'],
      ['python', SCRIPT, 'summary', '--days', '0'],
    ])
  })

  test('uses py -3 when earlier launchers exit nonzero', async ($, on) => {
    const calls = engine(on, SUMMARY, { probe: argv => argv[0] === 'py' ? 0 : 1 })
    await $.session.start(START)
    expect(calls.map(c => c.argv)).toEqual([
      ['python3', '--version'],
      ['python', '--version'],
      ['py', '-3', '--version'],
      ['py', '-3', SCRIPT, 'summary', '--days', '0'],
    ])
  })

  test('uses USERPROFILE for the script and fallback when HOME is unset', async ($, on) => {
    const calls = engine(on, SUMMARY, { env: { USERPROFILE: 'C:/Users/test' }, fallback: true })
    await $.session.start(START)
    expect(calls[1].argv).toEqual(['python3', 'C:/Users/test/.claude/skills/todo/scripts/belki.py', 'summary', '--days', '0'])
    expect(calls[1].init?.env).toBeUndefined()
    expect(calls[2].argv).toEqual(calls[1].argv)
    expect(calls[2].init?.env).toEqual({ BELKI_DIR: 'C:/Users/test/work-brain/_belki_files' })
  })

  test('WORK_BRAIN_DIR overrides the fallback after trying cwd first', async ($, on) => {
    const calls = engine(on, SUMMARY, { env: { HOME: '/home/test', WORK_BRAIN_DIR: 'D:/brain' }, fallback: true })
    await $.session.start(START)
    expect(calls.length).toBe(3)
    expect(calls[1].argv).toEqual(['python3', SCRIPT, 'summary', '--days', '0'])
    expect(calls[1].init?.env).toBeUndefined()
    expect(calls[2].argv).toEqual(calls[1].argv)
    expect(calls[2].init?.env).toEqual({ BELKI_DIR: 'D:/brain/_belki_files' })
  })

  test('BELKI_HELPER replaces the default helper path', async ($, on) => {
    const calls = engine(on, SUMMARY, { env: { HOME: '/home/test', BELKI_HELPER: '/brain/.claude/skills/todo/scripts/belki.py' } })
    await $.session.start(START)
    expect(calls[1].argv).toEqual(['python3', '/brain/.claude/skills/todo/scripts/belki.py', 'summary', '--days', '0'])
  })

  test('preserves python3 and HOME with the default work-brain fallback', async ($, on) => {
    const calls = engine(on, SUMMARY, { env: { HOME: '/home/test', USERPROFILE: 'C:/Users/ignored' }, fallback: true })
    await $.session.start(START)
    expect(calls.map(c => c.argv)).toEqual([
      ['python3', '--version'],
      ['python3', SCRIPT, 'summary', '--days', '0'],
      ['python3', SCRIPT, 'summary', '--days', '0'],
    ])
    expect(calls[2].init?.env).toEqual({ BELKI_DIR: '/home/test/work-brain/_belki_files' })
  })

  test('summarize drops recurring overdue tasks', () => {
    expect(summarize(SUMMARY)).toEqual({ overdue: 1, today: 1, chase: 1, first: 'Email the vendor' })
  })

  for (const surface of ['terminal', 'desktop'] as const) {
    test(`shows counts on ${surface}, hides on press`, async ($, on) => {
      engine(on, SUMMARY)
      await $.session.start({ surface, isInteractive: true, cwd: '/work' } as any)
      const band = await $.ui.mount({ plugin: 'belki-band', surface, ...BAND } as any)
      expect(await band.find({ type: 'Text', text: /Belki: 1 overdue · 1 due today · 1 to chase/ })).toBeDefined()
      await band.press({ key: 'hide' })
      expect(await band.find({ type: 'Text', text: /engine band/ })).toBeDefined()
      await band.unmount()
    })
  }

  test('nothing due: engine draws its own', async ($, on) => {
    engine(on, JSON.stringify({ overdue: [], due_soon: [] }))
    await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' } as any)
    const band = await $.ui.mount({ plugin: 'belki-band', surface: 'terminal', ...BAND } as any)
    expect(await band.find({ type: 'Text', text: /engine band/ })).toBeDefined()
    await band.unmount()
  })
})
