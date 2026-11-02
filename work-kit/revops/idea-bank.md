# RevOps AI idea bank

Starting hypotheses for AI and automation work in RevOps, distilled from 19 issues of a weekly RevOps AI
newsletter (2026-06 to 2026-10; `#n` = issue number, kept for provenance). **These are ideas to test, not playbooks.** Playbooks are rebuilt against the
company's real stack and data (see `BACKLOG.md`). Anything that writes to a system still goes through the
RevOps gate in `CLAUDE.md`. Vendor claims and benchmarks from the issues are unverified.

How to use: when a request lands, scan the matching section for a pattern before designing from scratch.
When an idea gets built or ruled out, note it here with a link to the project folder.

## First 30 days: audit before building

- **Data-readiness gate.** Before any AI work, be able to explain the object model, field ownership,
  routing rules, attribution, and lifecycle stage entry/exit criteria, and which fields are trusted vs
  enrichment guesses. Can't? Sprint 1 is cleanup. (#3, #5, #17)
- **Metric definitions first.** Write down 3 core definitions (e.g. ARR, source, qualified conversion)
  with a source of truth each, into `CONTEXT.md`. Without them, every agent invents its own numbers. (#2)
- **One owner per critical field.** Name the source-of-truth system and owner for each field that drives
  routing, forecast, segmentation, or scoring, so two systems can't overwrite it. Require only those
  fields; validate at workflow boundaries (owner, stage, forecast category changes). (#9)
- **Tool inventory.** Every tool that touches a lead: owner, inputs, outputs, monthly cost, failure rate,
  unique function. Mark which system holds truth, which acts, which measures. Feeds `stack-map.md`. (#7, #9)
- **Platform dependencies.** Check which routing / matching / CPQ tools are tied to one CRM before any
  AI-CRM decision. (#6)
- **Access matrix.** One page: roles x tools x permission level. Find ghost users and orphaned records;
  automate the top recurring access requests later. (#3)
- **Process write-up per revenue workflow.** Plain-English current process, systems with read/write
  access, the top 3 fields an AI would need and their blank rate, and an adoption owner. (#3, #5)

## Usage-based revenue

- **Two forecasts.** Keep contracted ARR and consumption forecasts in parallel. Usage informs the
  consumption view; it never silently inflates committed ARR. (#7)
- **Warehouse holds the joined view.** Unify CRM, billing, and product usage in the warehouse; model
  eligibility there; sync *decisions* to the CRM (`active_buying_signal`, `signal_reason`,
  `recommended_motion`), not raw telemetry. Drop synced fields nobody uses. (#4, #12, #19)
- **Usage triggers gated by fit.** Nightly job for usage spikes/drops, funding, hiring, champion moves →
  write trigger type, date, and context to the CRM and task the owner, only for accounts that clear the
  ICP score. Triggers give timing, not fit. (#1, #5)
- **Product-led pipeline as its own cohort.** Tag source (PLG, inbound, partner, agent-sourced) and
  compare stage conversion, cycle length, and realized revenue per cohort before trusting any of it in
  the forecast. (#7)
- **Self-serve to sales handoff.** Decide explicitly which buyer interactions may skip human
  qualification; route only high-confidence matches to booking, the rest to a queue or nurture. (#19)
- **Churn and expansion health.** Combine CRM, billing, support, and usage into health scores with
  rescue and expansion plays; humans stay on strategic accounts. (#10)

## Forecast

- **Input-quality gates.** Block forecast category updates without a current next step and recent
  activity; compute a completeness score; flag phantom deals (stale activity, repeated close-date slips,
  stage moves without evidence). Keep customer evidence, system signals, and owner commit as separate
  fields. (#9)
- **Deterministic first, LLM writes the prose.** Compute coverage, stage aging, missing next step, and
  pushed close dates in code; snapshot opportunity state weekly; the LLM only summarizes the top changes
  per deal. (#8, #17)
- **Evidence-backed deal queue.** Every risk label carries evidence (a quote, an excerpt, or a missing-
  activity window); bucket Immediate / This week / Next week; AI proposes, rep edits. (#2, #10)
- **"Where do you disagree with the model?"** Run model flags beside manager commits for a full quarter
  without letting the model own the number; track whose overrides were right. Add a required risk-reason
  picklist. (#6, #8, #13)
- **Forecast-critical autofill only.** List the 8-12 fields the forecast depends on, autofill only those
  from calls, audit 20 calls a week against ground truth. (#4, #6)
- **Monte Carlo vs commit (prototype).** Per-deal close-probability distributions over open pipeline,
  compared to the CRM commit; the biggest disagreements become the forecast-call agenda. Backtest before
  trusting. (#4)
- **Vendor pilots.** Before buying forecast or revenue-intelligence tools, pick what matters most
  (accuracy, explainability, coaching, adoption) and run a time-boxed weighted pilot. (#13)

## Routing and scoring

- **Rules are the base; AI only for fuzzy fields.** Territory, round-robin, SLA, and exclusions stay
  deterministic; an LLM classifies only ambiguous inputs (free-text use case, ICP tier, urgency) with a
  confidence score; low confidence goes to a human queue. (#1, #3, #4, #11, #18)
- **Every routed record says why.** Write `routing_decision`, `routing_reason`, and a timestamp to the
  CRM; review misroutes weekly before widening coverage. (#8, #13, #17)
- **Three outcomes.** Route now / nurture / suppress, from ~5 decision fields; only "route now" reaches
  reps. Good first AI workflow. (#13)
- **Test rule changes on history.** Before changing routing or SLA rules, replay them against recent
  records ("who would have received the last 500?"). (#15)
- **Scoring closed loop.** One target outcome per model; ~5 fields sales already believes in; 3 score
  bands with explicit routing; show top drivers in the CRM; check monthly conversion by band and rep
  override rate. Refresh the ICP quarterly from recent closed-won deals. (#2, #10, #17)
- **Speed-to-lead nudge.** If a new lead has no activity after 30-45 min, DM the owner with a drafted
  opener; track touch-within-SLA. (#1)
- **Capacity-aware assignment.** Re-evaluate unworked records every 24h; audit fairness per rep (volume,
  conversion, response time, overrides). (#9)

## Low-risk first builds

Read-only or recommend-only; each fits one project folder.

- **Nightly hygiene job.** Dedupe, ownership and hierarchy fixes, domain mismatches; flag conflicts
  instead of overwriting; DM issues by severity. The foundation for everything else. (#2, #19)
- **Bounded nightly agent.** One job (stale-opp detection or missing-field enrichment); allowed actions:
  recommend, tag, create task. Log before/after/source/confidence. Measure fill rate and correction rate
  after 7 days. (#10, #12)
- **Deal-by-deal win/loss.** One segment, last 90 days, one AI pass per deal (never bulk), roll up 3-5
  patterns. Feeds the closed-lost playbook in `BACKLOG.md`. (#5)
- **Voice-of-customer themes.** Weekly themes from calls for product and enablement. (#2)
- **Reopen dormant records.** Closed-lost, stalled evals, old inbound → enrich for a change (role,
  funding, usage) and route only records with an actionable reopen reason. Backtest the signal first. (#7)
- **Signal capture from calls.** One category (stakeholder change or expansion mention) → exact quote +
  drafted action to the owner; write only to notes / non-forecast fields at first. (#10)
- **Small internal apps** to replace spreadsheet-plus-Slack request flows (territory exceptions, discount
  checks, renewal prep). Internal first, never customer-facing first. (#18)
- **Slack summaries in the forecast cadence.** Replace one report-pull step with a Slack deal summary for
  two weeks and compare. (#3)

## Governance (before any agent writes)

- **Build vs Run.** RevOps owns definitions, field permissions, routing policy, forecast, audit;
  whoever builds automation ships against those primitives; sales leadership owns behavior change. (#8,
  #9, #12, #17)
- **Spec before build.** Owner, inputs, rules, override path, success metric. (#7, #9)
- **Action tiers.** Auto: enrich empty fields, classify, summarize, flag, create internal tasks.
  Approval: owner, stage, forecast category, close date, amount, sequence enrollment. Never without policy
  review: consent overrides, suppressed contacts, comp-affecting fields. (#2, #4, #8, #12)
- **Autonomy ladder.** Observe → recommend with approval → auto-execute, promoted per play by measured
  precision (30-60 days per field) and eval results. No production write access without an owner, eval
  set, cost cap, and kill switch. (#8, #11, #16)
- **Least privilege.** Classify each tool as read / suggest / write / delete / external-send; start
  read-only; scoped OAuth per connector; log prompt, tool call, record, before/after. (#11, #15, #18)
- **Evals.** 50-200 labeled examples incl. edge cases, rerun before any prompt or schema change. (#15,
  #16)
- **Red-team the workflow.** Prompt injection via inbound forms, cross-account leakage, wrong writes,
  bad sends. (#15)
- **Execution log.** Inputs, decision, output, timestamp, outcome per automated run: debugging plus proof
  of pipeline influence. (#14, #17)
- **Check agent answers against a hand-built report.** Connectors often cap pulls at a few hundred to a
  few thousand records. (#2)

## Measuring it

- **Agent KPIs:** completion rate (not adoption), escalation rate, trust incidents, correction/override
  rate, touch-within-SLA. (#1, #5, #6)
- **Plays as products:** each has an owner, trigger, expected outcome, and a retirement condition; watch
  for decay. (#16)
- **Usage-priced vendors:** track enrichment credits as a RevOps metric; cheap source first, costly one
  only on a miss. (#10, #12)
- **Judge automation on outcomes:** routing accuracy, speed-to-lead, data quality, pipeline influenced,
  hours saved. (#7, #17, #19)

## Later (once more than one agent runs)

Shared-record leases and idempotency keys, one gateway with grants instead of per-agent credentials,
tool descriptions as contracts (purpose, when / when not, side effects), retrieval choice per workflow,
agent-assisted CRM migration with a read-only validator, quote-to-cash identity binding, a 30-day
autonomous pilot on one low-ACV slice. (#5, #10, #11, #14, #15, #16)
