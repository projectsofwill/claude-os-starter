---
name: example-memory
description: A worked example showing the one-fact-per-file memory format. Delete once you get the shape.
metadata:
  type: reference
---

This file is an example of a single memory. The rules that make the pattern work:

- **One durable fact per file.** Not a journal, not project status. Just a thing that stays true and is
  worth carrying across sessions (a preference, a decision, a stable detail about you or a project).
- **The frontmatter does the routing.** The `description` line is what Claude scans to decide whether
  this file is relevant, so write it as a clear one-line summary.
- **`type`** is one of: `user` (who you are), `feedback` (how you want Claude to work, with the why),
  `project` (ongoing work not obvious from the files), `reference` (pointers to external resources).
- **Link related memories** with `[their-name](their-name.md)`, using the other file's `name:` slug as
  both the link text and the target filename. Standard markdown — renders in every tool, not just Obsidian.
- **Live, moving status does NOT go here.** That belongs in a project's `STATUS.md`. Memory is for what
  stays true; STATUS is for "where things stand right now." Keeping them separate is what stops this
  index from bloating and going stale.

Whenever you add a file like this, add a matching one-line pointer to `MEMORY.md`.
