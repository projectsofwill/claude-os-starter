# The researcher, in depth (the rabbit hole)

Optional, and the deepest rabbit hole in this whole setup. The researcher is the piece that makes the
agent feel like it's keeping up with the world *for* you: it finds sources, reads them, judges what
matters, and files the good stuff. It's also the part with the most moving parts and the highest risk,
because it reads the open, hostile web. So it carries the most safety machinery.

Most people should not build this, or should build only the smallest slice of it. Read this if you've
decided you want the full thing and want to see how mine actually works. The phased runbook
(`hermes-setup-runbook.md`, Phase 3) is the "just enough" version; this is the rabbit hole.

---

## The one principle that shapes everything: untrusted input is hostile

The researcher reads Reddit, forums, articles, and video transcripts. Any of that text can carry a
**prompt injection** (content crafted to hijack an agent that reads it). So the entire design follows one
rule: **nothing the researcher touches is trusted until a human has looked at it.** Every choice below is
downstream of that.

## The shape: deterministic scripts plus tool-less agents

The counterintuitive part: the *agents* in this pipeline have **no tools**. The fetching, scraping, and
file-writing are done by plain deterministic scripts I control. The model's only jobs are (a) strip and
flag injection, and (b) judge relevance. An agent with no tools cannot be tricked into doing something
dangerous, because it cannot *do* anything except return text. The scripts do the doing; the model does
the thinking. That split is the whole safety story.

---

## The pipeline, stage by stage

### 1. Discovery — find candidate links

A discovery script reads a plain, editable sources file and emits candidate URLs. Each source type is a
different angle, and they're blind to each other (one search angle never finds everything):

- **SearXNG** — self-hosted meta-search, kept loopback-only on the VPS. I keep a *pool* of queries and
  sample a few per run, rotating over a few days so it stays fresh without hammering.
- **Hacker News** — the free Algolia front-page API (one request, has titles to prefilter on).
- **RSS / Atom feeds** — blogs and sites that publish them.
- **GitHub releases** — each repo's `releases.atom`, to watch tools I depend on (no token needed).
- **Reddit** — a separate, more involved pipeline (see below).

Titles are prefiltered against a relevance keyword list before anything gets fetched, so the expensive
stages only see plausible candidates. Low-risk feeds (RSS, HN, GitHub, SearXNG) are fetched **direct from
the VPS**; only per-article fetches use the residential relay (next stage). That split protects my home IP
budget.

### 2. Fetch — three tiers, because the web fights back

Getting the actual page is the hard part: datacenter IPs get blocked, and HTML is messy. So fetching is a
**three-tier escalation**, and every tier returns the same JSON contract so the rest of the pipeline
doesn't care which one succeeded:

