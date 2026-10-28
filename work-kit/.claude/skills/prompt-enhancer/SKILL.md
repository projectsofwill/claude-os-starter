---
name: prompt-enhancer
description: Transform a rough, informal request into a rigorous, execution-ready specification before Claude acts on it. Use when the user prefixes a request with "/prompt-enhancer", asks to "build an agent", "build a skill", "build a profile", "automate", or "build a report", or when a request involves ambiguous business or RevOps terms that must be pinned before any work runs.
---

# Prompt Enhancer

## Purpose

Rough requests produce rough work. This skill pins ambiguous terms, classifies what's actually being built, and produces a spec someone could execute from — with every assumption made visible and auditable before any data is queried or any agent runs.

It is an explainability layer, not a clever-prompt generator. Narrow scope + stated assumptions + a human checkpoint beats silently guessing.

## Step 0 — Classify the build class

Read the request and assign one of:

| Class | When to use |
|---|---|
| **CLAUDE-SKILL** | Building a new Claude Code skill in `.claude/skills/` — invoked by `/skill-name` in sessions |
| **REVOPS-AUTOMATION** | A CRM data agent, report, pipeline monitor, or alert touching live CRM data |
| **GENERAL-AUTOMATION** | Any other recurring automation, workflow, or integration not covered above |
| **LEAN** | A one-off prompt sharpening or "rewrite this" request — no system to build |

State the build class at the top of the output. If ambiguous, ask one question to resolve it before proceeding.

## Step 1 — Disambiguate

Before producing any output, scan the request for ambiguous terms and pin each to a precise definition. State every assumption in the "Assumptions" block — never bury them. For REVOPS-AUTOMATION, use the RevOps disambiguation reference at the end of this skill.

---

## CLAUDE-SKILL spec

For building a new skill in `.claude/skills/`. First read `.claude/skills/writing-great-skills/SKILL.md` — the reference on making a skill predictable (vocabulary, determinism, the levers below). Apply it alongside this spec; it is the fuller version of the Quality checklist.

### Assumptions
Bulleted list — what the skill does, what triggers it, what it must not do.

### Intent
One paragraph: what problem this skill solves, when it activates, what it produces, how it hands off.

### Trigger conditions
Exact phrases or request patterns that should invoke this skill (these go in the `description:` frontmatter).

### Procedure
Numbered steps the skill executes. Each step is concrete and ordered. Note which steps are read-only vs. write (anything that edits files or calls external services). Flag any step that should require the user's approval before proceeding.

### Constraints and non-goals
- What this skill must NOT do (scope guard)
- What's explicitly out of scope

### Acceptance criteria
How to know the skill worked — specific, observable outputs.

### Output format
What the skill surfaces to the user: sections, structure, length, tone.

### RevOps gate
Does this skill write to the CRM, change a prod automation, or send numbers to leadership or customers? If yes, the router's RevOps gate applies (dry-run, backup export, critique) before its first real run. Note it here.

### Quality checklist (required — verify before declaring the spec done)

1. **Description-as-trigger:** Does the `description:` field read as trigger conditions ("Use when the user says X / wants Y"), not a label or internal procedure? Claude pattern-matches on this to auto-invoke. Trim any procedural tail; keep trigger phrases and behavior constraints only.
2. **Verification-first:** Does the skill mutate state (write files, commit, run scripts, update docs)? If yes: does each write step verify the target exists and is in the expected state before acting? Add a guard ("verify X exists; if missing, stop and tell the user") for every write step that assumes a precondition.
3. **Folder power:** Does the skill live in `.claude/skills/<name>/SKILL.md` and carry everything it needs? No cross-skill imports, no implicit session state it doesn't establish itself. Note any external dependencies (like referencing another repo's doc) explicitly with "if X is missing, stop."
4. **Baseline delta:** Name 2–3 concrete prompts that should trigger this skill. For each, state what Claude does *without* it. If you can't articulate a meaningful difference for any of them, the skill doesn't earn its context load — tighten the scope or drop it.

### Gotchas
Environment-specific quirks to hardcode into the skill (markdown formatter behavior, git remotes, connector rate limits, etc.).

---

## REVOPS-AUTOMATION spec

For CRM data agents, pipeline monitors, reports, and alerts. All 10 sections; mark optional ones where noted.

### 1. Assumptions
Bulleted list translating every ambiguous term to a precise definition. Include which object/field/connector, delivery/audience/timing interpretation.

### 2. Intent
One tight paragraph: trigger, what it identifies, what analysis, what it delivers, to whom, when.

### 3. Action
Numbered build steps, concrete and ordered. Show filter logic in pseudo-SQL where a step queries data. Show structure or message template where a step produces a deliverable. Typical flow: capture cohort (with snapshot if forecast/stage history matters) → pull supporting records → pull call/conversation data → synthesize per-item diagnosis → compose and deliver.

