# Setup prompts (drive your own Claude Code through this)

This bundle is the map. These prompts are how you get **your own Claude Code** to actually build it with
you, one step at a time. Each prompt is scoped to one step, tells Claude Code to read the right bundle
files first, and includes the guardrails so it guides you instead of running off and doing the wrong thing.

## How to use

1. Put this whole bundle in a folder, and open **Claude Code** in that folder (so it can read these files).
2. Start with **Prompt 0** below. Then do one step at a time, in order, pasting the matching prompt when
   you're ready for that step.
3. Do **not** paste them all at once. Each step should be useful before you move to the next. Stop whenever
   the value stops being worth the effort; the build map explains the three natural stopping points.
4. Fill in any `<angle-bracket>` bits before pasting.
5. Most prompts end by having Claude Code **verify the step actually worked** (run it, check the output)
   before you move on. Don't skip that. It's how you know it built the right thing, not just plausible
   files. If a check fails, tell Claude Code what you saw and have it fix it before continuing.

A note on safety: these prompts tell Claude Code to ask before anything risky (spending money, touching a
server, deleting things). Keep that. If a prompt ever wants to do something you don't understand, stop and
ask it to explain first.

---

## Prompt 0 — Orientation (paste this first)

```
You're going to help me build a personal "second brain plus assistant" on top of you (Claude Code),
following a bundle of docs in this folder. The system is organized around two ideas worth knowing up
front: Nate Herk's "Four C's" (Context, Connections, Capabilities, Cadence — the four layers we build in
priority order), and Andrej Karpathy's context engineering (keep the always-on context lean, and store
knowledge as a plain-markdown wiki, not a vector database). Frame your guidance around those.

Before we do anything, read these files and get oriented:

1. START-HERE.md
2. build-map.md  (the main plan: 7 steps across four layers — credits and sources are in its principles table)
3. file-structure.md  (the folder layout)
4. tools-and-services.md  (the concrete tools)

Then, do NOT start building yet. Instead:
- Give me a 5-sentence summary of what this system is and the order we'd build it in.
- Ask me the orientation questions from START-HERE (which stopping point I'm aiming for, whether I already
  use a markdown notes app, how many machines I'm on).
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

---

## Prompt 1 — Context (Step 1)

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

---

## Prompt 2 — Memory (Step 2)

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

---

## Prompt 3 — Portability / sync (Step 3)

```
Let's do Step 3 (Portability) from build-map.md. Read build-map.md Step 3, file-structure.md, and the
Step 3 section of tools-and-services.md.

Help me put this under git and sync it. Do the manual basics first; save any automation for later.
- Initialize a git repo here if there isn't one, with a sensible .gitignore (make sure secrets and any
  .env files are ignored).
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

---

## Prompt 4 — Capabilities / skills (Step 4)

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

---

## Prompt 5 — The second brain / wiki (Step 5)

```
Let's do Step 5 (the wiki) from build-map.md. Read build-map.md Step 5 (it has the most best-practices),
file-structure.md (the research/ layout), and the Step 5 section of tools-and-services.md.

Set up the knowledge wiki, and do it INCREMENTALLY — confirm each piece works before building the next.
Do not build it all in one shot:

5a. Create the research/ structure: an index.md, a raw/ folder for immutable captures, and a wiki/ folder
    organized BY FUNCTION (concepts/, patterns/, sources/, tools/, guides/), not by topic. Explain how I'll
    capture sources (e.g. the Obsidian Web Clipper into raw/), and that raw captures stay immutable except
    a status field while curation happens in wiki/ pages with [[wikilinks]].
5b. Ingest ONE real source by hand into a wiki/ page (summary, key takeaways, a couple of [[wikilinks]]),
    so I see the capture-to-page flow once before any automation. Define a small controlled tag vocabulary
    with me while we do it.
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

---

## Prompt 6 — Cadence / first automation (Step 6)

```
Let's do Step 6 (Cadence) from build-map.md. Read build-map.md Step 6 (note the Step 6 vs Step 7
clarification) and the Step 6 section of tools-and-services.md.

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

---

## Prompt 7 — The always-on agent (Step 7, optional)

```
I want to consider Step 7 (the always-on Hermes agent) from build-map.md. Read build-map.md Step 7, the
whole hermes-setup-runbook.md, ARCHITECTURE-SUMMARY.md, and the Step 7 section of tools-and-services.md.

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

---

## After any step

```
We just finished Step <N>. Append a short entry to a running changelog at ops/CHANGES.log (create the
file and the ops/ folder if they don't exist yet) noting what we set up, then remind me which step and
which setup prompt comes next. If anything is half-finished or blocked, say so plainly.
```
