---
name: usage-cost
description: Calculate the API-equivalent (pay-as-you-go) dollar cost of Claude Code token usage from local transcripts, broken down by model, and compare it against flat subscription plans. Use when the user asks how much their usage would cost on the API / metered / pay-as-you-go, their token spend, the cost of a session / day / week, or whether their Max plan is worth it.
model: sonnet
effort: medium
context: fork
---

# Usage cost

Estimates what the user's Claude Code usage would have cost if billed per token on the API/Console, by parsing the local transcript JSONL files (`~/.claude/projects/**/*.jsonl`) and pricing the recorded token counts (input, output, cache read, cache write) at current per-token rates. On a flat Max subscription the user pays the monthly fee regardless; this surfaces the metered-equivalent so they can see the value they're getting (or decide between plans).

## How to run

Run the bundled script with `python3` (it has no dependencies):

```
python3 .claude/skills/usage-cost/cost.py [options]
```

Options:
- `--since YYYY-MM-DD` (or `YYYYMMDD`) — from a date onward
- `--days N` — last N days
- `--today` — today only
- `--project SUBSTRING` — only project dirs whose path contains the substring (e.g. the work repo's folder name)
- `--cache-ttl 1h` — price cache writes at the 1-hour rate instead of the default 5-minute rate
- `--blocks` — replace the model table with a **5-hour billing window** view. Shows one row per rolling block: start time (UTC), status (ACTIVE with time remaining, or done with elapsed), total tokens, cost, and models used. The active block also shows a rough projected token total based on current burn rate. Respects all window/project filters.
- `--by-session` — append an **exact** per-session breakdown: cost bucketed by `sessionId`, every token counted once, each row labeled with the session's first prose ask (or aiTitle/lastPrompt when present). Sorted by cost, top 25 shown, the rest rolled into one line. Use when the user asks "which session/work cost what."
- `--by-area` — append an **approximate** per-sub-project breakdown. There is only one transcript dir per workspace, so sub-folders (e.g. `meetings/`, `projects/*`) can't be told apart natively; this heuristic attributes a turn's cost to an area only by the file paths in that same assistant message. Reasoning/text-only turns carry no path and land in `(unattributed)` — typically ~75-80% of cost. The section prints how much it could actually attribute. Present it as proportions, never precise dollars.

Both `--by-session` and `--by-area` compose with the window/`--project` filters and print **after** the model table; the default output is unchanged when neither is passed. Both sections reconcile to the model-table TOTAL (the script prints a warning line if they ever don't).

Default (no args) = all time, all projects.

Pick the window from what the user asked ("this week" → `--days 7`, "today" → `--today`, "the work repo" → `--project <folder>`). If they just say "my usage," run it with no args and offer to narrow. Add `--by-session` when they ask which work/session cost what; add `--by-area` (with the heuristic caveat) when they ask to split cost across sub-projects.

## Presenting the result

The script prints a per-model table plus the total. When you relay it:
- Lead with the headline: **API-equivalent cost = $X** for the window.
- Note the dominant driver if one model or token type dominates (long agentic sessions are usually cache-read heavy; that's prompt caching saving ~10x vs full input price — worth pointing out).
- **Metered (API key) profile:** this number is the real bill, not an equivalent. Compare it to the week's budget in `BUDGET.md` and name the biggest driver (session or model).
- **Subscription profile:** frame against the flat plans: Max 5x ~$100/mo, Max 20x ~$200/mo (approximate commercial prices, not from the API reference). For heavy Opus use the metered number often exceeds a full month of Max, i.e. the flat plan is the better value.
- Enterprise is **not** a usage comparison — it's a negotiated per-seat license; don't try to quote it from token usage.

## Caveats to state

- Per-token rates live in the `RATES` dict at the top of `cost.py`; update them if pricing changes (check the `claude-api` skill for current rates).
- Cache-write cost assumes the 5-minute TTL by default; pass `--cache-ttl 1h` if the user's workload uses 1-hour caching (raises the cache-write portion).
- The number is the metered API/Console cost, not what the user actually paid on a subscription.
- `--by-area` is a heuristic, not an accounting: most cost is reasoning/text with no file op in the message, so the `(unattributed)` bucket usually dominates and the attributed slice is a rough proportion. `--by-session` is exact (every token counted once, reconciled to the total).

## Not /insights

`/insights` is a built-in Claude Code command and can't be modified. This skill is the standalone, on-demand cost view; it complements `/insights` (which covers behavior/patterns, not metered cost).