### 4. Data sources
Each as: object/entity — specific fields — system/connector. Flag any field whose API name must be confirmed in the target org.

### 5. Filters
Explicit query filters including `IsDeleted = false`, type/category filters, date-window filters, stage exclusions — each annotated with the point in time it applies.

### 6. Output format
Delivery channel and timing; structure (executive summary → per-item blocks → pattern synthesis); fields in each per-item block; fallback for large item counts.

### 7. Metrics *(optional — include for recurring agents, skip for one-off reports)*
Measurable KPIs the agent tracks over time, each with a definition and benchmark. Prefer metrics that turn the agent's own activity into a health signal (coverage rate, signal-miss rate).

### 8. Attention *(optional — include when point-in-time or mutable-field risk is high)*
Critical caveats: mutable-field/snapshot risks, field-API-name variance by org config, connector retrieval gaps, and any distinction preventing over-flagging (legitimate managed push vs. unforecast slip).

### 9. Dependencies
Connectors and scope, field mappings, bot permissions, integrations, storage for snapshots — all must be configured before first run.

### 10. Closing and RevOps gate
Name the single trickiest part of the build and how to handle it. Note the compounding-value angle (how tracking the pattern over months turns per-item review into team-level coaching). Then: **"Before I start building this, I'll run the RevOps-gate critique if it applies. Confirm the spec above and I'll proceed."**

---

## GENERAL-AUTOMATION spec

For recurring automations not tied to CRM data.

### Assumptions
What the automation does, what triggers it, what it produces.

### Intent
One paragraph: trigger, logic, output, delivery, cadence.

### Steps
Numbered, concrete, ordered. Include error handling for each external call.

### Constraints and non-goals
What it must not do. What's out of scope.

### Acceptance criteria
Specific observable outputs that confirm it works.

### Dependencies
APIs, credentials, environment (local vs. cloud), scheduler (launchd/Task Scheduler/cron), secrets handling.

### Closing and RevOps gate
**"Before I start building this, I'll run the RevOps-gate critique if it applies. Confirm the spec and I'll proceed."** *(No critique for clearly reversible, low-risk single-file scripts.)*

---

## LEAN mode output

For one-off prompt sharpening — no system to build.

```
## Goal
<one sentence restating intent>

## Enhanced prompt
Objective: ...
Inputs / data sources: ...
Logic / steps: ...
Output format: ...
Delivery: ...
Edge cases: ...

## Assumptions made
- "<term>" = <precise definition>

## Constraints and non-goals
- Must NOT: ...
- Out of scope: ...

## Acceptance criteria
- <how to know this worked>

## Open questions
- <anything unresolved>

## Proceed?
Proceed with these assumptions, or adjust?
```

---

## RevOps term disambiguation reference

When any of these appear in a REVOPS-AUTOMATION request, pin to a concrete definition and state it in "Assumptions."

- **"New business"** → Opportunity Type = 'New Business', excluding renewals and expansions.
- **"Commit" / "Best case" / "Pipeline"** → `ForecastCategoryName`, evaluated as of a fixed point in time (default: last day of the month). Forecast category is mutable — always fix the date and snapshot it.
- **"Slip" / "pushed"** → CloseDate was in Month N but as of Month N+1 the deal is still open or closed later; OR forecast category downgraded between two snapshots. State which.
- **"Stale"** → no logged activity for N days (default: 14). State N.
- **"At-risk"** → list the signals explicitly (no champion, no economic buyer, vague critical event, compressed timeline, no mutual close plan, single-threaded, activity drop). Don't use the phrase without listing them.
- **"Stage X"** → the org's actual stage picklist values, not generic names. If unknown, flag as an open question.
- **"Segment" / "tier"** → the specific field and value cutoffs (e.g. Enterprise / Commercial / SMB by ACV band or employee count).
- **"Attainment" / "coverage"** → numerator and denominator stated explicitly.
- **"This month / quarter"** → fixed fiscal calendar with exact boundary dates, not relative phrasing.

## Principles

- **State assumptions, never bury them.** A wrong assumption caught at the checkpoint costs seconds; one caught after the agent messages leadership costs trust.
- **Pin every date and threshold.**
- **Snapshot mutable fields.** Forecast category, stage, and close date reflect current state; to analyze history you must freeze the cohort or use field history tracking.
- **Separate managed push from unforecast slip** so the agent doesn't flag legitimate, documented reschedules.
- **Narrow the scope.** If the request is doing three things, say so and confirm priority.
- **Critique before building.** Builds that trip the router's RevOps gate get a critique pass before execution. The spec is the input; incorporate findings before starting.
