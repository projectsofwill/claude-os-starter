# Claude OS — Build Map

How I built a personal "second brain plus assistant" on top of Claude, in the order I built it, and what each step buys you. Written so someone else can follow the same path.

This is written in my own voice and references my own setup. The "Yours to fill" notes mark where you swap in your own life.

> **Who this is for:** someone already comfortable with Claude (ideally Claude Code). You do not need to be an engineer. You do need to be willing to keep a few markdown files and run a sync script.

---

## The one idea

The system is not the newsletter, the wiki, or the agent. Those are my *filling*. The reusable thing is the **frame**: four layers you grow, in priority order.

**The Four C's** (credit: Nate Herk's "AIOS" framing):

1. **Context** — what the AI knows about you and your world.
2. **Connections** — the live data it can read (email, calendar, files).
3. **Capabilities** — the repeatable skills it can run.
4. **Cadence** — the work it does on a schedule, without you asking.

Two rules about how you build across them:

- **Get Context right first.** Everything downstream is more useful when the model already knows who you are. It is the highest-leverage hour you will spend.
- **Wide-then-tall.** Stand all four up thinly before you deepen any one of them. A thin version of all four beats a perfect version of one.

The honest test the whole thing builds toward: it *perceives* your world and *acts* across it on a daily cadence, not just runs a few isolated automations.

---

## How to read this

The build is seven steps. Each one tells you:

- **What it is** — the files or tools.
- **What it buys you** — the functionality you get.
- **The practice** — the research-backed reason it is built this way, and the source.
- **Yours to fill** — what is reusable skeleton versus what you personalize.

You do not have to do all seven. Three useful stopping points:

- **Minimum viable (Steps 1 to 2):** the AI knows you and remembers across sessions. An afternoon.
- **The 80/20 (Steps 1 to 5):** a real second brain with skills and a knowledge base. This is where most people should live.
- **The full system (Steps 6 to 7):** scheduled automations and an always-on agent. Powerful, and the most work to run. Treat it as opt-in.

This file stays at the level of *patterns* so it doesn't go stale. The companion files turn it into action:

