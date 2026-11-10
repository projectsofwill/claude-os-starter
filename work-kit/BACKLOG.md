# Backlog (day 30+)

Captured so they don't get lost. Build each one only when a real need shows up.

| Item | Build when |
|---|---|
| CRM connector, **read-only** first (HubSpot/Salesforce MCP) | AI policy allows it and a weekly question needs live CRM data |
| Team task tool sync (Asana/Jira/Linear): mirror Belki tasks others need to see | You know what the team uses and a task needs to be visible |
| Deadline notifications (macOS banner from `belki.py summary`) | Overdue items slip despite the sidebar + band |
| `/promote` skill (format a note for the company wiki) | You know which wiki and connector the company uses |
| `/assess` for GTM tools ("does tool X fit our stack?") | First tool evaluation lands on your desk |
| Weekly brief (meetings + tasks + STATUS → one page) | 4+ weeks of meeting notes exist |
| Request-intake log (ad hoc asks, who, SLA) | Ad hoc requests start slipping |
| Playbook: deal health / slip signals | Pipeline reviews are recurring and the CRM connector exists |
| Playbook: forecast hygiene (category snapshots, push vs slip) | You own or support the forecast call |
| Playbook: closed-lost analysis (dropdown reason vs evidence) | A quarter of closed-lost data + call transcripts are reachable |
| Recall layer over notes: a local search index first (SQLite FTS5: BM25 ranking built in, ships with Python's `sqlite3`, no install), then episodic memory (e.g. a self-hosted Hindsight on the laptop, LLM calls on the company account) | About 200+ notes, or "didn't we decide X?" stops getting answered by grep |
| Folder-index checker (fails a commit when an `index.md` drifts) | Indexes start going stale by hand |
| Obsidian as a viewer | You'd actually browse the graph (IT approval needed) |
| `/spinoff` + `/handback` (parallel sessions) | You regularly run two sessions at once |
| Hygiene pass (stale STATUS, bloated memory index) | Monthly, once the repo has a month of use |
| Process inventory: one table in `revops/` (process, owner, frequency, AI level, value 1-5, pain 1-5, consumes/produces); high value + high pain = pilot candidate. Pattern: ICM Context map form (RinDig/icm-architect), table only, no folder graph | `stack-map.md` is filled in and you're choosing a first automation |
| Stage contracts for a recurring workstream (inputs, job, output, check per step). Pattern: ICM | A `## Runbook` has run about 3 cycles and still misses steps |
| Document claim sourcing: a source register with page/section locators, plus a flag on figures never checked against their source. Pattern: familiar (familiar-md/familiar); rebuild it, don't install it | A wrong or untraceable claim from a long document (comp plan, pricing policy, order form), or a workstream resting on several of them |

Playbooks are rebuilt from first principles against the company's real stack and data. Nothing is copied
from personal projects. Starting hypotheses for each live in `revops/idea-bank.md`.
