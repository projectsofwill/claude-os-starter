# Hermes setup runbook (Step 7)

A distilled, ordered checklist for standing up the always-on agent from `build-map.md` Step 7. Mine runs
on **Hermes** (NousResearch's self-hostable agent framework). This is the "how," in sequence. The "why"
for every choice is in the build map, so read that first.

**You do not run these commands from memory.** This is a checklist of *what* happens in *what order*. The
actual terminal commands, the Docker config, the SSH setup — Claude Code walks you through each one when
you use **Prompt 7** in `setup-prompts.md`. Read this to understand the shape and the safety rules; let
Claude Code do the typing. This is the one tier where leaning on it for the literal commands is expected,
not a failure.

**Before you start, internalize one thing:** the failure mode here is that you build the whole stack, it
runs, and you never look at it because the setup exhausted you. So this runbook is phased. **Each phase
delivers something real and usable on its own.** Do not move to the next phase until the current one has
been useful for about two weeks. If Phase 1 isn't useful, stop. That's a valid outcome.

---

## Prerequisites

- A small Linux VPS (2 vCPU / 8 GB RAM is plenty to start; Ubuntu LTS). A few dollars a month.
- Docker + Docker Compose on the VPS.
- A free Tailscale account (the private VPN), installed on the VPS and your laptop/phone.
- A Telegram account, and a bot created via BotFather (you'll get a bot token).
- Claude OS Steps 1 to 5 already paying off. Do not build this on top of nothing.

---

## Phase 1 — Base: "the agent runs and texts me"

Goal: a message from your agent arrives on your phone, with your laptop turned off.

1. **Lock down access first.** Put the VPS on Tailscale. Bind SSH and the agent dashboard to the Tailscale
   interface only, never the public IP. The dashboard is the entire agent control plane, so treat it like
   SSH.
2. **Bring up the core stack** with Docker Compose, as a non-root user, on its own Docker network:
   - the **agent** container, **pinned to a specific version tag** (never `:latest`, or an upstream update
     will silently break things),
   - a **self-hosted search** container (e.g. SearXNG),
   - a **key-isolation** container that holds your cloud API keys (the agent calls it for inference but
     never holds the keys itself).
3. **Connect Telegram and set the allow-list to exactly one user ID (yours).** This is not optional.
   Test it from a second account: it must refuse, not answer.
4. **Create the orchestrator profile.** One agent, connected to Telegram, owning the schedule. No real
   work yet, just routing.
5. **Set up a nightly config backup** to a private git repo so the VPS state is recoverable.

**Phase 1 is done when:** your phone gets a Telegram message from the agent and your laptop is off.

---

## Phase 2 — one real job: the morning brief

Goal: you wake up to a brief that already read your day.

1. **Add the EA profile.** Give it read-only calendar and inbox access (scoped keys, read-only, never
   your main credentials). It can draft a reply but must never send one.
2. **Write the brief as a scheduled job** (cron, or the framework's built-in scheduler): calendar today +
   tomorrow, inbox triage, one nudge. Make it degrade gracefully: if one source is down, send a partial
   brief with a note, never nothing.
3. **Run it on a schedule** (mine is 8am). Confirm a few unattended runs actually fire.

**Phase 2 is done when:** the brief arrives on its own for a week without you triggering it.

---

## Phase 3 — the researcher (only if you want news ingestion)

Goal: the agent pulls in sources on a schedule without you asking.

1. **Add the researcher profile, locked down hard.** It touches untrusted web content, so it gets the
   smallest toolset of any profile. In my build it is deliberately tool-less: it can read and classify but
   physically cannot write anywhere dangerous.
2. **Make its output inert.** Whatever it captures lands as plain files that a human reviews before
   anything is trusted. Treat anything it fetched as hostile until you've looked at it.
3. **Put a fail-closed safety gate in front of ingestion** (the same one from Step 5): a dumb,
   regex-only scan that quarantines suspicious files before any model reads them.
4. **Coordinate work through a shared task board**, not agent-to-agent chat. You drop a request, the
   orchestrator files it, the researcher picks it up.

**Phase 3 is done when:** a daily ingest runs, captures real sources, and nothing it pulled in can act on
its own.

> The researcher is the deepest rabbit hole in the whole setup (three-tier fetching, a dual-LLM firewall,
> human-gated ingest). The full architecture and the services behind it are in `researcher-deep-dive.md`.
> And before you build any of this, `building-into-hermes.md` covers *how* to build and change the agent
> safely (from a git blueprint, not by editing the live box).

---

## The security checklist (do not skip any of these)

- [ ] Telegram allow-list = exactly your user ID, tested from a second account.
- [ ] Dashboard and SSH bound to the private VPN only, never the public internet.
- [ ] Agent version pinned, never `:latest`.
- [ ] Cloud API keys in their own container, never in the agent.
- [ ] Every key scoped read-only and to the narrow thing it needs; never a main account.
- [ ] Agent runs non-root, inside Docker.
- [ ] Sensitive actions (sending email, pushing to a repo) require manual approval.
- [ ] The agent cannot rewrite its own config at runtime.
- [ ] Untrusted web content passes the fail-closed safety gate before any model reads it.
- [ ] A hard monthly spend alert is set.

The principle under all of these is **keys, not prompts**: a rule in a config file is a *request*; a
scoped, read-only key is a *hard line*. Where you can make something impossible instead of merely
discouraged, do.

---

## Rough cost

A small VPS is a few dollars a month. The one quality model you pay per-token for (the EA's brief) is the
main variable. Search and the lightweight profiles ride on free tiers or a subscription you may already
have. Budget roughly **$10 to $30 a month** and set a hard spend alert from day one.

---

## What to skip (unless you specifically need it)

- A local LLM on the VPS (no GPU; free cloud tiers cover the light profiles).
- A self-hosted git server, a secrets-manager service, an app/web stack — none of this is the second brain.
- A separate search-index / vector database for the wiki, until you're past ~1,000 pages.
- Any profile you don't have a concrete daily use for. Start with one, earn the next.
