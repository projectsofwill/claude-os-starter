# File structure (a layout you can copy)

This is the shape of my OS, de-personalized, so you have a concrete skeleton instead of a blank folder.
It's organized by *function*, not by topic, and it grows step by step. You do **not** build all of this
at once. Each folder shows up when its build-map step does, so start with the top few and add the rest as
you go.

The whole thing is one git repo (or a few; see "One repo per project" below).

---

## The full layout

```
my-os/                          # the root repo. Mine is called "claude-os-core".
│
├── CLAUDE.md                   # Step 1 — the router. Claude reads this first. Keep it short.
├── README.md                   # a project map. Add it once you have more than one project.
│
├── context/                    # Step 1 — who you are
│   ├── about-me.md
│   ├── working-style.md
│   └── brand-voice.md
│
├── memory/                     # Step 2 — durable facts, one per file, + a one-line index
│   ├── MEMORY.md               #   the index that loads every session
│   └── <some-fact>.md          #   one fact per file
│
├── ops/                        # operational docs (grows over time)
│   ├── STATUS.md               #   live "where things stand" dashboard
│   ├── ROADMAP.md              #   committed direction
│   ├── CHANGES.log             #   session checkpoint log (the discipline layer)
│   ├── reference/              #   stable lookups (docs like this one)
│   └── records/                #   executed one-off plans, kept for history
│
├── research/                   # Step 5 — the second-brain wiki
│   ├── index.md                #   the wiki's home page
│   ├── raw/                    #   immutable captures (never edited; only a status field changes)
│   └── wiki/                   #   curated, linked pages, organized BY FUNCTION:
│       ├── concepts/           #     ideas
│       ├── patterns/           #     reusable approaches
│       ├── sources/            #     captured articles/videos as pages
│       ├── tools/              #     tools you use
│       └── guides/             #     how-tos
│
├── automations/                # Step 6 — scheduled jobs (or wherever your scheduler points)
│
├── Hermes/                     # Step 7 — the always-on agent blueprint (docs + canonical scripts)
│
├── Projects/                   # your actual projects, one folder each
│   └── <a-project>/            #   can be its own git repo (see below)
│       ├── CLAUDE.md           #   project-specific router/instructions
│       └── STATUS.md
│
└── .claude/                    # Claude Code config for this workspace
    ├── settings.json           #   permissions, hooks
    ├── hooks/                  #   automated guards (e.g. "block destructive git")
    └── skills/                 #   Step 4 — your slash-command skills
```

---

## Two organizing rules that make it work

**1. Organize by function, not by topic.** Notice the wiki folders are *kinds of page* (concepts,
patterns, sources, tools), not subjects (AI, cooking, finance). The subject goes in a `tags:` field
inside each file. This keeps the tree flat as it grows, instead of spawning a new folder per topic.

**2. Signpost files in CAPS, everything else lowercase-with-dashes.** A small fixed set of all-caps names
(`README`, `CLAUDE`, `ROADMAP`, `STATUS`, `MEMORY`, `CHANGES`) act as landmarks; every other file is
`lowercase-with-dashes.md`. Boring and consistent beats clever.

---

## One repo per project (Step 3)

The root is one git repo. Each folder under `Projects/` can be **its own** git repo, self-contained, so
that a project never depends on files above it. This matters if you ever run a project in the cloud or on
a schedule: it gets cloned alone and must still work. My root repo gitignores the project folders so each
stays independent. You don't need this on day one; adopt it when you have a project that runs somewhere
other than your laptop.

---

## A note on where `memory/` lives

I keep my `memory/` folder as its own little repo outside the main tree (it holds personal facts I want
synced but isolated). For a simpler start, a `memory/` folder right inside the root repo, as drawn above,
is completely fine. Split it out later only if you want that separation.

---

## Scale it to your stopping point

You almost certainly should not start with the whole tree. Build it in this order:

- **An afternoon (Steps 1 to 2):** `CLAUDE.md` + `context/` + `memory/`. That's it. Three folders.
- **The 80/20 (Steps 1 to 5):** add `ops/`, `.claude/skills/`, and `research/`. This is where most people
  should live.
- **The full system (Steps 6 to 7):** add `automations/`, `Hermes/`, and the one-repo-per-project split.

Copy the slice you need now. The structure is designed so adding the next folder never forces you to
rearrange the last one.
