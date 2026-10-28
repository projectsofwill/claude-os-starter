# Claude OS Starter

A guide to building a personal "second brain plus assistant" on top of Claude. I built one; this repo is the map, the reasoning, and the build order, so you can copy the parts that fit and skip the rest.

It is not a product and there is nothing to install. The repo holds the *plan* (what to build and why), the *prompts* (that drive Claude Code to build it with you), and *templates* (starter files you fill in). You build the system by talking to Claude Code, one step at a time, right from this page.

## What you'll have when it's done

The build is seven steps across four layers (Context, Connections, Capabilities, Cadence). Each step leaves you with something that works on its own, and there are three honest stopping points:

- **An afternoon (Steps 1 to 2):** Claude knows who you are, how you work, and how you write, and it remembers durable facts across sessions. You stop re-explaining yourself.
- **The 80/20 (Steps 1 to 5):** a real second brain. Your system follows you across machines with full version history, you have repeatable skills (session handoff, resume), and a growing plain-markdown knowledge wiki that both you and your future agents can read. Most people should live here.
- **The full system (Steps 6 to 7):** scheduled automations (a weekly brief that researches, drafts, and publishes on its own) and an always-on agent on a small server. You message it from your phone, it reads your calendar and inbox, and you wake up to a morning brief that already read your day. Powerful, the most work to run, and genuinely optional.

There is no prize for reaching Step 7. Stop wherever the value stops being worth the upkeep.

**Using it for a job?** [work-kit/](work-kit/README.md) is a separate, copy-ready version for a RevOps role: a private work repo with a metric glossary, meeting-transcript ingest, task tracking, and token-budget profiles. It's the one part of this repo that ships real files (skills and hooks) instead of prompts.

## How this actually works (read this first)

This matters, because it's not obvious from a repo of markdown files:

- **There is no app here, and no code to install.** The flow: open **Claude Code** in this folder, read a step in [build-map.md](build-map.md), then paste that step's prompt from the walkthrough below. Claude Code reads the repo and builds that step *with* you, asking you questions as it goes.
- **When a step needs a script, a skill, or a tool** (a sync script, an ingest skill, a safety scanner), **Claude Code writes it for you** during that step. Those files are not in this repo on purpose. The deep-dives describe how *mine* work, in plain language, so Claude Code can recreate the same thing for you. You don't need to be able to write any of it yourself.
- **Build in your OWN folder, not this one.** Keep this repo as read-only reference. Your actual system lives in a separate, fresh folder (call it `my-os/` or whatever you like). Prompt 0 sets that up. Don't let Claude Code edit these starter files; you want your system separate from the instructions for building it.

So the loop for every step is: **read the step in the build map → paste its prompt below → answer Claude Code's questions.** If you only remember one thing from this page, remember that.

## What you actually need

- You should be comfortable with **Claude** (ideally **Claude Code**). You do **not** need to be an engineer.
- You do need to be willing to keep a few markdown files and run a sync script.
- Steps 1 to 5 need only your laptop. Step 6 adds a scheduled job. Step 7 adds a cheap Linux VPS (a few dollars a month) and is the only step with ongoing cost and real upkeep.

## Before you start