- **`setup-prompts.md`** — copy-paste prompts that drive your own Claude Code through each step below. The intended way to *build* this: read a step here, then paste its matching prompt. There's one per step.
- **`tools-and-services.md`** — the concrete answer to "what service do I use for this, and what does it cost."
- **`file-structure.md`** — a folder layout you can copy.
- **`templates/`** — fill-in-the-blank starting points for the Step 1 and Step 2 files.
- **Optional deep-dives and extras** (all indexed in `START-HERE.md`): `wiki-deep-dive.md` and `researcher-deep-dive.md` (the rabbit holes under Step 5 and Step 7), `building-into-hermes.md` (why I build the agent from my desk, not on the box), `optimizations.md` (speed and cost add-ons once it's running), and `additional-resources.md` (who I follow and what my researcher crawls).

So the loop for each step is: read the step here for the *why*, grab the service from `tools-and-services.md`, and paste the step's prompt from `setup-prompts.md` to have Claude Code build it with you.

---

## Step 1 — Personal context (C: Context)

**What it is.** A small set of plain-markdown files the AI reads at the start of every session: a router file (`CLAUDE.md`), plus `about-me`, `working-style`, and `brand-voice`.

- `about-me` — who you are, your goals, how you spend your week.
- `working-style` — how you want the AI to behave (ask vs. assume, how much to explain, when to push back).
- `brand-voice` — how you write, so anything drafted in your name sounds like you.
- `CLAUDE.md` — a short router that says "here is who I am and where everything lives," and points to the other three.

**What it buys you.** Every session starts warm. The model already knows your context, your preferences, and your voice, so you stop re-explaining yourself.

**The practice.**
- **Keep the always-on file lean.** `CLAUDE.md` loads every session and competes for the model's attention. Shorter means more attention on what matters. Make it a router, not an encyclopedia. (Karpathy: "the delicate art of filling the context window with just the right information.")
- **Layer it.** A global behavior file (rules that apply everywhere) plus a per-project router. Each project can have its own `CLAUDE.md`.
- **Write identity tool-agnostic.** Keep "who I am and how I think" in a portable file so moving between tools (Claude Code, another agent) costs nothing. (Nick Milo: "file over app.")

**Yours to fill.** This step is *entirely* filling. The skeleton is just the four file names and the router pattern. Everything inside is you.

---

## Step 2 — Persistent memory (C: Context)

**What it is.** A flat folder of small markdown files (`memory/`), one fact per file, plus a one-line index (`MEMORY.md`) that loads every session.

**What it buys you.** Durable facts survive across sessions. One-off chats start *accumulating* into knowledge the AI carries forward, instead of resetting every time.

**The practice.**
- **Durable fact goes to memory; live status goes to a `STATUS.md`.** Never let moving project state creep into always-loaded memory, or the index bloats and goes stale. Facts in memory, "where things stand right now" in a per-project status file.
- **Four kinds of memory, not one pile** (the CoALA taxonomy): working (the live context window), semantic (durable facts, this step), procedural (skills, Step 4), and episodic (handoff notes, Step 4). Each behaves differently.
- **Always-on lean index plus on-demand detail.** The index is the cheap semantic layer that is always loaded; the full files are read only when relevant.
- **Run a consolidation pass.** Periodically prune stale or contradictory entries. Memory you never forget from is memory that rots. (I do this with an `/os-hygiene` skill.)

**Yours to fill.** Skeleton: the one-fact-per-file pattern and the loaded index. Filling: your actual facts, preferences, and decisions.

---

## Step 3 — Portability (infrastructure)

**What it is.** Git as the backbone. One repo per project, each self-contained. A small sync script (`sync.py` plus a list of repos) runs on a schedule and keeps every machine in step.

**What it buys you.** The OS follows you across machines, fully version-controlled. You get history, rollback, and a real backup for free, and notes/memory auto-commit so you do not babysit it.

**The practice.**
- **One repo per project, self-contained.** A project never depends on files above it. Cloud and scheduled runs clone a single repo in isolation and must still work.
- **Sync via git, not file-sync.** File-sync tools corrupt and conflict on live folders; git gives you real merge history.
- **Secrets stay out of git** (committed only as ciphertext, with the key held separately). Never commit a plaintext secret.

**Yours to fill.** This step is almost pure skeleton. The pattern (git, one repo per project, a sync script, secrets handling) transfers directly. The only filling is which repos you list.

---

## Step 4 — Capabilities: skills (C: Capabilities)

**What it is.** Reusable workflows you invoke with a slash command. Global ones install everywhere; project ones live with the project. The first two to build: `/wrap-up` (write a handoff note at the end of a session) and `/resume` (read it back at the start of the next one).

**What it buys you.** The OS gains repeatable procedures instead of one-off prompting. Session continuity specifically kills the cold-start problem: you pick up exactly where you left off.

**The practice.**
- **Session continuity first.** A start/end handoff loop (`/resume` plus `/wrap-up`) is the single highest-value skill for a personal system, and the most common first recommendation for second-brain setups. It is also your *episodic* memory.
- **Battle-test a skill by hand before you automate it.** A skill is the water; a loop (Step 6) is the plumbing. Never wire an unproven skill into something that runs on its own.
- **A loop-ready skill emits a verdict.** When you do automate, the skill should output a clear signal (pass/fail or a score) that a loop can check against a goal. Abstract goals ("is this good?") have to become measurable.

**Yours to fill.** Skeleton: `/resume` and `/wrap-up` (and the "skills are version-controlled and synced" pattern from Step 3). Filling: every domain-specific skill you add later.

---

## Step 5 — Knowledge: the second brain (C: Context)

**What it is.** A plain-markdown knowledge wiki (mine lives in `research/`), built as a pipeline: capture raw sources, then ingest them into durable, linked pages. An Obsidian vault sits on top for navigation and `[[wikilinks]]`. Capture is one path (the Obsidian Web Clipper, which also pulls YouTube transcripts); ingestion is a deliberate, step-by-step process the model runs.

**What it buys you.** A growing, interlinked knowledge base that both you and your future agents can read. It is the difference between "I read something useful once" and "my system knows it."

**The practice.** This step carries the most researched-and-applied practices:

- **A markdown wiki, not a vector database.** Build a persistent plain-text wiki with an index and `[[wikilinks]]`. Skip embeddings until scale forces it (friction shows up somewhere in the hundreds-to-low-thousands of pages, when flat-file navigation starts to hurt). (Karpathy's "build the LLM wiki"; later formalized by Google's Open Knowledge Format.)
- **Organize by function, not by topic.** Folders for *kinds* of page (sources, concepts, patterns, guides). Topic lives in a `tags:` field, not in the folder tree. This keeps the structure flat as it grows.
- **Lean into the fact that LLMs do not get bored.** Humans abandon wikis because cross-linking and upkeep is tedious. The model maintains references far more reliably than a person will, so a periodic lint-and-review pass keeps the cross-linking healthy instead of letting it rot. It reduces the upkeep that kills human wikis; it does not make upkeep zero (models still miss or invent links, which is exactly what the lint step catches).
- **Linting is a first-class step, not a nicety.** A periodic health check (orphan pages, dead links, contradictions, stale claims, off-vocabulary tags) prevents rot. It proposes fixes; a human approves them.
- **Raw captures are immutable.** A captured source never changes except for a status field. All curation and versioning happens in the wiki pages, never in the raw capture.
- **Ingestion is where curation happens.** Raw sources are never queried directly. A fixed sequence (validate, dedupe, write the source page, update durable pages, resolve contradictions, tag freshness, update the index, log it) turns a dump of links into actual knowledge.
- **Separate reference from decisions.** A *guide* is reference. A *recommendation* is a verdict with a rationale (and a review date). Keep them in different places so you can trust each.
- **Controlled vocabulary.** Define your canonical tags up front and let the lint enforce them. New tags require a decision, not a typo.
- **A safety gate on untrusted content.** Anything fetched from the open web gets a deterministic, regex-only scan that quarantines suspicious files *before* any model reads them. The scanner is dumb on purpose, so it cannot itself be prompt-injected. Fail closed.

**Yours to fill.** Skeleton: the entire pipeline (capture, immutable raw, ingest steps, lint, function-folders, controlled vocab, safety gate). Filling: your domains and the actual notes. Mine span AI, plus travel and food, which is the point: the machine is domain-agnostic.

> **Going deeper:** `wiki-deep-dive.md` walks through the actual capture-to-ingest workflow and its decisions (the Web Clipper default, the PDF scanner, the YouTube frame-analysis gate, the `/ingest` skill). The autonomous arm that fills the wiki from the web is its own rabbit hole in `researcher-deep-dive.md`.

---

## Step 6 — Cadence: automations (C: Cadence + Connections)

**What it is.** One place to register and run scheduled jobs (do not scatter one-off cron jobs). The first real automation: a weekly brief that researches a topic, drafts an email, and publishes an archive, with a hard rule that it *never sends on its own*.

> **Is this the same as Step 7 (Hermes)?** No, and the difference is worth getting straight. Step 6 is just "something runs on a schedule," and it needs no server and no agent. Mine started as a plain scheduled job on my laptop (a timer firing a Python script). Step 7 is the always-on *agent* you talk to from your phone that also perceives your calendar and inbox. The two overlap in my setup today only because I later moved this newsletter job onto the Hermes box once it existed, but you do not need Step 7 to do Step 6. You can do this on your laptop and stop here.

**What it buys you.** The OS crosses from "responds when asked" to "does scheduled work." This is the first taste of Cadence, and it forces your first real Connection (it has to read and write something live).

**The practice.**
- **Write the loop, not the prompt.** A prompt runs once. A loop re-runs toward a defined goal with verification, until the goal is met or a hard cap is hit. (Boris Cherny: "I don't prompt Claude anymore. My job is to write loops.")
- **Every loop has four parts:** a trigger (schedule), the skills that do the work, a goal plus verification (how it knows it is done), and an output written to a file (the repo does not forget).
- **Think queues, not daemons.** Frame an automation as a backlog of tasks with human checkpoints, not an infinite runner. (Matt Pocock's "queues, not loops.")
- **Cap everything.** A hard iteration limit, a way to detect when it is stuck and bail, and a token ceiling. Unbounded loops burn money fast.
- **Keep a human gate on anything that leaves the building.** My newsletter drafts an email and never sends it. The send is one click, by me. (More on why under "keys not prompts" below.)

**Yours to fill.** Skeleton: the single-runner discipline, the loop anatomy, the caps, the never-auto-send gate. Filling: what the automation actually does. A weekly brief is a good first one because it exercises research, drafting, and publishing at once.

---

## Step 7 — The heartbeat: an always-on agent (C: Connections + Cadence)

**What it is.** A persistent agent on a small server, reachable from your phone (mine runs on a VPS and talks over Telegram). It reads your calendar and inbox, sends a morning brief, and ingests new sources on a schedule.

**What it buys you.** This is the step that makes it feel like an assistant rather than a collection of scripts. It *perceives* (calendar and inbox are the two missing Connections) and *acts* on a daily heartbeat. It is also the hardest tier to build and run safely, and the most optional. Most people get most of the value from Steps 1 to 5.

**The practice.**
- **Scale to need.** There is a four-tier ladder of agent complexity, from "one agent with throwaway helpers" up to "separate instances per domain." Start at the bottom. Most setups never need the top two tiers. Mine sits at tier two (one orchestrator plus a couple of specialists).
- **Orchestrator plus specialists.** One router agent reads the rules and dispatches to narrow-purpose agents (a researcher, an assistant), instead of one agent trying to do everything.
- **Persistent agents for durable work; disposable agents for short parallel reasoning.** Matching the wrong type to the job wastes tokens.
- **Coordinate through a shared task board, not agent-to-agent chat.** A durable queue survives restarts and keeps a human in the loop.
- **Keys, not prompts.** A rule in a markdown file is a *request*. A scoped, read-only API key is a *hard line*. The cautionary tale: an agent that auto-sent a discount to roughly 150 to 200 thousand people because "write and send" was ambiguous in a prompt. The fix is not a better prompt, it is a key that physically cannot send.
- **Hooks over instructions for rules you cannot lose.** A `CLAUDE.md` rule competes for attention; a tool-level hook can deny an action outright. For the few things that must never happen, enforce them at the tool layer plus a filesystem or CI backstop.
- **Treat untrusted input as hostile.** The researcher reads the open web, so it runs behind the same fail-closed safety gate from Step 5, and sensitive keys live nowhere the agent can reach them.

**Yours to fill.** This step is mostly skeleton (the architecture and the security posture transfer), but it is the heaviest to operate. Honest take: do not start here, and do not build it until Steps 1 to 5 are paying off.

---

## Step 7, concretely: Hermes

Step 7 is the only step where I run a named third-party framework, so here is the actual shape of it in case you want to copy the build rather than just the idea. Mine runs on **Hermes** (NousResearch's open-source, self-hostable agent framework). You do not have to use Hermes. Any always-on agent host works, and the principles in Step 7 are what matter. But a concrete reference is easier to follow than an abstraction.

**The shape.** A cheap Linux VPS runs a small Docker stack. One agent is always listening; you talk to it from your phone over Telegram; it runs jobs on a schedule. That is the whole idea. Everything else is detail.

**The stack (Docker, one network).**
- **The agent container** — the Hermes gateway itself. Pin it to a specific version tag, never `:latest`, so an upstream update can't silently break your setup.
- **A search container** — a self-hosted meta-search engine (I use SearXNG) so the agent can find things on the web without you handing it a paid search key.
- **A key-isolation container** — a tiny container whose only job is to hold your cloud API keys. The agent calls it to run inference but never sees the keys itself. If the agent is ever compromised, the keys are in a different box. This is "keys, not prompts" made physical.

**The profiles (orchestrator plus specialists).** Three agent "profiles," each with its own narrow job and its own minimal set of tools:
- **The orchestrator** — the only one connected to Telegram. It owns the schedule and routes your messages. It does no real work itself; it dispatches.
- **The researcher** — reads the open web to pull in news and sources. It is the most locked-down profile because it touches untrusted content. In my build it is deliberately tool-less: it can read and classify, but it physically cannot write anywhere dangerous. Whatever it captures lands as inert files that a human (me, at my desk) reviews before anything is trusted.
- **The assistant (EA)** — reads my calendar and inbox and writes the morning brief. The brief is **read-only** (a read-only inbox/calendar scope, nothing more). Drafting a reply is a *separate, deliberately-added* permission you grant later, and even then it only ever saves a draft for me to review. It can never send. Sending is always one human click.

**The task board.** The profiles coordinate through a shared task board (a small database), not by chatting to each other. You drop a request ("research the new model release and flag anything that affects my setup"), the orchestrator files it, a specialist picks it up. The board survives restarts, which agent-to-agent chat does not.

**What it does on a cadence.** A morning brief at 8am (calendar plus inbox plus overnight research plus one nudge), a daily news ingest, and the weekly newsletter from Step 6, all firing on their own. That is the payoff: I wake up to a brief that already read my day.

**The security posture (non-negotiable, all from Step 7's principles).**
- **Telegram allow-list.** Exactly one user ID (yours) can talk to the agent. Test it from a second account; it must refuse.
- **Scoped, read-only keys.** A separate key per tool, scoped to read-only and to the narrow thing it needs. Never your main account credentials.
- **Keys in their own container**, never in the agent.
- **The control panel is private.** The dashboard is the entire agent, so I treat it like SSH: bound to a private VPN (Tailscale), never the public internet.
- **The agent runs non-root, inside Docker**, so a bad day has a small blast radius.
- **Manual approval for sensitive actions**, and the agent cannot rewrite its own config at runtime.
- **Untrusted input is treated as hostile.** Anything fetched from the web passes the same fail-closed safety gate as Step 5 before any model reads it.

**The honest cost.** A small VPS is a few dollars a month; the one quality model I pay per-token for (the assistant) is the main variable; everything else rides on free tiers or a subscription I already have. Budget roughly $10 to $30 a month and set a hard spend alert.

**The honest warning.** This tier has the most moving parts and the worst failure mode: it all runs, and you never look at it because the setup exhausted you. So build the minimum first (VPS plus the agent plus Telegram plus one morning-brief job) and live on that for two weeks before adding anything. If that one brief is useful, add the researcher. Do not build the whole thing before you have felt one piece of it work.

**Yours to fill.** The architecture, the profile split, and the security posture copy directly. What the agent researches, whose calendar it reads, and what your brief says are yours.

> **Going deeper:** `hermes-setup-runbook.md` is the phased, concrete setup checklist. `building-into-hermes.md` explains why I build the agent from my desk (a git blueprint deployed to the box) instead of editing it live, with the pros and cons. The researcher is its own rabbit hole in `researcher-deep-dive.md`.

---

## The discipline layer (built throughout)

These are not steps. They run across all seven and are most of what keeps the system from rotting.

- **Doc coherence.** After any change to how the system works, update *every* doc that describes it in the same pass. Drift between docs is how a system quietly stops being trustworthy.
- **A checkpoint log.** One shared file (`CHANGES.log`) gets an entry at meaningful checkpoints (code/config changes, decisions, blockers, session end): what changed, what is next. It is what lets a future session pick up cleanly.
- **A second model checks the first.** Before I execute anything non-trivial, a different model (I use Codex) stress-tests the plan. Feedback loops are the cheapest 2-to-3x on quality you can buy. The rule that matters: **never let a loop verify its own work.**
- **Tools do the work, docs say how, the agent orchestrates.** Deterministic scripts for anything that should be reliable; markdown for the how-to; the agent wires them together. Look for an existing tool before writing a new one.
- **Naming and structure conventions.** A small fixed set of signpost files in caps (`README`, `CLAUDE`, `ROADMAP`, `STATUS`, `MEMORY`), everything else lowercase-with-dashes. Boring and consistent beats clever.

---

## The principles behind it, and where they came from

The whole build rests on a handful of load-bearing ideas, all of them already in use (not aspirational):

| Principle | One line | Source |
|---|---|---|
| The Four C's | Context, Connections, Capabilities, Cadence, built in that priority | Nate Herk (AIOS) |
| Context engineering | Fill the context window with just the right info; keep the always-on file lean | Andrej Karpathy |
| Knowledge as a markdown wiki | Plain-text wiki with wikilinks, not a vector DB, until scale forces it | Karpathy; Google Open Knowledge Format |
| Four types of memory | Working, semantic, procedural, episodic | CoALA |
| File over app | Keep identity and knowledge portable as plain files | Nick Milo |
| Session continuity | A start/end handoff loop kills cold-start | Project-brain pattern |
| Loops over prompts | Write the harness (trigger, skills, goal, verification, output), not the prompt | Boris Cherny, Peter Steinberger |
| Queues, not loops | An automation is a backlog with checkpoints, not a daemon | Matt Pocock |
| Verifier loop | A second model grades the output; never self-verify | Boris Cherny |
| Keys, not prompts | Enforce hard limits with scoped keys and hooks, not instructions | Karpathy (guardrail hooks); Nate Herk |
| Scale to need | Add agent complexity only when friction appears | Multi-agent orchestration writeups |

---

## Skeleton vs. filling, in one view

What you copy versus what you make your own:

- **Pure skeleton (copy directly):** the Four C's frame, the file structure, the memory pattern, git/sync, `/resume` and `/wrap-up`, the wiki pipeline (capture, ingest, lint, safety gate), the loop anatomy, the discipline layer.
- **Pure filling (entirely yours):** `about-me`, your goals and voice, your memory facts, your knowledge domains, what your automations actually do.
- **Mixed:** the automations and the agent share a reusable architecture, but what they do and the data they touch are yours.

---

## Where to start

If you do one thing, do **Step 1**. It is an hour and it changes every conversation you have afterward.

Then go in order. The order is not arbitrary: each step is more useful once the one before it exists. Context makes memory worth keeping; memory and skills make the wiki worth building; the wiki and skills make automations worth scheduling; everything below makes the agent worth trusting.

Stop wherever the value stops being worth the upkeep. There is no prize for reaching Step 7.
