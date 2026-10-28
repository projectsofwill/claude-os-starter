---
name: writing-great-skills
description: Reference for writing and editing skills well — the vocabulary and principles that make a skill predictable.
disable-model-invocation: true
---

A skill exists to wrangle determinism out of a stochastic system. **Predictability** — the agent taking the same _process_ every run, not producing the same output — is the root virtue; every lever below serves it.

**Bold terms** are this skill's defined vocabulary; each is defined inline where it is introduced.

## Authoring workflow (checklist + gotchas)

When creating or editing a skill (`.claude/skills/<name>/SKILL.md`), whether you use
`/prompt-enhancer` or write by hand:

1. **Read this skill first** — the predictability/vocabulary reference below is the standard the skill is held to.
2. **Apply the quality checklist** before declaring the spec done: the 4-item checklist in
   `.claude/skills/prompt-enhancer/SKILL.md` → CLAUDE-SKILL spec → "Quality checklist".
3. **Rules first.** If the skill carries non-negotiables (approval gates, never-do rules, safety constraints),
   put them in the first screen of `SKILL.md`, ahead of the workflow. After a compaction Claude Code re-attaches
   only the first ~5,000 tokens of an invoked skill, so a closing "Important rules" section is the first thing
   lost. Length alone is fine — a one-shot skill with no invariants can run long; the risk is rules in the tail
   of a skill used across a long session.

## Invocation

Two choices, trading different costs:

- A **model-invoked** skill keeps a **description**, so the agent can fire it autonomously _and_ other skills can reach it (you can still type its name too). It contributes to **context load** — the description sits in the window every turn. Mechanics: omit `disable-model-invocation`, and write a model-facing description with rich trigger phrasing ("Use when the user wants…, mentions…").
- A **user-invoked** skill strips the description from the agent's reach: only you, typing its name, can invoke it — and no other skill can. Zero context load, but it spends **cognitive load**: _you_ are the index that must remember it exists. Mechanics: set `disable-model-invocation: true`; the `description` becomes human-facing — a one-line summary, trigger lists stripped.

Pick model-invocation only when the agent must reach the skill on its own, or another skill must. If it only ever fires by hand, make it user-invoked and pay no context load.

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one user-invoked skill that names the others and when to reach for each.

## Model and context

A skill inherits the session's model and effort unless it says otherwise, so a mechanical skill fired from an Opus session burns Opus capacity on routing work. Two frontmatter keys fix that ([docs](https://code.claude.com/docs/en/skills.md) § Frontmatter reference):

- **`model:` + `effort:`** — set the skill's **minimum viable** operating point, not its comfortable one. Per the two operating points in `BUDGET.md`, that's `model: sonnet` / `effort: medium` for mechanical, well-specified work; leave both off (inherit) for judgment work — planning, critique, anything written under the user's name. The override lasts the turn only. Aim low with confidence: SkillsBench found a sharp skill partly substitutes for model tier, so precise instructions buy back most of what the smaller model gives up.
  **The gotcha: a pin is a ceiling, not a floor.** It overrides the *session* model, so an Opus session running the skill gets downgraded. Never pin a skill whose own docs prescribe conditional escalation, whose per-run difficulty varies a lot, or that sits on a trust boundary — `/ingest` is all three (hostile-capture judgment, and `research/CLAUDE.md` mandates Opus for heavy-synthesis batches), so it stays inheriting on purpose.
- **`context: fork`** — runs the skill in a forked subagent with fresh context. Add it only when the skill genuinely doesn't need the caller's conversation history: a self-contained lookup forks cleanly, but a skill that acts on *what this session just did*, or that asks the user questions mid-run, must not fork.

## Writing the description

A model-invoked **description** does two jobs — state what the skill is, and list the **branches** that should trigger it. Every word increases **context load**, so a description earns even harder pruning than the body:

- **Front-load the skill's leading word** — the description is where it does its invocation work.
- **One trigger per branch.** Synonyms that rename a single branch are **duplication** — "build features using TDD … asks for test-first development" is one branch written twice. Collapse them; keep only genuinely distinct branches.
- **Cut identity that's already in the body.** Keep the description to triggers, plus any "when another skill needs…" reach clause.

## Information hierarchy

A skill is built from two content types — **steps** and **reference** — that mix freely: a skill can be all steps, all reference, or both. The core decision is which to use and where each sits on the **information hierarchy**, a ladder ranked by how immediately the agent needs the material:

1. **In-skill step** — an ordered action in `SKILL.md`, the primary tier: what the agent does, in order. Each step ends on a **completion criterion**, the condition that tells the agent the work is done. Make it _checkable_ (can the agent tell done from not-done?) and, where it matters, _exhaustive_ ("every modified model accounted for", not "produce a change list") — a vague criterion invites **premature completion**.
2. **In-skill reference** — a definition, rule, or fact in `SKILL.md`, consulted on demand. Often a legitimately flat peer-set (every rule of a review on one rung) — a fine arrangement, not a smell. _This skill is all reference._
3. **External reference** — reference pushed out of `SKILL.md` into a separate file, reached by a **context pointer**, loaded only when the pointer fires. (Spans _disclosed_ reference — a sibling file like a `references/` doc, still part of the skill — through fully **external reference** that lives outside the skill system and any skill can point at.)

