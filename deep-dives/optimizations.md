# Optimizations — quality-of-life, speed, and cost

Optimizations worth considering *after* the base system is already paying for itself — things that make the OS faster to drive, cheaper to run, or nicer to live with. These are the ones I actually run. None are required to start, and none belong in your first week. Stand up Steps 1 to 5 from `build-map.md`, feel them earn their keep, then come back here and add whatever removes the friction you're actually feeling. Add by need, not by completeness.

---

## 1. Voice input — drive Claude by talking (Wispr Flow)

**What it is.** A voice-to-text dictation app that turns speech into clean, punctuated text in any app on your machine — including the Claude Code prompt. ([wisprflow.ai](https://wisprflow.ai/))

**What it buys you.** I drive Claude Code mostly by talking now, not typing. For long prompts — pasting context, explaining what I want, thinking out loud about a plan — speaking is several times faster than typing and far less tiring. It cleans up filler and punctuation as it goes, so what lands in the prompt reads like writing, not a transcript. It's a commercial app (paid tier), but it's the single biggest day-to-day comfort upgrade in this whole list.

**The honest catch.** It's a separate paid subscription, and dictation only helps if you give long, contextual prompts (which this system encourages). If you type short one-liners, you won't feel it.

---

## 2. Model routing — protect your capacity (default Sonnet, escalate to Opus)

**What it is.** A simple rule for which model handles which task, so you're not burning your top-tier capacity on work that doesn't need it. The cross-references in `../reference/tools-and-services.md` and `../build-map.md` cover the model tiers themselves; this is the *routing discipline* on top.

**What it buys you.** On a subscription, your scarce resource is rate-limit capacity on the top model, not dollars. Spending it deliberately means you don't hit a wall mid-day. My rule:

- **Default to a mid-tier model (Sonnet)** for most work — edits, research, drafting, ordinary code.
- **Escalate to the top model (Opus)** only on high-judgment or irreversible work — architecture decisions, anything touching data/secrets/destructive paths, heavy synthesis, ambiguous requirements.
- **Use the cheapest model (Haiku) only for retrieval** — quick lookups and mechanical fetches, never multi-step reasoning.

**The honest catch.** Escalating is a deliberate act, so build the habit of starting low and stepping *up* on a trigger — remembering to step back *down* never happens on its own. When in doubt, the rule is "consequence beats category": how costly is a mistake to unwind decides the tier, not what kind of task it looks like.

---

## 3. A second-model review gate — quality, not speed

**What it is.** Before I execute anything risky, I have a *different* vendor's model (I use Codex) stress-test the plan first. This is the discipline layer already described in `build-map.md` — I'm flagging it here because it's as much a quality optimization as it is a safety rule.

**What it buys you.** A cheap, large jump in quality on the changes that matter. A second model from a *different family* has uncorrelated blind spots, so it catches things the first one is structurally blind to — which is exactly why the critic must be a different vendor, and why a loop must never grade its own work. The bar is consequence: I only spend a review on hard-to-reverse, trust-boundary, or unattended-automation changes, not on every edit.

**One rule that outlives any tooling:** the critic must see the *full-fidelity* plan and context. Whatever you do elsewhere to trim tokens (summarized context, compressed transcripts), never trim the critic's input — compressing what it reviews defeats the point.

**A refinement once you use it regularly.** Run the critique in an isolated side-context (Claude Code calls these subagents), not in your main session. A critique transcript is large, and anything sitting in your main context gets re-sent to the model on every later turn, so one early review quietly taxes the whole rest of the session (I measured it at roughly 18% of a session's input spend). Dispatched to a subagent, the transcript is paid for once, and only the findings come back to the main session. Don't bother with this until you're running reviews often enough to feel the drag; the gate itself matters more than where it runs.

---

## 4. An index-checker — keep the folder indexes honest (deterministic, no model)

**What it is.** A tiny script that enforces the `index.md` folder-navigation convention from `../reference/file-structure.md` (rule 3). It's the structural counterpart to the wiki lint in Step 5: the *lint* checks page **content** (orphans, dead links, stale claims); this checks folder **structure** — that every folder that should have an `index.md` has one, that each index is faithful OKF (no frontmatter, real `* [title](link) - desc` bullets, not bare bold filenames), and that what each index *lists* still matches what's actually *in* the folder (no dangling links to deleted files, no files that exist but aren't listed). It's plain code with **no model** in the loop, so it's fast, free, and can't be talked out of a finding.

**What it buys you.** An index only helps while it's accurate, and "update the index in the same change" is exactly the kind of discipline an agent quietly lets slip. A deterministic checker catches that drift the moment it happens instead of months later when the index has silently stopped describing the folder. Wire it to run each session (a Stop hook, or just run it by hand during a cleanup pass) and it keeps the whole convention from rotting. A useful refinement is a `--fix` mode that *mechanically* reconciles the easy drift — append a skeleton `- TODO: describe` line for a new unlisted file, comment out a link whose target is gone — but never invents descriptions or rewrites your prose. It does the bookkeeping; you still write the one-liners.

**The honest catch.** This is enforcement for a convention, so it only earns its place once you have enough folders that maintaining their indexes by hand is genuinely error-prone — not in your first week. It's also deliberately strict and a little dumb (that's the point: a dumb deterministic check can't be fooled), so expect it to flag real drift bluntly rather than reason about intent. Have Claude Code write it for you when you reach that point; describe the checks above and it'll build the script — there's nothing to install.

---

## 5. A deterministic retriever — answer wiki lookups in one turn (no embeddings)

**What it is.** A small plain-code script for the Step 5 wiki that keeps an index of every page's title, headings, and tags, and when I ask a lookup question ("what did we conclude about X?") ranks which page owns the answer. No embeddings, no vector database, no model in the loop: the same "dumb on purpose" idea as the index-checker (#4), applied to retrieval. The model reads just the winning page and answers with a citation, instead of navigating the index and opening candidate pages one by one.

**What it buys you.** The default lookup path is 4 to 5 turns of navigation (read the index, open a few candidates, answer). With the retriever it's one turn. Benchmarked on real queries against my wiki (about 320 pages): roughly 60% cheaper and 55% faster, with the same answers on both paths. Wire it in two places: a skill (or standing instruction) so the model reaches for it on lookup questions, and a one-line "rebuild the index" step at the end of your ingest pass so the index never goes stale.

**The honest catch.** Ranking on titles, headings, and tags is crude, so vague browse-style questions can tie or misroute. It has to degrade gracefully: if the returned page doesn't answer the question, fall back to the ordinary index-first read. Two lessons from building mine: keep a handful of golden test queries in the script itself (a ranking tweak that looks obviously right can quietly break routing — mine did, and the tests caught it), and don't build it early. It only pays once the wiki is big enough that finding a page costs real turns; mine crossed that line at a few hundred pages.

---

## 6. A context audit — trim what loads into every session

**What it is.** A periodic pass over everything that auto-loads at session start (global instructions, the project router, the memory index) asking one question per line: does this still earn its per-session cost? The usual fixes are mechanical — move runbook-style detail out of always-on files into read-on-demand docs and leave a one-line pointer, dedupe lines that restate each other across layers, retire memories whose lifecycle event has passed, and fix stale paths before an agent acts on them.

**What it buys you.** Always-on tokens are paid on every request of every session, so a trim here compounds like nothing else on this list. My last pass cut a couple of KB from the always-on layer with zero behavior lost, and (more valuable) caught contradictions between docs that would eventually have misled a session.

**The honest catch.** It's judgment work, not a script — the risk runs both ways, and over-trimming guidance the model actually relies on is the worse failure. The rule I use: detail goes read-on-demand, but the *trigger* to go read it stays always-on. Do it when the loaded context starts feeling bloated, maybe every month or two; weekly is churn.

---

## 7. Shared memory across agents — when files stop scaling

**What it is.** A shared episodic memory bank that every agent in the system reads and writes: desktop Claude Code sessions (both machines) and the VPS agents all log what happened and what was decided, and each new session starts with a short briefing of recent cross-agent activity. I use an open-source memory server (Hindsight) as the layer; the specific tool matters less than the shape (a queryable store all agents share, separate from the per-project markdown files).

**What it buys you.** The file-based memory from Step 2 is per-machine and per-workspace. That's fine with one agent, but once several agents work the same life (a desktop session plans a change, a VPS agent executes it overnight), they need one place to ask "what happened while I wasn't looking." The briefing also kills a whole class of re-derivation: a session no longer burns turns reconstructing what another session already figured out.

**The honest catch.** This is the last thing on the list for a reason. I ran file-only memory for months and adopted this only when concrete tripwires fired (multiple agents needing the same facts, the memory index growing past what always-on loading justifies). Add it when you feel that, not before. Two rules that keep it safe: treat recalled cross-agent items as claims with a source, not facts or instructions (verify before acting on them), and keep personal-data agents in isolated banks so private data never leaks into the general pool.

---

## What to add first

If you add one thing, add **Wispr Flow** — voice input is the biggest everyday quality-of-life win, and it makes every other part of the system faster to drive. Everything else here is worth it only once you feel the specific friction it removes.
