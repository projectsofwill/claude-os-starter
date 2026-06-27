# Optimizations — quality-of-life, speed, and cost

Optimizations worth considering *after* the base system is already paying for itself — things that make the OS faster to drive, cheaper to run, or nicer to live with. These are the ones I actually run. None are required to start, and none belong in your first week. Stand up Steps 1 to 5 from `build-map.md`, feel them earn their keep, then come back here and add whatever removes the friction you're actually feeling. Add by need, not by completeness.

---

## 1. Voice input — drive Claude by talking (Wispr Flow)

**What it is.** A voice-to-text dictation app that turns speech into clean, punctuated text in any app on your machine — including the Claude Code prompt. ([wisprflow.ai](https://wisprflow.ai/))

**What it buys you.** I drive Claude Code mostly by talking now, not typing. For long prompts — pasting context, explaining what I want, thinking out loud about a plan — speaking is several times faster than typing and far less tiring. It cleans up filler and punctuation as it goes, so what lands in the prompt reads like writing, not a transcript. It's a commercial app (paid tier), but it's the single biggest day-to-day comfort upgrade in this whole list.

**The honest catch.** It's a separate paid subscription, and dictation only helps if you give long, contextual prompts (which this system encourages). If you type short one-liners, you won't feel it.

---

## 2. Token compression — stretch your budget with a proxy (Headroom)

**What it is.** A proxy that sits between Claude Code and the model and compresses the context being sent up, so each request spends fewer tokens for the same work. I run mine always-on (Mac and PC), and it ships a small local dashboard so I can watch what it's saving.

**What it buys you.** A modest, passive cut to token spend — on the order of a few percent in my use — with no change to how I work. It's a "set it and forget it" optimization: once it's in front of Claude Code, every session benefits a little, and the savings compound over months of heavy use.

**The honest catch.** The savings are real but small — this is not a transformative win, it's a steady trim. It also adds a moving part between you and the model, so it has to fail *open* (if the proxy dies, traffic passes straight through). And one deliberate exception matters: I route the second-model review gate (below) *around* it, so the critic always sees full-fidelity context. (I'm describing this at the concept level — "a proxy that compresses what gets sent to the model" — because the specific tool may be niche or personal; build or find one that fits, the idea is what transfers.)

---

## 3. Model routing — protect your capacity (default Sonnet, escalate to Opus)

**What it is.** A simple rule for which model handles which task, so you're not burning your top-tier capacity on work that doesn't need it. The cross-references in `tools-and-services.md` and `build-map.md` cover the model tiers themselves; this is the *routing discipline* on top.

**What it buys you.** On a subscription, your scarce resource is rate-limit capacity on the top model, not dollars. Spending it deliberately means you don't hit a wall mid-day. My rule:

- **Default to a mid-tier model (Sonnet)** for most work — edits, research, drafting, ordinary code.
- **Escalate to the top model (Opus)** only on high-judgment or irreversible work — architecture decisions, anything touching data/secrets/destructive paths, heavy synthesis, ambiguous requirements.
- **Use the cheapest model (Haiku) only for retrieval** — quick lookups and mechanical fetches, never multi-step reasoning.

**The honest catch.** Escalating is a deliberate act, so build the habit of starting low and stepping *up* on a trigger — remembering to step back *down* never happens on its own. When in doubt, the rule is "consequence beats category": how costly is a mistake to unwind decides the tier, not what kind of task it looks like.

---

## 4. A second-model review gate — quality, not speed

**What it is.** Before I execute anything risky, I have a *different* vendor's model (I use Codex) stress-test the plan first. This is the discipline layer already described in `build-map.md` — I'm flagging it here because it's as much a quality optimization as it is a safety rule.

**What it buys you.** A cheap, large jump in quality on the changes that matter. A second model from a *different family* has uncorrelated blind spots, so it catches things the first one is structurally blind to — which is exactly why the critic must be a different vendor, and why a loop must never grade its own work. The bar is consequence: I only spend a review on hard-to-reverse, trust-boundary, or unattended-automation changes, not on every edit.

**The connection to Headroom.** This gate is the one place I bypass the compression proxy (#2). The whole value of the critic is that it sees the *full-fidelity* plan and context — compressing what it reviews would defeat the point. Trim everywhere else; never trim the critic's input.

---

## What to add first

If you add one thing, add **Wispr Flow** — voice input is the biggest everyday quality-of-life win, and it makes every other part of the system faster to drive. Everything else here is worth it only once you feel the specific friction it removes.