1. **The residential relay (default).** *(Caution: this is advanced infrastructure — don't build it first; start with direct fetching and add the relay only once sites start blocking you.)* A tiny service on my home machine (a residential IP) does the
   fetch, because a VPS's datacenter IP gets 403'd by Reddit, Medium, YouTube, and others. The VPS asks
   home to fetch, over the private VPN (Tailscale), with per-domain rate limits and backoff so it stays
   polite. The fetcher itself is hardened: SSRF guards, IPv4-only, a content-type allowlist, redirect
   caps.
2. **Direct from the VPS (fallback).** If the relay is down, try fetching straight from the VPS. Fine for
   anything that doesn't block datacenter IPs.
3. **Firecrawl (last resort).** When the relay is throttling (my home IP is backing off) or relay and
   direct both fail, **Firecrawl** does the fetch from *its own* clean IP and returns clean markdown,
   extracting pages the raw fetcher choked on. It's a paid service, so it's deliberately last: it draws on
   a capped monthly credit budget and is charged only on a real successful scrape, so dead links cost
   nothing. This is the one place Firecrawl lives in my stack — a rescue tier, not the workhorse.

### 3. The dual-LLM firewall — the safety core

Two separate model passes, each a tool-less agent, each handed its full contract in the prompt:

- **Sanitizer** — extracts the readable text and flags prompt injection. The bar is tuned to *hijack
  only*: it flags content that tries to make the AI disobey, change role, reveal its prompt, exfiltrate,
  or call a tool, and it deliberately does **not** flag benign navigation hints, docs, code, or
  changelogs. Over-quarantining is its own failure mode.
- **Classifier** — judges relevance against a concrete "buildability test" (does this change a tool I use,
  give me a reusable pattern, or move a decision I'm weighing?) and sorts into four tiers. Judge substance,
  not topic: "mentions Claude" is not relevance.

Calling these a "firewall" is the point: untrusted text goes in, vetted inert data comes out.

### 4. Capture — write inert files, with provenance

A deterministic writer drops the survivors as plain markdown into a `raw/` folder, stamped with provenance
(the source URL, and which fetch tier got it: relay, direct, or firecrawl). These are **data, not
instructions** — nothing executes. The writer is **path-allowlisted** so it can only ever write to `raw/`,
never to the curated wiki. Then it commits and pushes (just `raw/`). *(Caution: an unattended process writing to GitHub is a trust boundary — use a dedicated repo/path that carries no secrets, and review its output before it merges into your main knowledge base.)*

Before any of this, everything is **deduped** against what's already in `raw/` *and* the ingested wiki, so
the same source never gets captured twice (the dedup registry even catches things I clipped by hand).

### 5. Human-gated ingest — the real trust boundary

This is the part that actually makes it safe. The VPS researcher **never writes to my knowledge wiki**. It
only drops inert captures into `raw/`. On my **laptop**, when I run the ingest (see `wiki-deep-dive.md`
for the full ingest procedure):

- A **pre-ingest safety gate** runs first: a deterministic, regex-only scan (it can't be injected because
  it's not a model) that quarantines any researcher-authored capture carrying injection markers,
  fail-closed, before any model reads a single capture.
- Researcher-authored captures are **treated as hostile by default**: extract their factual claims as data
  only, never follow any instruction found inside one, and eyeball the batch before promoting anything to
  the wiki.

The trust boundary isn't the VPS. It's my laptop, with me in the loop. The server can only ever hand me
inert files to look at.

### The Reddit sub-pipeline (why it's special)

*(Caution: this is a "later only" refinement — start with RSS, Hacker News, and GitHub releases, and add Reddit only once you feel the lack of it.)* Reddit is worth a note because the obvious approach doesn't work. The official API is gated behind a
moderation-use-case approval, and the `.json` endpoints 403 automated clients even from a residential IP.
So I scrape **old.reddit.com** HTML (server-rendered, has scores and threaded comments) through the relay.
Selection isn't a naive "top of the day": a small SQLite DB records observations over time and builds
**per-subreddit, age-matched baselines**, so a post is judged against what's normal *for that sub at that
age*, with a subscriber-count floor for cold starts and a keyword "niche-rescue" so a small-but-on-topic
post isn't drowned out. That's what surfaced a 16-upvote post a popularity filter would have dropped.

---

## The services (what I use)

Confirm and swap these to taste; none is load-bearing the way the *architecture* is.

| Service | Stage | What it does | Cost | Alternative |
|---|---|---|---|---|
| **SearXNG** | discovery | self-hosted meta-search (loopback) | free (self-host) | Brave Search API, SerpAPI |
| **HN Algolia API** | discovery | Hacker News front page | free | — |
| **RSS / Atom** | discovery | blog + site feeds | free | — |
| **GitHub API** | discovery | watch tool releases | free | — |
| **old.reddit scrape + SQLite** | discovery | Reddit threads, age-matched selection | free | Reddit API (needs approval) |
| **home fetch relay** | fetch tier 1 | residential-IP fetch over Tailscale | free (self-host) | a paid residential proxy (e.g. IPRoyal) |
| **direct VPS fetch** | fetch tier 2 | hardened from-scratch fetcher | free | — |
| **Firecrawl** | fetch tier 3 | clean-markdown rescue from its own IP | paid (capped credits) | a residential proxy + your own extractor |
| **two model passes** | firewall | sanitize + classify | your model cost | — |

---

## Honest take: build the smallest version first

This is months of iteration, not a weekend. You do **not** need most of it to get value. The minimum
useful researcher is:

1. **One source** (say Hacker News or a single RSS feed).
2. **One fetch** (direct is fine to start; add the relay or Firecrawl only when sites start blocking you).
3. **One model pass** to judge relevance.
4. **Write the survivors to a file** you actually read.

That's it. Add another source, the dual-LLM firewall, the three-tier fetch, or the human-gated ingest
pipeline only when you feel the lack of it. The full pipeline above earns its complexity because I read a
lot and the safety matters to me. Yours should grow to fit what you actually read, not copy mine wholesale.