1. **Install Claude Code and sign in.** It runs in your terminal and inside VS Code (see [claude.com/claude-code](https://claude.com/claude-code)). You don't need anything else yet; [reference/tools-and-services.md](reference/tools-and-services.md) lists the rest, introduced per step.
2. **Clone or download this repo somewhere boring and local:** your home directory or Desktop. *Avoid* a cloud-synced folder (iCloud Drive, OneDrive, Dropbox); those fight with git once you reach Step 3.
3. **Open the folder in Claude Code** (open a terminal in the folder and run Claude Code there, or open the folder in VS Code and start the Claude Code extension). Quick check that it can see the files: ask it *"list the files in this folder and tell me what README.md says."* If it answers, you're set.
4. **Paste Prompt 0 below.** That's your first action; it orients Claude Code and sets up your own working folder. Everything flows from there.

Each later step tells you what else to set up (a free GitHub account around Step 3, an Obsidian install around Step 5, and so on) right when you need it, not before.

A note on safety: these prompts tell Claude Code to ask before anything risky (spending money, touching a server, deleting things). Keep that. If a prompt ever wants to do something you don't understand, stop and ask it to explain first. And most prompts end by having Claude Code **verify the step actually worked** before you move on. Don't skip that; it's how you know it built the right thing, not just plausible files.

---

# The build

Seven steps, in order. For each: read the step in [build-map.md](build-map.md) first (the *why* and the practices behind it), then expand the prompt here and paste it into your Claude Code. Do **not** paste them all at once; each step should be useful before you move to the next. Fill in any `<angle-bracket>` bits before pasting.

One session rule: the prompts assume you're continuing the session where you pasted Prompt 0. If you come back in a **fresh session** (a new day, or the context got too large), open Claude Code in this starter folder again and re-paste Prompt 0 first — it's safe to re-run, it will see your existing working folder and pick up where you left off. Then paste the step prompt you're on.

## Prompt 0 — Orientation (paste this first)

<details>
<summary><b>Show Prompt 0</b></summary>

```
You're going to help me build a personal "second brain plus assistant" on top of you (Claude Code),
following a bundle of docs in this folder. The system is organized around two ideas worth knowing up
front: Nate Herk's "Four C's" (Context, Connections, Capabilities, Cadence — the four layers we build in
priority order), and Andrej Karpathy's context engineering (keep the always-on context lean, and store
knowledge as a plain-markdown wiki, not a vector database). Frame your guidance around those.

Before we do anything, read these files and get oriented:

1. README.md  (the entry point and the per-step prompts)
2. build-map.md  (the main plan: 7 steps across four layers — credits and sources are in its principles table)
3. reference/file-structure.md  (the folder layout)
4. reference/tools-and-services.md  (the concrete tools)

Then, do NOT start building yet. Instead:
- Give me a 5-sentence summary of what this system is and the order we'd build it in.
- Ask me the orientation questions (which stopping point I'm aiming for, whether I already use a
  markdown notes app, how many machines I'm on).
- Based on my answers, recommend which steps I should actually do and which I should skip, and tell me
  which setup prompt to use next.
- Set up my workspace: create a new, separate folder for my actual system (suggest a location like a
  `my-os/` folder in my home directory, and confirm it with me). Everything we build goes there. Treat
  this starter bundle as READ-ONLY reference — never edit the starter files themselves.

Rules for our whole project: build everything in my own folder, never modify the starter bundle; don't
spend money or sign me up for anything without asking; never put a secret (API key, password) into a file
that git tracks; confirm before deleting or overwriting anything; and let's stay in this same Claude Code
session as we move through the steps unless you tell me the context is getting too large.
```

</details>

## Step 1 — Personal context

The highest-leverage hour of the whole build: a small set of markdown files (who you are, how you work, how you write, plus a short router) that Claude reads at the start of every session. Read [build-map.md](build-map.md) Step 1; starter files live in [templates/](templates/).

<details>
<summary><b>Show Prompt 1</b></summary>

```
Let's do Step 1 (Context) from build-map.md. Read build-map.md Step 1 and the files in templates/
(CLAUDE.md, about-me.md, working-style.md, brand-voice.md).

Then set up my context files for me by interviewing me:
- Create context/about-me.md, context/working-style.md, context/brand-voice.md, and a root CLAUDE.md
  router, based on the templates.
- Ask me the questions needed to fill in about-me.md first (it's the highest-leverage one). Ask a few at
  a time, not all at once.
- For working-style.md and brand-voice.md, start from the template defaults and ask me only what you need
  to personalize them. For brand-voice, offer to extract my voice from 3 to 5 writing samples if I paste
  them.
- Keep CLAUDE.md short; it's just a router that points to the other three.

Show me each file before saving it. Keep my answers concrete.
```

</details>

## Step 2 — Persistent memory

A flat folder of small markdown files, one durable fact per file, plus a one-line index that loads every session. One-off chats start accumulating into knowledge Claude carries forward. Read [build-map.md](build-map.md) Step 2.

<details>
<summary><b>Show Prompt 2</b></summary>

```
Let's do Step 2 (Memory) from build-map.md. Read build-map.md Step 2 and templates/memory/ (MEMORY.md and
example-memory.md).

Set up a memory/ folder with a MEMORY.md index, following the one-fact-per-file pattern. Then, from
everything you now know about me (and our conversation so far), propose 3 to 5 starter memory files:
durable facts worth carrying across sessions. For each, show me the file and a one-line index entry, and
let me approve or edit before saving.

Remember the rule: durable facts go in memory/; live, changing project status goes in a STATUS.md, NOT in
memory. Don't put anything that changes week to week into the always-loaded index.
```

</details>

## Step 3 — Portability (git + sync)

Git as the backbone: your system follows you across machines, fully version-controlled, with history, rollback, and backup for free. Read [build-map.md](build-map.md) Step 3 and [reference/file-structure.md](reference/file-structure.md).

<details>
<summary><b>Show Prompt 3</b></summary>

```
Let's do Step 3 (Portability) from build-map.md. Read build-map.md Step 3, reference/file-structure.md,
and the Step 3 section of reference/tools-and-services.md.

Help me put this under git and sync it. Do the manual basics first; save any automation for later.
All of this happens in MY working folder (the one we set up in Prompt 0), never in this starter bundle.
- Initialize a git repo in my working folder if there isn't one, with a sensible .gitignore (make sure
  secrets and any .env files are ignored).
- Walk me through creating a private GitHub repo and pushing to it. Tell me whether you're going to run
  each git command yourself or give it to me to paste, and pause for my OK before anything that touches the
  remote (creating the repo, the first push). I'm still learning git, so explain each command.

Check it worked (do this before the first push):
- Run `git status` and confirm `.env` and any secret/credential files are NOT listed, and that `.gitignore`
  contains them. If a secret would be committed, stop and fix .gitignore first.
- After pushing, confirm on GitHub that the repo is private and that no `.env` or secret file is in it.

Only AFTER I've done manual pull / status / commit / push myself a few times and I'm comfortable: if I use
more than one machine, set up the simplest possible scheduled sync (a small `git pull && git push` on a
timer). Explain the tradeoffs and the failure modes (merge conflicts, accidental commits) before building
it. Never commit a secret.
```

</details>

## Step 4 — Capabilities (skills)

Your first two reusable skills: `/wrap-up` writes a handoff note at the end of a session, `/resume` reads it back at the start of the next. Kills the cold-start problem. Read [build-map.md](build-map.md) Step 4.

<details>
<summary><b>Show Prompt 4</b></summary>

```
Let's do Step 4 (Capabilities) from build-map.md. Read build-map.md Step 4.

Create my first two Claude Code skills as slash commands:
- /wrap-up — writes a short handoff note (what I did, what's next, open questions) into the current
  project's STATUS.md at the end of a session.
- /resume — reads that note back at the start of the next session so I pick up where I left off.

Build them as proper Claude Code skills in my project (not in the starter bundle). I may not know what a
Claude Code skill even is, so tell me in one line what it is, exactly where the skill files live, how I
invoke them, and how I'd remove one.

Check it worked: run /wrap-up to write a handoff note, then start a fresh session (or have me close and
reopen) and run /resume, and confirm the note actually round-trips before we move on. Battle-test the loop
by hand before we rely on it.
```

</details>

## Step 5 — The second brain (knowledge wiki)

A plain-markdown knowledge wiki built as a pipeline (capture raw sources, ingest them into durable linked pages), with an Obsidian vault on top for navigation. The difference between "I read something useful once" and "my system knows it." Read [build-map.md](build-map.md) Step 5 (it carries the most best-practices); the deep dive is [deep-dives/wiki-deep-dive.md](deep-dives/wiki-deep-dive.md).

<details>
<summary><b>Show Prompt 5</b></summary>

```
Let's do Step 5 (the wiki) from build-map.md. Read build-map.md Step 5 (it has the most best-practices),
reference/file-structure.md (the research/ layout), and the Step 5 section of
reference/tools-and-services.md.

Set up the knowledge wiki, and do it INCREMENTALLY — confirm each piece works before building the next.
Do not build it all in one shot:

5a. Create the research/ structure: an index.md, a raw/ folder for immutable captures, and a wiki/ folder
    organized BY FUNCTION (concepts/, patterns/, sources/, tools/, guides/), not by topic. Give each
    folder a short, frontmatter-free index.md that lists its files one line each (`* [title](file.md) -
    description`), so I (and you) can read cheap folder metadata before opening files — this is Google's
    OKF navigation pattern; see reference/file-structure.md rule 3 for the exact format, and keep these
    indexes updated whenever we add or rename a file. Explain how I'll capture sources (e.g. the Obsidian
    Web Clipper into raw/), and that raw captures stay immutable except a status field while curation
    happens in wiki/ pages linked with standard markdown links [page-name](page-name.md). Configure
    Obsidian with `Use [[Wikilinks]]` turned OFF — this keeps links standard markdown so they render on
    GitHub, in VS Code, and in agents without Obsidian installed.
5b. Ingest ONE real source by hand into a wiki/ page (summary, key takeaways, a couple of cross-links),
    so I see the capture-to-page flow once before any automation. Use standard markdown links
    [page-name](page-name.md) — NOT Obsidian [[wikilinks]] — so the links render in every tool.
    Define a small controlled tag vocabulary with me while we do it.
5c. THEN build a simple "ingest" skill that turns a raw capture into a linked wiki page, with a
    read-before-write rule so it never blindly overwrites an existing page.
5d. THEN build the fail-closed safety gate from the build map. Here's what "good" looks like, and how
    we'll verify it together: it must (i) run BEFORE any capture is read, (ii) be plain regex with NO model
    (so hostile text can't trick it), (iii) move anything suspicious into a gitignored quarantine/ folder,
    and (iv) fail closed (if it errors, STOP and ingest nothing). Verify it: feed it a test file containing
    an obvious injection line like "ignore previous instructions and ..." and confirm it quarantines that
    file while leaving a clean file untouched.

Only after 5a to 5d work, walk me through ingesting one real fetched source end to end.
```

</details>

## Step 6 — Cadence (your first automation)

One scheduled job on your laptop, no server needed: a weekly brief or digest built as a proper loop (trigger, work, verification, output to a file), with a hard rule that anything outbound drafts and never sends. Read [build-map.md](build-map.md) Step 6, including the Step 6 vs Step 7 clarification.

<details>
<summary><b>Show Prompt 6</b></summary>

```
Let's do Step 6 (Cadence) from build-map.md. Read build-map.md Step 6 (note the Step 6 vs Step 7
clarification) and the Step 6 section of reference/tools-and-services.md.

This step needs NO server. Help me build one scheduled automation that runs on my laptop:
- Pick a simple, genuinely useful weekly job with me (e.g. a digest or brief).
- Write it as a "loop": a trigger (the schedule), the work, a goal + how it verifies it's done, and an
  output written to a file so nothing is lost.
- Set it up with my OS's built-in scheduler (cron / launchd / Task Scheduler) — tell me which I have and
  walk me through it.
- Hard rule: if it produces anything that leaves the building (an email, a post), it DRAFTS only and never
  sends. Sending stays a manual click by me.

Explain the schedule setup before running it, and let's do a manual test run first.

Check it worked: show me the scheduled job you created, run it manually once and show me the output, tell
me where its log/output goes and when it next runs, and give me the exact command to disable or remove it.
Confirm the scheduler command matches my actual OS and user account, and that the job does NOT run from a
Downloads or cloud-synced folder.
```

</details>

## Step 7 — The always-on agent (optional)

A persistent agent on a cheap VPS, reachable from your phone over Telegram. It reads your calendar and inbox and sends a morning brief on its own heartbeat. The hardest tier to build and run safely, and the most optional. Read [build-map.md](build-map.md) Step 7 (and "Step 7, concretely"), then [reference/hermes-setup-runbook.md](reference/hermes-setup-runbook.md).

<details>
<summary><b>Show Prompt 7</b></summary>

```
I want to consider Step 7 (the always-on Hermes agent) from build-map.md. Read build-map.md Step 7, the
whole reference/hermes-setup-runbook.md, reference/ARCHITECTURE-SUMMARY.md, and the Step 7 section of
reference/tools-and-services.md.

First, talk me OUT of it if I'm not ready: confirm I've actually gotten value from Steps 1 to 5, and that
I understand this is the only tier with real monthly cost (~$10 to $30) and ongoing upkeep. If I'm not
ready, say so.

If I am ready, guide me through Phase 1 of the runbook ONLY (the base: VPS + the core stack + Telegram +
the orchestrator), one numbered step at a time. For each step:
- Tell me exactly what to do and which service to use (the runbook and tools-and-services name them).
- Stop and wait for me to confirm each step worked before moving to the next.
- Be extremely careful with the security checklist — the Telegram allow-list, keeping the dashboard on the
  private VPN, scoped read-only keys, and keys in their own container are non-negotiable.

Before I connect any real account or key, VERIFY the security posture with me using concrete checks, not
just "a message arrived":
- From a network OUTSIDE the private VPN (e.g. my phone on cellular), confirm the dashboard and SSH ports
  refuse or time out — only the VPN address should work.
- Have me message the bot from a DIFFERENT Telegram account (or ask a friend to), and confirm it refuses
  and that the rejection shows in the logs.
- Confirm the API keys are not readable from inside the agent's own container.
- Confirm the config-backup repo is private.
- Confirm a hard monthly spend alert is set.
Phase 1 is not "done" until these checks pass.

Do NOT do Phases 2 or 3 yet. Phase 1 has to be useful for about two weeks first. And never put a real key,
token, or password into anything git tracks.
```

</details>

## After any step

<details>
<summary><b>Show the after-any-step prompt</b></summary>

```
We just finished Step <N>. Append a short entry to a running changelog at ops/CHANGES.log (create the
file and the ops/ folder if they don't exist yet) noting what we set up, then remind me which step and
which setup prompt comes next. If anything is half-finished or blocked, say so plainly.
```

</details>

---

# What's in this repo

```
README.md                  <- you are here: the entry point + the build walkthrough
build-map.md               <- the main read: 7 steps, what each buys you, and the practices behind them
templates/                 <- fill-in starting points for Steps 1-2 (router, context files, memory)
reference/                 <- pull these up when you need the "exactly how"
  tools-and-services.md    <- what service to use at each step, costs, alternatives
  file-structure.md        <- a folder layout you can copy, mapped to the steps
  secrets-101.md           <- keys and passwords, safely (read before your first API key)
  ARCHITECTURE-SUMMARY.md  <- plain-language picture of where data lives and how it moves
  claude-os-architecture.excalidraw  <- the diagram (open at excalidraw.com or the VS Code extension)
  hermes-setup-runbook.md  <- the phased Step 7 checklist (only if you do Step 7)
deep-dives/                <- optional rabbit holes; skip until you're building that step
  wiki-deep-dive.md        <- Step 5: the full capture-to-ingest workflow
  researcher-deep-dive.md  <- Step 7: the autonomous web-research arm
  building-into-hermes.md  <- Step 7: why the agent is built from a git blueprint, not live on the box
  optimizations.md         <- speed and cost add-ons once it's running
  additional-resources.md  <- the people and ideas behind the build, plus my researcher's sources
```

**Reading order:** this page → [build-map.md](build-map.md) → everything else when a step points you at it. The architecture summary and diagram are most useful once you reach Step 3 (multi-machine sync) or Step 7 (the server); skim early for the shape, come back when you're there.

# What's in here vs. what's yours

This repo is the **skeleton**: the structure, the patterns, the order. The **filling** is entirely yours — who you are, your voice, your facts, your knowledge domains, what your automations do. The build map flags which is which at every step. Nothing here contains my private data or any secrets, so it's safe to read, copy, and adapt freely.

Questions worth answering honestly before you start (Prompt 0 asks them):

- Which stopping point are you actually aiming for? (Most people want Steps 1 to 5.)
- Do you already use Obsidian or a markdown notes app? (Step 5 assumes a plain-markdown vault.)
- Are you on one machine or several? (That changes how much the sync layer in Step 3 matters.)
