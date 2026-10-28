---
name: todo
description: Manage the Belki task list (the `_belki_files/` markdown store in this repo, shown in Obsidian's Belki plugin). Use when the user says "/todo", "add to my list", "what's on my list / due today / overdue", "mark X done", "what am I owed", "who do I need to chase", or "what fell through the cracks" (the sweep verb). Also the write path other skills use to park action items (meeting-ingest, wrap-up). NOT for workstream state (STATUS.md).
effort: medium
---

# /todo: Belki tasks, with waiting-on and deadlines

**Rules first:**
- **`scripts/belki.py` is the only write path.** Never hand-edit `_belki_files/Data/*.md` with Edit/Write,
  and never open those files in an editor pane (Obsidian has them open; the helper writes atomically and verifies).
- **Never write a line Belki wouldn't write.** The helper enforces format, unique ids, dedupe, LF endings.
- **Deadline discipline:** every add gets `--due`. If the source gave no date, propose one (default: 5
  business days) or ask "no date?". Undated is allowed only when the user confirms it.
- **Waiting-on:** if someone else owes the item, add it with `--waiting-on "<Name (team)>"`. The helper adds
  the `waiting` label so the item filters in Belki's UI.
- Never delete tasks (that's the user's, in the UI). Never touch `repeat::` tasks.
- Mention every write in one line in the same turn.

Helper: `python3 .claude/skills/todo/scripts/belki.py <verb>` (finds `_belki_files/` by walking up from cwd;
`BELKI_DIR` overrides).

## Verbs

- **add**
  ```bash
  python3 .claude/skills/todo/scripts/belki.py add "Title" --due YYYY-MM-DD [--project <workstream>] \
    [--priority P1-P4] [--description "from meetings/<note>.md"] [--waiting-on "Name (team)"] [--claude]
  ```
  `--project` = the `projects/<name>` workstream (omit for Inbox). Convert relative dates ("Friday") to
  absolute ones. Pass `--claude` for Claude-initiated adds. Dedupe is enforced (same open title + project is refused).
- **list**: `belki.py list` → group by project, overdue first. Filter by project, person, or `waiting:` on request.
- **summary**: `belki.py summary [--days N]` → JSON `{overdue, due_soon, waiting, undated}`. Waiting-on items
  appear only in `waiting` (each with `who`, `due`, `stale`). `stale` = past due, or undated and added more
  than 7 days ago. The script does the date math; you narrate.
- **done**: `belki.py done <id | unique title substring>`. Ambiguous → rerun with the id.
- **sweep** ("what fell through the cracks"), read-only, then propose:
  1. `summary --days 7`: overdue Mine items, oldest first.
  2. `waiting` items with `stale: true`: who to chase, for what, how late. Offer to draft the nudges; never send.
  3. `undated` > 0: list those tasks and propose dates.
  4. Open tasks whose `description` links a meeting note that marks them resolved: propose `done` (ask first).
  At most about 10 lines, chase list last.

## Proactive adds

Only work follow-ups that would otherwise be lost (a parked next step, a commitment made in a meeting).
Dedupe first; soft cap about 3 per session, past that list the candidates and ask.

## If Data/ is empty

The helper refuses to add to an empty store (calibration). The kit ships one seed task. If it was deleted,
ask the user to create any task in the Belki UI first.
