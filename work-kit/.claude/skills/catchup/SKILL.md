---
name: catchup
description: Start-of-session catch-up. Use when the user types "/catchup", or asks "where did I leave off", "what's next", "catch me up", or wants to pick up a workstream at the start of a session. Reads STATUS.md (root dashboard + the active project's), Belki tasks, and recent git history, then reports where things stand and the top unblocked next step. Pairs with /wrap-up.
---

# /catchup: restore context and say what's next

Start a session warm. Read the last handoff and recent activity, then say exactly where things were left
and what's unblocked. Don't make the user re-explain the work.

## Steps

1. **Find the handoff.** Root `STATUS.md` is the dashboard (one line per workstream + the top `## Next`).
   If cwd is inside `projects/<name>/`, or the user names a workstream, its `projects/<name>/STATUS.md` is
   the primary handoff. Otherwise lead with the root `## Next`.

   **The handoff is the primary signal. Git is only reconciliation.** Brief from `## Now` / `## Next`
   first. If the git log disagrees about what's most recent, surface that as a staleness flag; don't
   switch handoffs because of it.

2. **Read the state** (few calls, the session pays for each one):
   - The handoff's `## Now`, `## Next`, `## Open questions`.
   - `git log --oneline -8` and `git status -s`.
   - Tasks: `python3 .claude/skills/todo/scripts/belki.py summary --days 7` (read-only JSON:
     `overdue`, `due_soon`, `waiting` with `stale`, `undated`).

3. **Report** (a briefing, keep it tight):
   - **Where you left off**: from `## Now`, reconciled against the latest commits.
   - **Next up**: the top 1-3 items from `## Next`.
   - **Tasks**: 1-3 lines. Overdue and due-soon items, then stale `waiting` items to chase (who, what,
     how late), then the `undated` count if > 0. Omit the line if all are empty.
   - **Open questions / watch-outs**: anything that needs the user before proceeding.
   - **In progress**: uncommitted changes, if any.

4. **Initialize TodoWrite** from `## Next` with the actionable items (short, outcome-focused). As items
   complete during the session, remove them from the matching `## Next` in the same pass.

5. **Offer to start** the top item. Wait for the user to confirm.

## If there's no STATUS.md

Say so plainly. Skim `CLAUDE.md` and `git log --oneline -10`, and suggest `/wrap-up` at the end of this
session to create the first handoff. Don't invent state that isn't recorded.
