# Tools & services (what I actually use)

The build map deliberately talks in terms of *patterns* so it doesn't rot when a tool changes. This file
is the opposite: the concrete answer to "what service do I use for this, exactly." These are my picks.
None of them is load-bearing in the way the patterns are, so swap freely. Where there's an obvious
cheaper or simpler alternative, I've named it. Links go to each tool's GitHub repo or official site.

Each section maps to a step in `build-map.md`.

---

## The foundation (before any step)

- **[Claude Code](https://claude.com/claude-code)** (Anthropic) — the desk-side tool the whole OS is built
  on. It's a CLI that also runs in VS Code and JetBrains. Everything below is me directing Claude Code. I
  run it on a **Claude Max** subscription so usage isn't metered per-token; a Pro plan or the API also works.
- **[VS Code](https://code.visualstudio.com)** — where I run Claude Code. Free. Any terminal works too.

If you do nothing else, this plus Steps 1 to 2 is a real upgrade.

---

## Step 1 to 2 — Context & Memory

- **Plain markdown files.** No service, no app required. This is the point.
- **An editor you already have** (VS Code, or [Obsidian](https://obsidian.md) if you do Step 5). The files
  are just text.

Cost: $0. Don't overthink this step's tooling; the value is the content, not the tool.

---

## Step 3 — Portability (sync)

- **[Git](https://git-scm.com)** — version control and the real backbone. Free.
- **[GitHub](https://github.com)** — where the repos live and how machines sync. Free for private repos.
  - *Alternatives:* [GitLab](https://gitlab.com), or any git host. The pattern doesn't care.
- **A sync script** — I wrote a small Python script that pulls/pushes the repos on a schedule. There's no
  product to buy here; it's ~100 lines of glue. (A plain `git pull && git push` on a timer is the MVP.)

Cost: $0.

---

## Step 4 — Capabilities (skills)

- **Claude Code skills** — reusable workflows you invoke as slash commands (e.g. `/wrap-up`, `/resume`).
  Built into Claude Code. No external service.

Cost: $0 beyond your Claude plan.

---

## Step 5 — The second brain (wiki)

- **[Obsidian](https://obsidian.md)** — the lens over the markdown wiki. Free for personal use. Configure
  it with **`Use [[Wikilinks]]` turned OFF** (`Settings → Files & Links → Use [[Wikilinks]]`): this makes
  Obsidian write standard markdown links (`[page-name](page-name.md)`) instead of its own syntax, so your
  links render in every tool — GitHub, VS Code, agents — without Obsidian installed.
- **[Obsidian Web Clipper](https://github.com/obsidianmd/obsidian-clipper)** — the official browser
  extension I use to capture articles into the vault. Free. It also pulls **YouTube transcripts** when you
  clip a video.
- **[`youtube-transcript-api`](https://github.com/jdepoix/youtube-transcript-api)** (a Python package) —
  for fetching transcripts outside the clipper. Free.

Cost: $0 to start. Obsidian Sync is a paid add-on and you don't strictly need it (Step 3's git already
syncs the vault on desktop). I do pay for it because it pairs with the Obsidian mobile app, whose web
clipper works well with mobile Safari for capturing on my phone. Optional.

The full capture-to-ingest workflow and its decisions (PDF handling, the YouTube frame-analysis gate, the
`/ingest` skill) are in `../deep-dives/wiki-deep-dive.md`.

---

## Step 6 — Cadence (scheduled automations)

- **A scheduler you already have** — this is the key point: Step 6 needs no server.
  - macOS: **launchd** (what I started on). Linux: **cron** or **systemd timers**. Windows: **Task Scheduler**.
- **[Perplexity API](https://docs.perplexity.ai)** — research synthesis for my weekly newsletter (it does
  the "go read the web and summarize" part). Paid, usage-based; modest at weekly cadence.
  - *Alternative:* have Claude do the synthesis directly and skip Perplexity.
- **[Gmail API](https://developers.google.com/gmail/api)** (Google Cloud, free tier) — to create the email
  **draft**. The automation never sends; I do.
- **[GitHub Pages](https://pages.github.com)** (free) — hosts the public newsletter archive.

Cost: a few dollars a month if you use Perplexity; otherwise ~$0.

---

## Step 7 — The always-on agent (Hermes)

This is the only tier with real recurring cost and setup. Full sequence is in `hermes-setup-runbook.md`.

**Infrastructure**

- **VPS: [Hostinger](https://www.hostinger.com/vps-hosting)** (I run a KVM 2: 2 vCPU, 8 GB RAM, Ubuntu LTS).
  Roughly $7 to $10/month.
  - *Alternatives:* **[Hetzner](https://www.hetzner.com)** (cheaper in the EU),
    **[DigitalOcean](https://www.digitalocean.com)** (simpler dashboard). Any Linux VPS works.
- **[Docker](https://www.docker.com) + Docker Compose** — runs the stack. Free, pre-installable on the VPS.
- **[Tailscale](https://tailscale.com)** — the private VPN. The VPS dashboard and SSH are bound to it, never
  the public internet. Free personal tier.

**The agent**

- **[Hermes](https://github.com/NousResearch/hermes-agent)** (NousResearch) — the self-hostable agent
  framework. Open source. *Alternative:* any always-on agent host; the Step 7 principles are what matter,
  not Hermes specifically.
- **[Telegram](https://telegram.org)** — how I talk to the agent from my phone. Free. Create a bot via
  **[BotFather](https://t.me/BotFather)**, and set the allow-list to your single user ID.
- **[SearXNG](https://github.com/searxng/searxng)** — self-hosted meta-search so the researcher can find
  sources without a paid search key. Free.
- **[Postgres](https://www.postgresql.org)** — the database for structured personal data (workouts, etc.).
  Free, runs in a container.

**Models (the agent's brains)**

- **GPT-5.6 via [OpenAI Codex](https://github.com/openai/codex)** (ChatGPT Plus OAuth) — my primary across
  the profiles: the orchestrator and the newsletter synthesis. At the time of writing this runs under my
  existing ChatGPT Plus subscription with no extra per-token cost (these OAuth arrangements change, so
  check the current terms before you count on it).
- **[Claude](https://claude.com)** (Anthropic) — the quality model for the morning brief, where it matters most.

**News sources for the researcher** *(all optional, add the ones you care about)*

- **Hacker News:** the free [Algolia HN API](https://hn.algolia.com/api).
- **Reddit:** scraped from old.reddit.com (the official API is gated behind an approval process). *(Caution: scraping is brittle — it can break whenever the site's HTML changes — so treat this as optional.)*
- **GitHub releases:** the GitHub API, to watch tools you depend on.
- **Newsletters:** Gmail labels + filter.
- **Twitter/X:** a low-cost scraping API (I use GetXAPI, ~$1/month). Optional. *(Caution: scraping social platforms is brittle and ToS-sensitive — it can violate their terms — so do it knowingly.)*

*Recommendation: start with the robust feeds (RSS, Hacker News, GitHub releases) before adding any scraping.*

*How those sources actually get fetched* (the three-tier residential-relay → direct → Firecrawl escalation,
and why a [Firecrawl](https://github.com/mendableai/firecrawl) rescue tier exists) is in
`../deep-dives/researcher-deep-dive.md`.

**Secrets & connections** *(new to handling keys safely? read `secrets-101.md` first — it's two rules and a one-line check.)*

- **[1Password](https://1password.com)** — where I keep the keys, SSH keys, and OAuth files. Any password
  manager works.
- **[dotenvx](https://github.com/dotenvx/dotenvx)** — encrypts `.env` files so config can live in git
  without exposing secrets. Free.
- **[Google Cloud](https://console.cloud.google.com)** (free tier) — the OAuth project behind the Gmail +
  Google Calendar access the EA uses. Scoped read-only.
  - *(Deferred option: a self-hosted secrets manager like [Infisical](https://github.com/Infisical/infisical),
    once the stack is stable. Not needed to start.)*

**Rough Step 7 cost:** ~$10 to $30/month all in (VPS plus the one quality model; most else rides on free
tiers or subscriptions you may already have). Set a hard spend alert from day one.

---

## The discipline layer (throughout)

- **[Codex](https://github.com/openai/codex)** (OpenAI's CLI, running GPT-5.6 on a ChatGPT Plus plan) — my
  **second-model review gate**. Before I run anything risky, a *different* model family stress-tests it.
  Using a different vendor than Claude is deliberate: independent error modes, so it catches what Claude's
  own review would miss.
  - *Alternative:* any capable model from a different vendor than your primary. The point is independence,
    not Codex specifically.
- **`/code-review`** (built into Claude Code) — for reviewing a diff before it lands.

Cost: covered by a ChatGPT Plus subscription (~$20/month) if you use Codex.

See `../deep-dives/optimizations.md` for the quality-of-life and cost optimizations I layer on top (Wispr
Flow, model routing, the review gate, shared agent memory).

---

## The shortest path to "useful"

If you want the cheapest possible start that still delivers:

1. **Claude Code** on any Claude plan + **VS Code**. (Steps 1, 2, 4.)
2. **Git + GitHub**, free. (Step 3.)
3. **Obsidian + Web Clipper**, free. (Step 5.)

That's a complete second brain for the price of your Claude subscription. Steps 6 and 7 add scheduling and
the always-on agent only when you want them, and only Step 7 adds real monthly cost.
