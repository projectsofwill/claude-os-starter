// Diff Fold: every Edit/Write diff, Bash-made diffs, and Bash output over BASH_MAX_LINES, becomes
//   one dim line in the transcript. Raise MAX_LINES to keep diffs that small
//   visible. Display only: the edit, the stored result and what the model reads
//   are untouched. `git diff` shows a folded change in full.
import type { Register } from 'claude-code'

export const MAX_LINES = 0 // fold everything; a no-op write (+0 −0) draws as usual
export const BASH_MAX_LINES = 2 // 1-2 line summaries (exit=0, 61 passed) stay visible: folding saves no space
export const INDENT = 4 // sit under the tool row's ⎿ (prismantis tree toolStyle), not at column 0
export const MUTED = '#444c56' // fixed muted grey, matches prismantis's toolColor default; terminal faint is too bright on dark themes

type Hunk = { lines: string[] }

export const register: Register = on => {
  on('ui.render', { component: 'ToolResult' }, async ($, e, next) => {
    const { tool, output, isErrored } = e.props
    if (isErrored) return next(e)
    if (tool === 'Bash' || tool === 'PowerShell') { // PowerShell (PC): assumed same stdout/stderr shape
      // bashEditDiff: files the command itself changed (sed, a script); the engine draws them as full diffs
      const { stdout = '', stderr = '', bashEditDiff } = output as { stdout?: string; stderr?: string; bashEditDiff?: { files: { hunks: Hunk[] }[]; moreFiles: number } }
      const n = lineCount(stdout) + lineCount(stderr)
      const files = bashEditDiff?.files ?? []
      if (n <= BASH_MAX_LINES && files.length === 0) return next(e)
      const { Box, Text } = $.ui.resolve(e)
      const { added, removed } = count(files.flatMap(f => f.hunks))
      const nFiles = files.length + (bashEditDiff?.moreFiles ?? 0)
      const edits = files.length ? <Box paddingLeft={INDENT}><Text color={MUTED}>{`edited ${nFiles} file${nFiles === 1 ? '' : 's'} · +${added} −${removed} (folded)`}</Text></Box> : null
      // last non-blank line: usually the summary (61 passed, exit=0); truncated, never wraps
      const last = `${stdout}\n${stderr}`.split('\n').findLast(l => l.trim())?.trim()
      if (n > BASH_MAX_LINES) return <Box flexDirection="column"><Box paddingLeft={INDENT}><Text color={MUTED} wrap="truncate-end">{`ran · ${n} lines (folded)${last ? ` · ${last}` : ''}`}</Text></Box>{edits}</Box>
      const { bashEditDiff: _, ...rest } = output as Record<string, unknown>
      return <Box flexDirection="column">{await next({ ...e, props: { ...e.props, output: rest } })}{edits}</Box>
    }
    if (tool === 'NotebookEdit') {
      // whole-cell line counts, not a line diff: the result carries old and new cell source only
      const { new_source = '', old_source = '' } = output as { new_source?: string; old_source?: string }
      const { Box, Text } = $.ui.resolve(e)
      return <Box paddingLeft={INDENT}><Text color={MUTED}>{`edited cell · +${lineCount(new_source)} −${lineCount(old_source)} (folded)`}</Text></Box>
    }
    if (tool !== 'Edit' && tool !== 'Write') return next(e)
    const out = output as { structuredPatch?: Hunk[]; type?: string; content?: string }
    const created = out.type === 'create'
    const { added, removed } = created ? { added: lineCount(out.content ?? ''), removed: 0 } : count(out.structuredPatch ?? [])
    if (added + removed <= MAX_LINES) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    return <Box paddingLeft={INDENT}><Text color={MUTED}>{`${created ? 'created' : 'edited'} · +${added} −${removed} (folded)`}</Text></Box>
  })
}

export function count(hunks: Hunk[]) {
  let added = 0
  let removed = 0
  for (const h of hunks)
    for (const l of h.lines) {
      if (l.startsWith('+')) added++
      else if (l.startsWith('-')) removed++
    }
  return { added, removed }
}

export function lineCount(text: string) {
  return text === '' ? 0 : text.split('\n').length - (text.endsWith('\n') ? 1 : 0)
}
