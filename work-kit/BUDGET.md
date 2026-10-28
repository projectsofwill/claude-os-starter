# Budget profiles

The router's `Budget profile:` line picks one. Set it on day 1, once you know how Claude is paid for.

| | **subscription** (seat with usage limits) | **metered** (API key, pay per token) |
|---|---|---|
| Everyday model | Sonnet @ medium | Sonnet @ medium |
| Escalate to Opus | When a trigger fires (below); on a borderline call, escalate | Only when asked, or for irreversible / RevOps-gate work |
| Haiku | Retrieval and lookups | Retrieval, lookups, **all transcript extraction** |
| Subagent fan-out | OK for 2+ independent threads | Not automatic. Ask first |
| Sessions | Long sessions fine | `/clear` between unrelated tasks (long sessions resend history every turn) |
| Check spend | Watch usage limits | `/usage-cost --days 7` weekly. Set a spend alert in the console on day 1 |

**Opus triggers:** irreversible or data-destructive work, RevOps-gate changes, ambiguous requirements,
architecture decisions, heavy multi-source synthesis, final pass on anything leadership- or customer-facing.

**Either profile:**
- Keep always-loaded context small. `CLAUDE.md` stays a router; detail lives in files read on demand.
- Meeting ingest: Haiku extracts, Sonnet writes, one batch per day.
- Prefer grep and targeted reads over reading whole folders.
- Model IDs can differ if the company routes Claude through a cloud provider or internal gateway. Use the
  aliases (`sonnet`, `opus`, `haiku`) where the tool accepts them.

**Benchmark:** a heavy personal setup can reach hundreds of dollars a day at API rates, so habits formed on a
flat plan are expensive on a metered key. Run `/usage-cost --days 7` after the first week and adjust.
