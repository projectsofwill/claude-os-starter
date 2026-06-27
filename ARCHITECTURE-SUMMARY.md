# Memory & Data Architecture (plain-language summary)

A companion to the diagram (`claude-os-architecture.excalidraw`) and to `build-map.md`. It explains
*where the data lives*, *how it moves*, and *the naming* so the whole thing stops being confusing. This
describes my setup; yours would have the same shape with your own content.

---

## The one-paragraph version

There are **two places**: your **laptops** (mine are a Mac + a PC) and one **VPS** (the always-on
"Hermes" box from Step 7 of the build map). Content travels between them through **one hub: GitHub**,
never a direct laptop-to-VPS link. *Live* questions (from your phone over Telegram) travel a different
way, over a private VPN (**Tailscale**). Your research knowledge lives in a **markdown wiki** on your
laptops, and that IS the source of truth. It syncs Mac to PC via GitHub, and the VPS pulls a read-only
copy. Your private *facts* never leave your laptops. Your structured personal *data* (workouts, etc.,
handled by an agent I call Alfred) lives on the VPS in a database.

---

## The three stores (what you have, and where each lives)

| Store | Lives on | Holds | Notes |
|---|---|---|---|
| **`research/` wiki** | Your laptops | External knowledge (articles, tools, patterns) | Markdown = **source of truth**. Synced Mac to PC via GitHub; VPS pulls a read-only copy. |
| **`memory/` repo** | Your laptops **only** | Your most-sensitive facts: identity, finances, health *records*, preferences | **Never** goes to any server. The conservative tier. |
| **`alfred` database** | The **VPS** (private) | Operational self-logs you hand the assistant (a workout, a meal) | Where "I did 10 pushups" lands, logged over Telegram. |

**A fair question: isn't a workout personal too?** Yes. The line here isn't "personal vs. not" (both stores
hold personal data). It's **sensitivity plus purpose**. My most sensitive identity data (finances, health
*records*, anything damaging to leak or that the assistant doesn't need) stays in `memory/`, on my laptop,
never on a server at all. Operational data I *deliberately* log so the assistant can do its job (workouts,
meals) goes to the `alfred` database, which lives on my **own private VPS** (Tailscale-only, not the public
internet, not a third party). So it's two tiers: "most-sensitive, laptop-only" and "operational, on a
private server I control." If a piece of data feels too sensitive for even your own server, it belongs in
`memory/`.

**One honest nuance for *your* setup.** "Never leaves my laptops" is my strict choice: I keep `memory/` as
its own repo that I don't push anywhere. The simpler default most people start with is `memory/` *inside*
your main private repo, which means it does sync to your **own private GitHub** (private to you, never
public, and never to the VPS). That's fine for most personal facts. Only split `memory/` out into a
laptop-only repo if you have facts you don't want on GitHub at all. So read "never leaves your laptops" as
"this is the strict option"; the everyday default is "stays in your private repo, never on the server."

Key idea: the **markdown wiki is the knowledge layer**. There is no separate search index or vector
database. At this scale (a few hundred pages) flat markdown plus Obsidian's `[[wikilinks]]` is enough to
navigate, and the tools read the files directly. Add a search index only if the wiki grows past roughly a
thousand pages and flat-file navigation starts to hurt. (See `build-map.md` Step 5 for why a markdown
wiki beats a vector database until then.)

---

## The two channels (how content moves)

These are genuinely separate paths. Mixing them up is most of the confusion.

### Channel 1 — content sync (everything meets at GitHub)

- A small sync script (every 15 min) pushes/pulls **the core repo, research, and memory** between your
  laptops and GitHub.
- The **VPS independently pulls** the `research` wiki from GitHub on its own schedule (`git pull --ff-only`).
  It keeps a plain read-only copy of the wiki.
- **Deploy:** the agent scripts/config you edit in the `Hermes/` folder are pushed **repo to VPS** when
  you run the deploy. It is not a live sync (blueprint vs. the building).
- **Backup:** the VPS nightly-commits its live config to a separate private repo (a drift snapshot).
- **There is no direct laptop-to-VPS link for content.** GitHub sits in the middle.

### Channel 2 — live queries (over Tailscale, no GitHub)

- **Telegram to the Hermes orchestrator** routes your message to the right **agent**. I mostly talk to two
  personal-data agents: **Alfred** (food, people) and **Arnold** (fitness). They read and write my
  structured data in the database on the VPS. (Note: "Alfred" is an *agent*; the database is a separate
  thing it writes to. Different layers, same name by history.)
- **Claude Code** reads the markdown wiki files directly on your laptop (flat-file search, no index).

---

## The walls (what's isolated from what)

- **`memory/` never reaches the VPS.** Local-only trust boundary; your PII stays on your laptops.
- **The markdown wiki is read-only to every agent.** No agent writes to it. It stays the authoritative
  knowledge layer; only a human-initiated ingest adds pages.
- **The VPS is Tailscale-private**, not on the public internet. The agent's dashboard is treated like SSH.
- **Cloud API keys live in their own container** on the VPS, never inside the agent itself.

---

## The Hermes VPS (the always-on layer)

The VPS runs **Hermes** (NousResearch's self-hostable agent framework) as a small Docker stack:

- **hermes** — the agent gateway. You reach it from your phone over Telegram and from your desk via the
  dashboard (Tailscale-only). Pinned to a specific version, never `:latest`.
- **searxng** — a self-hosted meta-search engine the researcher uses to find sources.
- **a key-isolation container** — holds the cloud API keys so the agent never sees them directly.

Several agent **profiles**, each narrow. The three from the build map: an **orchestrator** (Telegram +
scheduling + dispatch), a **researcher** (reads the web, locked-down, captures inert files for human
review), and an **EA** (reads calendar/inbox, writes the morning brief, can draft but never send). I also
run two personal-data agents I talk to over Telegram day to day: **Alfred** (food, people) and **Arnold**
(fitness), which read and write the database. They coordinate through a shared task board, not by talking
to each other. Cadence: a morning brief at 8am, a daily news ingest, and the weekly newsletter. Full setup
steps are in `hermes-setup-runbook.md`.

### The `Hermes/` folder vs the Hermes VPS

- The top-level **`Hermes/` folder** (inside the OS repo) is the **blueprint**: docs plus canonical scripts.
- The **VPS** is the running system. You **deploy** the blueprint to it (repo to VPS).
- They are related but not live-synced. Editing the folder doesn't change the VPS until you deploy.

---

## Trace: "I did 10 pushups"

Telegram to the Hermes orchestrator, which routes a fitness log to the **Arnold** agent, which writes a
row to the personal-data database (a `workout_entries` table) in the Postgres container on the private
VPS, and replies "Logged." The morning brief later reads it (read-only) to add your fitness line.
