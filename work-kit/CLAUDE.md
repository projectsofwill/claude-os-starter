# Work brain: router

You're working with **<Name>**, <role> on the <team> team at <company>. This repo is Claude's private
working memory for that job. It is a router: read the file that fits the task, don't restate it here.

**Budget profile: subscription** <!-- subscription | metered. Set on day 1; rules in BUDGET.md -->

## Where things are

- `context/about-me-work.md`: role, manager, team, goals this quarter. Read when reasoning about priorities.
- `context/working-style.md`: how to work with me. Always applies.
- `context/brand-voice.md`: **read before drafting anything sent under my name** (email, Slack, docs).
- `CONTEXT.md`: the glossary (metric definitions, stage names, fields, each with a source of truth).
  Use its terms exactly. If a request uses an undefined term, pin it (`/prompt-enhancer`) before querying anything.
- `revops/`: `stack-map.md` (GTM systems, objects, automations, owners), `queries.md` (saved queries: what
  each answers and what it ties to), `changelog.md` (every production change, gated or not).
- `analysis/`: one folder per data question (query + notes with the tie-out). Raw exports are gitignored.
- `STATUS.md`: dashboard, one line per workstream. Each workstream's handoff is `projects/<name>/STATUS.md`.
  A workstream is **recurring** (forecast, QBR prep: STATUS + a `## Runbook` improved each cycle) or a
  **project** (an integration, a quota plan: STATUS with a target date). Open a folder only for work that
  spans more than one session; smaller asks are Belki tasks.
- `_belki_files/`: tasks (Obsidian's Belki plugin is the UI). Every task has a due date; items someone
  else owes carry `waiting_on::`. Write only through `/todo` (its `belki.py`), never by hand.
- `meetings/`: processed meeting notes (`/meeting-ingest`). `meetings/raw/` holds transcripts, gitignored.
- `people/`: stakeholder cards.
- `memory/MEMORY.md`: durable facts, one per file, auto-loaded each session (setup symlinks Claude Code's
  auto-memory folder here, so there is one store). Moving status goes in STATUS, not memory.
- Each folder with 2+ files has an `index.md`. Read it before opening files there, and update it when you add, remove, or rename files.

## House rules

- **Company data stays here.** Never copy work content into a personal account, personal repo, or personal
  AI tool. Git remote: company-approved host only, never a personal GitHub.
- **Company systems are the source of truth.** This repo links to them and doesn't mirror them. Promote
  finished, team-useful artifacts (approved definitions, stack map, decisions) to the company wiki, then
  add `promoted:: <link>` to the source note.
- **People cards:** write every card as if the person will read it. Roles, priorities, asks, decisions.
  No judgments or gossip. Cards are never promoted.
- **Secrets** live only in a gitignored `.env`. Never paste one into chat or a committed file.
- **Confirm first** before deleting/overwriting anything you didn't create, and before anything outward-facing
  (sending, posting, writing to a shared system).
- **State as you go:** refresh the workstream's STATUS `## Now` / `## Next` at each milestone or commit, not
  only at `/wrap-up`. Commit completed work with a descriptive message, staging specific files.
- **Done means verified.** Don't claim tested unless it ran (give the command + result). Use the real exit
  code. Zero rows or zero tests counts as a failure to explain, not a pass.
- **Clarify only when it changes the result.** Otherwise state the assumption and proceed. Give options with
  a recommendation when tradeoffs differ.

## Grounding (don't guess)

- **Numbers and facts carry a source.** Every metric, date, owner, or config claim names where it came from
  (a file here, a CRM report, a meeting note). Not checked → say "unverified". Never state a number from memory.
- **Numbers tie out.** Before a number leaves this repo, reconcile it to an independent total in the source
  system and record both (`analysis/README.md`). No tie-out: label it "unreconciled".
- **Terms come from `CONTEXT.md`.** A term that isn't defined there, or still says `<confirm>`, gets pinned
  with me before it drives a query or a number.
- **Quotes vs reasoning.** Text an AI quotes from a file or a command's output is evidence. An AI's
  explanation of how something works (including yours and a subagent's) is a hypothesis: verify it against
  the system before acting on it, especially before RevOps-gate work.
- **Look before answering.** For "what did we decide / who owns / what's the status", check STATUS
  `## Decisions`, `meetings/`, `people/`, and `memory/` first (indexes, then grep). If nothing's recorded, say so.

## RevOps gate (before high-consequence changes)

Before any of these: **bulk CRM writes/merges/imports/deletes, prod workflow or automation changes,
comp/quota/forecast numbers going to leadership, or anything customer-facing**:

1. Dry-run or sandbox first, and show the row count and a sample of what would change.
2. Take a backup export of the affected records/config.
3. Critique: a different-model reviewer if the company provides one, otherwise an Opus subagent with the
   literal change + intent. Incorporate material findings.
4. Get my explicit go.
5. For a system or data change, after it runs: add the entry to `revops/changelog.md` (why, scope, backup, rollback, verified).

## Models and delegation

Follow the active profile in `BUDGET.md`. Delegate a slice to a subagent only when it's self-contained and
only its conclusion needs to come back (e.g. a long transcript → `/meeting-ingest`'s Haiku extractor).
Verify a subagent's reasoning before acting on it.
