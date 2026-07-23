# Context templates

Starting points for the Step 1 (Context) and Step 2 (Memory) files from `build-map.md`. These are my
own files with the personal content stripped out and replaced by prompts and light examples, so you get a
real scaffold instead of a blank page.

## What's here

- **`CLAUDE.md`** — the router. The one file Claude reads first. Keep it short; it points to the other three.
- **`about-me.md`** — who you are, your goals, how you spend your week. This is the highest-leverage file.
- **`working-style.md`** — how you want Claude to behave (ask vs. assume, how much to explain, when to push back). Most of this is good default behavior, so you can keep a lot of it as-is.
- **`brand-voice.md`** — how you write, so anything Claude drafts in your name sounds like you. Read this before having Claude write anything people-facing.
- **`memory/`** — the Step 2 persistent-memory pattern: a one-line index (`MEMORY.md`) plus one fact per file. Includes one example memory so you can see the shape.

## How to use them

**The easy way:** don't fill these in by hand. Use **Prompt 1** in the root `README.md` — Claude Code reads
these templates and fills them in by interviewing you. That's the intended path. The steps below are the
manual version if you'd rather do it yourself.

1. Copy this `templates/` folder to wherever your OS lives (the files normally sit in a `context/`
   folder, with `CLAUDE.md` at the root).
2. Fill in every `<angle-bracket placeholder>`. Delete the guidance lines (the *italic* notes and the
   `<!-- comments -->`) as you go.
3. Start with `about-me.md`. Get it right before anything else. The build map explains why Context is the
   first hour you spend.
4. `working-style.md` and `brand-voice.md` carry my own preferences as the default (for example, I avoid
   em dashes). Where a preference is mine and not a rule, I've said so. Change those to match you.

Nothing in here contains my private data. Make them yours.
