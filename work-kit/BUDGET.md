# Budget profiles

The router's `Budget profile:` line picks one. Set it on day 1, once you know how Claude is paid for.

| | **subscription** (seat with usage limits) | **metered** (API key, pay per token) |
|---|---|---|
| Everyday model | Sonnet @ medium | Sonnet @ medium |
| Escalate to Opus | When a trigger fires (below); on a borderline call, escalate | Only when asked, or for irreversible / RevOps-gate work |
| Haiku | Retrieval and lookups | Retrieval, lookups, **all transcript extraction** |
| Subagent fan-out | OK for 2+ independent threads | Not automatic. Ask first |
| Sessions | Long sessions fine | `/clear` between unrelated tasks (long sessions resend history every turn) |
| Check spend | Watch usage limits | Statusline spend line (below); `/usage-cost --days 7` weekly. Set a spend alert in the console on day 1 |
| Settings | Installer defaults | Add the metered settings below to `~/.claude/settings.json` |

**Opus triggers:** irreversible or data-destructive work, RevOps-gate changes, ambiguous requirements,
architecture decisions, heavy multi-source synthesis, final pass on anything leadership- or customer-facing.

**Either profile:**
- Keep always-loaded context small. `CLAUDE.md` stays a router; detail lives in files read on demand.
- Meeting ingest: Haiku extracts, Sonnet writes, one batch per day.
- Prefer grep and targeted reads over reading whole folders.
- Model IDs can differ if the company routes Claude through a cloud provider or internal gateway. Use the
  aliases (`sonnet`, `opus`, `haiku`) where the tool accepts them.

## Metered settings

The installer leaves these out because they depend on the plan. On a metered plan, merge them into
`~/.claude/settings.json` on day 1 (the two `WORK_SPEND_*` values are your cap in dollars and the day of
the month it resets; drop them if there's no cap):

```json
{
  "model": "sonnet",
  "effortLevel": "medium",
  "maxEffortLevel": "high",
  "promptCacheTtl": "1h",
  "promptSuggestionEnabled": false,
  "awaySummaryEnabled": false,
  "env": { "WORK_SPEND_CAP_USD": "100", "WORK_SPEND_RESET_DAY": "30" }
}
```

- `model` / `effortLevel`: every session starts on Sonnet at medium. Opus is a deliberate `/model opus`.
  `maxEffortLevel` stops an accidental xhigh/max: thinking bills as output tokens, the expensive kind.
- `promptCacheTtl: "1h"`: metered plans default to a 5-minute cache, so any 5-60 minute break (a meeting)
  makes the next message reprocess the whole conversation. One-hour writes cost more (2x input vs 1.25x),
  but a replay of two weeks of real sessions came out ~7% cheaper on 1h with only 2% of turns after such
  a break. Check the miss count in `/usage` ("Prompt cache (main)") after week one.
- Prompt suggestions and the session recap each send a background request (after every reply / on your
  return). Small, but they add up across a day.
- Leave idle compaction on: on the 1h cache it summarizes a long idle conversation before the cache
  expires, so your next message sends the summary instead of the whole history.
- `WORK_SPEND_*` turns on the statusline spend line: `$23/$100 20d` = estimated spend this cycle, cap, days
  to reset. Green on pace, yellow ahead of an even pace, red at 80%. It's a list-price estimate of this
  machine's Claude Code use only (not claude.ai chat, not other machines); the admin console has the real
  number.

**Habits that matter more than any file trim:**
- `/clear` between unrelated tasks. Every turn re-reads the whole conversation, so cost grows with length.
- Pick model and effort at the start. Switching model mid-session rebuilds the cache from scratch.
- Batch small asks into one message instead of five round trips.
- Keep connectors (CRM, Slack MCP servers) to the ones you use; their tool definitions ride along every turn.

**Benchmark:** Anthropic's cost docs put the enterprise average at about $13 per developer per active day.
A $100/month cap is about $5 a workday, so the habits above aren't optional. Run `/usage-cost --days 7`
after the first week and adjust.
