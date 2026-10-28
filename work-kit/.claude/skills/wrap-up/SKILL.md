---
name: wrap-up
description: End-of-session handoff. Use when the user types "/wrap-up", or wants to end a work session, save progress, or write a handoff so the next session picks up cleanly, including "done for the day", "save where we are", or before a /clear. Writes current state, next steps, open questions, and decisions into STATUS.md so /catchup can restore context. Pairs with /catchup.
---

# /wrap-up: write the session handoff

Record where things stand so the next session resumes without re-deriving everything. Live status lives
in `STATUS.md`. Durable facts go to `memory/` instead.

**Be fast.** Every tool call re-sends the whole session. STATUS should already be refreshed at milestones
(router rule "state as you go"), so wrap-up is usually a small delta. History lives in git, never in STATUS.

## Steps

1. **Find the handoff.** The workstream touched this session has `projects/<name>/STATUS.md` (create it
   from `projects/_template/STATUS.md` if missing). Root `STATUS.md` is the dashboard.

2. **Reconstruct the session** from the conversation plus `git status -s`, `git diff --stat`,
   `git log --oneline -10`. Reference artifacts by path; don't duplicate them.

3. **Update the project `STATUS.md`** (a handoff, not a transcript):
   - **`## Now`**: rewrite. Where things stand, what's in progress (2-5 lines).
   - **`## Next`**: rewrite. Unblocked next steps, most important first, specific enough to act on cold.
   - **`## Open questions`**: unresolved items or things waiting on someone.
   - **`## Decisions`**: append this session's decisions, dated, each with a one-line *why*.
     **Supersede, never overwrite:** if a new decision reverses an old line, strike the old one through and
     add the reason: `- ~~<date>: <old>~~ superseded <today>: <why>`, then the new line below it.

4. **Update the root dashboard.** Refresh this workstream's one line in root `STATUS.md` (date + focus)
   and put its top `## Next` item into root `## Next`, prefixed `[<name>]`, replacing any older
   `[<name>]` item.

5. **Park loose ends.** Concrete follow-ups that don't belong in `## Next` become Belki tasks via the
   `/todo` add path (due date required, dedupe enforced). Commitments someone else owes get `--waiting-on`.

6. **Commit** the files you wrote (`wrap-up: <workstream>: <one-line summary>`), staging only those files.
   Push only to the company-approved remote, if one is configured. Never to a personal account.

7. **Confirm in one or two lines**: what you wrote, and the top `## Next` item /catchup will open with.
