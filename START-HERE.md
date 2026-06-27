# Start here

This is a small bundle that explains a personal "second brain plus assistant" I built on top of Claude,
and how you'd build your own. It is not a product or an installer. It is the map, the reasoning, and the
order, so you can copy the parts that fit and skip the rest.

## How this actually works (read this first)

This is important, because it's not obvious from a folder of markdown files:

- **There is no app here, and no code to install.** This bundle is the *plan* (what to build and why),
  the *prompts* (that drive Claude Code to build it), and *templates* (starter files you fill in). That's it.
- **You build it by talking to Claude Code, not by running these files.** The flow: open **Claude Code**
  in this folder, read a step in `build-map.md`, then paste that step's prompt from `setup-prompts.md`.
  Claude Code reads the bundle and builds that step *with you*, asking you questions as it goes.
- **When a step needs a script, a skill, or a tool** (a sync script, the `/ingest` skill, a safety
  scanner), **Claude Code writes it for you** during that step. Those files are not in this bundle on
  purpose. The deep-dives (`wiki-deep-dive.md`, `researcher-deep-dive.md`) describe how *mine* work, in
  plain language, so Claude Code can recreate the same thing for you. You do not need to be able to write
  any of it yourself.
- **Build in your OWN folder, not this one.** Keep this bundle as read-only reference. Your actual system
  should live in a separate, fresh folder (call it `my-os/` or whatever you like). Prompt 0 tells Claude
  Code to set that up. Don't let it edit these starter files — you want your system separate from the
  instructions for building it.

So the loop for every step is: **read the step → paste its prompt → answer Claude Code's questions.** If
you only remember one thing from this page, remember that.

## Before you start

1. **Install Claude Code and sign in.** It runs in your terminal and inside VS Code — see
   [claude.com/claude-code](https://claude.com/claude-code). You don't need anything else yet;
   `tools-and-services.md` lists the rest, introduced per step.
2. **Put this folder somewhere boring and local** — your home directory or Desktop. *Avoid* a cloud-synced
   folder (iCloud Drive, OneDrive, Dropbox); those can fight with git once you reach Step 3.
3. **Open this folder in Claude Code** (open a terminal in the folder and run Claude Code there, or open
   the folder in VS Code and start the Claude Code extension). Quick check that it can see the files: ask
   it *"list the files in this folder and tell me what START-HERE.md says."* If it answers, you're set.
4. **Paste Prompt 0** from `setup-prompts.md`. That's your first action; it orients Claude Code and sets up
   your own working folder. Everything flows from there.

Each later step tells you what else to set up (a free GitHub account around Step 3, an Obsidian install
around Step 5, and so on) right when you need it, not before.

## Read in this order

1. **`build-map.md`** — the main read. Seven steps across four layers (Context, Connections,
   Capabilities, Cadence), in the order I built them, with what each step buys you and the research-backed
   reason it's built that way. Start here even if you only ever do Step 1.
2. **`ARCHITECTURE-SUMMARY.md`** (+ the diagram) — the plain-language picture of where data lives and how
   it moves between your laptops and the server. **You don't need this to start.** It's most useful once
   you're doing multi-machine sync (Step 3) or the always-on agent (Step 7); it describes my fuller setup,
   so skim it early for the shape and come back to it when you actually reach those steps.
3. **`claude-os-architecture.excalidraw`** — the diagram for #2 (it shows *my* example system, agents and
   all). Open it at [excalidraw.com](https://excalidraw.com) (File → Open) or with the Excalidraw VS Code
   extension.
4. **`hermes-setup-runbook.md`** — only if you decide to do Step 7 (the always-on agent). This is the
   ordered, concrete setup checklist for the VPS. Most people should not start here, and many should never
   do it at all. The build map explains why.

## Reference files (pull these up when you need the "exactly how")

- **`setup-prompts.md`** — the way you actually *build* this. Copy-paste prompts (one per step) that point
  your own Claude Code at this bundle and have it guide you through each step. Start with Prompt 0.
- **`tools-and-services.md`** — the concrete answer to "what service do I actually use for this?" The exact
  tools I use at each step (Hostinger, Tailscale, Obsidian, Codex, and so on), what each costs, and the
  cheaper alternatives. Read this whenever the build map names a *pattern* and you want a *product*.
- **`file-structure.md`** — a folder layout you can copy, based on mine, mapped to the build steps so you
  know which folders to add when.
- **`secrets-101.md`** — how to handle keys and passwords safely (you can ignore it until Step 6, but read
  it before you touch your first API key).
- **`templates/`** — fill-in-the-blank starting points for the Step 1 and Step 2 files (`CLAUDE.md`,
  `about-me.md`, `working-style.md`, `brand-voice.md`, and a `memory/` example), de-personalized from my
  own. See `templates/README.md`.

## Optional deep-dives (the rabbit holes)

Skip these until you're actually building the step they belong to. They go deeper than the build map, into
the decisions behind my own setup.

- **`wiki-deep-dive.md`** (Step 5) — the full capture-to-ingest workflow and its decisions: Web Clipper as
  the default, the PDF scanner, the YouTube frame-analysis gate, the `/ingest` skill walked through.
- **`researcher-deep-dive.md`** (Step 7) — the autonomous web-research arm: three-tier fetching, the
  dual-LLM safety firewall, and the human-gated ingest. The deepest part of the whole build.
- **`building-into-hermes.md`** (Step 7) — why I build the agent from my desk (a versioned git blueprint
  deployed to the server) instead of editing it live, with the pros and cons of each.
- **`optimizations.md`** — speed and cost add-ons once it's running (Wispr Flow, Headroom, model routing).
- **`additional-resources.md`** — the people and ideas behind the build, and the actual sources my
  researcher crawls (a starter follow-list you should swap for your own domains).

## What you actually need

- You should be comfortable with **Claude** (ideally **Claude Code**). You do **not** need to be an engineer.
- You do need to be willing to keep a few markdown files and run a sync script.
- Steps 1 to 5 need only your laptop. Step 6 adds a scheduled job. Step 7 adds a cheap Linux VPS
  (a few dollars a month) and is the only step that costs ongoing money and real upkeep.

## Three honest stopping points

- **An afternoon (Steps 1 to 2):** Claude knows you and remembers across sessions.
- **The 80/20 (Steps 1 to 5):** a real second brain with skills and a knowledge base. Most people should
  live here.
- **The full system (Steps 6 to 7):** scheduled automations and an always-on agent. Powerful, the most
  work to run, genuinely optional.

There is no prize for reaching Step 7. Stop wherever the value stops being worth the upkeep.

## A note on what's in here vs. what's yours

The bundle is the **skeleton** (the structure, the patterns, the order). The **filling** is entirely
yours: who you are, your voice, your facts, your knowledge domains, what your automations do. The build
map flags which is which at every step. Nothing in this bundle contains my private data or any secrets,
so it's safe to read, copy, and adapt freely.

## Questions worth asking me before you start

- Which stopping point are you actually aiming for? (Be honest. Most people want Steps 1 to 5.)
- Do you already use Obsidian or a markdown notes app? (Step 5 assumes a plain-markdown vault.)
- Are you on one machine or several? (That changes how much the sync layer in Step 3 matters.)
