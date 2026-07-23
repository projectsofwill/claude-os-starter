# Additional resources — where the ideas and the inputs come from

The build map tells you *how* I built this. This file tells you *where it comes from*: the thinkers
whose ideas the whole thing rests on, and the actual feeds my researcher crawls to keep the second
brain fed. Treat it as a **starter follow-list, not gospel.** My inputs skew hard toward AI tooling and
RevOps because that's my life; the value for you is the *shape* of the list (a few high-signal people, a
few crawlable feeds, one tight relevance filter), not my exact picks. Swap in your own domains and the
machine works the same.

Every link below I verified before writing it down. Where I couldn't confirm a canonical URL I left the
name without one rather than guess.

---

## People and ideas behind the build

Two people shaped this more than anyone else, and they're the two worth following:

- **Nate Herk** — the **Four C's** (Context, Connections, Capabilities, Cadence) and the "AIOS" framing
  that the entire build map is organized around. If the four-layer priority order clicked for you, it's
  his. ([youtube.com/@nateherk](https://www.youtube.com/@nateherk))
- **Andrej Karpathy** — **context engineering**: "the delicate art of filling the context window just
  right." Also the seed of the plain-markdown LLM wiki instead of a vector DB (skip embeddings until scale
  forces it). Keep your always-on file lean. ([karpathy.ai](https://karpathy.ai/))

The build leans on a few other well-known ideas too — write loops not prompts, the four types of memory,
queues over daemons, file over app — but you don't need to chase down every source. They're listed with
their attributions in `build-map.md`'s principles table if you're curious.

---

## What my researcher crawls

This is the actual source list my researcher samples from (the full pipeline is in
`researcher-deep-dive.md`). It lives in a plain, editable sources file — **a friend should gut it and put
their own domains in.** Mine is AI-and-RevOps-heavy; yours should match what *you* read.

**Subreddits** (observed over time, age-matched selection — see the deep dive):

- [reddit.com/r/ClaudeCode](https://reddit.com/r/ClaudeCode)
- [reddit.com/r/mcp](https://reddit.com/r/mcp)
- [reddit.com/r/hermesagent](https://reddit.com/r/hermesagent)
- [reddit.com/r/LocalLLaMA](https://reddit.com/r/LocalLLaMA)
- [reddit.com/r/OpenAI](https://reddit.com/r/OpenAI)

**YouTube channels** (channel RSS feed → transcript, so the agent reads the talk, not the video):

- Nate Herk ([youtube.com/@nateherk](https://www.youtube.com/@nateherk)) — also the source of the Four C's
  framing above.
- Jack ([youtube.com/@Itssssss_Jack](https://www.youtube.com/@Itssssss_Jack))

**Other feeds:**

- **LessWrong** — RSS from [lesswrong.com](https://www.lesswrong.com/) (AI-safety / rationality long-form).
- **Hacker News** front page — pulled via the free Algolia API, relevance-filtered against the keyword
  list before anything gets fetched. ([news.ycombinator.com](https://news.ycombinator.com/))
- **SearXNG web/science queries** — a self-hosted meta-search engine I keep a *pool* of queries for and
  sample a few per run, rotating so it stays fresh. The topics I rotate through:
  agentic AI system architecture · multi-agent orchestration patterns · LLM prompt engineering · AI agent
  failure modes · context engineering · RAG architecture tradeoffs · MCP production deployment · LLM
  security / red-teaming · AI in RevOps / GTM · agentic coding workflows · second-brain workflows.

---

## The relevance filter is what makes a crawl worth running

A crawl without a relevance filter is just noise on a schedule. Before anything gets fetched or judged,
titles are prefiltered against a **keyword list that defines "worth keeping."** Mine centers on:

> Claude / Anthropic · MCP (model context protocol) · agents / agentic · LLMs · Claude Code · Opus /
> Sonnet · Hermes / Nous · Obsidian · RevOps / GTM · RAG · prompting · OpenAI / Codex / GPT · Cursor /
> Copilot · automation.

That list is the single most personal thing in the whole researcher. **Write your own before you point a
crawl at anything** — the keywords *are* the difference between a feed that surfaces the one post you
needed and a feed you stop reading after a week. Define them, then let the lint and the classifier
enforce them.
