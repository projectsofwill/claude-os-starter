import { describe, expect, test } from 'claude-code/testing'

import { count } from '../hooks/register'

const lines = (sign: string, n: number) => Array.from({ length: n }, (_, i) => `${sign}line ${i}`)
const result = (tool: string, output: unknown, isErrored = false) => ({
  component: 'ToolResult',
  requestId: 't1',
  props: { tool_use_id: 't1', tool, output, isErrored },
})

function engine(on: any) {
  on('ui.render', ($: any, e: any) => $.ui.resolve(e).Text({ children: 'engine diff' }))
}

describe('diff-fold', () => {
  test('count tallies added and removed lines', () => {
    expect(count([{ lines: [' ctx', '+a', '+b', '-c'] }, { lines: ['-d'] }])).toEqual({ added: 2, removed: 2 })
  })

  test('folds a big Edit diff to one line', async ($, on) => {
    engine(on)
    const row = await $.ui.mount({ plugin: 'diff-fold', surface: 'terminal', ...result('Edit', { structuredPatch: [{ lines: [...lines('+', 18), ...lines('-', 1)] }] }) } as any)
    expect(await row.find({ type: 'Text', text: /edited · \+18 −1 \(folded\)/ })).toBeDefined()
    expect(await row.find({ type: 'Text', text: 'engine diff' })).toBeUndefined()
    await row.unmount()
  })

  test('folds a big new file', async ($, on) => {
    engine(on)
    const row = await $.ui.mount({ plugin: 'diff-fold', surface: 'terminal', ...result('Write', { type: 'create', content: lines('', 40).join('\n') + '\n', structuredPatch: [] }) } as any)
    expect(await row.find({ type: 'Text', text: /created · \+40 −0/ })).toBeDefined()
    await row.unmount()
  })

  test('folds a one-line edit too', async ($, on) => {
    engine(on)
    const row = await $.ui.mount({ plugin: 'diff-fold', surface: 'terminal', ...result('Edit', { structuredPatch: [{ lines: ['-a', '+b'] }] }) } as any)
    expect(await row.find({ type: 'Text', text: /edited · \+1 −1 \(folded\)/ })).toBeDefined()
    await row.unmount()
  })

  test('folds long Bash output, stdout and stderr together', async ($, on) => {
    engine(on)
    const row = await $.ui.mount({ plugin: 'diff-fold', surface: 'terminal', ...result('Bash', { stdout: lines('', 8).join('\n') + '\n', stderr: lines('', 5).join('\n') }) } as any)
    expect(await row.find({ type: 'Text', text: /^ran · 13 lines \(folded\) · line 4$/ })).toBeDefined()
    await row.unmount()
  })

  test('folds files a Bash command edited, empty output draws as usual', async ($, on) => {
    on('ui.render', ($: any, e: any) => $.ui.resolve(e).Text({ children: e.props.output.bashEditDiff ? 'engine diff' : 'engine stdout' }))
    const bashEditDiff = { files: [{ filePath: '/x.py', hunks: [{ lines: [' a', '-b', '+c', '+d'] }] }], moreFiles: 0 }
    const row = await $.ui.mount({ plugin: 'diff-fold', surface: 'terminal', ...result('Bash', { stdout: '', stderr: '', bashEditDiff }) } as any)
    expect(await row.find({ type: 'Text', text: /edited 1 file · \+2 −1 \(folded\)/ })).toBeDefined()
    expect(await row.find({ type: 'Text', text: 'engine stdout' })).toBeDefined()
    expect(await row.find({ type: 'Text', text: 'engine diff' })).toBeUndefined()
    await row.unmount()
  })

  test('folds a notebook cell edit and PowerShell output', async ($, on) => {
    engine(on)
    const cell = await $.ui.mount({ plugin: 'diff-fold', surface: 'terminal', ...result('NotebookEdit', { new_source: 'a\nb\nc', old_source: 'a' }) } as any)
    expect(await cell.find({ type: 'Text', text: /edited cell · \+3 −1 \(folded\)/ })).toBeDefined()
    await cell.unmount()
    const ps = await $.ui.mount({ plugin: 'diff-fold', surface: 'terminal', ...result('PowerShell', { stdout: 'a\nb\nc\n', stderr: '' }) } as any)
    expect(await ps.find({ type: 'Text', text: /^ran · 3 lines \(folded\) · c$/ })).toBeDefined()
    await ps.unmount()
  })

  test('errors, Bash output of 2 lines or fewer, and other tools draw as usual', async ($, on) => {
    engine(on)
    for (const r of [
      result('Edit', { structuredPatch: [{ lines: lines('+', 40) }] }, true),
      result('Bash', { stdout: '', stderr: '' }),
      result('Bash', { stdout: '61 passed\nexit=0\n', stderr: '' }),
      result('Read', { content: lines('', 40).join('\n') }),
    ]) {
      const row = await $.ui.mount({ plugin: 'diff-fold', surface: 'terminal', ...r } as any)
      expect(await row.find({ type: 'Text', text: 'engine diff' })).toBeDefined()
      await row.unmount()
    }
  })
})
