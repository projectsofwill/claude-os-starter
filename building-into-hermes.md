# Building *into* Hermes, not *on* Hermes

A choice I made that most people don't, and why. This is a sidecar to `build-map.md` Step 7 and the
`hermes-setup-runbook.md` — read those first for *what* the agent is and *how* to stand it up. This doc is
narrower: once you have an always-on agent (mine runs on **Hermes**, [NousResearch's self-hostable agent
framework](https://github.com/NousResearch/hermes-agent)), *how do you change it over time?* There are two
honest answers, and the one I picked is the less obvious one.

---

## The two methods

**Method A — build it from your desk (what I do).** The agent's whole design lives as a folder in my main
repo: docs, config, the canonical copies of every script. That folder is the **blueprint**. The running VPS
is a separate thing. To change the agent, I edit the blueprint at my desk with Claude Code (the same
desk-side build tool from the rest of the OS), review the change, then **deploy** it to the VPS on purpose
(repo → VPS). The folder and the live box are *not* live-synced — editing the blueprint changes nothing
until I deploy. When the live agent breaks, Claude Code SSHes in to diagnose and fix, using the connection
details and diagnostic commands kept in the blueprint.

**Method B — build it on the box (what a lot of people do).** You change the agent where it runs: SSH into
the VPS and edit files in place, or use the agent's own dashboard / skill-builder and let it write and
modify its own skills, memory, and config. Fast, direct, no deploy step. The agent can extend itself while
you watch.

The difference in one line: **in A, the source of truth is a reviewed git blueprint and the box is
downstream of it; in B, the box *is* the source of truth and it edits itself.**

---

## Pros and cons

| | Method A — desk-side blueprint (deploy repo → VPS) | Method B — direct on the box / agent self-edits |
|---|---|---|
| **Change history** | Every change is a git commit — versioned, diffable, revertible | Live and unversioned; "what changed and when?" has no clean answer |
| **Review** | A change can be read, critiqued, and gated *before* it touches the live system | No natural review gate; the change is already live by the time you'd review it |
| **Who plans the change** | A top-tier model (Opus, my Claude Code builder) plans it; cheap models run the runtime | Whatever the agent's own runtime model is — fine for routine, weaker for risky design |
| **Self-modification risk** | The agent **cannot** rewrite its own backbone; a prompt-injection in something it reads can't turn into a config edit | The agent editing itself *is* the mechanism — so a prompt-injection that reaches it can become a real change |
| **Reproducibility / DR** | The blueprint rebuilds the whole agent from git — a real disaster-recovery path | Reproducing the box means re-deriving undocumented in-place edits; rebuild is a guess |
| **Portability** | The design moves to a new host (or a new framework) because it's plain files | Tied to this box and this dashboard's state |
| **Iteration speed** | Slower — there's a deliberate deploy step | Fast — edit and it's live |
| **Drift** | Real risk: the folder and the live box can fall out of step (see the mitigation below) | No folder to drift from — but also nothing to drift *toward*, i.e. no canonical truth |

So B genuinely wins on one axis: speed. A wins on every axis that matters once the thing runs unattended and
can touch real data, real keys, real outbound actions.

**The drift cost of A is real, and I pay it down deliberately.** Because the folder isn't live-synced to the
box, the two can diverge (a hotfix applied directly on the VPS in an emergency, say). The mitigation is a
**nightly config backup**: the VPS commits its live config to a private backup repo every night, so any
change that landed on the box outside the blueprint shows up as a reviewable diff the next morning. Drift
becomes *visible and recoverable* instead of silent. It doesn't eliminate the extra deploy step — it just
means drift can't hide.

---

## Why I chose A

This isn't a one-off preference. It's the same discipline that runs through the whole OS (the "discipline
layer" in `build-map.md`), applied to the riskiest component I run:

- **Tools do the work, docs say how, the agent orchestrates.** The agent is the *runtime*, not the author of
  its own machinery. Its skills and config are deterministic artifacts I version and deploy, the same way
  every other tool in the OS is. Letting it freely author its own backbone inverts that.
- **Keys, not prompts. Hooks over instructions.** The whole Step 7 security posture is about making
  dangerous things *impossible*, not merely discouraged. "The agent can't rewrite its own config at runtime"
  is one of those hard lines — and method B is exactly the capability that line forbids. If the way you
  evolve the agent is "the agent evolves itself," then a prompt-injection that reaches it inherits that
  power. Building from the desk keeps self-modification off the table by construction.
- **Everything reproducible from git.** If the VPS died tomorrow, I rebuild from the blueprint. That's only
  true because the blueprint, not the box, is the source of truth.
- **Use the most capable model to build, cheap models to run.** The hard thinking — designing a skill,
  changing the security config — happens once, at my desk, on the strongest model. The runtime then executes
  on cheap (often free-tier) models, because routine operation doesn't need a frontier model. Method B blurs
  that: the runtime model ends up doing build-time work it isn't the right tool for.
- **A different-vendor model stress-tests risky changes.** Before a high-stakes or unattended-backbone change
  ships, I run it past a second model from a *different* vendor (I use Codex) for a ruthless read-only
  critique — blind spots between vendors aren't correlated the way one model re-checking itself is. That gate
  only exists because there's a reviewable change, sitting in git, *before* it goes live. Method B has no
  such moment.

The live agent still pulls real weight in this loop — just not as the builder. I use it as a cheap,
authoritative **information source**: I ask it read-only questions about its own system, its reasoning runs
on its own cheap model (off my main budget), and only the short answer comes back to me. I trust what it
reads off its own files as ground truth; I verify its *reasoning* before acting on anything irreversible.
Builder at the desk, informant on the box.

**The trade, stated honestly:** I give up iteration speed. In exchange I get reviewability, reproducibility,
and a much smaller blast radius. That's a good trade *specifically because* this is the unattended automation
backbone — the part that runs while I'm asleep and can touch my inbox, my keys, and the open web. The faster
I can change something, the faster I can break it without noticing. For the backbone, "deliberate" beats
"fast."

---

## Who should pick which

Be honest with yourself about where you are:

- **Just experimenting?** Build directly on the box (Method B). It's faster, the feedback loop is tight, and
  if the whole thing is a sandbox you'll throw away, the overhead of a git blueprint earns you nothing. Most
  people kicking the tires on an agent should start here.
- **Running it unattended, where it can touch real things?** Move to the blueprint (Method A). The moment the
  agent fires on a schedule, reads your real inbox, holds scoped keys, or reaches the open web, the git
  blueprint's overhead starts paying for itself — in changes you can review, revert, and rebuild, and in an
  agent that can't quietly rewrite its own backbone.

The line between them is the same line `build-map.md` draws for Step 7 as a whole: don't build the heavy,
safe version until the thing is doing real work unattended. Until then, the box is your workshop. After that,
the box is production — and you don't edit production by hand.

---

*Sources: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent),
[Hermes Agent docs](https://hermes-agent.nousresearch.com/docs/).*
