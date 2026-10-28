---
name: prep
description: Prep for a meeting or 1:1 from what this repo already knows. Use when the user says "/prep <person or meeting>", "prep me for my 1:1 with X", "what do I need for the <meeting>", or "what's open with X". Read-only.
---

# /prep: meeting brief from the repo

Read-only: builds a one-screen brief from people cards, meeting notes, Belki tasks, and STATUS. Every line
links its source; if nothing is recorded, say so rather than guess. After the meeting, `/meeting-ingest`
does the writes.

## Arguments

- A person: `/prep Jordan`.
- A meeting: `/prep pipeline review`. Take the attendees from the latest note with a matching title
  (`grep -il "^title: .*<words>" meetings/*.md`).
- Several people: one section each, shared items once.

## Steps

1. **Card:** `people/<name>.md` (match the filename or the `# ` heading): role, cares about, open asks,
   context. No card: say so.
2. **History:** the last 3 notes in `meetings/` that list them (`grep -l "<Name>" meetings/*.md`, newest
   first). Pull decisions and open questions only, with links.
3. **Owed both ways:** `python3 .claude/skills/todo/scripts/belki.py list`. They owe me: tasks with
   `waiting:<name>`. I owe them: my open tasks whose title or project ties to them or their asks. Overdue first.
4. **Projects:** for projects tied to them (their notes' `project:` field, or their card), the `## Now` and
   `## Open questions` of `projects/<name>/STATUS.md`.
5. **Brief** (omit empty lines):

   ```markdown
   ## Prep: <person or meeting> (<date>)
   **They care about:** ...
   **Since last time:** decisions and changes since <last note date>
   **I owe them:** ... (due)
   **They owe me:** ... (due, overdue first)
   **Open questions to raise:** ...
   **Suggested agenda:** 3 bullets max
   ```

## Rules

- No edits to cards, tasks, or STATUS.
- The people-card rule applies to the brief: no judgments.
- Read files directly; no subagent (the inputs are small).
