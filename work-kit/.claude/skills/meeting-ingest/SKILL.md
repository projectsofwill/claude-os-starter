---
name: meeting-ingest
description: Turn meeting recordings/transcripts into structured notes, tasks, and stakeholder updates. Use when the user says "/meeting-ingest", "ingest today's meetings", "process my meetings", "process this transcript", or drops a transcript into meetings/raw/. Sources are a recorder connector (e.g. Granola, Gong) or files in meetings/raw/. On-demand only, never scheduled.
---

# /meeting-ingest: transcripts → notes, tasks, people

**Rules first:**
- **Never read a long transcript in the main loop.** Over the size threshold (step 2), a Haiku subagent
  extracts and the main loop reads only its extract. This is the skill's main cost control.
- **Shared references are proposals.** New terms, changed definitions (`CONTEXT.md`) and system facts
  (`revops/stack-map.md`) are listed for approval and edited only on the user's OK. A project's `## Next` is
  flagged, never rewritten.
- **People-card rule:** write every card as if the person will read it (role, priorities, asks, decisions).
  No judgments or gossip. If a meeting is HR-sensitive (performance, comp of a named person, personal matters),
  skip people-card updates for it and say so.
- **Idempotent.** A source already referenced by a note's `source:` field is skipped, never re-ingested.
- Nothing leaves the repo: no posting, emailing, or wiki writes from this skill.

## Arguments

- `today` (default) / `yesterday` / a date: every unprocessed meeting from that day.
- A path: that file only.
- A meeting name: match it in the connector or `meetings/raw/`.

## Steps

1. **Collect sources.**
   - Files: `meetings/raw/*` matching the date (filename or modified date). Skip any whose path already
     appears in a `source:` line under `meetings/*.md` (`grep -l "source: raw/<file>" meetings/*.md`).
   - Connector (if a recorder MCP is connected): list that day's meetings. **Prefer the recorder's own AI
     summary/notes.** Fetch the full transcript only when the summary has no decisions, owners, or numbers.
     Skip meetings whose `granola:<id>` (or equivalent) is already a `source:`.
   - If there's nothing to process, say so in one line and stop.

2. **Extract** into the schema below.
   - Small source (a summary, or a file under ~25 KB by `wc -c`): read it directly.
   - Large source: dispatch **one** subagent (`model: haiku`) for all large sources together. Give it the
     file paths or meeting IDs, the schema, and the list of terms in `CONTEXT.md` (headings only), and
     tell it to return only the filled schema per meeting, with no transcript excerpts beyond one-line quotes
     for decisions or numbers.

   **Schema** (per meeting): `title`, `date`, `attendees` (name, role/team if stated),
   `summary` (3-5 bullets), `decisions` (each with who decided), `my_actions` (task, due if stated),
   `others_commitments` (who, what, due if stated), `metrics` (figure + what it measures + period),
   `open_questions`, `new_terms` (terms used that aren't in CONTEXT.md, with how they were used),
   `definition_changes` (a decision that changes how a CONTEXT.md term is defined or calculated),
   `system_facts` (a GTM system, object, field, automation, integration or owner stated in the meeting),
   `project` (best match among `projects/*/`, or none).

3. **Write the note** `meetings/YYYY-MM-DD-<slug>.md`:

   ```markdown
   ---
   date: YYYY-MM-DD
   title: <title>
   attendees: [<Name (team)>, ...]
   source: raw/<file> | granola:<id>
   project: <name or none>
   ---
   # <title> (YYYY-MM-DD)

   ## Summary
   ## Decisions
   ## Action items
   ### Mine
   ### Waiting on
   ## Metrics mentioned
   ## Open questions
   ```
   Omit empty sections. Link people as `[Name](../people/<name>.md)` when a card exists.

4. **Tasks.** Add each `my_actions` item and each `others_commitments` item (with `--waiting-on "<who>"`)
   with this repo's helper, `python3 .claude/skills/todo/scripts/belki.py add "<title>" --due <date>` (the
   `/todo` rules apply): `--project` = the matched workstream, `--description "from meetings/<note>.md"`,
   `--claude`. Every item gets `--due`: the stated date, else propose one in the report and ask (deadline
   discipline). Dedupe is enforced by the helper; a refused duplicate is reported, not retried.

5. **People.** For each attendee who has a card in `people/`, or who appears in two or more notes: create
   the card from `people/_template.md` if missing, then update `last touch`, append to `cares about` /
   `open asks` only when the meeting showed something new. One line per change.

6. **Projects.** If `project` matched, in that `projects/<name>/STATUS.md`:
   - append each decision to `## Decisions`, dated, with a link to the note;
   - append each open question to `## Open questions`, with a link to the note (skip one already listed);
   - if a decision or commitment changes what's next, don't edit `## Next`: flag it in the report.

7. **Report** (short): meetings processed, notes written, tasks added (Mine / Waiting on), people updated,
   STATUS lines added. Then the proposals, each a list with one question:
   - **Glossary candidates** (`term: how it was used`): "Add any to CONTEXT.md?" On a yes, add them in
     CONTEXT.md's format with `<definition to confirm>` where the meeting didn't define the term.
   - **Definition changes** (`term: current definition -> what was decided`, with the note link):
     "Update CONTEXT.md?"
   - **Stack-map updates** (`system: fact`, with the note link): "Update revops/stack-map.md?"
   - **Next may change** (`project: why`): "Update ## Next?"

## Budget note

Under `Budget profile: metered` (see `BUDGET.md`), batch the whole day in one run and one subagent dispatch.
Don't re-ingest to "improve" a note: edit the note directly.
