# Mac setup

Everything outside the repo itself: Claude Code mods, statusline, VS Code launcher + keybindings, and one
memory store. Run once from the repo root (dry run first):

```bash
bash setup/install-mac.sh --dry-run
bash setup/install-mac.sh
```

Safe to re-run. It never replaces an existing settings key or a key that's already bound (it prints the
kit binding instead), backs up every JSON file it edits, and prints a pass/fail checklist.

| Step | What it does |
|---|---|
| Prereqs | Checks `claude`, `python3`, `jq` (statusline), Obsidian (Belki UI) |
| Mods | Adds `setup/mods` as the `work-mods` marketplace and installs every listed mod |
| Claude settings | Adds `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` (mods need it), `BELKI_HELPER` + `WORK_BRAIN_DIR` (the Belki band), and the statusline |
| Statusline | Copies `claude/statusline.sh` to `~/.claude/` if absent (model, effort, context %, rate limits, cache) |
| VS Code | Adds `claudeCode.useTerminal` + the terminal keybindings (Cmd+A clears the prompt line, Ctrl+Z can't suspend Claude) to the default profile; installs the launcher extension unpacked |
| Memory | Symlinks Claude Code's auto-memory folder for this repo to `memory/`, so the harness, the `reflect` mod, and the router share one versioned store |

**Manual steps:** install Obsidian, open the repo as a vault, enable community plugins, install **belki**
(the repo already lists it in `.obsidian/community-plugins.json`). Repo-level VS Code settings
(`.vscode/settings.json`) turn on Claude auto-launch for this folder only.

## Mods

| Mod | What it shows | Note |
|---|---|---|
| belki-band | Belki overdue · due today · to chase, above the prompt | Own build. Reads `BELKI_HELPER` |
| diff-fold | Folds diffs and long command output to one line | Own build |
| prismantis | Themed rendering: tables, alerts, diagrams | MIT (Nahum Litvin); bundles Prism + beautiful-mermaid, see `docs/THIRD_PARTY_NOTICES.md` |
| agent-radar | Live line per running subagent; `/radar` | MIT (Hamza Zafar, claude-code-mods) |
| review-watch | Live line per running review | MIT (Hamza Zafar) |
| session-tracker | Other Claude sessions in this repo | Own build |
| md-preview | Rendered pane of edited Markdown; `/md` | MIT (Hamza Zafar). Patched: no GitHub rendering, no remote images/fonts/media |
| next-steps | 2-3 suggested next prompts (one Haiku call per turn) | MIT (Hamza Zafar). Costs tokens: turn off under the metered profile |
| reflect | Turns corrections into feedback memories | MIT (Bayram Annakov), ported; one Haiku check per prompt |

**Known:** on Claude Code 2.1.310, `claude plugin test` fails 8 reflect tests and 19 md-preview tests. The
identical source copies fail the same way, so this is test-kit drift, not a kit change. Check both mods
work before relying on them.

Update a mod: edit it under `setup/mods/<name>`, bump its `version` in `setup/mods/.claude-plugin/marketplace.json`,
then `claude plugin update <name>@work-mods`.
