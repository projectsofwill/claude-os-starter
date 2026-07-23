# Secrets 101 (handling keys safely)

A short, beginner's guide to handling the keys and passwords your setup needs without leaking them. **You can ignore this entirely until Step 6** — Steps 1 to 5 are just markdown files, no secrets involved. Skim it then, read it properly at Step 7.

---

## What a "secret" is

A **secret** is anything that lets someone act as you or spend your money if they get it. In this build that means:

- **API keys** (the long strings that let a tool call a paid service — Perplexity, an LLM provider).
- **Access tokens** (e.g. your Telegram bot token in Step 7).
- **Passwords** (a database password, an account login).
- **OAuth credential files** — the files Google hands you to connect Gmail/Calendar (often named `credentials.json` and `token.json`). These *are* secrets even though they're files, not strings.

Simple test: **if leaking it would let someone act as you or spend your money, it's a secret.**

---

## The two golden rules

1. **Never paste a secret into a chat or a tracked file.** Not into a chat window (including Claude), not into any file that git tracks (so not `CLAUDE.md`, not a note, not code you'll commit). Once it's in a chat or in git history, treat it as exposed.
2. **A secret lives in exactly one of two safe places** — your **password manager**, or a local **`.env` file that git ignores**. Nowhere else.

That's the whole discipline. Everything below is just the detail.

---

## What goes where

- **Password manager** (I use **[1Password](https://1password.com)**, any one works) — holds the **master copy** of every key, token, and OAuth file. This is your source of truth. If your laptop dies, the keys are here.
- **A gitignored `.env` file** — holds the **working copy** your tools actually read on your machine. It sits in the project folder, and git is told to ignore it so it never gets committed. Think of it as a local scratch copy of what's in your password manager.
- **`dotenvx`** (**[dotenvx.com](https://dotenvx.com)** · [github](https://github.com/dotenvx/dotenvx)) — an *optional* Step-7 tool that **encrypts** a `.env` file so it *can* safely live in git (the committed values are gibberish without a private key you keep separate). Useful once you're syncing an agent's config across machines. **Skip it until Step 7** — a plain gitignored `.env` is all you need before then.

---

## Check before your first push

Before you ever run `git push`, confirm your `.env` won't be committed. The easy way: **ask Claude Code to verify it for you.** Tell it:

> "Confirm my `.env` is safely ignored: run `git status` and check `.env` is not listed, and check that `.gitignore` actually contains a `.env` line. Don't push if it's not."

What you're confirming:

- **`.gitignore` contains `.env`** (the line that tells git to skip it). See git's official [gitignore docs](https://git-scm.com/docs/gitignore) if you want the why.
- **`git status` does not list `.env`** as a file to be committed. If git shows it, it is *not* yet ignored — stop and fix `.gitignore` first.

Do this **before** the first push, not after. Once a secret is pushed, the next section applies.

---

## If you leak one

If a secret ever lands in a chat, a commit, or anywhere public — **rotate it immediately**:

1. Go to the provider (Google, the API service, BotFather, etc.) and **regenerate the key** — this kills the old one.
2. **Update your `.env`** (and your password manager) with the new value.

And know this: **a committed secret is compromised even if you delete the commit.** Git keeps history, so the old value is still recoverable from the repo. Deleting the file doesn't undo it — only rotating at the provider does. When in doubt, rotate. It costs you two minutes and a key is cheap to regenerate.

---

## When you'll actually deal with this

- **Steps 1 to 5:** nothing. Those are plain markdown — no keys, no `.env`, nothing to leak. Don't worry about any of this yet.
- **Step 6 (scheduled automation):** your first real secret — usually one API key (e.g. Perplexity) plus the Gmail OAuth files for the draft. This is where you create your first `.env` and run the "check before push" step above.
- **Step 7 (always-on agent):** several keys at once (model keys, the Telegram token, a database password). This is where `dotenvx`, scoped read-only keys, and keeping keys out of the agent's reach start to matter — covered in the Step 7 material.

So: read this, then forget it until Step 6. By the time you need it, it's two rules and a one-line check.
