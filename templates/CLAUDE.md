<!--
  This is the ROUTER. It's the one file Claude reads at the start of every session.
  Keep it SHORT. Its only job is to say who you are at a glance and point to the detail files.
  A short always-on file means more of Claude's attention is on what matters. Do not turn this
  into an encyclopedia. Delete this comment block when you're done.
-->

# <Your Name> — personal context router

You're working with **<Your Name>**, <one line: role / what you do>. This file is a router. Read the
file that fits the task; don't restate them here.

## Who I am, how to work with me

- **`context/about-me.md`** — background, goals, how I spend my week. Read when reasoning about what I'd want.
- **`context/working-style.md`** — how I want you to work with me (ask vs. assume, tone, when to push back). Always applies.
- **`context/brand-voice.md`** — how I write. **Read this before drafting anything in my name** (emails, posts, public copy).
- **`memory/MEMORY.md`** — durable facts about me and my projects, loaded each session. One fact per file.

## House rules

<!-- A few hard, always-on rules. Keep it to the ones that actually matter. Examples: -->

- **Don't spend money or API credits** without checking first.
- **Secrets** live only in a gitignored `.env`. Never commit a secret or paste one into chat.
- **Destructive or hard-to-reverse actions** (deleting, overwriting, anything outward-facing): confirm first.
- <add your own>

<!--
  Tip: as your system grows, this router can also point to a project map (README.md), a status
  dashboard (STATUS.md), and per-project CLAUDE.md files. Start minimal; add pointers as you create
  the things they point to.
-->