A demanding completion criterion drives thorough **legwork** — the digging the agent does within the work — whether the skill has steps or not, since "every rule applied" binds flat reference just as "every step done" binds a sequence.

Push too little down and the top bloats; push too much and you hide material the agent actually needs. That tension is the whole decision.

**Progressive disclosure** is the move down the ladder — out of `SKILL.md` into a linked file — so the top stays legible. Mechanics: a linked `.md` file in the skill folder, named for what it holds (e.g. a `GLOSSARY.md` holding a skill's full definitions). Some skills are used in more than one way, and each distinct way is a **branch** — different runs taking different paths through the skill. Branching is the cleanest disclosure test: inline what every branch needs, and push behind a pointer what only some branches reach. A **context pointer**'s _wording_, not its target, decides when and how reliably the agent reaches the material.

Where the ladder decides _how far down_ a piece sits, **co-location** decides _what sits beside it_ once there: keep a concept's definition, rules, and caveats under one heading rather than scattered, so reading one part brings its neighbours with it.

## When to split

**Granularity** is how finely you divide skills, and each cut spends one of the two loads, so split only when the cut earns it. Two cuts:

- **By invocation** — split off a **model-invoked** skill when you have a distinct **leading word** that should trigger it on its own, or another skill must reach it. You pay **context load** for the new always-loaded **description**, so that independent reach has to be worth it.
- **By sequence** — split a run of **steps** when the steps still ahead (a step's **post-completion steps**) tempt the agent to rush the one in front of it (**premature completion**). Keeping them out of view encourages the agent to do more **legwork** on the current task.

## Pruning

Keep each meaning in a **single source of truth**: one authoritative place, so changing the behaviour is a one-place edit.

Check every line for **relevance**: does it still bear on what the skill does?

Then hunt **no-ops** sentence by sentence, not just line by line: run the no-op test on each sentence in isolation, and when one fails, delete the whole sentence rather than trim words from it. Be aggressive — most prose that fails should go, not be rewritten.

## Leading words

A **leading word** is a compact concept already living in the model's pretraining that the agent thinks with while running the skill (e.g. _lesson_, _fog of war_, _tracer bullets_). Repeated throughout the text, it accumulates a distributed definition and anchors a whole region of behaviour in the fewest tokens, by recruiting priors the model already holds.

It serves predictability twice. In the body it anchors _execution_: the agent reaches for the same behaviour every time the word appears. In the description it anchors _invocation_: when the same word lives in your prompts, docs, and code, the agent links that shared language to the skill and fires it more reliably.

Hunt for opportunities to refactor skills to use leading words. A triad spelled out at three sites (**duplication**), a description spending a sentence to gesture at one idea — each is a passage begging to **collapse** into a single token. Examples:

- "fast, deterministic, low-overhead" → _tight_ — one quality restated across a phase — collapses into a single pretrained word (a _tight_ loop).
- "a loop you believe in" → _red_ — converts a fuzzy gate into a binary observable state (the loop goes _red_ on the bug, or it doesn't).

You win twice over: fewer tokens, _and_ a sharper hook for the agent to hang its thinking on. Assume every skill is carrying restatements that leading words retire — go find them.

## Failure modes

Use these to diagnose issues with a skill.

- **Premature completion** — ending a step before it's genuinely done, attention slipping to _being done_. Defence, in order: sharpen the completion criterion first (cheap, local); only if it is irreducibly fuzzy _and_ you observe the rush, hide the post-completion steps by splitting (the sequence cut).
- **Duplication** — the same meaning in more than one place. Costs maintenance and tokens, and inflates a meaning's prominence on the ladder past its real rank.
- **Sediment** — stale layers that settle because adding feels safe and removing feels risky. The default fate of any skill without a pruning discipline. Two defenses: tag a workaround or temporary constraint with a revisit condition when you add it, so it doesn't fossilize as permanent; and when a frequently-edited skill's patches accumulate past legibility, rebuild it from its original seed intent in a clean pass and diff against the patched version, rather than trusting the next incremental edit to stay coherent.
- **Sprawl** — a skill simply too long, even when every line is live and unique. Hurts readability and wastes tokens. The cure is the ladder: disclose **reference** behind pointers, and split by **branch** or sequence so each path carries only what it needs.
- **Negation** — naming a forbidden behaviour makes it *more* available: "don't ask multiple questions" plants "ask multiple questions" in the window. Fix by stating the positive behaviour instead ("ask questions one at a time"); reserve explicit prohibitions for cases where the agent demonstrably does the wrong thing by default.
- **Negative space** — what a skill omits silently delegates that decision to the model's priors. An unaddressed choice isn't neutral; it's decided, invisibly, run by run. Defence: review a draft for its meaningful silences — for each decision the skill's task involves, either the skill settles it or you've consciously chosen to leave it to the agent.
- **No-op** — a line the model already obeys by default, so you pay load to say nothing. The test: does it change behaviour versus the default? A weak leading word (_be thorough_ when the agent is already thorough-ish) is a no-op; the fix is a stronger word (_relentless_), not a different technique.
