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
│   ├── index.md                #   (OKF) one-line list of this folder's files; read before the files (rule 3)
│   ├── about-me.md
│   ├── working-style.md
│   └── brand-voice.md
│
├── memory/                     # Step 2 — durable facts, one per file, + a one-line index
│   ├── MEMORY.md               #   the index that loads every session (memory's version of the folder index)
│   └── <some-fact>.md          #   one fact per file
│
├── ops/                        # operational docs (grows over time)
│   ├── index.md                #   (OKF) folder index — see rule 3 below
│   ├── STATUS.md               #   live "where things stand" dashboard
│   ├── ROADMAP.md              #   committed direction
│   ├── CHANGES.log             #   session checkpoint log (the discipline layer)
│   ├── reference/              #   stable lookups (docs like this one) — has its own index.md
│   └── records/                #   executed one-off plans, kept for history — has its own index.md
│
├── research/                   # Step 5 — the second-brain wiki
│   ├── index.md                #   the wiki's home page (also serves as its OKF folder index)
│   ├── raw/                    #   immutable captures (never edited; only a status field changes)
│   └── wiki/                   #   curated, linked pages, organized BY FUNCTION (each subfolder gets its own index.md):
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

## Three organizing rules that make it work

**1. Organize by function, not by topic.** Notice the wiki folders are *kinds of page* (concepts,
patterns, sources, tools), not subjects (AI, cooking, finance). The subject goes in a `tags:` field
inside each file. This keeps the tree flat as it grows, instead of spawning a new folder per topic.

**2. Signpost files in CAPS, everything else lowercase-with-dashes.** A small fixed set of all-caps names
(`README`, `CLAUDE`, `ROADMAP`, `STATUS`, `MEMORY`, `CHANGES`) act as landmarks; every other file is
`lowercase-with-dashes.md`. Boring and consistent beats clever.

**3. Every navigable folder gets an `index.md`.** A short, frontmatter-free file that lists what's in the
folder, one line per file. Claude reads this cheap index *before* opening the files themselves, so it
spends fewer tokens and misroutes less often when it's hunting for something. This is the **`index.md`
navigation pattern** from Google's **Open Knowledge Format** (the same OKF behind the markdown-wiki idea
in Step 5) — you adopt OKF's per-folder index, not its full spec (OKF also defines per-document
frontmatter, which this starter skips). Three habits keep the index useful:

- **Read** the folder's `index.md` before drilling into its files.
- **Create** one whenever you add a folder that holds 2+ files. (Skip it for single-file or pure-cache
  folders — there's nothing to index.)
- **Update** it in the *same change* you add, rename, or remove a file. A stale index is worse than none.

The format is plain: no YAML frontmatter, just `#`-heading groups, each followed by a markdown list of
`* [file-title](file-name.md) - one-sentence description`. Group child folders under a `# Subdirectories`
heading and link each one to *its own* `index.md` (`* [reference](reference/index.md) - …`) — this is
exactly what OKF does, so you match the spec here rather than diverge from it. The one place you'll go
off-spec: a folder you deliberately leave *un-indexed* (a plain code directory, say) has no `index.md` to
point at, so list it as plain text (`* tools/ - …`) rather than a bare-folder link like
`[tools](tools/)`. Obsidian only resolves links that point to a note (a `.md` file), not to a folder, so a
bare-folder link becomes an *unresolved* link: it shows up as a phantom placeholder node in the graph,
and clicking it makes Obsidian create the note it thinks is missing — an empty junk file dumped in your
vault root. Plain text has no link to resolve, so none of that happens.
(If a folder holds scripts you want navigable, list them under a `# Scripts` heading — that's a small
Claude-OS add-on; OKF itself indexes only markdown files and subfolders.) You don't write these by hand
every time — once the pattern exists, Claude Code maintains them for you, and the Step 5 lint pass flags
any that have drifted from their folder's actual contents.

> `MEMORY.md` and `README.md` are this same idea in different clothes: `MEMORY.md` is the index for
> `memory/`, and a folder's human-prose `README.md` (if it has one) is the narrative companion to its
> machine-readable `index.md`. They coexist; the `index.md` is the one Claude scans to navigate cheaply.

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
